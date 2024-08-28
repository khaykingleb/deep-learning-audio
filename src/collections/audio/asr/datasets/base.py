"""Base module for ASR datasets."""

import typing as tp
from abc import ABC, abstractmethod
from pathlib import Path

import pandera as pa
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

    path: Series[Path] = pa.Field(
        description="Path to the audio file.",
        regex=r".+\.(wav|mp3|flac)$",
    )
    text: Series[str] = pa.Field(
        description="Transcription of the audio.",
        nullable=False,
    )
    duration: Series[float] = pa.Field(
        description="Duration of the audio in seconds.",
        gt=0,
    )


@define
class ASRDataset(Dataset, ABC):
    """Base dataset for training an ASR model."""

    data_url: str = field()
    data_dir: Path = field()
    data_samples_limit: int = field()
    text_max_length: int = field()
    text_tokenizer: TextTokenizer = field()
    audio_max_duration: int = field()
    audio_sample_rate: int = field()
    audio_augmenter: AudioAugmenter = field(repr=False)
    audio_augmentation_enabled: bool = field()
    audio_transformer: Transformer = field(repr=False)

    def __attrs_post_init__(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.download()

        self.data = self.setup()
        ASRDataSchema.validate(self.data)

        self._filter_data()
        self._sort_data()
        if self.data_samples_limit is not None:
            self._limit_data()

    @abstractmethod
    def download(self) -> None:
        """Download the dataset."""

    @abstractmethod
    def setup(self) -> pl.DataFrame:
        """Set up the dataset."""

    def __getitem__(self, idx: int) -> dict[str, tp.Any]:
        audio_path, text, _ = self.data.row(idx)
        waveform = load_waveform(audio_path, self.audio_sample_rate)
        if self.audio_augmentation_enabled:
            waveform = self.audio_augmenter(waveform)
        return {
            "waveform": waveform,
            "transform": self.audio_transformer(waveform),
            "tokens": self.text_tokenizer.encode(text),
        }

    def __len__(self) -> int:
        return len(self.data)

    def _filter_data(self) -> None:
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
                self.data.get_column("duration").le(self.audio_max_duration)
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

        logger.info(
            f"{len(filtered_data) / len(self.data):.2%} "
            "of records are excluded."
        )
        self.data = filtered_data

    def _sort_data(self) -> None:
        self.data = self.data.sort(by="duration")

    def _limit_data(self) -> None:
        self.data = self.data.head(self.data_samples_limit)
