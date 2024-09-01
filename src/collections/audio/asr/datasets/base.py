"""Base module for ASR datasets."""

import random
import typing as tp
from abc import ABC, abstractmethod

import pandera.polars as pa
import polars as pl
import torchaudio.transforms as T
from attrs import define, field
from loguru import logger
from pandera.typing import Series
from torch.utils.data import Dataset

from src.collections.audio.dsp.audio import load_waveform
from src.collections.audio.dsp.augmentation import AudioAugmenter
from src.collections.common.preprocessing.tokenizers import TextTokenizer

Transformer = T.Spectrogram | T.MelSpectrogram | T.MFCC | T.LFCC


# 1. Make streaming dataset: huggingface or https://lightning.ai/lightning-ai/studios/convert-parquets-to-lightning-streaming
# 2. Some processing on GPU?
class ASRDataSchema(pa.DataFrameModel):
    """Schema for ASR data."""

    audio_path: Series[str] = pa.Field(
        description="Path to the audio file.",
        regex=r".+\.(wav|mp3|flac)$",
    )
    audio_duration: Series[float] = pa.Field(
        description="Duration of the audio in seconds.",
        gt=0,
    )
    text: Series[str] = pa.Field(
        description="Transcription of the audio.",
        nullable=False,
    )


@define(kw_only=True)
class ASRDataset(Dataset, ABC):
    """Base dataset for training an ASR model.

    Attributes:
        tokenizer (TextTokenizer): Tokenizer for text encoding.
        augmenter (AudioAugmenter): Augmenter for audio signals.
        transformer (Transformer): Audio transformation.
        data_samples_limit (int): Maximum number of samples.
        text_max_length (int): Maximum length of text.
        audio_max_duration (int): Maximum duration of audio.
        audio_sample_rate (int): Sample rate in Hz.
        audio_aug_prob (float): Probability of audio augmentation.
    """

    tokenizer: TextTokenizer = field(repr=False)
    augmenter: AudioAugmenter = field(repr=False)
    transformer: Transformer = field(repr=False)

    data_samples_limit: int = field(default=None)
    text_max_length: int = field(default=None)
    audio_max_duration: int = field(default=None)
    audio_sample_rate: int = field(default=22050)
    audio_aug_prob: float = field(default=0.0)

    @abstractmethod
    def download(self) -> None:
        """Download the dataset."""
        msg = "Method 'download' must be implemented in a subclass."
        raise NotImplementedError(msg)

    @abstractmethod
    def setup(self, stage: tp.Literal["train", "val", "test"]) -> pl.DataFrame:
        """Set up the dataset.

        Args:
            stage (str): Dataset stage to set up.

        Returns:
            pl.DataFrame: The dataset.
        """
        msg = "Method 'setup' must be implemented in a subclass."
        raise NotImplementedError(msg)

    def validate_data_before_finalizing(self) -> None:
        """Validate the dataset before finalizing it."""
        ASRDataSchema.validate(self.data)

    def finalize_data(self) -> None:
        """Finalize the dataset by filtering, sorting, and limiting data."""
        self._filter_data()
        self._sort_data()
        if self.data_samples_limit is not None:
            self._limit_data()

    def __getitem__(self, idx: int) -> dict[str, tp.Any]:
        """Get a single item from the dataset.

        Args:
            idx (int): Index of the item to retrieve.

        Returns:
            dict[str, tp.Any]: A dictionary containing the waveform,
                transformed audio, and encoded text.
        """
        audio_path, text, _ = self.data.row(idx)
        waveform = load_waveform(
            audio_path,
            sample_rate=self.audio_sample_rate,
        )
        if random.random() < self.audio_aug_prob:
            waveform = self.augmenter(waveform)
        return {
            "waveform": waveform,
            "transform": self.transformer(waveform),
            "tokens": self.tokenizer.encode(text),
        }

    def __len__(self) -> int:
        """Get the length of the dataset.

        Returns:
            int: The number of items in the dataset.
        """
        return len(self.data)

    def _filter_data(self) -> None:
        """Filter the dataset based on text length and audio duration."""
        filtered_data = self.data.clone()

        if self.text_max_length is not None:
            text_filtered_data = self.data.filter(
                self.data.get_column("text")
                .map_elements(lambda x: len(x))
                .le(self.text_max_length)
            )
            percentage_filtered = (
                len(self.data) - len(text_filtered_data)
            ) / len(self.data)
            logger.info(
                f"{percentage_filtered:.2%} of records are longer than "
                f"{self.text_max_length} characters."
            )
            filtered_data = filtered_data.join(
                text_filtered_data,
                how="inner",
            )

        if self.audio_max_duration is not None:
            audio_filtered_data = self.data.filter(
                self.data.get_column("audio_duration").le(
                    self.audio_max_duration
                )
            )
            percentage_filtered = (
                len(self.data) - len(audio_filtered_data)
            ) / len(self.data)
            logger.info(
                f"{percentage_filtered:.2%} of records are longer than "
                f"{self.audio_max_duration} seconds."
            )
            filtered_data = filtered_data.join(
                audio_filtered_data,
                how="inner",
            )

        percentage_filtered = (len(self.data) - len(filtered_data)) / len(
            self.data
        )
        logger.info(f"{percentage_filtered:.2%} of records are excluded.")
        self.data = filtered_data

    def _sort_data(self) -> None:
        """Sort the dataset by audio duration."""
        self.data = self.data.sort(by="audio_duration")

    def _limit_data(self) -> None:
        """Limit the dataset to a specified number of samples."""
        self.data = self.data.head(self.data_samples_limit)
