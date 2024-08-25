"""Audio signal visualizations."""

import io

import matplotlib.pyplot as plt
import torch


def plot_transform(
    x: torch.Tensor,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    sample_rate: int,
    audio_size: int,
    show_fig: bool | None = True,
) -> io.BytesIO:
    """Plot audio signal transformation and return it as a buffer.

    Args:
        x (Tensor): Audio singnal transformation with shape of (1, n_transform, input_lenght).
        title (str): Plot title.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        sample_rate (int): Sample rate of a digital signal.
        audio_size (int): Length of a digital signal.
        show_fig (bool, optional): Whether to show the figure.

    Returns:
        Buffer containing the plot image.
    """
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.imshow(
        x.squeeze().detach().cpu().numpy(),
        origin="lower",
        aspect="auto",
        extent=[0, audio_size / sample_rate, 0, sample_rate / 2_000],
    )
    plt.grid(False)
    buffer = io.BytesIO()
    plt.savefig(buffer, dpi=300, bbox_inches="tight", format="jpeg")
    if not show_fig:
        plt.close()
    buffer.seek(0)
    return buffer
