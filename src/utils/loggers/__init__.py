"""Entry point for the loggers module."""

import sys

from loguru import logger

from src.utils import env

if env.LOGGING_FORMAT == "HUMAN":
    handler = {
        "level": env.LOGGING_LEVEL,
        "sink": sys.stdout,
        "format": (
            "<level>{level}</level>: {time:YYYY-MM-DD at HH:mm:ss} | <blue>{name}</blue> | "
            "<level>{message}</level>"
        ),
        "colorize": True,
        "enqueue": True,
    }

elif env.LOGGING_FORMAT == "JSONL":
    handler = {
        "level": env.LOGGING_LEVEL,
        "sink": sys.stdout,
        "format": "{message}",
        "serialize": True,
        "enqueue": True,
    }

else:
    raise ValueError("LOGGING_FORMAT can be only HUMAN or JSONL")

logger.configure(handlers=[handler])
