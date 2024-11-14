import math
import typing as tp

import torch
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler


class CosineAnnealingWarmupLRScheduler(LRScheduler):
    """Cosine Annealing with Warmup.

    Taken from https://github.com/katsura-jp/pytorch-cosine-annealing-with-warmup.
    """

    def __init__(
        self,
        optimizer: Optimizer,
        first_cycle_steps: int,
        cycle_multiplier: float = 1.0,
        min_lr: float = 0.001,
        max_lr: float = 0.1,
        warmup_steps: int = 0,
        gamma: float = 1.0,
        last_epoch: int = -1,
    ) -> None:
        """Constructor.

        Args:
            optimizer: PyTorch optimizer.
            first_cycle_steps: The number of steps in the first cycle.
            cycle_multiplier: The multiplier for the cycle length.
            min_lr: The minimum learning rate.
            max_lr: The maximum learning rate.
            warmup_steps: The number of steps for the warmup phase.
            gamma: The gamma factor for the learning rate decay.
            last_epoch: The index of last epoch.
        """
        self.__check_args(
            first_cycle_steps,
            cycle_multiplier,
            min_lr,
            max_lr,
            warmup_steps,
            gamma,
        )
        super().__init__(optimizer, last_epoch)

        self.first_cycle_steps = first_cycle_steps
        self.cycle_multiplier = cycle_multiplier
        self.base_max_lr = max_lr
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.warmup_steps = warmup_steps
        self.gamma = gamma

        self.cycle = 0
        self.current_cycle_steps = first_cycle_steps
        self.step_in_cycle = last_epoch

        # Set learning rate min_lr
        self.base_lrs = []
        for param_group in self.optimizer.param_groups:
            param_group["lr"] = min_lr
            self.base_lrs.append(param_group["lr"])

    def __check_args(
        self,
        first_cycle_steps: int,
        cycle_multiplier: float,
        min_lr: float,
        max_lr: float,
        warmup_steps: int,
        gamma: float,
    ) -> None:
        if first_cycle_steps <= 0:
            raise ValueError("First cycle steps should be greater than 0.")
        if cycle_multiplier <= 0:
            raise ValueError("Cycle multiplier should be greater than 0.")
        if min_lr <= 0:
            raise ValueError("Minimum learning rate should be greater than 0.")
        if max_lr <= min_lr:
            raise ValueError(
                "Maximum learning rate should be greater than minimum learning rate."
            )
        if warmup_steps >= first_cycle_steps:
            raise ValueError(
                "Warmup steps should be less than first cycle steps."
            )
        if gamma <= 0:
            raise ValueError("Gamma should be greater than 0.")

    def get_lr(self):
        if self.step_in_cycle == -1:
            return self.base_lrs
        elif self.step_in_cycle < self.warmup_steps:
            return [
                (self.max_lr - base_lr)
                * self.step_in_cycle
                / self.warmup_steps
                + base_lr
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

    def step(self, epoch=None):
        if epoch is None:
            epoch = self.last_epoch + 1
            self.step_in_cycle = self.step_in_cycle + 1
            if self.step_in_cycle >= self.cur_cycle_steps:
                self.cycle += 1
                self.step_in_cycle = self.step_in_cycle - self.cur_cycle_steps
                self.cur_cycle_steps = (
                    int(
                        (self.cur_cycle_steps - self.warmup_steps)
                        * self.cycle_multiplier
                    )
                    + self.warmup_steps
                )
        else:
            if epoch >= self.first_cycle_steps:
                if self.cycle_multiplier == 1.0:
                    self.step_in_cycle = epoch % self.first_cycle_steps
                    self.cycle = epoch // self.first_cycle_steps
                else:
                    n = int(
                        math.log(
                            (
                                epoch
                                / self.first_cycle_steps
                                * (self.cycle_multiplier - 1)
                                + 1
                            ),
                            self.cycle_multiplier,
                        )
                    )
                    self.cycle = n
                    self.step_in_cycle = epoch - int(
                        self.first_cycle_steps
                        * (self.cycle_multiplier**n - 1)
                        / (self.cycle_multiplier - 1)
                    )
                    self.cur_cycle_steps = (
                        self.first_cycle_steps * self.cycle_multiplier**n
                    )
            else:
                self.cur_cycle_steps = self.first_cycle_steps
                self.step_in_cycle = epoch

        self.max_lr = self.base_max_lr * (self.gamma**self.cycle)
        self.last_epoch = math.floor(epoch)
        for param_group, lr in zip(self.optimizer.param_groups, self.get_lr()):
            param_group["lr"] = lr
