import lightning as L
from omegaconf import ListConfig


class ASRData(L.LightningDataModule):
    "Prepare and setup data for ASR model"

    def __init__(
        self,
        *,
        batch_size: int,
        datasets_cfg: ListConfig,
    ) -> None:
        super().__init__()
        self.save_hyperparameters(logger=True)

    def prepare_data(self) -> None:
        pass


# class ASRData(L.LightningDataModule):

#     # If you need information from the dataset to build your model, then run prepare_data and setup manually (Lightning ensures the method runs on the correct devices).
#     # dm = MNISTDataModule()
#     # dm.prepare_data()
#     # dm.setup(stage="fit")

#     # model = Model(num_classes=dm.num_classes, width=dm.width, vocab=dm.vocab)
#     # trainer.fit(model, dm)

#     # dm.setup(stage="test")
#     # trainer.test(datamodule=dm)


#     def __init__(self) -> None:
#         super().__init__()

#         # If set to True will call prepare_data() on LOCAL_RANK=0 for every node.
#         # If set to False will only call from NODE_RANK=0, LOCAL_RANK=0.
#         # self.prepare_data_per_node = True

#         #  DataModules support hyperparameters with the same API
#         # self.save_hyperparameters()

#         # class CustomDataModule(L.LightningDataModule):
#         # def __init__(self, *args, **kwargs):
#         #     super().__init__()
#         #     self.save_hyperparameters()

#         # def configure_optimizers(self):
#         #     # access the saved hyperparameters
#         #     opt = optim.Adam(self.parameters(), lr=self.hparams.lr)


#     def prepare_data(self):
#         # Downloading and saving data with multiple processes (distributed settings) will result in corrupted data.
#         # Lightning ensures the prepare_data() is called only within a single process on CPU, so you can safely add your downloading logic within.
#         # In case of multi-node training, the execution of this hook depends upon prepare_data_per_node.

#         # setup() is called after prepare_data and there is a barrier in between which ensures
#         # that all the processes proceed to setup once the data is prepared and available for use.

#         # download, i.e. download data only once on the disk from a single process
#         # tokenize. Since it’s a one time process, it is not recommended to do it on all processes
#         # etc…

#         # Warning:
#         # prepare_data is called from the main process.
#         # It is not recommended to assign state here (e.g. self.x = y) since
#         # it is called on a single process and if you assign states here then they won’t be available for other processes.

#     def setup(self, stage: str) -> None:
#         # There are also data operations you might want to perform on every GPU. Use setup() to do things like:

#         # count number of classes

#         # build vocabulary

#         # perform train/val/test splits

#         # create datasets

#         # apply transforms (defined explicitly in your datamodule)

#         # etc…


#         # This method expects a stage argument. It is used to separate setup logic for trainer.{fit,validate,test,predict}.

#         # NB: setup is called from every process across  all the nodes. Setting state here is recommended.

#     def teardown(self, stage: str) -> None:
#         # teardown can be used to clean up the state. It is also called from every process across all the nodes.
#         # Called at the end of fit (train + validate), validate, test, or predict.
#         # stage (str) – either 'fit', 'validate', 'test', or 'predict'

#     def test_dataloader(self):
#         # . Usually you just wrap the dataset you defined in setup. This is the dataloader that the Trainer fit() method uses.

#     def val_dataloader(self):
#         # This is the dataloader that the Trainer fit() and validate() methods uses.

#     def test_dataloader(self):
#         # This is the dataloader that the Trainer test() method uses.

#     def predict_dataloader(self):
#         # This is the dataloader that the Trainer predict() method uses.

#     # https://lightning.ai/docs/pytorch/stable/data/datamodule.html#on-before-batch-transfer
#     def on_before_batch_transfer(batch, dataloader_idx):
#         # Override to alter or apply batch augmentations to your batch before it is transferred to the device.

#         # def on_before_batch_transfer(self, batch, dataloader_idx):
#         #     batch['x'] = transforms(batch['x'])
#         #     return batch

#     # https://lightning.ai/docs/pytorch/stable/data/datamodule.html#transfer-batch-to-device
#     def transfer_batch_to_device(self, batch, device, dataloader_idx):
#         # Override this hook if your DataLoader returns tensors wrapped in a custom data structure.

#         # The data types listed below (and any arbitrary nesting of them) are supported out of the box:

#         # torch.Tensor or anything that implements .to(…)

#         # list

#         # dict

#         # tuple

#         # For anything else, you need to define how the data is moved to the target device (CPU, GPU, TPU, …).


#         # This hook should only transfer the data and not modify it, nor should it move the data to any
#         # other device than the one passed in as argument (unless you know what you are doing).
#         # To check the current state of execution of this hook you can use
#         # self.trainer.training/testing/validating/predicting so that you can add different logic as per your requirement.


#         # def transfer_batch_to_device(self, batch, device, dataloader_idx):
#         #     if isinstance(batch, CustomBatch):
#         #         # move all tensors in your custom data structure to the device
#         #         batch.samples = batch.samples.to(device)
#         #         batch.targets = batch.targets.to(device)
#         #     elif dataloader_idx == 0:
#         #         # skip device transfer for the first dataloader or anything you wish
#         #         pass
#         #     else:
#         #         batch = super().transfer_batch_to_device(batch, device, dataloader_idx)
#         #     return batch

