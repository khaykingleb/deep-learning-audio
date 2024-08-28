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

LJ_SPEECH_URL = "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"


@define(kw_only=True)
class LJSpeechDataset(ASRDataset):
    """Dataset class for LJSpeech.

    Attributes:
        data_dir (Path): Directory to save the dataset.
        data_url (str): URL to the dataset.
        data_part (str): Part of the dataset to use.
        proportions (list[float]): Proportions for train, val, and test sets.
        tokenizer (TextTokenizer): Tokenizer for text encoding.
        augmenter (AudioAugmenter): Augmenter for audio signals.
        transformer (Transformer): Audio transformation.
        samples_limit (int): Maximum number of samples.
        text_max_length (int): Maximum length of text.
        audio_max_duration (int): Maximum duration of audio.
        audio_sample_rate (int): Sample rate in Hz.
        audio_aug_prob (float): Probability of audio augmentation.
    """

    data_dir: Path = field()
    data_url: str = field(default=LJ_SPEECH_URL)
    data_part: str = field(default="train")
    proportions: list[float] = field(default=[0.7, 0.15, 0.15])

    def __attrs_post_init__(self):
        self.tar_path = self.data_dir.joinpath("LJSpeech.tar.bz2")
        self.meta_path = self.data_dir.joinpath("LJSpeech-1.1/metadata.csv")
        self.wavs_path = self.data_dir.joinpath("LJSpeech-1.1/wavs")
        super().__attrs_post_init__()

    def download(self) -> None:
        """Download and extract the LJSpeech dataset."""
        if self.data_dir.exists():
            logger.info("LJSpeech dataset already exists. Skipping download.")
            return

        logger.info("Downloading LJSpeech tar archive.")
        if self.data_url.startswith(("http:", "https:")):
            msg = "URL must start with 'http:' or 'https:'."
            raise ValueError(msg)
        urllib.request.urlretrieve(self.data_url, self.tar_path)  # noqa: S310

        logger.info("Extracting LJSpeech tar archive.")
        with tarfile.open(self.tar_path, mode="r:bz2") as tar:
            tar.extractall(path=self.data_dir, filter="data")

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
            msg = f"Proportions must sum to 1.0, got {sum(self.proportions)}."
            raise ValueError(msg)

        n = len(data)
        last_train_idx = math.ceil(n * self.proportions[0])
        last_val_idx = last_train_idx + math.ceil(n * self.proportions[1])

        match self.data_part:
            case "train":
                data = data[:last_train_idx]
            case "val":
                data = data[last_train_idx:last_val_idx]
            case "test":
                data = data[last_val_idx:]
            case _:
                msg = f"Invalid data part: {self.data_part}."
                raise ValueError(msg)

        return data

    def _process_data(self, data: pl.DataFrame) -> pl.DataFrame:
        final_data = []
        for audio_name, _, normalized_text in data.iter_rows():
            audio_path = self.wavs_path.joinpath(f"{audio_name}.wav")
            audio_info = torchaudio.info(audio_path)
            final_data.append(
                {
                    "path": str(audio_path),
                    "text": normalized_text,  # TODO: look at old code
                    "duration": audio_info.num_frames / audio_info.sample_rate,
                }
            )
        return pl.DataFrame(final_data)
