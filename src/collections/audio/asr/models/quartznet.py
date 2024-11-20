"""Realization of QuartzNet BxR architecture based on the proposed paper.

https://arxiv.org/abs/1910.10261
"""

# TODO: Запихнуть инициализацию весов в модель?

from collections import OrderedDict

import torch
from torch import nn


class TCSConv(nn.Module):
    """1D time-channel separable convolution."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 1,
        dilation: int = 1,
        groups: int = 1,
    ) -> None:
        """Constructor.

        Args:
            in_channels: Number of channels in the input
            out_channels: Number of produced channels by the convolution
            kernel_size: Size of the convolving kernel
            stride: Stride of the convolution
            padding: Padding added to both sides of the input
            dilation: Spacing between kernel elements
            groups: Number of blocked connections from input channels
                to output channels
        """
        super().__init__()
        # 1D depthwise convolution that operates on each channel individually
        # but across kernel_size time frames
        self.depthwise_conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
        )
        # Pointwise convolution that operates on each time frame independently
        # but across all channels
        self.pointwise_conv = nn.Conv1d(
            in_channels=out_channels,
            out_channels=out_channels,
            kernel_size=1,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Defines the 1D time-channel separable convolution structure.

        Args:
            x: Tensor of shape (batch_size, in_channels, transform_length).

        Returns:
            Tensor of shape (batch_size, out_channels, transform_length).
        """
        return self.pointwise_conv(self.depthwise_conv(x))


class QuartzBlock(nn.Module):
    """QuartzNet's block that is repeated S times containing R subblocks."""

    def __init__(
        self,
        n_subblocks: int,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        normalization: type[nn.Module],
        activation: type[nn.Module],
        dropout_rate: float = 0.25,
    ) -> None:
        """Constructor.

        Args:
            n_subblocks (int): Number of subblocks within QuartzBlock.
            in_channels (int): Number of channels in the input.
            out_channels (int): Number of produced channels by the convolution.
            kernel_size (int): Size of the convolving kernel.
            normalization (Module): Normalization layer.
            activation (Module): Activation layer.
            dropout_rate (float): Dropout rate.
        """
        super().__init__()
        self.quartz_blocks = nn.ModuleList(
            [
                nn.ModuleList(
                    [
                        TCSConv(
                            in_channels=in_channels
                            if i == 0
                            else out_channels,
                            out_channels=out_channels,
                            kernel_size=kernel_size,
                            padding=kernel_size // 2,
                            groups=in_channels if i == 0 else out_channels,
                        ),
                        normalization(num_features=out_channels),
                        activation(inplace=False),
                        nn.Dropout(
                            p=dropout_rate,
                            inplace=False,
                        ),
                    ]
                )
                for i in range(n_subblocks)
            ]
        )
        self.skip_connection = nn.Sequential(
            nn.Conv1d(
                in_channels,
                out_channels,
                kernel_size=1,
            ),
            normalization(num_features=out_channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Defines the QuartzNet's block structure."""
        residual = self.skip_connection(x)
        for i, subblock in enumerate(self.quartz_blocks):
            for j, module in enumerate(subblock):
                if i == len(self.quartz_blocks) - 1 and j == len(subblock) - 1:
                    x = x + residual
                x = module(x)
        return x


class QuartzNet(nn.Module):
    """QuartzNet's design implementation based on the proposed paper.

    The architecture follows the QuartzNet BxR structure where:
    - B represents the number of blocks.
    - R represents the number of subblocks within each block.
    - Each block is repeated S times.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        n_blocks: int = 5,
        n_repeats: int = 3,
        n_subblocks: int = 5,
        block_channels: list[tuple[int, int]] | None = None,
        block_kernel_sizes: list[int] | None = None,
        normalization_name: str = "BatchNorm1d",
        activation_name: str = "ReLU",
        dropout_rate: float = 0.25,
    ) -> None:
        """Constructor.

        Args:
            in_channels: Number of channels in the input which is
                the length of transform feature
            hidden_channels: Number of channels in the hidden layers
            out_channels: Number of channels in the output
                which is the size of vocabulary
            n_blocks: Number of QuartzBlocks (B)
            n_repeats: Number of times each block is repeated (S)
            n_subblocks: Number of subblocks within QuartzBlock (R)
            block_channels: List of (in_channels, out_channels)
                for each block B
            block_kernel_sizes: List of kernel sizes for each block B
            normalization_name: Name of normalization layer (e.g. BatchNorm1d)
            activation_name: Name of activation layer (e.g. ReLU)
            dropout_rate: Dropout rate
        """
        super().__init__()
        normalization = getattr(nn, normalization_name)
        activation = getattr(nn, activation_name)

        # Layer C_1: TCSConv-Normalization-Activation
        initial_channels = block_channels[0][0]
        self.C1 = nn.Sequential(
            TCSConv(
                in_channels=in_channels,
                out_channels=initial_channels,
                kernel_size=33,
                stride=2,
                padding=33 // 2,
                groups=in_channels,
            ),
            normalization(num_features=initial_channels),
            activation(inplace=False),
            nn.Dropout(
                p=dropout_rate,
                inplace=False,
            ),
        )

        # Blocks B_1, ..., B_B that are repeated S times
        # with R subblocks in each block
        blocks = OrderedDict()
        for i in range(n_blocks):  # B
            for j in range(n_repeats):  # S
                block_in_channels, block_out_channels = block_channels[i]
                block_in_channels = (
                    block_in_channels if j == 0 else block_out_channels
                )  # adjust in_channels for repeats
                blocks[f"B_{i}{j}"] = QuartzBlock(
                    n_subblocks,  # R
                    block_in_channels,
                    block_out_channels,
                    block_kernel_sizes[i],
                    normalization,
                    activation,
                    dropout_rate,
                )
        self.Bs = nn.Sequential(blocks)

        # Layer C_2: TCSConv-Normalization-Activation
        final_channels = block_channels[-1][1]
        self.C2 = nn.Sequential(
            TCSConv(
                in_channels=final_channels,
                out_channels=512,
                kernel_size=87,
                padding=87 - 1,
                dilation=2,
                groups=512,
            ),
            normalization(num_features=512),
            activation(inplace=False),
            nn.Dropout(
                p=dropout_rate,
                inplace=False,
            ),
        )

        # Layer C_3: Conv-Normalization-Activation
        self.C3 = nn.Sequential(
            nn.Conv1d(
                in_channels=512,
                out_channels=1024,
                kernel_size=1,
            ),
            normalization(num_features=1024),
            activation(inplace=False),
            nn.Dropout(
                p=dropout_rate,
                inplace=False,
            ),
        )

        # Layer C_4: Pointwise Conv
        self.C4 = nn.Conv1d(
            in_channels=1024,
            out_channels=out_channels,
            kernel_size=1,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Defines the QuartzNet structure."""
        x = self.C1(x)
        x = self.Bs(x)
        x = self.C2(x)
        x = self.C3(x)
        x = self.C4(x)
        return x.softmax(dim=1)
