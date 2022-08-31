"""Loss functions for Automatic Speech Recognition."""

import torch.nn as nn


class CTCLossWrapper(nn.CTCLoss):
    """Wrapper around Pytorch Connectionist Temporal Classification loss."""

    def __init__(
        self: "CTCLossWrapper",
        blank_idx: int,
    ) -> None:
        """Constructor.

        Args:
            blank_idx (int): Index of the blank token.
        """
        super().__init__(blank=blank_idx)
