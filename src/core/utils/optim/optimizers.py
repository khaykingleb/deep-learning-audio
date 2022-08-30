"""Optimizers for training models."""

import typing as tp

import torch
import torch_optimizer
from omegaconf import DictConfig


class AdamWWrapper(torch.optim.AdamW):
    """Wrapper around AdamW optimizer."""

    def __init__(self: "AdamWWrapper", params: tp.Iterable, config: DictConfig) -> None:
        """Constructor.

        Args:
            params (Iterable): Parameters to optimize.
            config (DictConfig): Configuration file.
        """
        super().__init__(
            params,
            lr=config.training.optimizer.args.lr,
            betas=config.training.optimizer.args.betas,
            eps=config.training.optimizer.args.eps,
            weight_decay=config.training.optimizer.args.weight_decay,
            amsgrad=config.training.optimizer.args.amsgrad,
        )


class NovoGradWrapper(torch_optimizer.NovoGrad):
    """Wrapper around NovoGrad optimizer."""

    def __init__(self: "NovoGradWrapper", params: tp.Iterable, config: DictConfig) -> None:
        """Constructor.

        Args:
            params (Iterable): Parameters to optimize.
            config (DictConfig): Configuration file.
        """
        super().__init__(
            params,
            lr=config.training.optimizer.args.lr,
            betas=config.training.optimizer.args.betas,
            eps=config.training.optimizer.args.eps,
            weight_decay=config.training.optimizer.args.weight_decay,
            grad_averaging=config.training.optimizer.args.grad_averaging,
            amsgrad=config.training.optimizer.args.amsgrad,
        )
