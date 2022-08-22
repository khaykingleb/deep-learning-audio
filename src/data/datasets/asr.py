"""Datasets for training ASR models."""

import typing as tp
from math import ceil

import pandas as pd
import torchaudio
from omegaconf import DictConfig
from torch.utils.data import Dataset

from ..preprocessing.text import BaseTextEncoder
from ... import cfg

# TODO: Form batches based on audio length.

# TODO: Resample audios


class BaseDatasetForASR(Dataset):
    """Base dataset for training an ASR model."""

    def __init__(
        self: "BaseDatasetForASR",
        data: pd.DataFrame,
        *,
        text_encoder: BaseTextEncoder,
        config: DictConfig,
        use_audio_aug: bool,
        use_transform_aug: bool,
    ) -> None:
        """Constructor.

        Args:
            data (DataFrame): Information about audio files.
            text_encoder (BaseTextEncoder): Text encoder used for text tokenization.
            config (DictConfig): Configuration file.
            use_audio_aug (bool): Whether to use audio augmentation on data.
            use_transform_aug (bool): Whether to use dsp augmentation on data.
        """
        self.data = self.filter_dataset(data, config)

        self.text_encoder = text_encoder

        self.config = config
        self.use_audio_aug = use_audio_aug
        self.use_transform_aug = use_transform_aug

    def __getitem__(self: "BaseDatasetForASR"):  # NOQA
        pass

    def __len__(self: "BaseDatasetForASR"):  # NOQA
        pass

    @staticmethod
    def filter_dataset(  # NOQA
        data: pd.DataFrame,
        *,
        config: DictConfig,
    ) -> pd.DataFrame:
        if config.data.max_text_length is not None:
            pass

        if config.data.max_audio_length is not None:
            pass


class LJSpeechDataset(BaseDatasetForASR):
    """LJ Speech dataset for training an ASR model."""

    LJ_SPEECH_DIR = cfg.BASE_DIR / "resources/datasets/asr/lj_speech"
    LJ_SPEECH_WAVS_DIR = LJ_SPEECH_DIR / "wavs"

    def __init__(
        self: "LJSpeechDataset",
        config: DictConfig,
        part: tp.Literal["train", "test", "val"],
    ) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
            part (Literal): Part of the dataset needed.
        """
        data = pd.read_csv(
            filepath_or_buffer=self.LJ_SPEECH_PATH / "metadata.csv",
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
        super(BaseDatasetForASR, self).__init__(
            data,
            config=config,
            use_audio_aug=True if part == "train" else False,
            use_transform_aug=True if part == "train" else False,
        )

    def __get_full_data(self: "LJSpeechDataset", data: pd.DataFrame) -> pd.DataFrame:
        full_data = []
        for idx, audio_name in enumerate(data[0]):
            audio_path = self.LJ_SPEECH_WAVS_DIR / str(audio_name + ".wav")
            audio_path = audio_path.resolve().as_posix()
            audio_info = torchaudio.info(audio_path)
            full_data.append(
                {
                    "path": audio_path,
                    "text": BaseTextEncoder.preprocess_text(data[2][idx]),
                    "audio_len": audio_info.num_frames / audio_info.sample_rate,
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
