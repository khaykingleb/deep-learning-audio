"""Connectionist Temporal Classification loss."""

import typing as tp

import torch
import torch.nn as nn


class CTCLossWrapper(nn.CTCLoss):
    """Wrapper around Pytorch CTCLoss."""

    def __init__(
        self: "CTCLossWrapper",
        blank_idx: int,
    ) -> None:
        """Constructor.

        Args:
            blank_idx (int): Index of the blank token.
        """
        super().__init__(blank=blank_idx)

    def forward(
        self: "CTCLossWrapper",
        log_probs: torch.Tensor,
        targets: torch.Tensor,
        input_lengths: tp.List[int],
        target_lengths: tp.List[int],
    ) -> torch.Tensor:
        """Computes CTC loss function.

        Args:
            log_probs (Tensor): Logarithmized probabilities of shape (input_length, batch_size, vocab_size).
            targets (Tensor): Encoded texts of shape (batch_size, max_target_length).
            input_lengths (List): Transformation lengths.
            target_lengths (List): Encoded texts lengths.

        Returns:
            Tensor: CTC loss value.
        """
        return super().forward(
            log_probs,
            targets,
            input_lengths,
            target_lengths,
        )
