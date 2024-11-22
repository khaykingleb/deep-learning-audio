"""Entrypoint for the package."""

from pathlib import Path

__version__ = Path(".version").read_text().strip()
