import hydra
import lightning as L
import torch
from lightning.pytorch.utilities.types import OptimizerLRScheduler
from omegaconf import DictConfig
from torch import nn
from torch.nn.modules.loss import CTCLoss
from torchmetrics.text import CharErrorRate, WordErrorRate

from src.collections.common.preprocessing.tokenizers import (
    CTCTextTokenizer,
    TextTokenizer,
)
from src.utils import env
from src.utils.loggers import logger

Tokenizer = TextTokenizer | CTCTextTokenizer


class ASRModel(L.LightningModule):
    def __init__(
        self,
        tokenizer: DictConfig,
        model: DictConfig,
        loss: DictConfig,
        optimizer: DictConfig,
        scheduler: DictConfig,
        rank_zero_only: bool | None = env.LOGGING_ONLY_RANK_ZERO,
    ) -> None:
        """Constructor.

        Args:
            model: Model configuration.

        Note:
            LightningModule knows what device it is on.
            You can access the reference via self.device.
            Sometimes it is necessary to store tensors as module attributes.
            However, if they are not parameters they **will remain** on the CPU even if the module gets moved to a new device.
            To prevent that and remain device agnostic, register the tensor as a buffer in your modules’ __init__ method with register_buffer().
            By using self.register_buffer("sigma", torch.eye(3)), you can now access self.sigma anywhere in your module.

        Note:
            For more information on optimization, see https://lightning.ai/docs/pytorch/stable/common/optimization.html
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

    def configure_optimizers(self) -> OptimizerLRScheduler:
        logger.info(
            f"Instantiating optimizer: {self.hparams['optimizer']['_target_']}"
        )
        optimizer = hydra.utils.instantiate(
            self.hparams["optimizer"],
            params=self.parameters(),
        )
        logger.info(
            f"Instantiating scheduler: {self.hparams['scheduler']['_target_']}"
        )
        scheduler = hydra.utils.instantiate(
            self.hparams["scheduler"],
            optimizer=optimizer,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                # The unit of the scheduler's step size, could also be 'step'.
                # 'epoch' updates the scheduler on epoch end whereas 'step'
                # updates it after a optimizer update.
                "interval": "epoch",
                # How many epochs/steps should pass between calls to
                # `scheduler.step()`. 1 corresponds to updating the learning
                # rate after every epoch/step.
                "frequency": 1,
                # Metric to to monitor for schedulers like `ReduceLROnPlateau`
                "monitor": "val_loss",
                # If set to `True`, will enforce that the value specified 'monitor'
                # is available when the scheduler is updated, thus stopping
                # training if not found. If set to `False`, it will only 
                # produce a warning
                "strict": True,
                # If using the `LearningRateMonitor` callback to monitor the
                # learning rate progress, this keyword can be used to specify
                # a custom logged name
                "name": None,
            },
        }

    def training_step(
        self,
        batch: dict[str, torch.Tensor],
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

            It is possible to perform some computation manually and log the reduced result on rank 0 as follows:
            >>> if self.trainer.is_global_zero:
            >>>     self.log("my_reduced_metric", mean, rank_zero_only=True)
            When you call `self.log` only on rank 0, don't forget to add `rank_zero_only=True` to avoid deadlocks on synchronization.
            Caveat: monitoring this is unimplemented, see https://github.com/Lightning-AI/lightning/issues/15852
        """
        probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(probs, batch)

        pred_tokens = probs.argmax(dim=1)
        metrics = self._compute_metrics(pred_tokens, batch)

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
    ) -> torch.Tensor:
        probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(probs, batch)

        pred_tokens = probs.argmax(dim=1)
        metrics = self._compute_metrics(pred_tokens, batch)

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
    ):
        probs: torch.Tensor = self.model(batch["transforms"])
        loss = self._compute_loss(probs, batch)

        pred_tokens = probs.argmax(dim=1)
        metrics = self._compute_metrics(pred_tokens, batch)

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
        probs: torch.Tensor,
        batch: dict[str, torch.Tensor],
    ) -> torch.Tensor:
        if isinstance(self.loss, CTCLoss):
            loss = self.loss(
                log_probs=probs.permute(2, 0, 1).log(),
                targets=batch["tokens"],
                input_lengths=batch["probs_lengths"],
                target_lengths=batch["tokens_lengths"],
            )
        else:
            raise ValueError(f"Loss {self.loss} is not supported")
        return loss

    def _compute_metrics(
        self,
        pred_tokens: torch.Tensor,
        batch: dict[str, torch.Tensor],
    ) -> dict[str, torch.Tensor]:
        # if isinstance(self.tokenizer, CTCTextTokenizer):
        #     pred_raw_texts = [
        #         self.tokenizer.raw_decode(tokens) for tokens in pred_tokens
        #     ]
        pred_texts = [self.tokenizer.decode(tokens) for tokens in pred_tokens]
        target_texts = [
            self.tokenizer.decode(tokens).strip() for tokens in batch["tokens"]
        ]
        return {
            "wer": self.wer(pred_texts, target_texts),
            "cer": self.cer(pred_texts, target_texts),
        }

    # # https://lightning.ai/docs/pytorch/stable/common/checkpointing_intermediate.html#modify-a-checkpoint-anywhere
    # def on_save_checkpoint(self, checkpoint):
    #     # checkpoint["something_cool_i_want_to_save"] = my_cool_pickable_object
    #     pass

    # # https://lightning.ai/docs/pytorch/stable/common/checkpointing_intermediate.html#modify-a-checkpoint-anywhere
    # def on_load_checkpoint(self, checkpoint):
    #     # my_cool_pickable_object = checkpoint["something_cool_i_want_to_save"]
    #     pass
