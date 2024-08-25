# https://lightning.ai/docs/pytorch/stable/visualize/logging_advanced.html#enable-metrics-for-distributed-training

# For certain types of metrics that need complex aggregation, we recommended to build your metric using torchmetric which ensures all the complexities of metric aggregation in distributed environments is handled.
# import torch
# import torchmetrics
# class MyAccuracy(Metric):
#     def __init__(self, dist_sync_on_step=False):
#         # call `self.add_state`for every internal state that is needed for the metrics computations
#         # dist_reduce_fx indicates the function that should be used to reduce
#         # state from multiple processes
#         super().__init__(dist_sync_on_step=dist_sync_on_step)

#         self.add_state("correct", default=torch.tensor(0), dist_reduce_fx="sum")
#         self.add_state("total", default=torch.tensor(0), dist_reduce_fx="sum")

#     def update(self, preds: torch.Tensor, target: torch.Tensor):
#         # update metric states
#         preds, target = self._input_format(preds, target)
#         assert preds.shape == target.shape

#         self.correct += torch.sum(preds == target)
#         self.total += target.numel()

#     def compute(self):
#         # compute final result
#         return self.correct.float() / self.total


# To use the metric inside Lightning, 1) initialize it in the init, 2) compute the metric, 3) pass it into self.log
# class LitModel(LightningModule):
#     def __init__(self):
#         # 1. initialize the metric
#         self.accuracy = MyAccuracy()

#     def training_step(self, batch, batch_idx):
#         x, y = batch
#         preds = self(x)

#         # 2. compute the metric
#         self.accuracy(preds, y)

#         # 3. log it
#         self.log("train_acc_step", self.accuracy)
