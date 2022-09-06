"""Datasets for training ASR models."""

import math
import os
import typing as tp
from pathlib import Path

import numpy as np
import pandas as pd
import torchaudio
from omegaconf import DictConfig
from torch.utils.data import Dataset

from ..preprocess.audio import load_audio
from ..preprocess.text import BaseTextEncoder
from ..preprocess.transform import preprocess_audio
from ... import cfg
from ...logging import logger


class ASRBaseDataset(Dataset):
    """Base dataset for training an ASR model."""

    def __init__(
        self: "ASRBaseDataset",
        data: tp.List[tp.Dict[str, tp.Any]],
        config: DictConfig,
        text_encoder: BaseTextEncoder,
        *,
        use_aug: bool,
    ) -> None:
        """Constructor.

        Args:
            data (List): Information about audio files.
            config (DictConfig): Configuration file.
            text_encoder (BaseTextEncoder): Text encoder used for tokenization.
            use_aug (bool): Whether to use audio and dsp augmentation on data.
        """
        data = self.filter_data(data, config)
        data = self.sort_data(data)
        self.data = self.limit_data(data, config)

        self.text_encoder = text_encoder
        self.config = config
        self.use_aug = use_aug

    def __getitem__(self: "ASRBaseDataset", idx: int) -> tp.Dict[str, tp.Any]:
        """Get a sample from the dataset according to the given index.

        Args:
            idx (int): The index of the sample to retrieve.

        Returns:
            Dict: Data sample.
        """
        sample = self.data[idx]
        audio = load_audio(sample["path"], self.config.preprocess, self.use_aug)
        transform = preprocess_audio(audio, self.config.preprocess, self.use_aug)
        return {
            "path": sample["path"],
            "text": sample["text"],
            "encoded_text": self.text_encoder.encode(sample["text"]),
            "audio": audio,
            "audio_duration": sample["audio_duration"],
            "transform": transform,
        }

    def __len__(self: "ASRBaseDataset") -> int:
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
        """Filter data in a dataset based on max_text_length and max_audio_duration params.

        Args:
            data (List): Information about audio files.
            config (DictConfig): Configuration file.

        Returns:
            List: Filtered data.
        """
        if config.data.max_text_length is not None:
            data_text_exceeds = (
                np.array([len(sample["text"]) for sample in data]) >= config.data.max_text_length
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
        if config.data.max_text_length is not None or config.data.max_audio_duration is not None:
            if config.data.max_text_length is None:
                data_exceeds = data_audio_exceeds
            elif config.data.max_audio_duration is None:
                data_exceeds = data_text_exceeds
            else:
                data_exceeds = data_text_exceeds + data_audio_exceeds
            logger.info(
                "{percentage:.3%} of records are excluded.".format(
                    percentage=data_exceeds.sum() / len(data)
                )
            )
            data = [data for data, exclude in zip(data, data_exceeds) if not exclude]
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

    @staticmethod
    def limit_data(
        data: tp.List[tp.Dict[str, tp.Any]],
        config: DictConfig,
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        """Limit data in a dataset.

        Args:
            data (List): Information about audio files.
            config (DictConfig): Configuration file.

        Returns:
            List: Limited data.
        """
        if config.data.limit is not None:
            data = data[: config.data.limit]
        return data


class LJSpeechDataset(ASRBaseDataset):
    """LJ Speech dataset for training an ASR model."""

    LJ_SPEECH_DIR = cfg.BASE_DIR / "resources" / "datasets" / "asr" / "lj_speech"
    LJ_SPEECH_WAVS_DIR = LJ_SPEECH_DIR / "wavs"

    def __init__(
        self: "LJSpeechDataset",
        config: DictConfig,
        text_encoder: BaseTextEncoder,
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
        data = self.__part_data(data.dropna(), config, part)
        data = self.__get_full_data(data.reset_index())
        super().__init__(
            data,
            config,
            text_encoder,
            use_aug=True if part == "train" and config.data.use_aug else False,
        )

    def __part_data(
        self: "LJSpeechDataset",
        data: pd.DataFrame,
        config: DictConfig,
        part: tp.Literal["train", "test", "val"],
    ) -> pd.DataFrame:
        train_idx = math.ceil(data.shape[0] * config.data.parts.train.proportion)
        test_idx = train_idx + math.ceil(data.shape[0] * config.data.parts.test.proportion)
        match part:
            case "train":
                data = data[:train_idx]
            case "test":
                data = data[train_idx:test_idx]
            case "val":
                data = data[test_idx:]
        return data

    def __get_full_data(
        self: "LJSpeechDataset",
        data: pd.DataFrame,
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        full_data = []
        for idx, audio_name in enumerate(data[0]):
            audio_path = self.LJ_SPEECH_WAVS_DIR / str(audio_name + ".wav")
            audio_info = torchaudio.info(audio_path)
            full_data.append(
                {
                    "path": audio_path,
                    "text": BaseTextEncoder.preprocess_text(data[2][idx]),
                    "audio_duration": audio_info.num_frames / audio_info.sample_rate,
                }
            )
        return full_data


class LibriSpeechDataset(ASRBaseDataset):
    """LibriSpeech dataset for training an ASR model."""

    LIBRI_SPEECH_DIR = cfg.BASE_DIR / "resources" / "datasets" / "asr" / "libri_speech"

    def __init__(
        self: "LibriSpeechDataset",
        config: DictConfig,
        text_encoder: BaseTextEncoder,
        part: tp.Literal[
            "dev-clean",
            "dev-other",
            "test-clean",
            "test-other",
            "train-clean-100",
            "train-clean-360",
            "train-other-500",
        ],
    ) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
            text_encoder (BaseTextEncoder): Text encoder used for tokenization.
            part (Literal): Part of the dataset needed.
        """
        data = self.__get_full_data(part)
        super().__init__(
            data,
            config,
            text_encoder,
            use_aug=True if part.startswith("train") and config.data.use_aug else False,
        )

    def __get_full_data(
        self: "LibriSpeechDataset",
        part: tp.Literal[
            "dev-clean",
            "dev-other",
            "test-clean",
            "test-other",
            "train-clean-100",
            "train-clean-360",
            "train-other-500",
        ],
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        dir_paths = set()
        for dir_path, _, files in os.walk(self.LIBRI_SPEECH_DIR / part, topdown=True):
            if any([file.endswith(".flac") for file in files]):
                dir_paths.add(Path(dir_path))
        full_data = []
        for dir_path in dir_paths:
            text_path = list(dir_path.glob("*.trans.txt"))[0]
            with text_path.open() as file:
                for line in file.readlines():
                    audio_id = line.split()[0]
                    audio_path = dir_path / str(audio_id + ".flac")
                    audio_info = torchaudio.info(audio_path)
                    text = " ".join(line.split()[1:])
                    full_data.append(
                        {
                            "path": audio_path,
                            "text": BaseTextEncoder.preprocess_text(text),
                            "audio_duration": audio_info.num_frames / audio_info.sample_rate,
                        }
                    )
        return full_data


class CommonVoiceDataset(ASRBaseDataset):
    """Common Voice dataset for training an ASR model."""

    def __init__(self: "CommonVoiceDataset", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        super(ASRBaseDataset, self).__init__(config)
        pass
