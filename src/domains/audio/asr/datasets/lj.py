"""Module for LJSpeech dataset."""

import math
import tarfile
import typing as tp
import urllib.request
from pathlib import Path

import pandas as pd
import polars as pl
import torchaudio
from attrs import define, field
from loguru import logger

from src.domains.audio.asr.datasets.base import ASRDataset
from src.domains.common.preprocessing.text import preprocess_text

LJ_SPEECH_URL = "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"


@define(kw_only=True)
class LJSpeechDataset(ASRDataset):
    """Dataset class for LJSpeech.

    Consists of 13,100 short audio clips of a single speaker reading passages
    from 7 non-fiction books. Clips vary in length from 1 to 10 seconds and
    have a total length of approximately 24 hours.

    Attributes:
        data_dir (str, Path): Directory to save the dataset.
        data_proportions (list[float]): Proportions for train, val, test sets.
        tokenizer (TextTokenizer): Tokenizer for text encoding.
        augmenter (AudioAugmenter): Augmenter for audio signals.
        transformer (Transformer): Audio transformation.
        text_max_length (int): Maximum length of text.
        audio_max_duration (int): Maximum duration of audio.
        audio_sample_rate (int): Sample rate in Hz.
        audio_aug_prob (float): Probability of audio augmentation.
    """

    data_dir: Path = field(converter=Path)
    data_proportions: list[float] = field(default=[0.7, 0.15, 0.15])

    def __attrs_post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tar_path = self.data_dir.joinpath("LJSpeech.tar.bz2")
        self.extracted_dir = self.data_dir.joinpath("LJSpeech-1.1")
        self.wavs_dir = self.extracted_dir.joinpath("wavs")
        self.meta_path = self.extracted_dir.joinpath("metadata.csv")

    def download(self) -> None:
        """Download and extract the LJSpeech dataset."""
        if self.extracted_dir.exists():
            logger.info("LJSpeech dataset already exists. Skipping download.")
            return

        logger.info("Downloading LJSpeech tar archive.")
        urllib.request.urlretrieve(LJ_SPEECH_URL, self.tar_path)

        logger.info("Extracting LJSpeech tar archive.")
        with tarfile.open(self.tar_path, mode="r:bz2") as tar:
            tar.extractall(path=self.data_dir, filter="data")

        self.tar_path.unlink()

    def remove(self) -> None:
        """Remove the LJSpeech dataset."""
        self.extracted_dir.rmdir()

    def setup(
        self,
        stage: tp.Literal["train", "val", "test"],
    ) -> type["LJSpeechDataset"]:
        """Set up the LJSpeech dataset.

        Args:
            stage (str): Dataset stage to set up.

        Returns:
            DataFrame: The dataset.
        """
        logger.info(
            f"Setting up '{stage}' partition "
            f"of the '{LJSpeechDataset.__name__}' dataset."
        )
        data = pd.read_csv(
            self.meta_path,
            sep="|",
            header=None,
            names=["audio_name", "text", "normalized_text"],
        )
        data = pl.from_pandas(data).drop_nulls()
        self._data = self._process_data(self._partition_data(data, stage))
        logger.info(self._data.head())
        self.finalize_data()
        return self

    def _partition_data(
        self,
        data: pl.DataFrame,
        stage: tp.Literal["train", "val", "test", "all"],
    ) -> pl.DataFrame:
        """Partition the data into train, val, and test sets.

        Args:
            data (DataFrame): Data to partition.
            stage (str): Dataset stage to set up.

        Raises:
            ValueError: If the proportions do not sum to 1.0.

        Returns:
            DataFrame: Partitioned data.
        """
        if not math.isclose(sum(self.data_proportions), 1.0):
            msg = (
                "Proportions must sum to 1.0, "
                f"got {sum(self.data_proportions)}."
            )
            raise ValueError(msg)

        total_samples = len(data)
        last_train_idx = math.ceil(total_samples * self.data_proportions[0])
        last_val_idx = last_train_idx + math.ceil(
            total_samples * self.data_proportions[1]
        )

        slices = {
            "all": slice(None),
            "train": slice(0, last_train_idx),
            "val": slice(last_train_idx, last_val_idx),
            "test": slice(last_val_idx, None),
        }
        if stage not in slices:
            msg = f"Invalid data part: {stage}."
            raise ValueError(msg)

        return data[slices[stage]]

    def _process_data(self, data: pl.DataFrame) -> pl.DataFrame:
        """Process the data by adding audio paths and durations.

        Args:
            data (DataFrame): Data to process.

        Returns:
            DataFrame: Processed data.
        """
        full_data = []
        for audio_name, _, normalized_text in data.iter_rows():
            text = preprocess_text(normalized_text, remove_punctuation=True)
            if not all(char in self.tokenizer.alphabet for char in text):
                logger.warning(
                    f"Skipping '{audio_name}' due to invalid text: '{text}'."
                )
                continue

            audio_path = self.wavs_dir.joinpath(f"{audio_name}.wav").as_posix()
            audio_info = torchaudio.info(audio_path)
            full_data.append(
                {
                    "audio_path": audio_path,
                    "audio_duration": audio_info.num_frames
                    / audio_info.sample_rate,
                    "text": text,
                }
            )
        return pl.DataFrame(full_data)
