"""Dataloaders for training models."""

import typing as tp

from omegaconf import DictConfig
from torch.utils.data import ConcatDataset, DataLoader

from .collater import Collater
from ....data import datasets
from ....data.preprocess.text import BaseTextEncoder
from ....utils import init_obj


def get_dataloaders(
    config: DictConfig,
    text_encoder: BaseTextEncoder,
    collater: tp.Optional[Collater] = None,
) -> tp.Dict[str, DataLoader]:
    """Combines datasets for every part and provides an iterable over the given data.

    Args:
        config (DictConfig): Configuration file.
        text_encoder (BaseTextEncoder): Text encoder used for tokenization.
        collater (Collater, optional): Collater of samples.

    Returns:
        Dict[str, DataLoader]: Dataloaders for training, test, and validation parts.
    """
    dataloaders = {}
    for part, config_part in config.data.parts.items():
        data = []
        for dataset in config_part.datasets:
            dataset_name = dataset.split(",")[0]
            dataset_part = dataset.split(",")[1]
            ds = init_obj(datasets, dataset_name, config, text_encoder, part=dataset_part)
            datasets.append(ds)
        dataset = ConcatDataset(data)
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
