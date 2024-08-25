"""Environment variables for the project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", "HUMAN")
LOGGING_ONLY_RANK_ZERO = os.getenv("LOGGING_ONLY_RANK_ZERO", True)

WANDB_API_KEY = os.getenv("WANDB_API_KEY")
