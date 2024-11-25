import pytest

from src.collections.common.preprocessing.tokenizers import CTCTextTokenizer


@pytest.mark.parametrize(
    ("input_text", "expected_text"),
    [
        ("heϵϵϵllllϵϵϵϵllllϵo ϵwwϵorllϵd", "hello world"),
    ],
)
def test_ctc_tokenizer_decode(input_text: str, expected_text: str):
    tokenizer = CTCTextTokenizer(
        blank_symbol="ϵ",
        alphabet=list("abcdefghijklmnopqrstuvwxyz "),
    )
    tokens = tokenizer.encode(input_text)
    decoded_text = tokenizer.ctc_decode(tokens.squeeze())
    decoded_text_raw = tokenizer.decode(tokens.squeeze())
    assert (
        decoded_text == expected_text
    ), f'Decoded text "{decoded_text}" does not match "{expected_text}"'
    assert (
        decoded_text_raw == input_text
    ), f'Decoded text "{decoded_text_raw}" does not match "{input_text}"'
