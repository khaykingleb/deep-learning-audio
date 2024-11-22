"""Learning rate scheduler with warmup."""

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
        """Initialize WarmupLRScheduler.

        Args:
            optimizer: Optimizer to update the learning rate.
            initial_lr: Initial learning rate.
            peak_lr: Peak learning rate.
            warmup_steps: Number of warmup steps.
            last_epoch: The index of the last epoch.
        """
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
            msg = f"Invalid learning rate: {initial_lr}"
            raise ValueError(msg)
        if peak_lr <= 0:
            msg = f"Invalid peak learning rate: {peak_lr}"
            raise ValueError(msg)
        if warmup_steps <= 0:
            msg = f"Invalid warmup steps: {warmup_steps}"
            raise ValueError(msg)

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
        return [
            param_group["lr"] for param_group in self.optimizer.param_groups
        ]
