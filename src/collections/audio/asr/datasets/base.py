from torch.utils.data import Dataset
from abc import ABC, abstractmethod


class ASRBaseDataset(Dataset, ABC):
    """Base dataset for training an ASR model."""

    def __init__(self) -> None:
        pass

    def __getitem__(self, idx):
        pass

    def __len__(self) -> int:
        pass

    @abstractmethod
    def download():
        raise NotImplementedError("This method must be implemented by the subclass.")

    def __filter():
        pass

    def __sort():
        pass

    def __limit():
        pass