#     # https://lightning.ai/docs/pytorch/stable/data/datamodule.html#on-after-batch-transfer
#     def on_after_batch_transfer(batch, dataloader_idx):
#         # Override to alter or apply batch augmentations to your batch after it is transferred to the device.
#         # To check the current state of execution of this hook you can use self.trainer.training/testing/validating/predicting
#         # so that you can add different logic as per your requirement.

#         # def on_after_batch_transfer(self, batch, dataloader_idx):
#         #     batch['x'] = gpu_transforms(batch['x'])
#         #     return batch

#     def state_dict(self):
#         pass

#     def load_state_dict(self, state_dict: Dict[str, EVAL_DATALOADERS]) -> None:
#         pass
#         # When a checkpoint is created, it asks every DataModule for their state.
#         # If your DataModule defines the state_dict and load_state_dict methods, the checkpoint
#         # will automatically track and restore your DataModules.

#         # class LitDataModule(L.LightningDataModule):
#         #     def state_dict(self):
#         #         # track whatever you want here
#         #         state = {"current_train_batch_index": self.current_train_batch_index}
#         #         return state

#         #     def load_state_dict(self, state_dict):
#         #         # restore the state based on what you tracked in (def state_dict)
#         #         self.current_train_batch_index = state_dict["current_train_batch_index"]


# ---

# # For eg., if you are working with NLP task where you need to tokenize the text
# # and use it, then you can do something like as follows:

# # class LitDataModule(L.LightningDataModule):
# #     def prepare_data(self):
# #         dataset = load_Dataset(...)
# #         train_dataset = ...
# #         val_dataset = ...
# #         # tokenize
# #         # save it to disk

# #     def setup(self, stage):
# #         # load it back here
# #         dataset = load_dataset_from_disk(...)

# ---


# # The LightningDataModule is a convenient way to manage data in PyTorch Lightning.
# # It encapsulates training, validation, testing, and prediction dataloaders, as well as any necessary steps for data processing, downloads, and transformations.
# # By using a LightningDataModule, you can easily develop dataset-agnostic models, hot-swap different datasets, and share data splits and transformations across projects


# # regular PyTorch
# test_data = MNIST(my_path, train=False, download=True)
# predict_data = MNIST(my_path, train=False, download=True)
# train_data = MNIST(my_path, train=True, download=True)
# train_data, val_data = random_split(train_data, [55000, 5000])

# train_loader = DataLoader(train_data, batch_size=32)
# val_loader = DataLoader(val_data, batch_size=32)
# test_loader = DataLoader(test_data, batch_size=32)
# predict_loader = DataLoader(predict_data, batch_size=32)

# class MNISTDataModule(L.LightningDataModule):
#     def __init__(self, data_dir: str = "path/to/dir", batch_size: int = 32):
#         super().__init__()
#         self.data_dir = data_dir
#         self.batch_size = batch_size

#     def setup(self, stage: str):
#         self.mnist_test = MNIST(self.data_dir, train=False)
#         self.mnist_predict = MNIST(self.data_dir, train=False)
#         mnist_full = MNIST(self.data_dir, train=True)
#         self.mnist_train, self.mnist_val = random_split(
#             mnist_full, [55000, 5000], generator=torch.Generator().manual_seed(42)
#         )

#     def train_dataloader(self):
#         return DataLoader(self.mnist_train, batch_size=self.batch_size)

#     def val_dataloader(self):
#         return DataLoader(self.mnist_val, batch_size=self.batch_size)

#     def test_dataloader(self):
#         return DataLoader(self.mnist_test, batch_size=self.batch_size)

#     def predict_dataloader(self):
#         return DataLoader(self.mnist_predict, batch_size=self.batch_size)

#     def teardown(self, stage: str):
#         # Used to clean-up when the run is finished
#         ...

# ---
# mnist = MNISTDataModule(my_path)
# model = LitClassifier()

# trainer = Trainer()
# trainer.fit(model, mnist)

# import lightning as L
# from torch.utils.data import random_split, DataLoader

# # Note - you must have torchvision installed for this example
# from torchvision.datasets import MNIST
# from torchvision import transforms


# class MNISTDataModule(L.LightningDataModule):
#     def __init__(self, data_dir: str = "./"):
#         super().__init__()
#         self.data_dir = data_dir
#         self.transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])

#     def prepare_data(self):
#         # download
#         MNIST(self.data_dir, train=True, download=True)
#         MNIST(self.data_dir, train=False, download=True)

#     def setup(self, stage: str):
#         # Assign train/val datasets for use in dataloaders
#         if stage == "fit":
#             mnist_full = MNIST(self.data_dir, train=True, transform=self.transform)
#             self.mnist_train, self.mnist_val = random_split(
#                 mnist_full, [55000, 5000], generator=torch.Generator().manual_seed(42)
#             )

#         # Assign test dataset for use in dataloader(s)
#         if stage == "test":
#             self.mnist_test = MNIST(self.data_dir, train=False, transform=self.transform)

#         if stage == "predict":
#             self.mnist_predict = MNIST(self.data_dir, train=False, transform=self.transform)

#     def train_dataloader(self):
#         return DataLoader(self.mnist_train, batch_size=32)

#     def val_dataloader(self):
#         return DataLoader(self.mnist_val, batch_size=32)

#     def test_dataloader(self):
#         return DataLoader(self.mnist_test, batch_size=32)

#     def predict_dataloader(self):
#         return DataLoader(self.mnist_predict, batch_size=32)
