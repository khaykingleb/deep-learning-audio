"""Digital signals."""

import torch
import torchaudio
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig


def load_audio(path: str, dsp_config: DictConfig) -> torch.Tensor:
    """Load an audio file from a given path and resample it with the accordance to config sample rate if needed.

    Args:
        path (str): Path to the audio file.
        dsp_config (DictConfig): Preprocess part of the configuration file.

    Returns:
        Tensor: Digital audio signal with shape of (1, audio_len).
    """
    audio, sample_rate = torchaudio.load(path)
    audio = audio[:1, :]  # remove all channels but the first
    if sample_rate != dsp_config.audio.sr:
        audio = T.Resample(sample_rate, dsp_config.audio.sr)(audio)
    return audio
