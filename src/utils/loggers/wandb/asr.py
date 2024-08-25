import typing as tp
import random
import wandb
import torch

from PIL import Image

from src.utils.loggers.wandb import WBLogger
from src.utils.vizualization.audio import plot_transform
from src.collections.common.tokenizers import CTCTextEncoder


class WBLoggerASR(WBLogger):
    def log_random_audio(
        self,
        batch: dict[str, tp.Any],
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Literal["train", "val"],
    ) -> None:
        """Log random audio in the given batch and its DSP transformation to W&B.

        Args:
            batch (Dict): Batch of data samples.
            level (Literal): Level of logging.
            part (Literal): Part of logging.
        """
        idx = random.randint(0, len(batch["audios"]) - 1)
        waveform: torch.Tensor = batch["waveforms"][idx]
        waveform = waveform.squeeze().detach().cpu().numpy()

        # Log waveform of the audio signal
        audio_name = " ".join(map(lambda w: w.capitalize(), (part + " audio").split()))
        audio_caption = batch["texts"][idx]
        self.wandb.log(
            {
                audio_name: wandb.Audio(
                    waveform,
                    caption=audio_caption,
                    sample_rate=self._config.preprocessing.audio.sr,
                )
            },
            step=self._levels[level][part],
        )

        # Log transformation of the audio signal
        transform = batch["transforms"][idx]
        transform_image_buffer = plot_transform(
            transform,
            title="",
            xlabel="Time (seconds)",
            ylabel="",
            sample_rate=self._config.preprocessing.audio.sr,
            audio_size=waveform.shape[-1],
            show_fig=False,
        )
        with Image.open(transform_image_buffer) as transform_image:
            transform_name = f"{part} {self._config.preprocessing.transform.name}"
            transform_name = " ".join(
                map(lambda w: w.capitalize(), transform_name.lower().split())
            )
            self.wandb.log(
                {transform_name: wandb.Image(transform_image)},
                step=self._levels[level][part],
            )

    def log_predictions_from_ctc_decoding(
        self,
        batch: dict[str, tp.Any],
        probs: torch.Tensor,
        text_encoder: CTCTextEncoder,
        *,
        level: tp.Literal["step", "epoch"],
        part: tp.Literal["train", "val"],
    ) -> None:
        pred_tokens = probs.argmax(dim=-1)
        pred_raw_texts = [text_encoder.raw_decode(tokens) for tokens in pred_tokens]
        pred_texts = [text_encoder.decode(tokens) for tokens in pred_tokens]
        logs = [
            (
                f"{idx})"
                f"<br> <font color='green'> reference </font>: '{ref_text}' "
                f"<br> <font color='red'> hypothesis_raw </font>: '{hypo_raw_text}' "
                f"<br> <font color='blue'> hypothesis </font>: '{hypo_text}'"
            )
            for idx, (ref_text, hypo_raw_text, hypo_text) in enumerate(
                zip(batch["texts"], pred_raw_texts, pred_texts)
            )
        ]
        logs = "<br> --- <br>".join(logs)
        logs_name = f"{part.capitalize()} Naive Predictions"
        self.wandb.log(
            {logs_name: wandb.Html(logs)},
            step=self._levels[level][part],
        )
