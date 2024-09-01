"""Text preprocessing functions."""

import re
import string


def preprocess_text(
    text: str,
    *,
    remove_punctuation: bool | None = True,
    remove_spaces: bool | None = True,
) -> str:
    """Preprocess text before using it with the tokenizer or model.

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
