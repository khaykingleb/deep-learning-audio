import pytest

from src.collections.audio.dsp.audio import load_waveform
from src.utils.env import BASE_DIR


@pytest.mark.parametrize("sample_rate", [None, 8000, 16000])
def test_load_waveform(sample_rate: int):
    waveform = load_waveform(
        BASE_DIR.joinpath("tests/data/test.wav").as_posix(),
        sample_rate=sample_rate,
    )
    assert len(waveform.shape) == 2, "Waveform should be 2D"
    assert waveform.shape[0] == 1, "Waveform should have one channel"
