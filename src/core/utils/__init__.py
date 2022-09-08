"""Utils for training models."""

import os
import random
import typing as tp

import numpy as np
import torch
import torch.nn as nn
from omegaconf import DictConfig
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler

from ... import cfg
from ...logging import logger


def fix_seed(seed: int) -> None:
    """Fix the seed for some vauge reproducibility.

    Args:
        seed (int): The seed to use.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:2"
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.enabled = False
    torch.backends.cudnn.deterministic = True


def prepare_device(n_gpu: int) -> tp.Tuple[torch.device, tp.List[int]]:
    """Set up GPU device.

    Args:
        n_gpu (int): Number of GPU devices.

    Returns:
        Tuple: GPU device and its indices which are used for DataParallel
    """
    n_gpu_available = torch.cuda.device_count()
    if n_gpu > 0 and n_gpu_available == 0:
        logger.warn("There's no GPU available. Use CPU instead.")
        n_gpu = 0
    elif n_gpu_available > n_gpu:
        logger.warn(
            f"The number of GPU's configured to use is {n_gpu},"
            f" but only {n_gpu_available} are available."
        )
        logger.info(f"Training will be performed on {n_gpu_available} GPUs")
        n_gpu = n_gpu_available
    return torch.device("cuda:0" if n_gpu > 0 else "cpu"), list(range(n_gpu))


def move_batch_to_device(
    batch: tp.Dict[str, tp.Any],
    device: torch.device,
    *,
    fields_on_device: tp.List[str],
) -> tp.Dict[str, tp.Any]:
    """Move all necessary fields to the device.

    Args:
        batch (Dict): Collated batch.
        device: CPU or GPU device.
        fields_on_device (List): What fields move to the device.

    Returns:
        Dict: Batch with selected fields on device.
    """
    for field in fields_on_device:
        batch[field] = batch[field].to(device)
    return batch


def save_architecture(
    config: DictConfig,
    epoch: int,
    model: nn.Module,
    optimizer: Optimizer,
    scheduler: _LRScheduler,
) -> None:
    """Save architecture.

    Args:
        config (DictConfig): Configuration used for architecture.
        epoch (int): Last epoch.
        model (Module): Nural network.
        optimizer (Optimizer): Optimizer used to optimize the model's weights.
        scheduler (_LRScheduler): Scheduler used to choose the learning rate for GD.
    """
    state = {
        "config": config,
        "epoch": epoch,
        "model": model.state_dict(),
        "model_name": type(model).__name__,
        "optimizer": optimizer.state_dict(),
        "optimizer_name": type(optimizer).__name__,
        "scheduler": scheduler.state_dict(),
        "scheduler_name": type(scheduler).__name__,
    }
    torch.save(state, cfg.BASE_DIR / config.model.path_to_save)
