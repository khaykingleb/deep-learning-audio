"""Realization of QuartzNet BxR architecture based on the proposed paper.

See:
https://arxiv.org/abs/1904.03288 (Jasper)
https://arxiv.org/abs/1910.10261 (QuartzNet)
"""

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
    ) -> None:
        """Constructor.

        Args:
            in_channels: number of channels in the input
            out_channels: number of produced channels by the convolution
            kernel_size: size of the convolving kernel
            stride: stride of the convolution
            padding: padding added to both sides of the input
            dilation: spacing between kernel elements
            groups: number of blocked connections from input channels
                to output channels
        """
        super().__init__()
        # 1D depthwise convolution that operates on each channel individually
        # but across kernel_size time frames
        self.depthwise_conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=in_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=in_channels,
        )
        # Pointwise convolution that operates on each time frame independently
        # but across all channels
        self.pointwise_conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=1,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Defines the 1D time-channel separable convolution structure.

        Args:
            x: tensor of shape (batch_size, in_channels, transform_length).

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
        dropout_rate: float = 0.25,
    ) -> None:
        """Constructor.

        Args:
            n_subblocks: number of subblocks within QuartzBlock (R)
            in_channels: number of channels in the input
            out_channels: number of produced channels by the convolution
            kernel_size: size of the convolving kernel
            dropout_rate: dropout rate
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
                            padding=(kernel_size - 1) // 2,
                        ),
                        nn.BatchNorm1d(num_features=out_channels),
                        nn.ReLU(inplace=False),
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
            nn.BatchNorm1d(num_features=out_channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Defines the QuartzNet's block structure."""
        residual = self.skip_connection(x)
        for i, subblock in enumerate(self.quartz_blocks):
            for _, module in enumerate(subblock):
                if i == len(self.quartz_blocks) - 1 and isinstance(
                    module, nn.ReLU
                ):
                    x = x + residual
                x = module(x)
        return x


class QuartzNet(nn.Module):
    """QuartzNet's design implementation based on the proposed paper.

    The architecture follows the QuartzNet BxR structure where:
    - B represents the number of blocks
    - R represents the number of subblocks within each block
    - Each block is repeated S times
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
        dropout_rate: float = 0.25,
    ) -> None:
        """Constructor.

        Args:
            in_channels: number of channels in the input which is
                the length of transform feature
            out_channels: number of channels in the output
                which is the size of vocabulary
            n_blocks: number of QuartzBlocks (B)
            n_repeats: number of times each block is repeated (S)
            n_subblocks: number of subblocks within QuartzBlock (R)
            block_channels: list of (in_channels, out_channels)
                for each block B
            block_kernel_sizes: list of kernel sizes for each block B
            normalization_name: name of normalization layer (e.g. BatchNorm1d)
            activation_name: name of activation layer (e.g. ReLU)
            dropout_rate: dropout rate for all layers
        """
        super().__init__()

        # Layer C_1: Conv-BN-ReLU
        initial_channels = block_channels[0][0]
        initial_kernel_size = block_kernel_sizes[0]
        initial_padding = (initial_kernel_size - 1) // 2
        self.C1 = nn.Sequential(
            nn.Conv1d(
                in_channels=in_channels,
                out_channels=initial_channels,
                kernel_size=initial_kernel_size,
                stride=2,
                padding=initial_padding,
            ),
            nn.BatchNorm1d(num_features=initial_channels),
            nn.ReLU(inplace=False),
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
                    n_subblocks=n_subblocks,  # R
                    in_channels=block_in_channels,
                    out_channels=block_out_channels,
                    kernel_size=block_kernel_sizes[i],
                    dropout_rate=dropout_rate,
                )
        self.Bs = nn.Sequential(blocks)

        # Layer C_2: Conv-BN-ReLU
        final_channels = block_channels[-1][1]
        self.C2 = nn.Sequential(
            nn.Conv1d(
                in_channels=final_channels,
                out_channels=512,
                kernel_size=87,
                padding=87 - 1,
                dilation=2,
            ),
            nn.BatchNorm1d(num_features=512),
            nn.ReLU(inplace=False),
            nn.Dropout(
                p=dropout_rate,
                inplace=False,
            ),
        )

        # Layer C_3: Conv-BN-ReLU
        self.C3 = nn.Sequential(
            nn.Conv1d(
                in_channels=512,
                out_channels=1024,
                kernel_size=1,
            ),
            nn.BatchNorm1d(num_features=1024),
            nn.ReLU(inplace=False),
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
        return x.log_softmax(dim=1)
