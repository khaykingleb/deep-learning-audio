"""Module for LibriSpeech dataset."""

import tarfile
import urllib.request
from pathlib import Path

import polars as pl
import torchaudio
from attrs import define, field
from loguru import logger

from src.collections.audio.asr.datasets.base import ASRDataset
from src.collections.common.preprocessing.text import preprocess_text

LIBRI_SPEECH_URL = "https://openslr.elda.org/resources/12"
STAGES = [
    "dev-clean",
    "dev-other",
    "test-clean",
    "test-other",
    "train-clean-100",
    "train-clean-360",
    "train-other-500",
]


@define(kw_only=True)
class LibriSpeechDataset(ASRDataset):
    """Dataset class for LibriSpeech.

    Corpus of approximately 1000 hours of 16kHz read English speech.
    The data is derived from read audiobooks from the LibriVox project.

    Attributes:
        data_dir (str, Path): Directory to save the dataset.
        data_url (str): URL to the dataset.
        data_include_other (bool): Whether to include the 'other' quality data.
        data_part (str): Part of the dataset to use.
        data_proportions (list[float]): Proportions for train, val, test sets.
        data_samples_limit (int): Maximum number of samples.
        tokenizer (TextTokenizer): Tokenizer for text encoding.
        augmenter (AudioAugmenter): Augmenter for audio signals.
        transformer (Transformer): Audio transformation.
        text_max_length (int): Maximum length of text.
        audio_max_duration (int): Maximum duration of audio.
        audio_sample_rate (int): Sample rate in Hz.
        audio_aug_prob (float): Probability of audio augmentation.
    """

    data_dir: Path = field(converter=Path)
    data_include_other: bool = field(default=False)
    data_part: str = field(default="train")
    data_proportions: list[float] = field(default=[0.7, 0.15, 0.15])

    def __attrs_post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir = self.data_dir.joinpath("LibriSpeech")

    def download(self) -> None:
        """Download the LibriSpeech dataset."""
        for stage in STAGES:
            if self.extracted_dir.joinpath(stage).exists():
                logger.info(
                    f"Libri speech {stage} stage already exists. "
                    "Skipping download."
                )
                continue

            if "other" in stage and not self.data_include_other:
                logger.info(f"Skipping {stage} stage download.")
                continue

            logger.info(f"Downloading {stage} stage tar archive.")
            tar_path = self.data_dir.joinpath(f"{stage}.tar.gz")
            urllib.request.urlretrieve(
                f"{LIBRI_SPEECH_URL}/{stage}.tar.gz",
                filename=tar_path,
            )

            logger.info(f"Extracting {stage} stage tar archive.")
            with tarfile.open(tar_path, mode="r:gz") as tar:
                tar.extractall(path=self.data_dir, filter="data")

            tar_path.unlink()

    def setup(self, stage: str) -> pl.DataFrame:
        """Set up the LibriSpeech dataset.

        Args:
            stage (str): Dataset stage to set up.

        Returns:
            DataFrame: The dataset.
        """
        stage = "dev" if stage == "val" else stage

        data = []
        for path in self.extracted_dir.glob("*"):
            if path.is_dir() and stage in path.name:
                for text_path in path.glob("**/*.txt"):
                    text_lines = text_path.read_text().splitlines()
                    for line in text_lines:
                        audio_id, text = line.split(" ", maxsplit=1)
                        audio_path = text_path.parent.joinpath(
                            f"{audio_id}.flac"
                        )
                        audio_info = torchaudio.info(audio_path)
                        data.append(
                            {
                                "audio_path": str(audio_path),
                                "audio_duration": audio_info.num_frames
                                / audio_info.sample_rate,
                                "text": preprocess_text(text),
                            }
                        )

        self._data = pl.DataFrame(data)
        self.validate_data_before_finalizing()
        self.finalize_data()
        return self._data
