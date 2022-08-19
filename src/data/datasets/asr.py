"""Datasets for training ASR models."""

from omegaconf import DictConfig
from torch.utils.data import Dataset


class BaseDatasetForASR(Dataset):
    """Base dataset for training an ASR model."""

    def __init__(self: "BaseDatasetForASR", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        pass


class LJSpeechDataset(BaseDatasetForASR):
    """LJ Speech dataset for training an ASR model."""

    def __init__(self: "LJSpeechDataset", config: DictConfig) -> None:
        """Constructor.

        Args:
            config (DictConfig): Configuration file.
        """
        super(BaseDatasetForASR, self).__init__(config)
        pass

    def __getitem__(self: "LJSpeechDataset", idx: int) -> None:  # NOQA: D105
        pass

    def __len__(self: "LJSpeechDataset") -> int:  # NOQA: D105
        pass


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
