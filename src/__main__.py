"""Main entrypoint."""

import typing as tp

import hydra
import lightning as L
from hydra.errors import ConfigCompositionException, MissingConfigException
from lightning import Callback, LightningDataModule, LightningModule, Trainer
from lightning.pytorch.tuner import Tuner
from omegaconf import DictConfig, OmegaConf
from typer import Exit, Option, Typer, echo

from src.utils import env
from src.utils.logger import logger

if tp.TYPE_CHECKING:
    from lightning.pytorch.loggers import Logger

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

        callbacks: list[Callback] = []
        if cfg.get("callbacks"):
            logger.info("Instantiating callbacks")
            for callback_cfg in cfg["callbacks"].values():
                logger.info(
                    f"Instantiating callback <{callback_cfg['_target_']}>"
                )
                callbacks.append(hydra.utils.instantiate(callback_cfg))
        else:
            logger.warning("No callbacks to instantiate")

        loggers: list[Logger] = []
        if cfg.get("loggers"):
            logger.info("Instantiating loggers")
            for logger_cfg in cfg["loggers"].values():
                logger.info(f"Instantiating logger <{logger_cfg['_target_']}>")
                lightning_logger = hydra.utils.instantiate(logger_cfg)
                loggers.append(lightning_logger)
                # if isinstance(lightning_logger, WandbLogger):
                #     # TODO(khaykingleb): Почему-то не работает
                #     logger.info("Watching model with WandbLogger")
                #     lightning_logger.watch(model)
        else:
            logger.warning("No loggers to instantiate")

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
