"""General W&B logger."""

import typing as tp

from loguru._logger import Logger
from omegaconf import DictConfig

import wandb
from src.utils import env

wandb.login(key=env.WANDB_API_KEY)


class WBLogger:
    """Wandb logger."""

    def __init__(
        self: "WBLogger",
        config: DictConfig,
        logger: Logger | None = None,
    ) -> None:
        """Initialize W&B logger.

        Args:
            config (DictConfig): Configuration file.
            logger (Logger, optional): Base logger.
        """
        self.wandb = wandb.init(project=config.project_name)
        self._config = config
        self._logger = logger
        self._levels = {
            "step": {
                "train": 0,
                "val": 0,
            },
            "epoch": {
                "train": 0,
                "val": 0,
            },
        }

    def increment_step(
        self: "WBLogger",
        part: tp.Literal["train", "val"],
    ) -> None:
        """Increment step.

        Args:
            part (Literal): Part for which to increase step by one.
        """
        self._levels["step"][part] += 1

    def increment_epoch(self: "WBLogger") -> None:
        """Increment epoch."""
        self._levels["epoch"]["train"] += 1
        self._levels["epoch"]["val"] += 1

    def log_data(
        self: "WBLogger",
        data: dict[str, tp.Any],
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Literal["train", "val"],
    ) -> None:
        """Log data to W&B.

        Args:
            data (Dict): Data metrics to log.
            level (Literal): Level of logging.
            part (Literal, optional): Part of logging.
        """
        formatted_data = {
            " ".join(
                map(lambda w: w.capitalize(), (part + " " + k).split())
            ): v
            for k, v in data.items()
        }
        self.wandb.log(formatted_data, step=self._levels[level][part])
