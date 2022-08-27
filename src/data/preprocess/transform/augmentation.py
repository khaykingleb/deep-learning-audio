"""Augmentations for digital signal transformations."""

import random

import torch
import torch.nn as nn
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig


class TransformCutoutAugmenter:
    """Augments DSP tranformations by zeroing out rectangulars as described in https://arxiv.org/abs/1708.04552."""

    def __init__(  # NOQA
        self: "TransformCutoutAugmenter",
        aug_config: DictConfig,
    ) -> None:
        pass

    def __call__(  # NOQA
        self: "TransformCutoutAugmenter",
        transform: torch.Tensor,
    ) -> torch.Tensor:
        pass


class TransformMaskAugmenter:
    """Augments DSP tranformations by zeroing out vertical and horizontal sections as described in https://arxiv.org/abs/1904.08779."""

    def __init__(
        self: "TransformMaskAugmenter",
        aug_config: DictConfig,
    ) -> None:
        """Constructor.

        Args:
            aug_config (DictConfig): Augmentation part of DSP tranformation of a configuration file.
        """
        self.aug_config = aug_config

    def __get_feature_masker(
        self: "TransformMaskAugmenter",
        transform_size: int,
    ) -> nn.Module:
        """Gets feature masker to mask y-axis.

        Args:
            transform_size (int): Length of y-axis.

        Returns:
            torchaudio.transforms.FrequencyMasking.
        """
        return T.FrequencyMasking(
            freq_mask_param=round(self.aug_config.feature_portion * transform_size)
        )

    def __get_time_masker(
        self: "TransformMaskAugmenter",
        time_size: int,
    ) -> nn.Module:
        """Gets time masker to mask x-axis.

        Args:
            time_size (int): Length of x-axis.

        Returns:
            torchaudio.transforms.TimeMasking.
        """
        return T.TimeMasking(
            time_mask_param=round(self.aug_config.time_portion * time_size),
            p=self.aug_config.time_portion * self.aug_config.n_time_masks,
        )

    def __feature_time_mask(
        self: "TransformMaskAugmenter",
        transform: torch.Tensor,
    ) -> torch.Tensor:
        """Masks x- and y-axes of DSP transformation.

        Args:
            transform (Tensor): DSP transformation of shape (1, n_feature, n_time).

        Returns:
            Tensor: Transformation with augmented x- and y-axes.
        """
        transform_size, time_size = transform.squeeze().shape
        feature_masker = self.__get_feature_masker(transform_size)
        time_masker = self.__get_time_masker(time_size)
        aug_type = random.randint(0, 2)
        if aug_type == 0:
            for _ in range(self.aug_config.n_feature_masks):
                if random.random() <= self.aug_config.feature_mask_prob:
                    transform = feature_masker(transform)
        elif aug_type == 1:
            for _ in range(self.aug_config.n_time_masks):
                if random.random() <= self.aug_config.time_mask_prob:
                    transform = time_masker(transform)
        else:
            transform = feature_masker(transform)
            transform = time_masker(transform)
        return transform

    def __call__(
        self: "TransformMaskAugmenter",
        transform: torch.Tensor,
    ) -> torch.Tensor:
        """Augmentate transformation of a digital signal.

        Args:
            transform (Tensor): DSP transformation of shape (1, n_feature, n_time).

        Returns:
            Tensor: Augmented transformation.
        """
        use_aug = random.choices(
            [False, True],
            weights=[
                1 - self.aug_config.feature_time_mask_prob,
                self.aug_config.feature_time_mask_prob,
            ],
        )[0]
        if use_aug:
            transform = self.__feature_time_mask(transform)
        return transform
