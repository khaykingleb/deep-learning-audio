"""Dataloaders for training models."""

import typing as tp

from omegaconf import DictConfig
from torch.utils.data import ConcatDataset, DataLoader

from .collater import Collater
from ..preprocess.text import BaseTextEncoder
from ...data import datasets as datasets_arch


def get_dataloaders(
    config: DictConfig,
    text_encoder: BaseTextEncoder,
) -> tp.Dict[str, DataLoader]:
    """Combines datasets for every part and provides an iterable over the given data.

    Args:
        config (DictConfig): Configuration file.
        text_encoder (BaseTextEncoder): Text encoder used for tokenization.

    Returns:
        Dict[str, DataLoader]: Dataloaders for training, test, and validation parts.
    """
    collater = Collater(config)
    dataloaders = {}
    for part, config_part in config.data.parts.items():
        datasets = []
        for dataset in config_part.datasets:
            ds_name = dataset.split(",")[0]
            ds_part = dataset.split(",")[1]
            ds = getattr(datasets_arch, ds_name)(config, text_encoder, ds_part)
            datasets.append(ds)
        dataset = ConcatDataset(datasets)
        dataloaders[part] = DataLoader(
            dataset,
            batch_size=config.data.batch.batch_size,
            shuffle=config.data.batch.shuffle,
            num_workers=config.data.batch.num_workers,
            sampler=config.data.batch.num_workers,
            collate_fn=collater,
            drop_last=config.data.batch.drop_last,
        )
    return dataloaders
