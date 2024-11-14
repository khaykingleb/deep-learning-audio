"""Environment variables for the project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_SINK_TO_FILE = os.getenv("LOGGING_SINK_TO_FILE", True)
LOGGING_ONLY_RANK_ZERO = os.getenv("LOGGING_ONLY_RANK_ZERO", True)

WANDB_API_KEY = os.getenv("WANDB_API_KEY")
