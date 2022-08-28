"""Utils for training models."""

import os
import random
import typing as tp

import numpy as np
import torch

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


def prepare_device(n_gpu: int) -> tp.Tuple[torch.device]:
    """Set up GPU device.

    Args:
        n_gpu (int): Number of GPU devices.

    Returns:
        Tuple: GPU device and its indices which are used for DataParallel
    """
    n_gpu_available = torch.cuda.device_count()
    if n_gpu > 0 and n_gpu_available == 0:
        logger.warn("There's no GPU available.")
        n_gpu = 0
    elif n_gpu_available > n_gpu:
        logger.warn(
            f"The number of GPU's configured to use is {n_gpu},"
            f" but only {n_gpu_available} are available."
        )
        logger.info(f"Training will be performed on {n_gpu_available} GPUs")
        n_gpu = n_gpu_available
    return torch.device("cuda:0" if n_gpu > 0 else "cpu"), list(range(n_gpu))
