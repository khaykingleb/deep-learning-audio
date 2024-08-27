"""Augmentations for digital audio signals."""

import math
import random
from pathlib import Path
from typing import TYPE_CHECKING

import torch
import torch.nn.functional as F
import torchaudio
from attrs import define, field

from src.collections.audio.dsp.audio import load_waveform

if TYPE_CHECKING:
    from collections.abc import Callable


RIR_ASSET_URL = (
    "tutorial-assets/Lab41-SRI-VOiCES-rm1-babb-mc01-stu-clo-8000hz.wav"
)
NOISE_ASSET_URL = (
    "tutorial-assets/Lab41-SRI-VOiCES-rm1-babb-mc01-stu-clo-8000hz.wav"
)


@define
class AudioAugmenter:
    """Augments digital signals.

    Attributes:
        sr (int): Sample rate.
        use_sox_effects (bool): Whether to use SOX effects.
        use_room_reverberation (bool): Whether to use room reverberation.
        use_background_noise (bool): Whether to use background noise.
        max_pitch_shift (int): Maximum pitch shift.
        max_tempo_change (float): Maximum tempo change.
        max_speed_change (float): Maximum speed change.
        snr_dbs (list[float]): List of signal-to-noise ratios in dB.
    """

    sr: int = field()
    use_sox_effects: bool = field(default=False)
    use_room_reverberation: bool = field(default=False)
    use_background_noise: bool = field(default=False)
    max_pitch_shift: int = field(default=0)
    max_tempo_change: float = field(default=0)
    max_speed_change: float = field(default=0)
    snr_dbs: list[float] = field(factory=list)

    def __attrs_post_init__(self) -> None:
        """Post-initialization setup."""
        self.augmentations: list[Callable[[torch.Tensor], torch.Tensor]] = []

        if self.use_room_reverberation:
            self.rir = self.__load_and_process_rir()
            self.augmentations.append(self.__simulate_room_reverberation)

        if self.use_background_noise:
            self.noise = self.__load_and_process_noise()
            self.augmentations.append(self.__add_background_noise)

        if self.use_sox_effects:
            self.augmentations.append(self.__apply_sox_effect)

        if not self.augmentations:
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
        return random.choice(self.augmentations)(waveform)

    def __load_and_process_rir(self) -> torch.Tensor:
        """Load and process the Room Impulse Response (RIR)."""
        rir_path = torchaudio.utils.download_asset(RIR_ASSET_URL)
        rir = load_waveform(Path(rir_path), sample_rate=self.sr)
        rir = rir[:, int(self.sr * 1.01) : int(self.sr * 1.3)]
        rir = rir / torch.norm(rir, p=2)
        return torch.flip(rir, [1])

    def __load_and_process_noise(self) -> torch.Tensor:
        """Load and process the background noise."""
        noise_path = torchaudio.utils.download_asset(NOISE_ASSET_URL)
        return load_waveform(Path(noise_path), sample_rate=self.sr)

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
            sample_rate=self.sr,
            effects=[random.choice(effects_to_choose)],
            channels_first=True,
        )
        return waveform

    def __simulate_room_reverberation(
        self,
        waveform: torch.Tensor,
    ) -> torch.Tensor:
        """Simulate room reverberation using Room Impulse Response (RIR)."""
        waveform = F.pad(waveform, (self.rir.shape[1] - 1, 0))
        return F.conv1d(waveform[None, ...], self.rir[None, ...])[0]

    def __add_background_noise(self, waveform: torch.Tensor) -> torch.Tensor:
        """Add background noise to the digital signal."""
        n_repeat = math.ceil(waveform.shape[1] / self.noise.shape[1])
        noise = self.noise.repeat([1, n_repeat])[:, : waveform.shape[1]]
        waveform_rms, noise_rms = waveform.norm(p=2), noise.norm(p=2)
        snr_db = random.choice(self.snr_dbs)
        snr = 10 ** (snr_db / 20)
        snr_ratio = snr * noise_rms / waveform_rms
        return (snr_ratio * waveform + noise) / 2
