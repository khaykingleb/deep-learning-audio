"""Module for LJSpeech dataset."""

import math
import tarfile
import urllib.request
from pathlib import Path

import polars as pl
import torchaudio
from attrs import define, field
from loguru import logger

from src.collections.audio.asr.datasets.base import ASRDataset


@define
class LJSpeechDataset(ASRDataset):
    """Dataset class for LJSpeech."""

    data_dir: Path = field()
    data_url: str = field(
        default="https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"
    )
    data_part: str = field(default="train")
    proportions: list[float] = field(default=[0.7, 0.15, 0.15])

    def __attrs_post_init__(self):
        self.tar_path = self.data_dir.parent.joinpath("LJSpeech.tar.bz2")
        self.meta_path = self.data_dir.joinpath("metadata.csv")
        super().__attrs_post_init__()

    def download(self) -> None:
        """Download and extract the LJSpeech dataset."""
        if self.data_dir.exists():
            logger.info("LJSpeech dataset already exists. Skipping download.")
            return

        logger.info("Downloading LJSpeech tar archive.")
        if self.data_url.startswith(("http:", "https:")):
            msg = "URL must start with 'http:' or 'https:'"
            raise ValueError(msg)
        urllib.request.urlretrieve(self.data_url, self.tar_path)  # noqa: S310

        logger.info("Extracting LJSpeech tar archive.")
        with tarfile.open(self.tar_path, mode="r:bz2") as tar:
            tar.extractall(path=self.data_dir.parent, filter="data")

        self.tar_path.unlink()

    def setup(self) -> pl.DataFrame:
        """Set up the LJSpeech dataset."""
        data = pl.read_csv(
            self.meta_path,
            has_header=False,
            separator="|",
            new_columns=["audio_name", "text", "normalized_text"],
        ).drop_nulls()

        return self._process_data(self._partition_data(data))

    def _partition_data(self, data: pl.DataFrame) -> pl.DataFrame:
        if not math.isclose(sum(self.proportions), 1.0):
            msg = "Proportions must sum to 1.0"
            raise ValueError(msg)

        n = len(data)
        last_train_idx = math.ceil(n * self.proportions[0])
        last_val_idx = last_train_idx + math.ceil(n * self.proportions[1])

        match self.part:
            case "train":
                data = data[:last_train_idx]
            case "val":
                data = data[last_train_idx:last_val_idx]
            case "test":
                data = data[last_val_idx:]
            case _:
                msg = f"Invalid part: {self.data_part}"
                raise ValueError(msg)

        return data

    def _process_data(self, data: pl.DataFrame) -> pl.DataFrame:
        final_data = []
        for audio_name, _, normalized_text in data.iter_rows():
            audio_path = self.data_dir.joinpath(f"wavs/{audio_name}.wav")
            audio_info = torchaudio.info(audio_path)
            final_data.append(
                {
                    "path": audio_path,
                    "text": normalized_text,  # TODO: look at old code
                    "duration": audio_info.num_frames / audio_info.sample_rate,
                }
            )
        return pl.DataFrame(final_data)
