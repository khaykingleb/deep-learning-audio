"""Data module for ASR model."""

import typing as tp

import hydra
import lightning as L
import torch
from omegaconf import ListConfig
from torch.utils.data import DataLoader

if tp.TYPE_CHECKING:
    from src.collections.audio.asr.datasets import ASRDataset


class ASRData(L.LightningDataModule):
    """Prepare and setup data for ASR model."""

    def __init__(
        self,
        *,
        dataset: ListConfig,
        batch_size: int | None = 32,
        num_workers: int | None = 0,
        pin_memory: bool | None = False,
    ) -> None:
        """Constructor.

        Args:
            dataset (ListConfig): Configuration for the dataset.
            data_dir (str): Directory to save the data.
            data_proportions (list): Proportions for train, val, test sets.
            batch_size (int): Batch size for the dataloaders.
            num_workers (int): Number of workers for the dataloaders.
            pin_memory (bool): Whether to pin memory for the dataloaders.
        """
        super().__init__()
        self.save_hyperparameters(logger=True)

        self._train_data: ASRDataset | None = None
        self._val_data: ASRDataset | None = None
        self._test_data: ASRDataset | None = None

    def prepare_data(self) -> None:
        """Download and save the datasets to disk with a single process.

        Note:
            Downloading and saving data with multiple processes (distributed
            settings) will result in corrupted data. Lightning ensures the
            prepare_data() is called only within a single process on CPU, so
            you can safely add your downloading logic within. In case of
            multi-node training, the execution of this hook depends upon
            prepare_data_per_node.

            setup() is called after prepare_data and there is a barrier in
            between which ensures that all the processes proceed to setup once
            the data is prepared and available for use.

            prepare_data() is called from the main process. It is not
            recommended to assign state here (e.g. self.x = y) since it is
            called on a single process and if you assign states here then they
            won't be available for other processes.
        """
        dataset: ASRDataset = hydra.utils.instantiate(self.hparams["dataset"])
        dataset.download()

    def setup(self, stage: str) -> None:
        """Setup the datasets on every GPU.

        Supposed to do things like:
            - count number of classes
            - build vocabulary
            - perform train/val/test splits
            - create datasets
            - apply transforms
            - etc.

        Note:
            setup() is called from every process across all the nodes.
            Setting state here is recommended.

        Args:
            stage (str): Stage of experiment (fit, validate, test, predict).
        """
        dataset: ASRDataset = hydra.utils.instantiate(self.hparams["dataset"])
        match stage:
            case "fit":
                self._train_data = dataset.setup("train")
                self._val_data = dataset.setup("val")
            case "test":
                self._test_data = dataset.setup("test")

    def teardown(self, stage: str) -> None:
        """Cleanup the state after the experiment.

        Args:
            stage (str): Stage of experiment (fit, validate, test, predict).
        """
        return super().teardown(stage)

    # TODO: set up sampler?
    def train_dataloader(self) -> DataLoader:
        """Return the train dataloader.

        Returns:
            DataLoader: Train dataloader.
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.hparams["batch_size"],
            num_workers=self.hparams["num_workers"],
            pin_memory=self.hparams["pin_memory"],
            # shuffle=True,
        )

    def val_dataloader(self) -> DataLoader:
        """Return the validation dataloader.

        Returns:
            DataLoader: Validation dataloader.
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.hparams["batch_size"],
            num_workers=self.hparams["num_workers"],
            pin_memory=self.hparams["pin_memory"],
            # shuffle=False,
        )

    def test_dataloader(self) -> DataLoader:
        """Return the test dataloader.

        Returns:
            DataLoader: Test dataloader.
        """
        return DataLoader(
            self.test_dataset,
            batch_size=self.hparams["batch_size"],
            num_workers=self.hparams["num_workers"],
            pin_memory=self.hparams["pin_memory"],
            # shuffle=False,
        )

    def on_before_batch_transfer(
        self,
        batch: tp.Any,
        dataloader_idx: int,
    ) -> None:
        """Alter or apply batch augmentations before transfer to device.

        Note:
            To check the current state of execution of this hook you can use
            self.trainer.training/testing/validating/predicting so that you can
            add different logic as per your requirement.

        Example:
            >>> def on_before_batch_transfer(self, batch, dataloader_idx):
            >>>     batch['x'] = transforms(batch['x'])
            >>>     return batch

        Args:
            batch (Any): Batch of data.
            dataloader_idx (int): Index of the dataloader.
        """

    def transfer_batch_to_device(
        self,
        batch: tp.Any,
        device: torch.device,
        dataloader_idx: int,
    ) -> tp.Any:
        """Override the default transfer to device behavior.

        The data types listed below (and any arbitrary nesting of them) are
        supported out of the box:
        - `torch.Tensor` or anything that implements `.to(...)`
        - `list`
        - `dict`
        - `tuple`

        For anything else, you need to define how the data is moved to the
        target device (CPU, GPU, TPU).

        Note:
            This hook should only transfer the data and not modify it, nor
            should it move the data to any other device than the one passed in
            as argument (unless you know what you are doing). To check the
            current state of execution of this hook you can use
            self.trainer.training/testing/validating/predicting so that you
            can add different logic as per your requirement.


        Example:
            >>> def transfer_batch_to_device(
            >>>     self,
            >>>     batch,
            >>>     device,
            >>>     dataloader_idx,
            >>> ):
            >>>     if isinstance(batch, CustomBatch):
            >>> # move all tensors in your custom data
            >>> # structure to the device
            >>>         batch.samples = batch.samples.to(device)
            >>>         batch.targets = batch.targets.to(device)
            >>>     elif dataloader_idx == 0:
            >>> # skip device transfer for the first dataloader or
            >>> # anything you wish
            >>>         pass
            >>>     else:
            >>>         batch = super().transfer_batch_to_device(
            >>>             batch,
            >>>             device,
            >>>             dataloader_idx,
            >>>         )
            >>>     return batch

        Args:
            batch (Any): Batch of data.
            device (torch.device): Device to transfer the data to.
            dataloader_idx (int): Index of the dataloader.

        Returns:
            Any: Transferred batch of data.
        """

    def on_after_batch_transfer(
        self,
        batch: tp.Any,
        dataloader_idx: int,
    ) -> None:
        """Alter or apply batch augmentations after transfer to device.

        Note:
            To check the current state of execution of this hook you can use
            self.trainer.training/testing/validating/predicting so that you can
            add different logic as per your requirement.

        Example:
            >>> def on_after_batch_transfer(self, batch, dataloader_idx):
            >>>     batch['x'] = gpu_transforms(batch['x'])
            >>>     return batch

        Args:
            batch (Any): Batch of data.
            dataloader_idx (int): Index of the dataloader.
        """

    def state_dict(self) -> dict[str, tp.Any]:
        """Called when saving a checkpoint.

        Implement to generate and save the datamodule state.

        Example:
            >>> def state_dict(self):
            >>>     return {
            >>>         "current_train_batch_index":
            >>>         self.current_train_batch_index
            >>>     }

        Returns:
            dict: State of the datamodule.
        """
        return super().state_dict()

    def load_state_dict(self, state_dict: dict[str, tp.Any]) -> None:
        """Called when loading a checkpoint.

        Implement to load the datamodule state.

        Example:
            >>> def load_state_dict(self, state_dict):
            >>>     self.current_train_batch_index = \
            >>>         state_dict["current_train_batch_index"]

        Args:
            state_dict (dict): Datamodule state returned by self.state_dict().
        """
        return super().load_state_dict(state_dict)
