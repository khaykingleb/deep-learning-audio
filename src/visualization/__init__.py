"""Plots for a Digital Singnal Processing visualization."""

import matplotlib.pyplot as plt
import torch


def plot_signal_transformation(
    transform: torch.Tensor,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    sample_rate: int,
    audio_size: int,
) -> None:
    """Plot audio singnal transformation.

    Args:
        transform (Tensor): Audio singnal transformation.
        title (str): Plot title.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        sample_rate (int): Sample rate for a digital signal.
        audio_size (int): Length of a digital signal.
    """
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.imshow(
        transform,
        origin="lower",
        aspect="auto",
        extent=[0, audio_size / sample_rate, 0, sample_rate / 2000],
    )
    plt.grid()
