"""Main entrypoint."""

import hydra
import lightning as L
from hydra.errors import ConfigCompositionException, MissingConfigException
from lightning import LightningDataModule, LightningModule, Trainer
from lightning.pytorch.tuner import Tuner
from omegaconf import DictConfig, OmegaConf
from typer import Exit, Option, Typer, echo

from src.utils import env
from src.utils.logger import logger
from src.utils.train import (
    instantiate_callbacks,
    instantiate_loggers,
    update_checkpoint_path,
)

app = Typer()


@app.command()
def train(
    experiment_name: str = Option(
        ...,
        "--experiment",
        "-e",
        help=(
            "Experiment name for training located in "
            '"configs/experiments" folder'
        ),
    ),
) -> None:
    """Train a PyTorch Lightning model."""
    with logger.catch(reraise=True):
        cfg = _get_cfg(f"experiments/{experiment_name}")
        logger.info(
            "Configuration is parsed",
            cfg=OmegaConf.to_container(cfg, resolve=True),
        )

        if cfg.get("seed"):
            logger.info(
                "Setting seed for torch, numpy, and random",
                seed=cfg["seed"],
            )
            L.seed_everything(cfg["seed"], workers=True)

        logger.info(f"Instantiating datamodule <{cfg['data']['_target_']}>")
        datamodule: LightningDataModule = hydra.utils.instantiate(cfg["data"])

        logger.info(
            f"Instantiating model module <{cfg['models']['_target_']}>"
        )
        model: LightningModule = hydra.utils.instantiate(cfg["models"])

        logger.info("Instantiating callbacks")
        callbacks = instantiate_callbacks(cfg)

        logger.info("Instantiating loggers")
        loggers = instantiate_loggers(cfg)

        logger.info(f"Instantiating trainer <{cfg['trainer']['_target_']}>")
        trainer: Trainer = hydra.utils.instantiate(
            cfg["trainer"],
            callbacks=callbacks,
            logger=loggers,
        )

        tuner = Tuner(trainer)
        if cfg["tuner"]["scale_batch_size"]["use"]:
            logger.info("Tuning batch size")
            tuner.scale_batch_size(
                model=model,
                datamodule=datamodule,
                mode=cfg["tuner"]["scale_batch_size"]["mode"],
            )
        if cfg["tuner"]["scale_lr"]["use"]:
            logger.info("Tuning learning rate")
            tuner.lr_find(
                model=model,
                datamodule=datamodule,
                mode=cfg["tuner"]["scale_lr"]["mode"],
            )

        ckpt_path = update_checkpoint_path(cfg, model)

        if cfg.get("train"):
            logger.info("Starting training")
            trainer.fit(
                model=model,
                datamodule=datamodule,
                ckpt_path=ckpt_path,
            )

        if cfg.get("test"):
            logger.info("Starting testing")
            trainer.test(
                model=model,
                datamodule=datamodule,
                ckpt_path=ckpt_path,
            )


@app.command()
def export() -> None:
    """Export a PyTorch Lightning model to a specific format.

    Args:
        model (str): Model name to export.
        type (str): Export type.
    """
    raise NotImplementedError


def _get_cfg(config_name: str) -> DictConfig:
    """Get configuration for PyTorch Lightning model.

    Args:
        config_name (str): Configuration name.

    Returns:
        Configuration for PyTorch Lightning model.

    Raises:
        Exit: If the configuration file is not found.
    """
    try:
        with hydra.initialize_config_dir(
            version_base="1.3",
            config_dir=f"{env.BASE_DIR}/configs",
        ):
            return hydra.compose(config_name)

    except MissingConfigException as e:
        echo(f"Configuration file not found:\n\n{e}", err=True)
        raise Exit(code=1) from e

    except ConfigCompositionException as e:
        echo(f"Error composing configuration:\n\n{e}", err=True)
        raise Exit(code=1) from e


if __name__ == "__main__":
    app()
