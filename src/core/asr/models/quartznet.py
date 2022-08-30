"""Realization of QuartzNet BxR architecture based on the proposed paper — https://arxiv.org/abs/1910.10261."""

import typing as tp
from collections import OrderedDict

import torch
import torch.nn as nn
from omegaconf import DictConfig


class TCSConv(nn.Module):
    """1D time-channel separable convolution."""

    def __init__(
        self: "TCSConv",
        in_channels: int,
        out_channels: int,
        kernel_size: tp.Optional[int] = 1,
        stride: tp.Optional[int] = 1,
        padding: tp.Optional[int] = 1,
        dilation: tp.Optional[int] = 1,
        groups: tp.Optional[int] = 1,
    ) -> None:
        """Constructor.

        Args:
            in_channels (int): Number of channels in the input.
            out_channels (int): Number of produced channels by the convolution.
            kernel_size (int, optional): Size of the convolving kernel.
            stride (int, optional): Stride of the convolution.
            padding (int, optional): Padding added to both sides of the input.
            dilation (int, optional): Spacing between kernel elements.
            groups (int, optional): Number of blocked connections from input channels to output channels.
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
        self.pointwise_conv = nn.Conv1d(out_channels, out_channels, kernel_size=1)

    def forward(self: "TCSConv", x: torch.Tensor) -> torch.Tensor:
        """Defines the 1D time-channel separable convolution structure.

        Args:
            x: Tensor of shape (batch_size, in_channels, transform_length).

        Returns:
            Tensor of shape (batch_size, out_channels, transform_length).
        """
        return self.pointwise_conv(self.depthwise_conv(x))


class QuartzBlock(nn.Module):
    """QuartzNet’s block that is repeated S times containing R subblocks."""

    def __init__(
        self: "QuartzBlock",
        n_subblocks: int,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        normalization: nn.Module,
        activation: nn.Module,
    ) -> None:
        """Constructor.

        Args:
            n_subblocks (int): Number of subblocks within QuartzBlock.
            in_channels (int): Number of channels in the input.
            out_channels (int): Number of produced channels by the convolution.
            kernel_size (int): Size of the convolving kernel.
            normalization (Module): Normalization layer.
            activation (Module): Activation layer.
        """
        super().__init__()
        self.R = n_subblocks
        self.quartz_blocks = nn.ModuleList(
            [
                nn.ModuleList(
                    [
                        TCSConv(
                            in_channels=in_channels if i == 0 else out_channels,
                            out_channels=out_channels,
                            kernel_size=kernel_size,
                            padding=kernel_size // 2,
                            groups=in_channels if i == 0 else out_channels,
                        ),
                        normalization(num_features=out_channels),
                        activation(inplace=True),
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

    def forward(self: "QuartzBlock", x: torch.Tensor) -> torch.Tensor:
        """Defines the QuartzNet's block structure.

        Args:
            x: Tensor of shape (batch_size, in_channels, transform_length).

        Returns:
            Tensor of shape (batch_size, out_channels, transform_lenght).
        """
        residual = self.skip_connection(x)
        for i, subblock in enumerate(self.quartz_blocks):
            for j, module in enumerate(subblock):
                if i == self.R - 1 and j == 3:
                    x += residual
                x = module(x)
        return x


class QuartzNet(nn.Module):
    """QuartzNet’s design implementation based on the proposed paper."""

    def __init__(self: "QuartzNet", config: DictConfig, vocab_size: int) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
            vocab_size (int): Size of vocabulary used.
        """
        super().__init__()
        normalization = getattr(nn, config.model.normalization.name)
        activation = getattr(nn, config.model.activation.name)

        # Layer C_1: TCSConv-Normalization-Activation
        self.C1 = nn.Sequential(
            TCSConv(
                in_channels=config.preprocess.transform.n_transform,
                out_channels=config.model.args.initial_hidden_channels,
                kernel_size=33,
                stride=2,
                padding=33 // 2,
                groups=config.preprocess.transform.n_transform,
            ),
            normalization(num_features=256),
            activation(inplace=True),
        )

        # Blocks B_1, ...., B_B blocks that repeated S times with R sublocks in each block
        blocks = OrderedDict()
        for i in range(config.model.args.B):
            for j in range(config.model.args.S):
                channels = list(map(int, config.model.args.block_hidden_channels[i].split(",")))
                in_channels = channels[0] if j == 0 else channels[1]
                out_channels = channels[1]
                blocks[f"B_{i}{j}"] = QuartzBlock(
                    config.model.args.R,
                    in_channels,
                    out_channels,
                    config.model.args.block_kernel_sizes[i],
                    normalization,
                    activation,
                )
        self.Bs = nn.Sequential(blocks)

        # Layer C_2: TCSConv-Normalization-Activation
        self.C2 = nn.Sequential(
            TCSConv(
                in_channels=int(config.model.args.block_hidden_channels[-1].split(",")[0]),
                out_channels=512,
                kernel_size=87,
                padding=87 - 1,
                dilation=2,
                groups=512,
            ),
            normalization(num_features=512),
            activation(inplace=True),
        )

        # Layer C_3: Conv-Normalization-Activation
        self.C3 = nn.Sequential(
            nn.Conv1d(in_channels=512, out_channels=1024, kernel_size=1),
            normalization(num_features=1024),
            activation(inplace=True),
        )

        # Layer C_4: Pointwise Conv
        self.C4 = nn.Conv1d(in_channels=1024, out_channels=vocab_size, kernel_size=1)

    def forward(self: "QuartzNet", x: torch.Tensor) -> torch.Tensor:
        """Defines the QuartzNet structure.

        Args:
            x: Tensor of shape (batch_size, in_channels, transform_length).

        Returns:
            Tensor of shape (batch_size, vocab_size, ceil(transform_lenght / 2)).
        """
        x = self.C1(x)
        x = self.Bs(x)
        x = self.C2(x)
        x = self.C3(x)
        x = self.C4(x)
        return x.softmax(dim=1)
