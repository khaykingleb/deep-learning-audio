"""Digital signal transformations."""

import typing as tp

import librosa
import torch
import torch.nn as nn
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig

from .augmentation import TransformAugmenter
from ..audio.augmentation import AudioAugmenter

Transform = tp.Union[
    T._transforms.Spectrogram,
    T._transforms.MelSpectrogram,
    T._transforms.MFCC,
]


def get_feature_extractors(dsp_config: DictConfig) -> tp.Dict[str, Transform]:
    """Common feature extractors for a digital signal.

    Args:
        dsp_config (DictConfig): Preprocess part of a configuration file.

    Returns:
        Dict: Common feature extractors.
    """
    win_length = round(dsp_config.audio.sr * dsp_config.transform.win_length_ms / 1000)
    hop_length = round(dsp_config.audio.sr * dsp_config.transform.hop_length_ms / 1000)
    return {
        "spectrogramer": T.Spectrogram(
            n_fft=win_length,
            win_length=win_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
        ),
        "melspectrogramer": T.MelSpectrogram(
            sample_rate=dsp_config.audio.sr,
            f_min=dsp_config.audio.frequency_min,
            f_max=dsp_config.audio.frequency_max,
            n_fft=win_length,
            win_length=win_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
            n_mels=dsp_config.transform.melspectrogram.n_mels,
            mel_scale=dsp_config.transform.melspectrogram.mel_type,
        ),
        "mfccer": T.MFCC(
            sample_rate=dsp_config.audio.sr,
            n_mfcc=dsp_config.transform.mfcc.n_mfcc,
            dct_type=dsp_config.transform.mfcc.dct_type,
            log_mels=dsp_config.transform.mfcc.log_mels,
            melkwargs={
                "f_min": dsp_config.audio.frequency_min,
                "f_max": dsp_config.audio.frequency_max,
                "n_fft": win_length,
                "win_length": win_length,
                "hop_length": hop_length,
                "window_fn": torch.hann_window,
                "power": 2,
                "n_mels": dsp_config.transform.melspectrogram.n_mels,
                "mel_scale": dsp_config.transform.melspectrogram.mel_type,
            },
        ),
    }


def preprocess_audio(
    audio: torch.Tensor,
    dsp_config: DictConfig,
    *,
    use_aug: bool,
) -> tp.Tuple[torch.Tensor]:
    """Performs digital signal processing with augmentation if specified.

    Args:
        audio (Tensor): Original digital signal.
        dsp_config (DictConfig): Preprocess part of a configuration file.
        use_aug (bool): Whether to use audio and transformation augmentation.

    Returns:
        Tuple: Digital signal and its transformation with augmentation if specified.
    """
    if use_aug:
        audio_augmenter = AudioAugmenter(dsp_config.audio.augmentation)
        audio = audio_augmenter(audio, sample_rate=dsp_config.audio.sr)

    feature_extractors = get_feature_extractors(dsp_config)
    transform = feature_extractors[dsp_config.main_transform](audio)
    if dsp_config.main_transform != "mfccer":
        transform = librosa.power_to_db(transform)

    if use_aug:
        transform_augmenter = TransformAugmenter(dsp_config.transform.augmentation)
        transform = transform_augmenter(transform)

    return audio, transform
