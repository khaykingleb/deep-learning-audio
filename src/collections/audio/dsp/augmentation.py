"""Augmentations for digital audio signals."""

import math
import random
from collections.abc import Callable
from pathlib import Path

import torch
import torch.nn.functional as F
import torchaudio
from attrs import define, field

from src.collections.audio.dsp.audio import load_waveform

RIR_ASSET_URL = (
    "tutorial-assets/Lab41-SRI-VOiCES-rm1-babb-mc01-stu-clo-8000hz.wav"
)
NOISE_ASSET_URL = (
    "tutorial-assets/Lab41-SRI-VOiCES-rm1-babb-mc01-stu-clo-8000hz.wav"
)


@define(kw_only=True)
class AudioAugmenter:
    """Augments digital audio signals.

    Attributes:
        sample_rate (int): Sample rate.
        use_sox_effects (bool): Whether to use SOX effects.
        use_room_reverberation (bool): Whether to use room reverberation.
        use_background_noise (bool): Whether to use background _noise.
        max_pitch_shift (int): Maximum pitch shift.
        max_tempo_change (float): Maximum tempo change.
        max_speed_change (float): Maximum speed change.
        snr_dbs (list[float]): List of signal-to-_noise ratios in dB.
    """

    sample_rate: int = field()
    use_sox_effects: bool = field(default=False)
    max_pitch_shift: int = field(default=0)
    max_tempo_change: float = field(default=0)
    max_speed_change: float = field(default=0)
    use_room_reverberation: bool = field(default=False)
    use_background_noise: bool = field(default=False)
    snr_dbs: list[float] = field(factory=list)

    _augmentations: list[Callable] = field(
        factory=list,
        init=False,
        repr=False,
    )
    _rir: torch.Tensor = field(
        init=False,
        default=None,
        repr=False,
    )
    _noise: torch.Tensor = field(
        init=False,
        default=None,
        repr=False,
    )

    def __attrs_post_init__(self) -> None:
        """Post-initialization setup."""
        if self.use_room_reverberation:
            self._rir = self.__load_and_process_rir()
            self._augmentations.append(self.__simulate_room_reverberation)

        if self.use_background_noise:
            self._noise = self.__load_and_process_noise()
            self._augmentations.append(self.__add_background_noise)

        if self.use_sox_effects:
            self._augmentations.append(self.__apply_sox_effect)

        if len(self._augmentations) == 0:
            msg = (
                "Invalid initialization: No augmentations selected. "
                "At least one augmentation method should be enabled. "
            )
            raise ValueError(msg)

    def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
        """Augment digital signal according to the configuration.

        Args:
            waveform (Tensor): Audio signal of shape (1, n_length).

        Returns:
            Tensor: Augmented audio signal.
        """
        return random.choice(self._augmentations)(waveform)

    def __load_and_process_rir(self) -> torch.Tensor:
        """Load and process the Room Impulse Response (RIR)."""
        rir_path = torchaudio.utils.download_asset(RIR_ASSET_URL)
        rir = load_waveform(Path(rir_path), sample_rate=self.sample_rate)
        rir = rir[
            :,
            int(self.sample_rate * 1.01) : int(self.sample_rate * 1.3),
        ]
        rir = rir / torch.norm(rir, p=2)
        return torch.flip(rir, [1])

    def __load_and_process_noise(self) -> torch.Tensor:
        """Load and process the background _noise."""
        noise_path = torchaudio.utils.download_asset(NOISE_ASSET_URL)
        return load_waveform(Path(noise_path), sample_rate=self.sample_rate)

    def __apply_sox_effect(self, waveform: torch.Tensor) -> torch.Tensor:
        """Apply SOX effect to the digital signal."""
        effects_to_choose = [
            ["pitch", str(random.randint(0, self.max_pitch_shift))],
            ["tempo", str(1 + self.max_tempo_change * random.uniform(-1, 1))],
            ["speed", str(1 + self.max_speed_change * random.uniform(-1, 1))],
            ["reverb", "-w"],
        ]
        waveform, _ = torchaudio.sox_effects.apply_effects_tensor(
            waveform,
            sample_rate=self.sample_rate,
            effects=[random.choice(effects_to_choose)],
            channels_first=True,
        )
        return waveform

    def __simulate_room_reverberation(
        self,
        waveform: torch.Tensor,
    ) -> torch.Tensor:
        """Simulate room reverberation using Room Impulse Response (RIR)."""
        waveform = F.pad(waveform, (self._rir.shape[1] - 1, 0))
        return F.conv1d(waveform[None, ...], self._rir[None, ...])[0]

    def __add_background_noise(self, waveform: torch.Tensor) -> torch.Tensor:
        """Add background _noise to the digital signal."""
        # TODO(khaykingleb): check https://pytorch.org/audio/main/generated/torchaudio.functional.add_noise.html
        n_repeat = math.ceil(waveform.shape[1] / self._noise.shape[1])
        noise = self._noise.repeat([1, n_repeat])[:, : waveform.shape[1]]
        waveform_rms, noise_rms = waveform.norm(p=2), noise.norm(p=2)
        snr_db = random.choice(self.snr_dbs)
        snr = 10 ** (snr_db / 20)
        snr_ratio = snr * noise_rms / waveform_rms
        return (snr_ratio * waveform + noise) / 2
