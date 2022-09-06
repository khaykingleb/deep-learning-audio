"""Wandb logging configuration."""

import random
import typing as tp
from logging import RootLogger

import torch
import wandb
from omegaconf import DictConfig
from PIL import Image

from . import cfg, logger
from ..data.preprocess.text import BaseTextEncoder
from ..visualization import plot_transform

wandb.login(key=cfg.WANDB_API_KEY)


class WBLogger:
    """Wandb logger."""

    def __init__(
        self: "WBLogger",
        config: DictConfig,
        root_logger: tp.Optional[RootLogger] = logger,
    ) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
            root_logger (RootLogger, optional): Base logger.
        """
        self.wandb = wandb.init(project=config.project_name)
        self.root_logger = root_logger
        self.config = config
        self._levels = {
            "step": {"train": 0, "val": 0},
            "epoch": {"train": 0, "val": 0},
        }

    def increment_step(self: "WBLogger", part: tp.Literal["train", "val"]) -> None:
        """Increment step.

        Args:
            part (Literal): For what part, train or val, need to increase step by one.
        """
        self._levels["step"][part] += 1

    def increment_epoch(self: "WBLogger") -> None:
        """Increment epoch."""
        self._levels["epoch"]["train"] += 1
        self._levels["epoch"]["val"] += 1

    def log_data(
        self: "WBLogger",
        data: tp.Dict[str, tp.Any],
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Optional[tp.Literal["train", "val"]],
    ) -> None:
        """Log data to W&B.

        Args:
            data (Dict): Metrics.
            level (Literal): With accordance to what, step or epoch, we need to log.
            part (Literal): For what part, train or val, we need to log.
        """
        data = {(part + " " + k).capitalize(): v for k, v in data.items()}
        self.wandb.log(data, step=self._levels[level][part])

    def log_random_audio(
        self: "WBLogger",
        batch: tp.Dict[str, tp.Any],
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Literal["train", "val"],
    ) -> None:
        """Log random audio in the given batch and its DSP transformation to W&B.

        Args:
            batch (Dict): Batch of data samples.
            level (Literal): With accordance to what, step or epoch, we need to log.
            part (Literal): For what part, train or val, we need to log.
        """
        idx = random.randint(0, len(batch["audios"]) - 1)
        audio = batch["audios"][idx].squeeze().detach().cpu().numpy()
        sr = self.config.preprocess.audio.sr
        audio_name = (part + " audio").capitalize()
        self.wandb.log(
            {audio_name: wandb.Audio(audio, caption=batch["texts"][idx], sample_rate=sr)},
            step=self._levels[level][part],
        )
        transform_image = Image.open(
            plot_transform(
                batch["transforms"][idx],
                title="",
                xlabel="Time (seconds)",
                ylabel="",
                sample_rate=self.config.preprocess.audio.sr,
                audio_size=len(audio),
                show_fig=False,
            )
        )
        transform_name = part + " " + self.config.preprocess.transform.name
        transform_name = transform_name.lower().capitalize()
        self.wandb.log(
            {transform_name: wandb.Image(transform_image)},
            step=self._levels[level][part],
        )

    def log_asr_predictions_form_ctc_decode(
        self: "WBLogger",
        batch: tp.Dict[str, tp.Any],
        probs: torch.Tensor,
        text_encoder: BaseTextEncoder,
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Literal["train", "val"],
    ) -> None:
        """Log ASR model results to W&B.

        Args:
            batch (Dict): Batch of data samples.
            probs (Tensor): Probabilities for each character of shape (batch_size, vocab_size, input_length).
            text_encoder (BaseTextEncoder): Text encoder used for tokenization.
            level (Literal): With accordance to what, step or epoch, we need to log.
            part (Literal): For what part, train or val, we need to log.
        """
        pred_idxs = probs.argmax(dim=1)
        pred_raw_texts = [text_encoder.decode(idxs) for idxs in pred_idxs]
        pred_texts = [text_encoder.ctc_decode(idxs) for idxs in pred_idxs]
        logs = []
        for ref_text, hypo_raw_text, hypo_text in zip(batch["texts"], pred_raw_texts, pred_texts):
            logs.append(
                f"reference: '{ref_text}' "
                f"| hypothesis_raw: '{hypo_raw_text}' "
                f"| hypothesis: '{hypo_text}'"
            )
        logs = "\n---\n".join(logs)
        logs_name = (part + " naive predictions").capitalize()
        self.wandb.log(
            {logs_name: wandb.Html(logs)},
            step=self._levels[level][part],
        )
