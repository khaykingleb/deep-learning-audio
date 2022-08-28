"""Common metrics for Automatic Speech Recognition."""

import editdistance


def calc_cer(reference_text: str, hypothesis_text: str) -> float:
    """Calculates the character error rate.

    Args:
        reference_text (str): True text.
        hypothesis_text (str): Predicted text by an ASR model.

    Returns:
        float: Character error rate.
    """
    if len(reference_text) == 0 and len(hypothesis_text) == 0:
        return 0.0
    if len(reference_text) == 0 and len(hypothesis_text) != 0:
        return 1.0
    return editdistance.eval(reference_text, hypothesis_text) / len(reference_text)


def calc_wer(reference_text: str, hypothesis_text: str) -> float:
    """Calculates the word error rate.

    Args:
        reference_text (str): True text.
        hypothesis_text (str): Predicted text by an ASR model.

    Returns:
        float: Word error rate.
    """
    reference_words = reference_text.split()
    hypothesis_words = hypothesis_text.split()
    if len(reference_words) == 0 and len(hypothesis_words) == 0:
        return 0.0
    elif len(reference_words) == 0 and len(hypothesis_words) != 0:
        return 1.0
    return editdistance.eval(reference_words, hypothesis_words) / len(reference_words)
