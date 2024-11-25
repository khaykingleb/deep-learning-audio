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

from src.domains.audio.dsp.audio import load_waveform
from src.domains.audio.dsp.augmentation import AudioAugmenter
from src.domains.common.preprocessing.tokenizers import TextTokenizer

Transformer = T.Spectrogram | T.MelSpectrogram | T.MFCC | T.LFCC


# 1. Make streaming dataset?
#   Huggingface or https://lightning.ai/lightning-ai/studios/convert-parquets-to-lightning-streaming
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
        text_max_length (int): Maximum length of text.
        audio_max_duration (int): Maximum duration of audio.
        audio_sample_rate (int): Sample rate in Hz.
        audio_aug_prob (float): Probability of audio augmentation.
    """

    tokenizer: TextTokenizer = field(repr=False)
    transformer: Transformer = field(repr=False)
    augmenter: AudioAugmenter = field(repr=False)

    text_max_length: int | None = field(default=None)
    audio_max_duration: int | None = field(default=None)
    audio_sample_rate: int = field(default=22050)
    audio_aug_prob: float = field(default=0.0)

    _data: pl.DataFrame = field(default=None, init=False, repr=False)

    @abstractmethod
    def download(self) -> None:
        """Download the dataset."""
        msg = "Method 'download' must be implemented in a subclass."
        raise NotImplementedError(msg)

    @abstractmethod
    def remove(self) -> None:
        """Remove the dataset."""
        msg = "Method 'remove' must be implemented in a subclass."
        raise NotImplementedError(msg)

    @abstractmethod
    def setup(
        self, stage: tp.Literal["train", "val", "test"]
    ) -> type["ASRDataset"]:
        """Set up the dataset for a specific stage (that is, self._data).

        Args:
            stage (str): Dataset stage to set up.

        Returns:
            pl.DataFrame: The dataset.
        """
        msg = "Method 'setup' must be implemented in a subclass."
        raise NotImplementedError(msg)

    def __getitem__(self, idx: int) -> dict[str, tp.Any]:
        """Get a single item from the dataset.

        Args:
            idx (int): Index of the item to retrieve.

        Returns:
            dict[str, tp.Any]: A dictionary containing the waveform,
                transformed audio, and encoded text.
        """
        audio_path, _, text = self._data.row(idx)
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
        return len(self._data)

    def finalize_data(self) -> None:
        """Finalize the dataset by validating, filtering, and sorting data."""
        self._validate_data()
        self._filter_data()
        self._sort_data()

    def _validate_data(self) -> None:
        """Validate the dataset to ensure it conforms to the schema."""
        ASRDataSchema.validate(self._data)

    def _filter_data(self) -> None:
        """Filter the dataset based on text length and audio duration."""
        filtered_data = self._data.clone()
        if self.text_max_length is not None:
            text_filtered = self._data.filter(
                self._data.get_column("text")
                .map_elements(len, return_dtype=pl.Int64)
                .le(self.text_max_length)
            )
            percentage_filtered = 1 - len(text_filtered) / len(self._data)
            logger.info(
                f"{percentage_filtered:.2%} of valid records are longer than "
                f"{self.text_max_length} characters."
            )
            filtered_data = filtered_data.join(
                text_filtered,
                on=["audio_path", "audio_duration", "text"],
                how="inner",
            )

        if self.audio_max_duration is not None:
            audio_filtered = self._data.filter(
                self._data.get_column("audio_duration").le(
                    self.audio_max_duration
                )
            )
            percentage_filtered = 1 - len(audio_filtered) / len(self._data)
            logger.info(
                f"{percentage_filtered:.2%} of valid records are longer than "
                f"{self.audio_max_duration} seconds."
            )
            filtered_data = filtered_data.join(
                audio_filtered,
                on=["audio_path", "audio_duration", "text"],
                how="inner",
            )

        percentage_filtered = 1 - len(filtered_data) / len(self._data)
        logger.info(
            f"{percentage_filtered:.2%} of valid records are excluded."
        )
        self._data = filtered_data

    def _sort_data(self) -> None:
        """Sort the dataset by audio duration."""
        self._data = self._data.sort(by="audio_duration")
