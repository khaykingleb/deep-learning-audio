"""Text tokenizers for preprocessing text data."""

import re
import string

import torch
from attrs import define, field


@define(kw_only=True)
class TextTokenizer:
    """Base text tokenizer.

    Attributes:
        alphabet (list[str]): List of characters in the alphabet.
    """

    alphabet: list[str] = field()

    _token2char: dict = field(init=False)
    _char2token: dict = field(init=False)

    def __attrs_post_init__(self):
        self._token2char = dict(enumerate(sorted(self.alphabet)))
        self._char2token = {v: k for k, v in self._token2char.items()}

    def encode(self, text: str) -> torch.Tensor:
        """Encode text according to char2token mapping.

        Args:
            text (str): Text to encode.

        Returns:
            Encoded text as a tensor.
        """
        text = self._preprocess_text(text)
        return torch.tensor(
            [self._char2token[char] for char in text]
        ).unsqueeze(0)

    def decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text.
        """
        return "".join([self._token2char[token.item()] for token in tokens])

    def _preprocess_text(
        self,
        text: str,
        *,
        remove_punctuation: bool | None = True,
        remove_spaces: bool | None = True,
    ) -> str:
        """Preprocess text before using it with the tokenizer.

        Args:
            text (str): Text to preprocess.
            remove_punctuation (bool, optional): Whether to remove punctuation.
            remove_spaces (bool, optional): Whether to remove multiple spaces.

        Returns:
            Preprocessed text.
        """
        text = text.lower()
        if remove_punctuation:
            text = text.translate(str.maketrans("", "", string.punctuation))
        if remove_spaces:
            text = re.sub(r"\s+", " ", text)
        return text.strip()


@define(kw_only=True)
class CTCTextTokenizer(TextTokenizer):
    """Text tokenizer for Connectionist Temporal Classification.

    Attributes:
        alphabet (list[str]): List of characters in the alphabet.
        blank_symbol (str): Blank symbol used in CTC loss.
    """

    blank_symbol: str = field(default="ϵ")
    _blank_token: int = field(init=False)

    def __attrs_post_init__(self):
        self.alphabet.append(self.blank_symbol)
        super().__attrs_post_init__()
        self._blank_token = self._char2token[self.blank_symbol]

    def raw_decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text with blank symbols.
        """
        return "".join([self._token2char[token.item()] for token in tokens])

    def decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text without blank symbols.
        """
        decoded_text = ""
        for idx, current_token in enumerate(tokens):
            token_value = current_token.item()
            if token_value == self._blank_token:
                continue
            if idx > 0 and token_value == tokens[idx - 1].item():
                continue
            decoded_text += self._token2char[token_value]
        return decoded_text
