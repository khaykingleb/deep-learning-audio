"""Schedulers for selecting learning rate."""

import typing as tp

import torch
from omegaconf import DictConfig
from torch.optim.lr_scheduler import _LRScheduler


class WarmupLRScheduler(_LRScheduler):
    """Warmups learning rate until warmup_steps."""

    def __init__(
        self: "WarmupLRScheduler",
        optimizer: torch.Tensor,
        init_lr: float,
        peak_lr: float,
        warmup_steps: int,
    ) -> None:
        """Constructor.

        Args:
            optimizer (Optimizer): Optimizer used to optimize the model's weights.
            init_lr (float): Learning rate at the star.
            peak_lr (float): Learning rate at the end.
            warmup_steps (int): Number of steps to increase the learning rate to peak_lr.
        """
        self.init_lr = init_lr
        self.lr = init_lr
        if warmup_steps != 0:
            self.warmup_rate = (peak_lr - init_lr) / warmup_steps
        else:
            self.warmup_rate = 0
        self.warmup_steps = warmup_steps
        self.steps = 1
        super().__init__(optimizer)

    def step(self: "WarmupLRScheduler") -> None:
        """Makes step in learning rate."""
        if self.steps < self.warmup_steps:
            lr = self.init_lr + self.warmup_rate * self.steps
            self.set_lr(self.optimizer, lr)
            self.lr = lr
        self.steps += 1

    @staticmethod
    def set_lr(optimizer: torch.optimizer.Optimizer, lr: float) -> None:
        """Set the learning rates to new value in each parameter group.

        Args:
            optimizer (Optimizer): Optimizer used to optimize the model's weights.
            lr (float): New learning rate.
        """
        for g in optimizer.param_groups:
            g["lr"] = lr

    def get_lr(self: "WarmupLRScheduler") -> tp.List[float]:
        """Get the learning rates from each parameter group.

        Returns:
            List: Learning rates for param_groups.
        """
        for g in self.optimizer.param_groups:
            return g["lr"]


class WarmupLRSchedulerWrapper(WarmupLRScheduler):
    """Wrapper around WarmupLRScheduler."""

    def __init__(
        self: "WarmupLRSchedulerWrapper",
        optimizer: torch.optim.Optimizer,
        config: DictConfig,
    ) -> None:
        """Constructor.

        Args:
            optimizer (Optimizer): Optimizer used to optimize the model's weights.
            config (DictConfig): Configuration file.
        """
        super().__init__(
            optimizer,
            init_lr=config.training.scheduler.args.init_lr,
            peak_lr=config.training.scheduler.args.peak_lr,
            warmup_steps=config.training.scheduler.args.warmup_steps,
        )
