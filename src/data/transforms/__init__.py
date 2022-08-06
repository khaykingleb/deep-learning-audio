"""Digital signal transformations."""

import typing as tp

import torch
import torch.nn as nn
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig


# TODO: use librosa.power_to_db(spec) for spec and melspec?
def get_feature_extractors(dsp_config: DictConfig) -> tp.Dict[str, nn.Module]:
    """Common feature extractors for a digital signal.

    Args:
        dsp_config (DictConfig): Preprocess part of a configuration file.

    Returns:
        Dict: Common feature extractors.
    """
    window_length = round(dsp_config.sr * dsp_config.window_length_ms / 1000)
    hop_length = round(dsp_config.sr * dsp_config.hop_length_ms / 1000)
    return {
        "spectrogramer": T.Spectrogram(
            n_fft=window_length,
            win_length=window_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
        ),
        "melspectrogramer": T.MelSpectrogram(
            sample_rate=dsp_config.sr,
            f_min=dsp_config.frequency_min,
            f_max=dsp_config.frequency_max,
            n_fft=window_length,
            win_length=window_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
            n_mels=dsp_config.spectrogram.n_mels,
            mel_scale=dsp_config.spectrogram.mel_type,
        ),
        "mfccer": T.MFCC(
            sample_rate=dsp_config.sr,
            n_mfcc=dsp_config.mfcc.n_mfcc,
            dct_type=dsp_config.mfcc.dct_type,
            log_mels=dsp_config.mfcc.log_mels,
            melkwargs={
                "f_min": dsp_config.frequency_min,
                "f_max": dsp_config.frequency_max,
                "n_fft": window_length,
                "win_length": window_length,
                "hop_length": hop_length,
                "window_fn": torch.hann_window,
                "power": 2,
                "n_mels": dsp_config.spectrogram.n_mels,
                "mel_scale": dsp_config.spectrogram.mel_type,
            },
        ),
    }
