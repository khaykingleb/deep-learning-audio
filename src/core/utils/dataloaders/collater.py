"""Collates data samples for dataloader."""

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
        batch: tp.List[tp.Dict[str, tp.Any]],
    ) -> tp.Dict[str, tp.Union[torch.Tensor, tp.List[torch.Tensor], tp.List[str]]]:
        """Collates samples and pads samples' fields in dataset.

        Args:
            batch (List): Batch of samples.

        Returns:
            Dict: Collated batch with padded fields.
        """
        transform_lens = torch.Tensor([item["transform"].shape[2] for item in batch])
        max_transform_len = int(transform_lens.max())
        if self.config.model.downsize:
            transform_lens = (transform_lens / self.config.model.downsize).ceil()

        encoded_text_lens = torch.Tensor([item["encoded_text"].shape[1] for item in batch])
        max_encoded_text_len = int(encoded_text_lens.max())

        audios, transforms, texts, encoded_texts = [], [], [], []
        for sample in batch:
            audios.append(sample["audio"])
            pad_size = max_transform_len - sample["transform"].shape[2]
            pad_tensor = torch.zeros(1, self.config.preprocess.transform.n_transform, pad_size)
            transform = torch.cat([sample["transform"], pad_tensor], dim=2)
            transforms.append(transform)

            texts.append(sample["text"])
            pad_size = max_encoded_text_len - sample["encoded_text"].shape[1]
            pad_tensor = torch.zeros(1, pad_size)
            encoded_text = torch.cat([sample["encoded_text"], pad_tensor], dim=1)
            encoded_texts.append(encoded_text)

        return {
            "audios": audios,
            "transform_lens": transform_lens,
            "transforms": torch.cat(transforms),
            "texts": texts,
            "encoded_text_lens": encoded_text_lens,
            "encoded_texts": torch.cat(encoded_texts),
        }
