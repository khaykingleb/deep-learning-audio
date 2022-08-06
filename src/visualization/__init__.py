"""Plots for a digital singnal processing visualization."""

import typing as tp

import librosa
import matplotlib.pyplot as plt
import torch


def plot_signal_transformation(
    transform: torch.Tensor,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    sample_rate: int,
    audio_len: int,
    use_db_transition: tp.Optional[bool] = True,
) -> None:
    """Plot audio singnal transformation.

    Args:
        transform (Tensor): Audio singnal transformation.
        title (str): Plot title.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        sample_rate (int): Sample rate for a digital signal.
        audio_len (int): Length of a digital signal.
        use_db_transition (bool, optional): Whether to use power-to-db transition
            according to the formula db = 10 * log_10(power) or not.
    """
    if use_db_transition:
        transform = librosa.power_to_db(transform)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.imshow(
        transform,
        origin="lower",
        aspect="auto",
        extent=[0, len(audio_len) / sample_rate, 0, sample_rate / 2000],
    )
    plt.grid()
