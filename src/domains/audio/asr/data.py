"""Data module for ASR model."""

import math
import typing as tp

import lightning as L
import torch
from omegaconf import ListConfig
from torch.utils.data import DataLoader

if tp.TYPE_CHECKING:
    from src.domains.audio.asr.datasets import ASRDataset


class ASRDataCollator:
    """Collator for ASR data."""

    def __init__(self, downsize: int) -> None:
        """Constructor.

        Args:
            downsize: Downsize factor for the transforms
        """
        self.downsize = downsize

    def __call__(
        self,
        batch: list[dict[str, torch.Tensor]],
    ) -> dict[str, torch.Tensor | list[int] | list[torch.Tensor]]:
        """Collate the batch.

        Args:
            batch: Batch of data

        Returns:
            Collated batch
        """
        max_tokens_len = max(x["tokens"].shape[-1] for x in batch)
        max_transform_len = max(x["transform"].shape[-1] for x in batch)

        tokens = torch.empty(size=(0, max_tokens_len))
        tokens_lengths = []
        transforms_freq_len = batch[0]["transform"].shape[1]
        transforms = torch.empty(
            size=(0, transforms_freq_len, max_transform_len),
        )
        probs_lengths = []
        waveforms = []
        for sample in batch:
            tokens_padded = torch.nn.functional.pad(
                sample["tokens"],
                (0, max_tokens_len - sample["tokens"].shape[-1]),
            )
            tokens = torch.cat([tokens, tokens_padded], dim=0)
            tokens_lengths.append(sample["tokens"].shape[-1])

            transforms_padded = torch.nn.functional.pad(
                sample["transform"],
                (0, max_transform_len - sample["transform"].shape[-1]),
            )
            transforms = torch.cat([transforms, transforms_padded], dim=0)

            probs_length = math.ceil(
                sample["transform"].shape[-1] / self.downsize
            )
            probs_lengths.append(probs_length)

            waveforms.append(sample["waveform"])

        return {
            "tokens": tokens,
            "tokens_lengths": tokens_lengths,
            "transforms": transforms,
            "probs_lengths": probs_lengths,
            "waveforms": waveforms,
        }


class ASRData(L.LightningDataModule):
    """Prepare and setup data for ASR model."""

    def __init__(
        self,
        *,
        dataset: ListConfig,
        batch_size: int = 32,
        num_workers: int = 0,
        pin_memory: bool = False,
        persistent_workers: bool = False,
        downsize: int = 2,
    ) -> None:
        """Constructor.

        Args:
            dataset: Configuration for the dataset
            batch_size: Batch size for the dataloaders
            num_workers: Number of workers for the dataloaders
            pin_memory: Whether to pin memory for the dataloaders
            persistent_workers: Whether to use persistent workers
            downsize: Downsize factor for the transforms
        """
        super().__init__()
        self.save_hyperparameters()

    def prepare_data(self) -> None:
        """Download and save the datasets to disk with a single process.

        Note:
            Downloading and saving data with multiple processes will result in
            corrupted data. Lightning ensures the prepare_data() is called only
            within a single process on CPU, so you can safely add your
            downloading logic within. In case of multi-node training, the
            execution of this hook depends upon prepare_data_per_node.

            setup() is called after prepare_data and there is a barrier in
            between which ensures that all the processes proceed to setup once
            the data is prepared and available for use.

            prepare_data() is called from the main process. It is not
            recommended to assign state here (e.g. self.x = y) since it is
            called on a single process and if you assign states here then they
            won't be available for other processes.
        """
        dataset: ASRDataset = self.hparams["dataset"]
        dataset.download()

    def setup(self, stage: tp.Literal["fit", "validate", "test"]) -> None:
        """Setup the datasets on every GPU.

        Supposed to do things like:
            - Count number of classes
            - Build vocabulary
            - Perform train/val/test splits
            - Create datasets
            - Apply transforms
            - etc.

        Note:
            setup() is called from every process across all the nodes.
            Setting state here is recommended.

        Raises:
            ValueError: If the stage is invalid.

        Args:
            stage: Stage of experiment (fit, validate, test, predict).
        """
        dataset: ASRDataset = self.hparams["dataset"]
        match stage:
            case "fit":
                self._train_data = dataset.setup("train")
                self._val_data = dataset.setup("val")
            case "test":
                self._test_data = dataset.setup("test")
            case _:
                msg = f"Invalid stage: {stage}"
                raise ValueError(msg)

    def teardown(self, stage: tp.Literal["fit", "validate", "test"]) -> None:
        """Cleanup the state after the experiment.

        Args:
            stage (str): Stage of experiment (fit, validate, test, predict).
        """
        return super().teardown(stage)

    def train_dataloader(self) -> DataLoader:
        """Return the train dataloader.

        Returns:
            DataLoader: Train dataloader.
        """
        return DataLoader(
            dataset=self._train_data,
            batch_size=self.hparams["batch_size"],
            shuffle=True,
            num_workers=self.hparams["num_workers"],
            collate_fn=ASRDataCollator(self.hparams["downsize"]),
            pin_memory=self.hparams["pin_memory"],
            persistent_workers=self.hparams["persistent_workers"],
        )

    def val_dataloader(self) -> DataLoader:
        """Return the validation dataloader.

        Returns:
            DataLoader: Validation dataloader.
        """
        return DataLoader(
            dataset=self._val_data,
            batch_size=self.hparams["batch_size"],
            shuffle=False,
            num_workers=self.hparams["num_workers"],
            collate_fn=ASRDataCollator(self.hparams["downsize"]),
            pin_memory=self.hparams["pin_memory"],
            persistent_workers=self.hparams["persistent_workers"],
        )

    def test_dataloader(self) -> DataLoader:
        """Return the test dataloader.

        Returns:
            DataLoader: Test dataloader.
        """
        return DataLoader(
            dataset=self._test_data,
            batch_size=self.hparams["batch_size"],
            shuffle=False,
            num_workers=self.hparams["num_workers"],
            collate_fn=ASRDataCollator(self.hparams["downsize"]),
            pin_memory=self.hparams["pin_memory"],
            persistent_workers=self.hparams["persistent_workers"],
        )
