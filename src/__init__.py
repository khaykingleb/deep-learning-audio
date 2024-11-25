"""Entrypoint for the package."""

from src.utils.env import BASE_DIR

__version__ = BASE_DIR.joinpath(".version").read_text().strip()
