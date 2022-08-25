"""Digital signals."""

import torch
import torchaudio
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig

from .augmentation import AudioAugmenter


def load_audio(path: str, dsp_config: DictConfig, use_aug: bool) -> torch.Tensor:
    """Load an audio file from a given path and resample it with the accordance to config sample.

    Args:
        path (str): Path to the audio file.
        dsp_config (DictConfig): Preprocess part of the configuration file.
        use_aug (bool): Whether to augment the audio or not.

    Returns:
        Tensor: Digital audio signal with shape of (1, audio_len).
    """
    audio, sample_rate = torchaudio.load(path)
    if use_aug:
        augmenter = AudioAugmenter(dsp_config.audio.augmentation)
        audio = augmenter(audio, sample_rate)
        sample_rate = augmenter.sample_rate
    audio = audio[:1, :]  # remove all channels but the first
    if sample_rate != dsp_config.audio.sr:
        resampler = T.Resample(sample_rate, dsp_config.audio.sr)
        audio = resampler(audio)
    return audio
