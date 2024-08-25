import re
import string

import torch


class BaseTextEncoder:
    """Base text encoder."""

    def __init__(self, alphabet: list[str]) -> None:
        """Constructor.

        Args:
            alphabet (list): Alphabet used for tokenization.
        """
        self.token2char = {k: v for k, v in enumerate(sorted(alphabet))}
        self.char2token = {v: k for k, v in enumerate(sorted(alphabet))}

    def encode(self, text: str) -> torch.Tensor:
        """Encode text according to char2token mapping.

        Args:
            text (str): Text to encode.

        Returns:
            Encoded text as a tensor.
        """
        text = self._preprocess_text(text)
        return torch.Tensor([self.char2token[char] for char in text]).unsqueeze(dim=0)

    def decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text.
        """
        return "".join([self.token2char[token.item()] for token in tokens])

    def _preprocess_text(
        self,
        text: str,
        *,
        remove_punctuation: bool | None = True,
        remove_spaces: bool | None = True,
    ) -> str:
        """Preprocess text by lowercasing and removing punctuation before using it with the tokenizer.

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


class CTCTextEncoder(BaseTextEncoder):
    """Text encoder for Connectionist Temporal Classification."""

    def __init__(self, alphabet: list[str], blank_symbol: str | None = "ϵ") -> None:
        """Constructor.
        Args:
           alphabet (list): Alphabet used for tokenization.
           blank_symbol (str, optional): Blank symbol. Defaults to "ϵ".
        """
        alphabet.append(blank_symbol)
        super().__init__(alphabet)

        self._blank_symbol = blank_symbol
        self._blank_token = self.char2token[blank_symbol]

    def raw_decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text with blank symbols.
        """
        return "".join([self.token2char[token.item()] for token in tokens])

    def decode(self, tokens: torch.Tensor) -> str:
        """Decode tokens according to token2char mapping.

        Args:
            tokens (Tensor): Tokens to decode.

        Returns:
            Decoded text without blank symbols.
        """
        decoded_text = ""
        for idx, token in enumerate(tokens):
            token = token.item()
            if token == self._blank_token:
                continue
            if idx >= 0 and token != tokens[idx - 1]:
                continue
            decoded_text += self.token2char[token]
        return decoded_text
