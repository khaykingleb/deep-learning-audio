"""Train part for Automatic Speech Recognition."""

import click
import torch
import torch.nn as nn
from omegaconf import OmegaConf

from .trainer import train
from ...collections.asr import models as models
from ...collections.asr import optim as optimizers
from ...collections.asr.optim import scheduler as schedulers
from ...data.dataloaders import get_dataloaders
from ...data.preprocess import text as text_encoders
from ...logging.wandb import WBLogger
from ...utils import fix_seed, prepare_device


@click.command()
@click.option("--config_path")
def main(config_path: str) -> None:
    """Trains an ASR model as defined in the configuration file.

    Args:
        config_path (str): Path to the configuration file.
    """
    config = OmegaConf.load(config_path)
    wb = WBLogger(config)

    fix_seed(config.seed)

    text_encoder = getattr(text_encoders, config.preprocess.text.encoder.name)()
    dataloaders = get_dataloaders(config, text_encoder)

    model = getattr(models, config.model.name)(config)
    if config.model.pretrained:
        model.load_state_dict(torch.load(config.model.checkpoint_path)["state_dict"])
    wb.root_logger.info(model)

    device, device_ids = prepare_device(config.device)
    model = model.to(device)
    if len(device_ids) > 1:
        model = nn.DataParallel(model, device_ids=device_ids)

    params = filter(lambda param: param.requires_grad, model.parameters())
    optimizer = getattr(optimizers, config.model.optimizer.name)(config, params)
    scheduler = getattr(schedulers, config.model.optimizer.scheduler.name)(config, optimizer)

    wb.wandb.watch(model)
    train(
        config,
        model,
        optimizer,
        scheduler,
        dataloaders,
        skip_oom=True,
    )


if __name__ == "__main__":
    main()
