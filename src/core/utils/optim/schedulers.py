"""Schedulers for selecting learning rate."""

import math
import typing as tp

import torch
from omegaconf import DictConfig
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler


class WarmupLRScheduler(_LRScheduler):
    """Warmups learning rate until warmup_steps."""

    def __init__(
        self: "WarmupLRScheduler",
        optimizer: Optimizer,
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
    def set_lr(optimizer: torch.optim.Optimizer, lr: float) -> None:
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


class CosineAnnealingWarmupRestarts(_LRScheduler):
    """Cosine Annealing with Warmup taken from https://github.com/katsura-jp/pytorch-cosine-annealing-with-warmup."""

    def __init__(  # NOQA
        self: "CosineAnnealingWarmupRestarts",
        optimizer: Optimizer,
        first_cycle_steps: int,
        cycle_mult: tp.Optional[float] = 1.0,
        max_lr: tp.Optional[float] = 0.1,
        min_lr: tp.Optional[float] = 0.001,
        warmup_steps: tp.Optional[int] = 0,
        gamma: tp.Optional[float] = 1.0,
        last_epoch: tp.Optional[int] = -1,
    ) -> None:
        assert warmup_steps < first_cycle_steps
        self.first_cycle_steps = first_cycle_steps
        self.cycle_mult = cycle_mult
        self.base_max_lr = max_lr
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.warmup_steps = warmup_steps
        self.gamma = gamma

        self.cur_cycle_steps = first_cycle_steps
        self.cycle = 0
        self.step_in_cycle = last_epoch

        super().__init__(optimizer, last_epoch)

        # set learning rate min_lr
        self.init_lr()

    def init_lr(self: "CosineAnnealingWarmupRestarts") -> None:  # NOQA
        self.base_lrs = []
        for param_group in self.optimizer.param_groups:
            param_group["lr"] = self.min_lr
            self.base_lrs.append(self.min_lr)

    def get_lr(self: "CosineAnnealingWarmupRestarts"):  # NOQA
        if self.step_in_cycle == -1:
            return self.base_lrs
        elif self.step_in_cycle < self.warmup_steps:
            return [
                (self.max_lr - base_lr) * self.step_in_cycle / self.warmup_steps + base_lr
                for base_lr in self.base_lrs
            ]
        else:
            return [
                base_lr
                + (self.max_lr - base_lr)
                * (
                    1
                    + math.cos(
                        math.pi
                        * (self.step_in_cycle - self.warmup_steps)
                        / (self.cur_cycle_steps - self.warmup_steps)
                    )
                )
                / 2
                for base_lr in self.base_lrs
            ]

    def step(self: "CosineAnnealingWarmupRestarts", epoch: tp.Optional[int] = None) -> None:  # NOQA
        if epoch is None:
            epoch = self.last_epoch + 1
            self.step_in_cycle = self.step_in_cycle + 1
            if self.step_in_cycle >= self.cur_cycle_steps:
                self.cycle += 1
                self.step_in_cycle = self.step_in_cycle - self.cur_cycle_steps
                self.cur_cycle_steps = (
                    int((self.cur_cycle_steps - self.warmup_steps) * self.cycle_mult)
                    + self.warmup_steps
                )
        else:
            if epoch >= self.first_cycle_steps:
                if self.cycle_mult == 1.0:
                    self.step_in_cycle = epoch % self.first_cycle_steps
                    self.cycle = epoch // self.first_cycle_steps
                else:
                    n = int(
                        math.log(
                            (epoch / self.first_cycle_steps * (self.cycle_mult - 1) + 1),
                            self.cycle_mult,
                        )
                    )
                    self.cycle = n
                    self.step_in_cycle = epoch - int(
                        self.first_cycle_steps * (self.cycle_mult**n - 1) / (self.cycle_mult - 1)
                    )
                    self.cur_cycle_steps = self.first_cycle_steps * self.cycle_mult ** (n)
            else:
                self.cur_cycle_steps = self.first_cycle_steps
                self.step_in_cycle = epoch

        self.max_lr = self.base_max_lr * (self.gamma**self.cycle)
        self.last_epoch = math.floor(epoch)
        for param_group, lr in zip(self.optimizer.param_groups, self.get_lr()):
            param_group["lr"] = lr


class CosineAnnealingWarmupRestartsWrapper(CosineAnnealingWarmupRestarts):
    """Wrapper around CosineAnnealingWarmupRestarts optimizer."""

    def __init__(
        self: "CosineAnnealingWarmupRestartsWrapper",
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
            first_cycle_steps=config.training.scheduler.args.first_cycle_steps,
            cycle_mult=config.training.scheduler.args.cycle_mult,
            max_lr=config.training.scheduler.args.max_lr,
            min_lr=config.training.scheduler.args.min_lr,
            warmup_steps=config.training.scheduler.args.warmup_steps,
            gamma=config.training.scheduler.args.gamma,
        )
