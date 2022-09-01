"""Train functions for the Automatic Speech Recognition models."""

import typing as tp

import numpy as np
import torch
import torch.nn as nn
from omegaconf import DictConfig
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import DataLoader
from tqdm import tqdm

from ..inference import get_metrics_from_ctc_decode
from ..loss import CTCLossWrapper
from ...utils import move_batch_to_device, save_architecture
from ....data.preprocess.text import BaseTextEncoder
from ....logging.wandb import WBLogger


def _train_epoch(
    config: DictConfig,
    model: nn.Module,
    optimizer: Optimizer,
    scheduler: _LRScheduler,
    criterion: CTCLossWrapper,
    dataloader: DataLoader,
    text_encoder: BaseTextEncoder,
    wb: WBLogger,
    device: torch.device,
    skip_oom: bool,
) -> tp.Tuple[float, tp.List[float], tp.List[float]]:
    model.train()
    train_loss = 0
    train_cers = []
    train_wers = []
    for batch_idx, batch in enumerate(tqdm(dataloader, desc="train", total=len(dataloader))):
        try:
            batch = move_batch_to_device(
                batch,
                device,
                fields_on_device=["transforms", "encoded_texts"],
            )

            lr = scheduler.get_lr()[0]

            optimizer.zero_grad()
            probs = model(batch["transforms"])

            loss = criterion(
                log_probs=probs.permute(2, 0, 1).log(),
                targets=batch["encoded_texts"],
                input_lengths=batch["char_probs_lengths"],
                target_lengths=batch["encoded_text_lengths"],
            )
            train_loss += loss.item()
            loss.backward()

            grad_norm = nn.utils.clip_grad_norm_(
                model.parameters(),
                config.training.grad_clip_val,
            )
            optimizer.step()
            scheduler.step()

            wb.increment_step(part="train")
            if batch_idx % config.training.log_every_n_steps == 0:
                metrics = {
                    "learning rate": lr,
                    "loss on batch": loss.item(),
                    "gradient norm": grad_norm.item(),
                }
                wb.log_data(metrics, level="step", part="train")
                wb.log_random_audio(batch, level="step", part="train")

            cers, wers = get_metrics_from_ctc_decode(batch, probs, text_encoder)
            train_cers.extend(cers)
            train_wers.extend(wers)

        except RuntimeError as exception:
            if "out of memory" in str(exception) and skip_oom:
                wb.root_logger.warn("OOM on batch. Skipping batch.")
                for param in model.parameters():
                    if param.grad is not None:
                        del param.grad
                torch.cuda.empty_cache()

    return train_loss / len(dataloader), train_cers, train_wers


@torch.no_grad()
def _validate_epoch(
    model: nn.Module,
    criterion: CTCLossWrapper,
    dataloader: DataLoader,
    text_encoder: BaseTextEncoder,
    wb: WBLogger,
    device: torch.device,
) -> tp.Tuple[float]:
    model.eval()
    val_loss = 0
    val_cers = []
    val_wers = []
    for batch in tqdm(dataloader, desc="val", total=len(dataloader)):
        batch = move_batch_to_device(
            batch,
            device,
            fields_on_device=["transforms", "encoded_texts"],
        )
        probs = model(batch["transforms"])
        loss = criterion(
            log_probs=probs.permute(2, 0, 1).log(),
            targets=batch["encoded_texts"],
            input_lengths=batch["char_probs_lengths"],
            target_lengths=batch["encoded_text_lengths"],
        )
        val_loss += loss.item()
        cers, wers = get_metrics_from_ctc_decode(batch, probs, text_encoder)
        val_cers.extend(cers)
        val_wers.extend(wers)

    wb.log_random_audio(batch, level="epoch", part="val")
    wb.log_asr_predictions_form_ctc_decode(batch, probs, text_encoder, level="epoch", part="val")

    return val_loss / len(dataloader), val_cers, val_wers


def train(
    config: DictConfig,
    model: nn.Module,
    optimizer: Optimizer,
    scheduler: _LRScheduler,
    criterion: CTCLossWrapper,
    dataloaders: tp.Dict[str, DataLoader],
    text_encoder: BaseTextEncoder,
    wb: WBLogger,
    device: torch.device,
    skip_oom: tp.Optional[bool] = True,
) -> None:
    """Train an ASR model.

    Args:
        config (DictConfig): Configuration file.
        model (Module): Neural network architecture.
        optimizer (Optimizer): Optimizer used to optimize the model.
        scheduler (_LRScheduler): Scheduler used to choose the learning rate for the model.
        criterion (CTCLossWrapper): CTC loss used to train the model.
        dataloaders (Dict): Data used for training and validation.
        text_encoder (BaseTextEncoder): Text encoder for tokenization.
        wb (WBLogger): Logger.
        device: CPU or GPU device.
        skip_oom (bool, optional): Whether to skip ... or not.
    """
    val_avg_wers = []
    for epoch in range(config.training.epochs):
        wb.increment_epoch()
        train_loss, train_cers, train_wers = _train_epoch(
            config,
            model,
            optimizer,
            scheduler,
            criterion,
            dataloaders["train"],
            text_encoder,
            wb,
            device,
            skip_oom,
        )
        metrics = {
            "global loss": train_loss,
            "average cer": np.mean(train_cers),
            "max cer": np.max(train_cers),
            "average wer": np.mean(train_wers),
            "max wer": np.max(train_wers),
        }
        wb.log_data(metrics, level="epoch", part="train")

        val_loss, val_cers, val_wers = _validate_epoch(
            model,
            criterion,
            dataloaders["val"],
            text_encoder,
            wb,
            device,
        )
        metrics = {
            "global loss": val_loss,
            "average cer": np.mean(val_cers),
            "max cer": np.max(val_cers),
            "average wer": np.mean(val_wers),
            "max wer": np.max(val_wers),
        }
        wb.log_data(metrics, level="epoch", part="val")
        avg_wer = np.mean(val_wers)
        val_avg_wers.append(avg_wer)

        if avg_wer <= min(val_avg_wers):
            wb.log_data({"best average wer": avg_wer}, level="epoch", part="val")
            save_architecture(config, epoch, model, optimizer, scheduler)
