"""Augmentations for digital signal transformations."""

import random

import torch
import torch.nn as nn
import torchaudio.transforms as T  # NOQA
from omegaconf import DictConfig


class TransformAugmenter:
    """Augments DSP tranformations."""

    def __init__(
        self: "TransformAugmenter",
        augmentation_config: DictConfig,
    ) -> None:
        """Constructor.

        Args:
            augmentation_config (DictConfig): Augmentation part of DSP tranformation of a
                configuration file.
        """
        self.augmentation_config = augmentation_config

    def __get_feature_masker(
        self: "TransformAugmenter",
        transformation_size: int,
    ) -> nn.Module:
        """Gets feature masker to mask y-axis.

        Args:
            transformation_size (int): Length of y-axis.

        Returns:
            torchaudio.transforms.FrequencyMasking.
        """
        return T.FrequencyMasking(
            freq_mask_param=round(self.augmentation_config.feature_portion * transformation_size)
        )

    def __get_time_masker(
        self: "TransformAugmenter",
        time_size: int,
    ) -> nn.Module:
        """Gets time masker to mask x-axis.

        Args:
            time_size (int): Length of x-axis.

        Returns:
            torchaudio.transforms.TimeMasking.
        """
        return T.TimeMasking(
            time_mask_param=round(self.augmentation_config.time_portion * time_size),
            p=self.augmentation_config.time_portion * self.augmentation_config.n_time_masks,
        )

    def __feature_time_mask(
        self: "TransformAugmenter",
        transformation: torch.Tensor,
    ) -> torch.Tensor:
        """Masks x- and y-axes of DSP transformation.

        Args:
            transformation (Tensor): DSP transformation of shape (1, n_feature, n_time).

        Returns:
            Tensor: Transformation with augmented x- and y-axes.
        """
        transformation_size, time_size = transformation.squeeze().shape
        feature_masker = self.__get_feature_masker(transformation_size)
        time_masker = self.__get_time_masker(time_size)
        aug_type = random.randint(0, 2)
        if aug_type == 0:
            for _ in range(self.augmentation_config.n_feature_masks):
                if random.random() <= self.augmentation_config.feature_mask_prob:
                    transformation = feature_masker(transformation)
        elif aug_type == 1:
            for _ in range(self.augmentation_config.n_time_masks):
                if random.random() <= self.augmentation_config.time_mask_prob:
                    transformation = time_masker(transformation)
        else:
            transformation = feature_masker(transformation)
            transformation = time_masker(transformation)
        return transformation

    def __call__(
        self: "TransformAugmenter",
        transformation: torch.Tensor,
    ) -> torch.Tensor:
        """Augmentate transformation of a digital signal.

        Args:
            transformation (Tensor): DSP transformation of shape (1, n_feature, n_time).

        Returns:
            Tensor: Augmented transformation.
        """
        use_aug = random.choices(
            [False, True],
            weights=[
                1 - self.augmentation_config.feature_time_mask_prob,
                self.augmentation_config.feature_time_mask_prob,
            ],
        )[0]
        if use_aug:
            transformation = self.__feature_time_mask(transformation)
        return transformation
