"""Datasets for training ASR models."""

from src.collections.audio.asr.datasets.base import ASRDataset
from src.collections.audio.asr.datasets.libri import LibriSpeechDataset
from src.collections.audio.asr.datasets.lj import LJSpeechDataset

__all__ = ["ASRDataset", "LJSpeechDataset", "LibriSpeechDataset"]
