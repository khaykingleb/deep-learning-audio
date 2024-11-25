"""ASR model."""

import random
import typing as tp

import hydra
import lightning as L
import torch
import torchaudio
from lightning.pytorch.utilities.types import OptimizerLRScheduler
from omegaconf import DictConfig
from PIL import Image
from torch.nn.modules.loss import CTCLoss
from torchmetrics.text import CharErrorRate, WordErrorRate

import wandb
from src.collections.common.preprocessing.tokenizers import (
    CTCTextTokenizer,
    TextTokenizer,
)
from src.utils import env
from src.utils.logger import logger
from src.utils.vizualization.audio import plot_transform

Tokenizer = TextTokenizer | CTCTextTokenizer


class ASRModel(L.LightningModule):
    """PyTorch Lightning ASR model."""

    def __init__(
        self,
        tokenizer: DictConfig,
        model: DictConfig,
        loss: DictConfig,
        sample_rate: int,
        optimizer: DictConfig,
        scheduler: DictConfig | None = None,
        *,
        compile_model: bool = False,
        rank_zero_only: bool = env.LOGGING_ONLY_RANK_ZERO,
    ) -> None:
        """Constructor.

        Args:
            model: Model configuration.

        Note:
            LightningModule knows what device it is on.
            You can access the reference via self.device.
            Sometimes it is necessary to store tensors as module attributes.
            However, if they are not parameters they **will remain** on the CPU
            even if the module gets moved to a new device. To prevent that and
            remain device agnostic, register the tensor as a buffer in your
            modules' __init__ method with register_buffer(). By using
            self.register_buffer("sigma", torch.eye(3)), you can now access
            self.sigma anywhere in your module.

        Note:
            For more information on optimization, see
            https://lightning.ai/docs/pytorch/stable/common/optimization.html

        Args:
            tokenizer: Tokenizer configuration
            model: Model configuration
            loss: Loss configuration
            sample_rate: Sample rate
            optimizer: Optimizer configuration
            scheduler: Scheduler configuration
            compile_model: Whether to compile the model
            rank_zero_only: Whether to log only on rank zero
        """
        super().__init__()
        self.save_hyperparameters()

        logger.info(f"Instantiating tokenizer: {tokenizer['_target_']}")
        self.tokenizer: Tokenizer = hydra.utils.instantiate(tokenizer)

        logger.info(f"Instantiating model: {model['_target_']}")
        self.model = hydra.utils.instantiate(
            model,
            out_channels=self.tokenizer.alphabet_size,
        )

        logger.info(f"Instantiating loss: {loss['_target_']}")
        if isinstance(self.tokenizer, CTCTextTokenizer):
            self.loss = hydra.utils.instantiate(
                loss,
                blank=self.tokenizer._blank_token,
            )
        else:
            self.loss = hydra.utils.instantiate(loss)

        logger.info("Instantiating metrics")
        self.wer = WordErrorRate()
        self.cer = CharErrorRate()

        self.amplitude_to_db = torchaudio.transforms.AmplitudeToDB(
            stype="power",
            top_db=80,
        )

    def setup(
        self,
        stage: tp.Literal["fit", "validate", "test", "predict"],
    ) -> None:
        """Lightning hook that is called at the beginning of each stage.

        Stages:
            * fit (train + validate)
            * validate
            * test
            * predict

        This is a good hook when you need to build models dynamically or
        adjust something about them. This hook is called on every process
        when using DDP. Normally you'd need one, but in the case of GANs or
        similar you might need multiple.

        Args:
            stage: Stage of the Lightning process.
        """
        if self.hparams["compile_model"] and stage == "fit":
            self.model = torch.compile(self.model)

    def configure_optimizers(self) -> OptimizerLRScheduler:
        """Choose optimizers and lr schedulers to use in your optimization.

        Normally you'd need one. But in the case of GANs or similar you
        might have multiple. Optimization with multiple optimizers only
        works in the manual optimization mode.

        Returns:
            Optimizer and scheduler
        """
        logger.info(
            f"Instantiating optimizer: {self.hparams['optimizer']['_target_']}"
        )
        optimizer = hydra.utils.instantiate(
            self.hparams["optimizer"],
            params=self.parameters(),
        )

        if self.hparams["scheduler"] is None:
            return {
                "optimizer": optimizer,
            }

        logger.info(
            f"Instantiating scheduler: {self.hparams['scheduler']['_target_']}"
        )
        lightning_config = self.hparams["scheduler"].pop("lightning")
        scheduler = hydra.utils.instantiate(
            self.hparams["scheduler"],
            optimizer=optimizer,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                **lightning_config,
            },
        }

    def training_step(
        self,
        batch: dict[str, torch.Tensor],
        batch_idx: int,
    ) -> torch.Tensor:
        """Compute and return the training loss.

        Note:
            Add sync_dist=True to sync logging across all GPU workers
            (may have performance impact):
            >>> self.log(
            ...     "train_loss",
            ...     loss,
            ...     on_step=True,
            ...     on_epoch=True,
            ...     sync_dist=True,
            ... )

            It is possible to perform some computation manually and log
            the reduced result on rank 0 as follows:
            >>> if self.trainer.is_global_zero:
            >>>     self.log("my_reduced_metric", mean, rank_zero_only=True)
            When you call `self.log` only on rank 0, don't forget to add
            `rank_zero_only=True` to avoid deadlocks on synchronization.
            Caveat: monitoring this is unimplemented, see
            https://github.com/Lightning-AI/lightning/issues/15852

        Args:
            batch: batch of data sampled from the training set
            batch_idx: index of the batch
        """
        self._log_audio(batch, batch_idx, stage="train")

        log_probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(log_probs, batch)

        pred_tokens = log_probs.argmax(dim=1)
        metrics = self._compute_metrics(
            pred_tokens,
            batch,
            batch_idx,
            stage="train",
        )

        values = {"train_loss": loss, **metrics}
        self.log_dict(
            values,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=self.hparams["rank_zero_only"],
            sync_dist=not self.hparams["rank_zero_only"],
            batch_size=batch["transforms"].shape[0],
        )

        return loss

    def validation_step(
        self,
        batch: dict[str, torch.Tensor],
        batch_idx: int,
    ) -> torch.Tensor:
        """Compute and return the validation loss.

        Args:
            batch: batch of data sampled from the validation set
            batch_idx: index of the batch
        """
        self._log_audio(batch, batch_idx, stage="val")

        log_probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(log_probs, batch)

        pred_tokens = log_probs.argmax(dim=1)
        metrics = self._compute_metrics(
            pred_tokens,
            batch,
            batch_idx,
            stage="val",
        )

        values = {"val_loss": loss, **metrics}
        self.log_dict(
            values,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=self.hparams["rank_zero_only"],
            sync_dist=not self.hparams["rank_zero_only"],
            batch_size=batch["transforms"].shape[0],
        )

        return loss

    def test_step(
        self,
        batch: dict[str, torch.Tensor],
        batch_idx: int,
    ) -> torch.Tensor:
        """Compute and return the test loss.

        Args:
            batch: batch of data sampled from the test set
            batch_idx: index of the batch
        """
        self._log_audio(batch, batch_idx, stage="test")

        log_probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(log_probs, batch)

        pred_tokens = log_probs.argmax(dim=1)
        metrics = self._compute_metrics(
            pred_tokens,
            batch,
            batch_idx,
            stage="test",
        )

        values = {"test_loss": loss, **metrics}
        self.log_dict(
            values,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=self.hparams["rank_zero_only"],
            sync_dist=not self.hparams["rank_zero_only"],
            batch_size=batch["transforms"].shape[0],
        )

        return loss

    def _compute_loss(
        self,
        log_probs: torch.Tensor,
        batch: dict[str, torch.Tensor],
    ) -> torch.Tensor:
        if isinstance(self.loss, CTCLoss):
            loss = self.loss(
                log_probs=log_probs.permute(2, 0, 1),
                targets=batch["tokens"],
                input_lengths=batch["probs_lengths"],
                target_lengths=batch["tokens_lengths"],
            )
        else:
            msg = f"Loss {self.loss} is not supported"
            raise TypeError(msg)
        return loss

    def _compute_metrics(
        self,
        pred_tokens: torch.Tensor,
        batch: dict[str, torch.Tensor],
        batch_idx: int,
        stage: tp.Literal["train", "val", "test"] = "train",
    ) -> dict[str, torch.Tensor]:
        if isinstance(self.tokenizer, CTCTextTokenizer):
            pred_raw_texts = [
                self.tokenizer.raw_decode(tokens) for tokens in pred_tokens
            ]
        pred_texts = [self.tokenizer.decode(tokens) for tokens in pred_tokens]
        target_texts = [
            self.tokenizer.decode(tokens).strip() for tokens in batch["tokens"]
        ]
        self._log_naive_predictions(
            batch_idx,
            target_texts,
            pred_texts,
            pred_raw_texts,
            stage,
        )
        return {
            f"{stage}_wer": self.wer(pred_texts, target_texts),
            f"{stage}_cer": self.cer(pred_texts, target_texts),
        }

    def _log_audio(
        self,
        batch: dict[str, torch.Tensor],
        batch_idx: int,
        stage: tp.Literal["train", "val", "test"],
    ) -> None:
        if batch_idx % self.trainer.log_every_n_steps != 0:
            return

        idx = random.randint(0, len(batch["waveforms"]) - 1)
        waveform: torch.Tensor = batch["waveforms"][idx]

        audio_name = " ".join(
            word.capitalize() for word in f"{stage} audio".split()
        )
        audio_caption = self.tokenizer.decode(batch["tokens"][idx])
        self.logger.experiment.log(
            {
                audio_name: wandb.Audio(
                    waveform.squeeze().detach().cpu().numpy(),
                    caption=audio_caption,
                    sample_rate=self.hparams["sample_rate"],
                )
            }
        )

        transform = batch["transforms"][idx]
        transform_db = self.amplitude_to_db(transform)
        transform_image_buffer = plot_transform(
            transform_db,
            title="",
            x_label="Time (seconds)",
            y_label="",
            sample_rate=self.hparams["sample_rate"],
            audio_size=waveform.shape[-1],
            show_fig=False,
        )
        with Image.open(transform_image_buffer) as transform_image:
            transform_name = " ".join(
                word.capitalize() for word in f"{stage} transform".split()
            )
            self.logger.experiment.log(
                {transform_name: wandb.Image(transform_image)}
            )

    def _log_naive_predictions(
        self,
        batch_idx: int,
        target_texts: list[str],
        pred_texts: list[str],
        pred_raw_texts: list[str] | None = None,
        stage: tp.Literal["train", "val", "test"] = "train",
    ) -> None:
        if batch_idx % self.trainer.log_every_n_steps != 0:
            return

        table = wandb.Table(
            columns=["Reference", "Hypothesis Raw", "Hypothesis"]
        )
        for ref_text, hypo_raw_text, hypo_text in zip(
            target_texts,
            pred_raw_texts,
            pred_texts,
            strict=True,
        ):
            table.add_data(ref_text, hypo_raw_text, hypo_text)

        logs_name = f"{stage.capitalize()} Naive Predictions"
        self.logger.experiment.log({logs_name: table})
