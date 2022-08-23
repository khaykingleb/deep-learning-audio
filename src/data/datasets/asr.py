"""Datasets for training ASR models."""

import typing as tp
from math import ceil

import numpy as np
import pandas as pd
import torchaudio
from omegaconf import DictConfig
from torch.utils.data import Dataset

from ..preprocessing.audio import load_audio
from ..preprocessing.text import BaseTextEncoder
from ..preprocessing.transform import preprocess_audio
from ... import cfg
from ...logging import logger

# TODO: Form batches based on audio length.


class BaseDatasetForASR(Dataset):
    """Base dataset for training an ASR model."""

    def __init__(
        self: "BaseDatasetForASR",
        data: tp.List[tp.Dict[str, tp.Any]],
        config: DictConfig,
        text_encoder: BaseTextEncoder,
        *,
        use_audio_aug: bool,
        use_transform_aug: bool,
    ) -> None:
        """Constructor.

        Args:
            data (List): Information about audio files.
            config (DictConfig): Configuration file.
            text_encoder (BaseTextEncoder): Text encoder used for tokenization.
            use_audio_aug (bool): Whether to use audio augmentation on data.
            use_transform_aug (bool): Whether to use dsp augmentation on data.
        """
        data = self.filter_data(data, config)
        self.data = self.sort_data(data)

        self.text_encoder = text_encoder
        self.config = config
        self.use_audio_aug = use_audio_aug
        self.use_transform_aug = use_transform_aug

    def __getitem__(self: "BaseDatasetForASR", idx: int) -> tp.Dict[str, tp.Any]:
        """Get a sample from the dataset according to the given index.

        Args:
            idx (int): The index of the sample to retrieve.

        Returns:
            Dict: Data sample.
        """
        data = self.data[idx]
        audio = load_audio(data["path"], self.config.preprocess)
        audio, transform = preprocess_audio(
            data["audio"],
            self.config.preprocess,
            self.use_audio_aug,
            self.use_transform_aug,
        )
        return {
            "path": data["path"],
            "text": data["text"],
            "encoded_text": self.text_encoder.encode(data["text"]),
            "audio": audio,
            "audio_duration": data["audio_duration"],
            "transformation": transform,
        }

    def __len__(self: "BaseDatasetForASR") -> int:
        """Get the total number of data samples in the dataset.

        Returns:
            int: Total number of data samples in the dataset.
        """
        return len(self.data)

    @staticmethod
    def filter_data(
        data: tp.List[tp.Dict[str, tp.Any]],
        config: DictConfig,
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        """Filter data in a dataset based max_text_length, max_audio_duration, and limit config params.

        Args:
            data (List): Information about audio files.
            config (DictConfig): Configuration file.

        Returns:
            List: Filtered data.
        """
        if config.data.max_text_length is not None:
            data_text_exceeds = (
                np.array([len(sample["text"]) for sample in data])
                >= config.data.max_text_length
            )
            logger.info(
                """\
                {percentage:.3%}% of records are longer than {max_text_length} characters.
                """.format(
                    percentage=data_text_exceeds.sum() / len(data),
                    max_text_length=config.data.max_text_length,
                )
            )
        if config.data.max_audio_duration is not None:
            data_audio_exceeds = (
                np.array([sample["audio_duration"] for sample in data])
                >= config.data.max_audio_duration
            )
            logger.info(
                """\
                {percentage:.3%} of records are longer than {max_audio_duration} seconds.
                """.format(
                    percentage=data_audio_exceeds.sum() / len(data),
                    max_audio_duration=config.data.max_audio_duration,
                )
            )
        if data_text_exceeds is not None or data_audio_exceeds is not None:
            if data_text_exceeds is None:
                data_exceeds = data_audio_exceeds
            elif data_audio_exceeds is None:
                data_exceeds = data_text_exceeds
            else:
                data_exceeds = data_text_exceeds + data_audio_exceeds
            logger.info(
                "{percentage:.3%} of records are excluded.".format(
                    percentage=data_exceeds.sum() / len(data)
                )
            )
            data = [
                data for data, not_exclude in zip(data, ~data_exceeds) if not_exclude
            ]
        if config.data.limit is not None:
            data = data[: config.data.limit]
        return data

    @staticmethod
    def sort_data(data: tp.List[tp.Dict[str, tp.Any]]) -> tp.List[tp.Dict[str, tp.Any]]:
        """Sort data in a dataset by audio length.

        Args:
            data (List): Information about audio files.

        Returns:
            List: Filtered data.
        """
        return sorted(data, key=lambda x: x["audio_duration"])


class LJSpeechDataset(BaseDatasetForASR):
    """LJ Speech dataset for training an ASR model."""

    LJ_SPEECH_DIR = cfg.BASE_DIR / "resources/datasets/asr/lj_speech"
    LJ_SPEECH_WAVS_DIR = LJ_SPEECH_DIR / "wavs"

    def __init__(
        self: "LJSpeechDataset",
        config: DictConfig,
        text_encoder: BaseTextEncoder,
        *,
        part: tp.Literal["train", "test", "val"],
    ) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
            text_encoder (BaseTextEncoder): Text encoder used for tokenization.
            part (Literal): Part of the dataset needed.
        """
        data = pd.read_csv(
            filepath_or_buffer=self.LJ_SPEECH_DIR / "metadata.csv",
            sep="|",
            header=None,
        )
        train_idx = ceil(data.shape[0] * config.data.parts.train.proportion)
        test_idx = train_idx + ceil(data.shape[0] * config.data.parts.test.proportion)
        match part:
            case "train":
                data = data[:train_idx]
            case "test":
                data = data[train_idx:test_idx]
            case "val":
                data = data[test_idx:]
        data = self.__get_full_data(data.reset_index())
        super().__init__(
            data,
            config,
            text_encoder,
            use_audio_aug=True if part == "train" else False,
            use_transform_aug=True if part == "train" else False,
        )

    def __get_full_data(self: "LJSpeechDataset", data: pd.DataFrame) -> pd.DataFrame:
        full_data = []
        for idx, audio_name in enumerate(data[0]):
            audio_path = self.LJ_SPEECH_WAVS_DIR / str(audio_name + ".wav")
            audio_path = audio_path.resolve().as_posix()
            audio_info = torchaudio.info(audio_path)
            alphabet = BaseTextEncoder.get_simple_alphabet()
            full_data.append(
                {
                    "path": audio_path,
                    "text": BaseTextEncoder.preprocess_text(data[2][idx], alphabet),
                    "audio_duration": audio_info.num_frames / audio_info.sample_rate,
                }
            )
        return full_data


class LibriSpeechDataset(BaseDatasetForASR):
    """LibriSpeech dataset for training an ASR model."""

    def __init__(self: "LibriSpeechDataset", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        super(BaseDatasetForASR, self).__init__(config)
        pass

    def __getitem__(self: "LibriSpeechDataset", idx: int) -> None:  # NOQA: D105
        pass

    def __len__(self: "LibriSpeechDataset") -> int:  # NOQA: D105
        pass


class CommonVoiceDataset(BaseDatasetForASR):
    """Common Voice dataset for training an ASR model."""

    def __init__(self: "CommonVoiceDataset", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        super(BaseDatasetForASR, self).__init__(config)
        pass

    def __getitem__(self: "CommonVoiceDataset", idx: int) -> None:  # NOQA: D105
        pass

    def __len__(self: "CommonVoiceDataset") -> int:  # NOQA: D105
        pass
