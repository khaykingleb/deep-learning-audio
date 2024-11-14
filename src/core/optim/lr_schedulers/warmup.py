import math
import typing as tp

import torch
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler


class WarmupLRScheduler(LRScheduler):
    """Warmups learning rate until warmup_steps."""

    def __init__(
        self,
        optimizer: Optimizer,
        initial_lr: float,
        peak_lr: float,
        warmup_steps: int,
        last_epoch: int = -1,
    ) -> None:
        self.__check_args(initial_lr, peak_lr, warmup_steps)
        super().__init__(optimizer, last_epoch)

        self.initial_lr = initial_lr
        self.peak_lr = peak_lr
        self.lr = initial_lr

        self.warmup_steps = warmup_steps
        self.warmup_rate = (peak_lr - initial_lr) / warmup_steps

        self.step_count = 1

    def __check_args(
        self,
        initial_lr: float,
        peak_lr: float,
        warmup_steps: int,
    ) -> None:
        if initial_lr <= 0:
            raise ValueError(f"Invalid learning rate: {initial_lr}")
        if peak_lr <= 0:
            raise ValueError(f"Invalid peak learning rate: {peak_lr}")
        if warmup_steps <= 0:
            raise ValueError(f"Invalid warmup steps: {warmup_steps}")

    def step(self) -> None:
        """Make a step in learning rate."""
        if self.step_count <= self.warmup_steps:
            self.lr = self.initial_lr + self.warmup_rate * self.step_count
            for g in self.optimizer.param_groups:
                g["lr"] = self.lr
        self.step_count += 1

    def get_lr(self) -> list[float]:
        """Get the learning rates from each parameter group.

        Returns:
            Learning rates for param_groups.
        """
        lrs = []
        for param_group in self.optimizer.param_groups:
            lrs.append(param_group["lr"])
        return lrs
