"""Collates data samples for dataloader."""

import math
import typing as tp
from abc import ABC, abstractmethod

import torch
from omegaconf import DictConfig


class Collater(ABC):
    """Abstract base class for collater."""

    @abstractmethod
    def __init__(self: "Collater", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        pass

    @abstractmethod
    def __call__(
        self: "Collater",
        batch: tp.List[tp.Dict[str, tp.Any]],
    ) -> tp.Dict[str, tp.Union[torch.Tensor, tp.List[torch.Tensor], tp.List[str]]]:
        """Collates samples and pads samples' fields in dataset.

        Args:
            batch (List): Batch of samples.

        Returns:
            Dict: Collated batch with padded fields.
        """
        pass


class ASRCollater(Collater):
    """ASR Collater of samples for dataloader with padding."""

    def __init__(self: "ASRCollater", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        self.config = config

    def __call__(
        self: "ASRCollater",
        samples: tp.List[tp.Dict[str, tp.Any]],
    ) -> tp.Dict[str, tp.Union[tp.List[str], tp.List[int], torch.Tensor, tp.List[torch.Tensor]]]:
        """Collates samples and pads samples' fields in dataset.

        Args:
            samples (List): Samples of data.

        Returns:
            Dict: Collated batch with padded fields.
        """
        max_encoded_text_length_sample = max(samples, key=lambda s: s["encoded_text"].shape[1])
        max_encoded_text_length = max_encoded_text_length_sample["encoded_text"].shape[1]
        max_transform_length_sample = max(samples, key=lambda s: s["transform"].shape[2])
        max_transform_length = max_transform_length_sample["transform"].shape[2]

        texts, encoded_texts, encoded_text_lengths = [], [], []
        audios, transforms, char_probs_lengths = [], [], []
        for sample in samples:
            texts.append(sample["text"])
            pad_size = max_encoded_text_length - sample["encoded_text"].shape[1]
            pad_tensor = torch.zeros(1, pad_size)
            encoded_text = torch.cat([sample["encoded_text"], pad_tensor], dim=1)
            encoded_texts.append(encoded_text)
            encoded_text_lengths.append(sample["encoded_text"].shape[1])

            audios.append(sample["audio"])
            pad_size = max_transform_length - sample["transform"].shape[2]
            pad_tensor = torch.zeros(1, self.config.preprocess.transform.n_transform, pad_size)
            transform = torch.cat([sample["transform"], pad_tensor], dim=2)
            transforms.append(transform)
            char_probs_lengths.append(
                math.ceil(sample["transform"].shape[2] / self.config.model.downsize)
            )

        return {
            "texts": texts,
            "encoded_texts": torch.cat(encoded_texts),
            "encoded_text_lengths": encoded_text_lengths,
            "audios": audios,
            "transforms": torch.cat(transforms),
            "char_probs_lengths": char_probs_lengths,
        }
