"""Plots for a Digital Singnal Processing visualization."""

import io
import typing as tp

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
    show_fig: tp.Optional[bool] = True,
) -> io.BytesIO:
    """Plots audio singnal transformation and saves it to a buffer.

    Args:
        transform (Tensor): Audio singnal transformation of shape (1, n_transform, input_lenght).
        title (str): Plot title.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        sample_rate (int): Sample rate for a digital signal.
        audio_size (int): Length of a digital signal.
        show_fig (bool, optional): Whether to show the figure.

    Returns:
        BytesIO: Buffer.
    """
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.imshow(
        transform.squeeze().numpy(),
        origin="lower",
        aspect="auto",
        extent=[0, audio_size / sample_rate, 0, sample_rate / 2000],
    )
    plt.grid(False)
    buffer = io.BytesIO()
    plt.savefig(buffer, dpi=250, format="jpeg")
    if not show_fig:
        plt.close()
    buffer.seek(0)
    return buffer
