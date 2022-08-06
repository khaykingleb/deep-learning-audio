"""Digital signal transformations."""

import typing as tp

import torch
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig


# TODO: use librosa.power_to_db(spec) for spec and melspec?
def get_feature_extractors(config: DictConfig) -> tp.Dict[str, tp.Any]:
    """Common feature extractors for a digital signal.

    Args:
        config (DictConfig): Configuration file.

    Returns:
        Dict: Common feature extractors.
    """
    wav_config = config.preprocess
    window_length = round(wav_config.sr * wav_config.window_length_ms / 1000)
    hop_length = round(wav_config.sr * wav_config.hop_length_ms / 1000)
    return {
        "spectrogramer": T.Spectrogram(
            n_fft=window_length,
            win_length=window_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
        ),
        "melspectrogramer": T.MelSpectrogram(
            sample_rate=wav_config.sr,
            f_min=wav_config.frequency_min,
            f_max=wav_config.frequency_max,
            n_fft=window_length,
            win_length=window_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=2,
            n_mels=wav_config.spectrogram.n_mels,
            mel_scale=wav_config.spectrogram.mel_type,
        ),
        "mfccer": T.MFCC(
            sample_rate=wav_config.sr,
            n_mfcc=wav_config.mfcc.n_mfcc,
            dct_type=wav_config.mfcc.dct_type,
            log_mels=wav_config.mfcc.log_mels,
            melkwargs={
                "f_min": wav_config.frequency_min,
                "f_max": wav_config.frequency_max,
                "n_fft": window_length,
                "win_length": window_length,
                "hop_length": hop_length,
                "window_fn": torch.hann_window,
                "power": 2,
                "n_mels": wav_config.spectrogram.n_mels,
                "mel_scale": wav_config.spectrogram.mel_type,
            },
        ),
    }
