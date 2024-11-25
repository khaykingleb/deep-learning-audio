"""Text tokenizers for preprocessing text data."""

import string

import torch
from attrs import define, field


@define(kw_only=True)
class TextTokenizer:
    """Base text tokenizer.

    Attributes:
        alphabet (list[str]): List of characters in the alphabet.
    """

    alphabet: list[str] = field(default=list(string.ascii_lowercase))

    _token2char: dict = field(init=False)
    _char2token: dict = field(init=False)

    def __attrs_post_init__(self):
        self._token2char = dict(enumerate(sorted(self.alphabet)))
        self._char2token = {v: k for k, v in self._token2char.items()}

    @property
    def alphabet_size(self) -> int:
        """Get the size of the alphabet.

        Returns:
            Size of the alphabet.
        """
        return len(self.alphabet)

    def encode(self, text: str) -> torch.Tensor:
        """Encode text according to char2token mapping.

        Args:
            text (str): Text to encode.

        Returns:
            Encoded text as a tensor.
        """
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

    @property
    def blank_token(self) -> int:
        """Get the blank token.

        Returns:
            Blank token.
        """
        return self._blank_token

    def ctc_decode(self, tokens: torch.Tensor) -> str:
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
