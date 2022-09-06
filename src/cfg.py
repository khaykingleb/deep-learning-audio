"""Configuration variables."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

WANDB_API_KEY = os.getenv("WANDB_API_KEY")
