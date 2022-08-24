"""Text data."""

import re
import string
import typing as tp
from pathlib import Path

import torch
from omegaconf import OmegaConf

# TODO: Decide what vocabulary to use for ASR models.


class BaseTextEncoder:
    """Base text encoder."""

    def __init__(
        self: "BaseTextEncoder",
        alphabet: tp.Optional[tp.List[str]] = None,
    ) -> None:
        """Constructor.

        Args:
            alphabet (List, optional): Alphabet used for tokenization.
        """
        self.alphabet = self.get_simple_alphabet() if alphabet is None else alphabet
        self.idx_to_char = {k: v for k, v in enumerate(sorted(self.alphabet))}
        self.char_to_idx = {v: k for k, v in enumerate(sorted(self.alphabet))}

    def __getitem__(
        self: "BaseTextEncoder",
        key: tp.Union[int, str],
    ) -> tp.Union[int, str]:
        """Get value from idx_to_char or char_to_idx based on the key type.

        Args:
            key (int, str): The key to get the associated value.

        Returns:
            The value.
        """
        if isinstance(key, int):
            return self.idx_to_char[key]
        elif isinstance(key, str):
            return self.char_to_idx[key]

    def encode(self: "BaseTextEncoder", text: str) -> torch.Tensor:
        """Encode text.

        Args:
            text (str): Text to encode.

        Raises:
            Exception: If encoding fails due to unknown characters.

        Returns:
            Tensor: Encoded text in form of torch.Tensor.
        """
        text = self.preprocess_text(text, self.alphabet)
        try:
            return torch.Tensor([self.char_to_idx[char] for char in text]).unsqueeze(0)
        except KeyError:
            unknown_chars = {char for char in text if char not in self.char_to_idx}
            raise Exception(
                """\
                Cannot encode text:\n\n
                {text}.\n\n
                Unknown chars: {unknown_chars}.""".format(
                    text=text,
                    unknown_chars=" ".join(unknown_chars),
                )
            )

    def decode(self: "BaseTextEncoder", x: torch.Tensor) -> str:  # NOQA
        pass

    @property
    def alphabet_length(self: "BaseTextEncoder") -> int:
        """Get the length of the alphabet used in the tokenization.

        Returns:
            int: Alphabet length.
        """
        return len(self.idx_to_char)

    @staticmethod
    def get_simple_alphabet() -> tp.List[str]:
        """Get the most simple alphabet.

        Returns:
            List: Simple alphabet.
        """
        return list(string.ascii_lowercase + " ")

    @staticmethod
    def preprocess_text(text: str, alphabet: tp.List[str]) -> str:
        """Preprocess text before using it with the tokenizer.

        Args:
            text (str): Text to preprocess.
            alphabet (List): Alphabet used in the tokenization.

        Returns:
            str: Preprocessed text that is ready to be tokenized.
        """
        # NB: Can be changed to increase an ASR model performance
        text = re.sub(r"[^\w\s]", " ", text.lower())
        text = re.sub(r"\s+", " ", text)
        return "".join([char for char in text if char in alphabet]).strip()

    @classmethod
    def from_yaml(cls: "BaseTextEncoder", file: str) -> "BaseTextEncoder":
        """Construct the tokenizer from the YAML file.

        Args:
            file (str): The YAML file.

        Raises:
            Exception: If the file extension is not YAML.

        Returns:
            Base tokenizer.
        """
        if not file.endswith(".yaml") or not file.endswith(".yml"):
            raise Exception("Provide a file with a .yaml or .yml extension.")
        with Path(file).open() as file:
            char_to_idx = OmegaConf.load(file)
            base_tokenizer = cls(list(char_to_idx.keys()))
        return base_tokenizer
