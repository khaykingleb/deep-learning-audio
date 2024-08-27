"""Audio functions for digital signal processing."""

from pathlib import Path

import torch
import torchaudio


def load_waveform(
    path: Path,
    *,
    sample_rate: int | None = None,
) -> torch.Tensor:
    """Load an audio file from a given path.

    Args:
        path (Path): Path to the audio file.
        sample_rate (int): Sample rate to resample the audio to.
            If None, the original sample rate is used.

    Returns:
        Digital audio signal.
    """
    waveform, sr = torchaudio.load(path)
    if sample_rate is not None and sr != sample_rate:
        waveform = torchaudio.functional.resample(
            waveform,
            orig_freq=sr,
            new_freq=sample_rate,
        )
    return waveform
