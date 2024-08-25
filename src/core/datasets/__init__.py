from torch.utils.data import Dataset


class ASRBaseDataset(Dataset):
    """Base dataset for training an ASR model."""

    def __init__(self) -> None:
        pass

    def __getitem__(self, idx):
        pass

    def __len__(self) -> int:
        pass

    @staticmethod
    def download():
        raise NotImplementedError("This method must be implemented by the subclass.")

    @staticmethod
    def filter():
        pass

    @staticmethod
    def sort():
        pass

    @staticmethod
    def limit():
        pass
