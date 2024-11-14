import typing as tp

import hydra
import lightning as L
import torch
from hydra.errors import ConfigCompositionException, MissingConfigException
from lightning import Callback, LightningDataModule, LightningModule, Trainer
from lightning.pytorch.loggers import Logger, WandbLogger
from lightning.pytorch.tuner import Tuner
from omegaconf import DictConfig, OmegaConf
from typer import Exit, Option, Typer, echo

from src.utils import env
from src.utils.loggers import logger

app = Typer()


@app.command()
def train(
    experiment_name: str | None = Option(
        None,
        "--experiment",
        "-e",
        help=(
            "Experiment name for training located in "
            "'src/configs/experiment' folder"
        ),
    ),
) -> None:
    """Train a PyTorch Lightning model."""
    with logger.catch(reraise=True):
        # Use experiment name if provided, or otherwise, use default configuration
        config_name = (
            f"experiment/{experiment_name}" if experiment_name else "train"
        )
        cfg = _get_cfg(config_name)
        logger.info(f"Configuration is parsed:\n{OmegaConf.to_yaml(cfg)}")

        # TODO(khaykingleb): Не забудь про torch.compile!!!
        if cfg.get("seed"):
            logger.info(
                "Setting seed for torch, numpy, and random",
                seed=cfg["seed"],
            )
            L.seed_everything(cfg["seed"], workers=True)

        logger.info(f"Instantiating datamodule <{cfg["data"]["_target_"]}>")
        datamodule: LightningDataModule = hydra.utils.instantiate(cfg["data"])

        logger.info(f"Instantiating model module <{cfg['model']['_target_']}>")
        model: LightningModule = hydra.utils.instantiate(cfg["model"])

        if cfg.get("callbacks"):
            callbacks: list[Callback] = []
            logger.info("Instantiating callbacks")
            for _, callback_cfg in cfg["callbacks"].items():
                logger.info(
                    f"Instantiating callback <{callback_cfg['_target_']}>"
                )
                callbacks.append(hydra.utils.instantiate(callback_cfg))
        else:
            logger.warning("No callbacks to instantiate")

        if cfg.get("loggers"):
            logger.info("Instantiating loggers")
            loggers: list[Logger] = []
            for _, logger_cfg in cfg["loggers"].items():
                logger.info(f"Instantiating logger <{logger_cfg['_target_']}>")
                lightning_logger = hydra.utils.instantiate(logger_cfg)
                loggers.append(lightning_logger)
                if isinstance(lightning_logger, WandbLogger):
                    logger.info("Watching model with WandbLogger")
                    lightning_logger.watch(model)
        else:
            logger.warning("No loggers to instantiate")

        logger.info(f"Instantiating trainer <{cfg["trainer"]["_target_"]}>")
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

        if cfg.get("train"):
            logger.info("Starting training")
            trainer.fit(
                model=model,
                datamodule=datamodule,
                ckpt_path=cfg.get("ckpt_path"),
            )

        if cfg.get("test"):
            logger.info("Starting testing")
            trainer.test(
                model=model,
                datamodule=datamodule,
                ckpt_path=cfg.get("ckpt_path"),
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
        # TOD(khaykingleb): Can I use hydra.main() instead?
        with hydra.initialize_config_dir(
            version_base="1.3",
            config_dir=f"{env.BASE_DIR}/configs",
        ):
            return hydra.compose(config_name)

    except MissingConfigException as e:
        echo(f"Configuration file not found:\n\n{e}", err=True)
        raise Exit(code=1)

    except ConfigCompositionException as e:
        echo(f"Error composing configuration:\n\n{e}", err=True)
        raise Exit(code=1)


if __name__ == "__main__":
    app()
