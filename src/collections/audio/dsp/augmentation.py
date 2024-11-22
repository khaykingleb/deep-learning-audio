"""Augmentations for digital audio signals."""

import math
import random
import typing as tp
from collections.abc import Callable

import torch
import torchaudio
import torchaudio.functional as F
from attrs import define, field

from src.collections.audio.dsp.audio import load_waveform
from src.utils.logger import logger

RIR_ASSET_URL = (
    "tutorial-assets/Lab41-SRI-VOiCES-rm1-impulse-mc01-stu-clo-8000hz.wav"
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
        max_pitch_shift (int): Maximum pitch shift.
        max_tempo_change (float): Maximum tempo change.
        use_room_reverberation (bool): Whether to use room reverberation.
        use_background_noise (bool): Whether to use background _noise.
        snr_dbs (list[float]): List of signal-to-noise ratios in dB.
    """

    sample_rate: int = field()
    use_sox_effects: bool = field(default=True)
    max_pitch_shift: int = field(default=2)
    max_tempo_change: float = field(default=0.3)
    use_room_reverberation: bool = field(default=True)
    use_background_noise: bool = field(default=True)
    snr_dbs: list[float] = field(default=[20, 10])

    _rir: torch.Tensor = field(repr=False)
    _noise: torch.Tensor = field(repr=False)
    _augmentations: dict[str, Callable] = field(repr=False)

    @_rir.default
    def _load_rir(self) -> torch.Tensor:
        """Load and process the Room Impulse Response (RIR).

        Using RIR, we can make clean speech sound as though it has been uttered
        in a conference room.

        Taken from: https://pytorch.org/audio/master/tutorials/audio_data_augmentation_tutorial.html
        """
        rir_path = torchaudio.utils.download_asset(RIR_ASSET_URL)
        rir = load_waveform(rir_path, sample_rate=self.sample_rate)
        rir = rir[
            :,
            int(self.sample_rate * 1.01) : int(self.sample_rate * 1.3),
        ]
        return rir / torch.linalg.vector_norm(rir, ord=2)

    @_noise.default
    def _load_noise(self) -> torch.Tensor:
        """Load and process the background noise."""
        noise_path = torchaudio.utils.download_asset(NOISE_ASSET_URL)
        return load_waveform(noise_path, sample_rate=self.sample_rate)

    @_augmentations.default
    def _setup_augmentations(self) -> dict[str, Callable]:
        """Setup augmentations."""
        augmentations = {}
        if self.use_sox_effects:
            logger.info("Enabling SOX effects.")
            augmentations["sox"] = self._apply_sox_effect
        if self.use_room_reverberation:
            logger.info("Enabling room reverberation.")
            augmentations["room_reverberation"] = (
                self._simulate_room_reverberation
            )
        if self.use_background_noise:
            logger.info("Enabling background noise.")
            augmentations["noise"] = self._add_background_noise

        if len(augmentations) == 0:
            msg = (
                "Invalid initialization: No augmentations selected. "
                "At least one augmentation method should be enabled. "
            )
            raise ValueError(msg)

        return augmentations

    def __call__(
        self,
        waveform: torch.Tensor,
        augmentation_type: tp.Literal[
            "sox",
            "room_reverberation",
            "noise",
        ]
        | None = None,
    ) -> torch.Tensor:
        """Augment digital signal according to the configuration.

        Args:
            waveform: Audio signal of shape (1, n_length).
            augmentation_type: Type of augmentation to apply if specified.
                Defaults to a random augmentation.

        Returns:
            Augmented audio signal.
        """
        if (
            augmentation_type is not None
            and augmentation_type not in self._augmentations
        ):
            msg = (
                f"Invalid augmentation type: {augmentation_type}. "
                f"Valid types are: {list(self._augmentations.keys())}. "
                "Check that augmentations are enabled in the configuration."
            )
            raise ValueError(msg)

        augmentation_name = (
            augmentation_type
            if augmentation_type is not None
            else random.choice(list(self._augmentations.keys()))
        )
        return self._augmentations[augmentation_name](waveform)

    def _apply_sox_effect(
        self,
        waveform: torch.Tensor,
        effect: list[str] | None = None,
    ) -> torch.Tensor:
        """Apply SOX effect to the digital signal."""
        effects_to_choose = [
            ["pitch", str(random.randint(0, self.max_pitch_shift))],
            ["tempo", str(1 + self.max_tempo_change * random.uniform(-1, 1))],
        ]
        selected_effect = effect or random.choice(effects_to_choose)
        waveform, _ = torchaudio.sox_effects.apply_effects_tensor(
            waveform,
            sample_rate=self.sample_rate,
            effects=[selected_effect],
            channels_first=True,
        )
        return waveform

    def _simulate_room_reverberation(
        self,
        waveform: torch.Tensor,
    ) -> torch.Tensor:
        """Simulate room reverberation using Room Impulse Response (RIR)."""
        return F.fftconvolve(waveform, self._rir, mode="full")

    def _add_background_noise(
        self,
        waveform: torch.Tensor,
        snr_db: float | None = None,
    ) -> torch.Tensor:
        """Add background noise to the digital signal."""
        n_repeat = math.ceil(waveform.shape[1] / self._noise.shape[1])
        noise = self._noise.repeat([1, n_repeat])[:, : waveform.shape[1]]
        waveform_rms, noise_rms = waveform.norm(p=2), noise.norm(p=2)
        snr_db = snr_db or random.choice(self.snr_dbs)
        snr = 10 ** (snr_db / 20)
        snr_ratio = snr * noise_rms / waveform_rms
        return (snr_ratio * waveform + noise) / 2
