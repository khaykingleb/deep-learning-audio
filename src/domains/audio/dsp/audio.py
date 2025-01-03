"""Functions for processing digital audio signals."""

import torch
import torchaudio


def load_waveform(
    path: str,
    *,
    sample_rate: int | None = None,
) -> torch.Tensor:
    """Load and optionally resample an audio file.

    Args:
        path: Path to the audio file.
        sample_rate: Sample rate to resample the audio to.
            If None, the original sample rate is used.

    Returns:
        Digital audio signal.
    """
    waveform, sr = torchaudio.load(path)
    if sample_rate and sr != sample_rate:
        return torchaudio.functional.resample(
            waveform,
            orig_freq=sr,
            new_freq=sample_rate,
        )
    return waveform
