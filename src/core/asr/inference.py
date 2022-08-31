"""Inference part for Automatic Speech Recognition."""

import typing as tp

import torch

from .metrics import calc_cer, calc_wer
from ...data.preprocess.text import BaseTextEncoder


def get_metrics_from_ctc_decode(
    batch: tp.Dict[str, tp.Any],
    probs: torch.Tensor,
    text_encoder: BaseTextEncoder,
) -> tp.Tuple[tp.List[float]]:
    """Get predictions for a given batch without using beam search.

    Args:
        batch (Dict): Batch of data sample.
        probs (Tensor): Probabilities of characters for each frame.
        text_encoder (BaseTextEncoder): Text encoder used for tokenization.

    Returns:
        Tuple: CERs and WERs for batch.
    """
    pred_idxs = probs.argmax(dim=1)
    pred_texts = [text_encoder.ctc_decode(idxs) for idxs in pred_idxs]
    cers = []
    wers = []
    for ref_text, hypo_text in zip(batch["texts"], pred_texts):
        cers.append(calc_cer(ref_text, hypo_text) * 100)
        wers.append(calc_wer(ref_text, hypo_text) * 100)
    return cers, wers
