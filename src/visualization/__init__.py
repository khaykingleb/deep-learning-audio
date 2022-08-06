"""Plots for digital singnal processing visualization."""

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
    audio_len: tp.Sized,
    sample_rate: int,
    power_to_db_transition: tp.Optional[bool] = True,
) -> None:
    """Plot audio singnal transformation.

    Args:
        transform (Tensor): Audio singnal transformation.
        title (str): Plot title.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        audio_len (Sized): Length of a digital signal.
        sample_rate (int): Sample rate for a digital signal.
        power_to_db_transition (bool, optional): Whether to use power-to-db transition
            according to the formula db = 10 * log_10(power) or not.
    """
    if power_to_db_transition:
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
