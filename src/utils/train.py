"""Train utilities."""

import hydra
import torch
from lightning import Callback
from lightning.pytorch.core import LightningModule
from lightning.pytorch.loggers import Logger
from omegaconf import DictConfig

from src.utils.logger import logger


def instantiate_callbacks(cfg: DictConfig) -> list[Callback]:
    """Instantiate callbacks.

    Args:
        cfg: Hydra config.

    Returns:
        List of instantiated callbacks.
    """
    callbacks = []
    if cfg.get("callbacks"):
        for callback_cfg in cfg["callbacks"].values():
            logger.info(f"Instantiating callback <{callback_cfg['_target_']}>")
            callbacks.append(hydra.utils.instantiate(callback_cfg))
    else:
        logger.warning("No callbacks to instantiate")
    return callbacks


def instantiate_loggers(cfg: DictConfig) -> list[Logger]:
    """Instantiate loggers.

    Args:
        cfg: Hydra config.

    Returns:
        List of instantiated loggers.
    """
    loggers = []
    if cfg.get("loggers"):
        for logger_cfg in cfg["loggers"].values():
            logger.info(f"Instantiating logger <{logger_cfg['_target_']}>")
            loggers.append(hydra.utils.instantiate(logger_cfg))
    else:
        logger.warning("No loggers to instantiate")
    return loggers


def update_checkpoint_path(
    cfg: DictConfig,
    model: LightningModule,
) -> str | None:
    """Update checkpoint path.

    Args:
        cfg: Hydra config.
        model: Lightning model.

    Returns:
        Path to checkpoint or None.
    """
    ckpt_path = None
    if cfg.get("ckpt_path"):
        if cfg.get("resume_weights_only"):
            logger.info(
                f"Resuming only weights from checkpoint <{cfg['ckpt_path']}>"
            )
            checkpoint = torch.load(
                cfg["ckpt_path"],
                map_location=model.device,
            )
            model.load_state_dict(
                checkpoint["state_dict"],
                strict=False,
            )
        else:
            logger.info(f"Resuming from checkpoint <{cfg['ckpt_path']}>")
            ckpt_path = cfg["ckpt_path"]
    return ckpt_path
