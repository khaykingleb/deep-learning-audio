"""Entry point for the configuration of the logging system."""

import sys

from loguru import logger

from src.utils import env

console_handler = {
    "level": env.LOGGING_LEVEL,
    "sink": sys.stdout,
    "format": (
        "{time:YYYY-MM-DD HH:mm:ss} | {name} | "
        "<level>{level}: {message}</level> | {extra}"
    ),
    "colorize": True,
    "enqueue": True,
}

log_config = {"handlers": [console_handler]}
logger.configure(**log_config)
