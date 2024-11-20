"""Audio signal visualizations."""

import io

import matplotlib.pyplot as plt
import torch


def plot_transform(
    x: torch.Tensor,
    *,
    title: str,
    x_label: str,
    y_label: str,
    sample_rate: int,
    audio_size: int,
    show_fig: bool | None = True,
) -> io.BytesIO:
    """Plot audio signal transformation and return it as a buffer.

    Args:
        x: Audio signal transformation
            with shape of (1, n_transform, input_length)
        title: Plot title
        x_label: Label for x-axis
        y_label: Label for y-axis
        sample_rate: Sample rate of a digital signal
        audio_size: Length of a digital signal
        show_fig: Whether to show the figure

    Returns:
        Buffer containing the plot image.
    """
    plt.title(title)
    plt.x_label(x_label)
    plt.y_label(y_label)
    plt.imshow(
        x.squeeze().detach().cpu().numpy(),
        origin="lower",
        aspect="auto",
        extent=[0, audio_size / sample_rate, 0, sample_rate / 2_000],
    )
    plt.grid(visible=False)
    buffer = io.BytesIO()
    plt.savefig(
        buffer,
        dpi=300,
        bbox_inches="tight",
        format="jpeg",
    )
    if not show_fig:
        plt.close()
    buffer.seek(0)
    return buffer
