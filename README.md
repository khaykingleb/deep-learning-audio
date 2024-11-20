use make help for getting updated on the build commands

make init-local for local development

make init for development inside a docker container

Попробовать флеймгаф тут

https://huggingface.co/spaces/fishaudio/fish-speech-1/blob/main/fish_speech/train.py

https://github.com/pytorch/ao

https://github.com/mynalabsai/speech/blob/main/examples/tts/train_tts.py

https://github.com/ashleve/lightning-hydra-template/blob/main/src/eval.py


>>> import lightning
>>> dir(lightning.pytorch.callbacks)
>>> ['BackboneFinetuning', 'BaseFinetuning', 'BasePredictionWriter', 'BatchSizeFinder', 'Callback', 'Checkpoint', 'DeviceStatsMonitor', 'EarlyStopping', 'GradientAccumulationScheduler', 'LambdaCallback', 'LearningRateFinder', 'LearningRateMonitor', 'ModelCheckpoint', 'ModelPruning', 'ModelSummary', 'OnExceptionCheckpoint', 'ProgressBar', 'RichModelSummary', 'RichProgressBar', 'SpikeDetection', 'StochasticWeightAveraging', 'TQDMProgressBar', 'ThroughputMonitor', 'Timer', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', 'batch_size_finder', 'callback', 'checkpoint', 'device_stats_monitor', 'early_stopping', 'finetuning', 'gradient_accumulation_scheduler', 'lambda_function', 'lr_finder', 'lr_monitor', 'model_checkpoint', 'model_summary', 'on_exception_checkpoint', 'prediction_writer', 'progress', 'pruning', 'rich_model_summary', 'spike', 'stochastic_weight_avg', 'throughput_monitor', 'timer']
>>>
>>
>
