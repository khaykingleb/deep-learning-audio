import lightning as L


class ASRModel(L.LightningModule):
    def __init__(self) -> None:
        super().__init__()
        # self.save_hyperparameters()  # The hyperparameters are saved to the “hyper_parameters” key in the checkpoint

        # The LightningModule knows what device it is on. You can access the reference via self.device
        # Sometimes it is necessary to store tensors as module attributes.
        # However, if they are not parameters they will remain on the CPU even if the module gets moved to a new device.
        # To prevent that and remain device agnostic, register the tensor as a buffer in your modules’ __init__ method with register_buffer().
        # self.register_buffer("sigma", torch.eye(3))
        # you can now access self.sigma anywhere in your module

        # This model only trains the decoder, we don't save the encoder
        # self.encoder = from_pretrained(...).requires_grad_(False)
        # self.decoder = Decoder()
        # # Set to False because we only care about the decoder
        # self.strict_loading = False
        # def state_dict(self):
        #     # Don't save the encoder, it is not being trained
        #     return {k: v for k, v in super().state_dict().items() if "encoder" not in k}
        # Loading a checkpoint is normally “strict”, meaning parameter names in the checkpoint must
        # match the parameter names in the model or otherwise PyTorch will raise an error.
        # In use cases where you want to load only a partial checkpoint, you can disabl
        # strict loading by setting self.strict_loading = False in the LightningModule
        # to avoid errors. A common use case is when you have a pretrained feature extractor
        # or encoder that you don’t update during training, and you don’t want it included in the checkpoint

    def configure_optimizers(self):
        pass

    def training_step(self):
        pass
        # self.log("train_loss", loss)
        # values = {"loss": loss, "acc": acc, "metric_n": metric_n}  # add more items if needed
        # self.log_dict(values)

        # To view metrics in the commandline progress bar, set the prog_bar argument to True.
        # self.log(..., prog_bar=True)
        # Epoch 3:  33%|███▉        | 307/938 [00:01<00:02, 289.04it/s, loss=0.198, v_num=51, acc=0.211, metric_n=0.937]

        # When running in distributed mode, we have to ensure that the validation and test step logging calls are synchronized across processes.
        # This is done by adding sync_dist=True to all self.log calls in the validation and test step
        # This ensures that each GPU worker has the same behaviour when tracking model checkpoints, which is important for later downstream tasks such as testing the best checkpoint across all workers.
        # The sync_dist option can also be used in logging calls during the step methods, but be aware that this can lead to significant communication overhead and slow down your training.

        # Add sync_dist=True to sync logging across all GPU workers (may have performance impact)
        # self.log("validation_loss", loss, on_step=True, on_epoch=True, sync_dist=True)

        # It is possible to perform some computation manually and log the reduced result on rank 0 as follows:
        # When you call `self.log` only on rank 0, don't forget to add
        # `rank_zero_only=True` to avoid deadlocks on synchronization.
        # Caveat: monitoring this is unimplemented, see https://github.com/Lightning-AI/lightning/issues/15852
        # if self.trainer.is_global_zero:
        # self.log("my_reduced_metric", mean, rank_zero_only=True)

    def test_step(self):
        pass
        # self.log("test_loss", loss)

    def validation_step(self):
        pass
        # self.log("val_loss", loss)

    # https://lightning.ai/docs/pytorch/stable/common/checkpointing_intermediate.html#modify-a-checkpoint-anywhere
    def on_save_checkpoint(self, checkpoint):
        # checkpoint["something_cool_i_want_to_save"] = my_cool_pickable_object
        pass

    # https://lightning.ai/docs/pytorch/stable/common/checkpointing_intermediate.html#modify-a-checkpoint-anywhere
    def on_load_checkpoint(self, checkpoint):
        # my_cool_pickable_object = checkpoint["something_cool_i_want_to_save"]
        pass
