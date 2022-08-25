"""Wandb logging configuration."""

import typing as tp
from logging import RootLogger

import wandb
from omegaconf import DictConfig

from . import logger


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
            root_logger (RootLogger): Base logger.
        """
        self.wandb = wandb.init(project=config.wandb_project_name)
        self.root_logger = root_logger
