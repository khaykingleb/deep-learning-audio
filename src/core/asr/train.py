"""Train part for Automatic Speech Recognition."""

import click
import torch
import torch.nn as nn
from omegaconf import OmegaConf

from .trainer import train
from ...core.asr import models as models
from ...core.utils import fix_seed
from ...core.utils import optim as optimizers
from ...core.utils import prepare_device
from ...core.utils.dataloaders import get_dataloaders
from ...core.utils.optim import scheduler as schedulers
from ...data.preprocess import text as text_encoders
from ...logging.wandb import WBLogger
from ...utils import init_obj


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

    text_encoder = init_obj(text_encoders, config.preprocess.text.encoder.name)
    dataloaders = get_dataloaders(config, text_encoder)

    model = init_obj(models, config.model.name, config, vocab_size=text_encoder.alphabet_length)
    if config.model.pretrained:
        model.load_state_dict(torch.load(config.model.checkpoint_path)["state_dict"])
    wb.root_logger.info(model)

    device, device_ids = prepare_device(config.device)
    model = model.to(device)
    if len(device_ids) > 1:
        model = nn.DataParallel(model, device_ids=device_ids)

    params = filter(lambda param: param.requires_grad, model.parameters())
    optimizer = init_obj(optimizers, config.model.optimizer.name, config, params)
    scheduler = init_obj(schedulers, config.model.optimizer.scheduler.name, config, optimizer)

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
