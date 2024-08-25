import hydra

from omegaconf import DictConfig
from typer import Typer, Option, echo, Exit
from src.utils import env
from lightning import LightningDataModule
from hydra.errors import MissingConfigException, ConfigCompositionException
from src.utils.loggers import logger


app = Typer()


@app.command()
def train(
    experiment_name: str | None = Option(
        None,
        "--experiment",
        "-e",
        help=(
            "Experiment name for training located in " "'src/configs/experiment' folder"
        ),
    ),
) -> None:
    """Train a PyTorch Lightning model."""
    config_name = (
        f"experiment/{experiment_name}"  # use experiment name if provided
        if experiment_name
        else "train"  # otherwise, use default configuration
    )
    cfg = _get_cfg(config_name)

    # if cfg.get("seed"):
    #     logger.info("Setting seed for torch, numpy, and random")
    #     L.seed_everything(cfg["seed"], workers=True)

    # if cfg.get("use_deterministic_algorithms"):
    #     logger.info("Setting deterministic algorithms for torch")
    #     torch.use_deterministic_algorithms(True)

    # if cfg.get("use_cudnn_benchmark"):
    #     logger.info("Setting CuDNN benchmark to True")
    #     torch.backends.cudnn.benchmark = True

    logger.info(f"Instantiating datamodule <{cfg["data"]["_target_"]}>")
    datamodule: LightningDataModule = hydra.utils.instantiate(cfg["data"])

    # logger.info(f"Instantiating model <{cfg["model"]["_target_"]}>")
    # model: LightningModule = hydra.utils.instantiate(cfg["model"])

    # logger.info("Instantiating callbacks")
    # callbacks: list[Callback] = []
    # for callback in cfg.get("callback", []):
    #     logger.info(f"Instantiating callback <{callback['_target_']}>")
    #     callbacks.append(hydra.utils.instantiate(callback))

    # # logger.info(f"Instantiating logger <{cfg["logger"]['_target_']}>")
    # # lightning_logger: Logger = hydra.utils.instantiate(cfg["logger"])
    # logger.info("Instantiating loggers")
    # loggers: list[Logger] = []
    # for lightning_logger in cfg.get("logger", []):
    #     logger.info(f"Instantiating logger <{lightning_logger['_target_']}>")
    #     loggers.append(hydra.utils.instantiate(lightning_logger))

    # logger.info(f"Instantiating trainer <{cfg["trainer"]["_target_"]}>")
    # trainer: Trainer = hydra.utils.instantiate(
    #     cfg["trainer"],
    #     callbacks=callbacks,
    #     logger=loggers,
    # )

    # tuner = Tuner(trainer)
    # if cfg["tuner"]["scale_batch_size"]:
    #     logger.info("Tuning batch size")
    #     tuner.scale_batch_size(
    #         model=model,
    #         datamodule=datamodule,
    #         mode=cfg["tuner"]["scale_batch_size_mode"],
    #     )
    # if cfg["tuner"]["scale_lr"]:
    #     logger.info("Tuning learning rate")
    #     tuner.lr_find(
    #         model=model,
    #         datamodule=datamodule,
    #     )

    # if cfg.get("train"):
    #     logger.info("Starting training")
    #     trainer.fit(
    #         model=model,
    #         datamodule=datamodule,
    #         ckpt_path=cfg.get("ckpt_path"),
    #     )

    # if cfg.get("test"):
    #     logger.info("Starting testing")
    #     trainer.test(
    #         model=model,
    #         datamodule=datamodule,
    #         ckpt_path=cfg.get("ckpt_path"),
    #     )


@app.command()
def export() -> None:
    """Export a PyTorch Lightning model to a specific format.

    Args:
        model (str): Model name to export.
        type (str): Export type.
    """
    cfg = _get_cfg(config_name="export")


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
            config_dir=f"{env.BASE_DIR}/src/configs",
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
