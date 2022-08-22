"""Utils."""

import os
import random

import numpy as np
import torch


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
