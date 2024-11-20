"""Entry point for the configuration of the logging system."""

import sys

from loguru import logger

from src.utils import env

# class InterceptHandler(Handler):
# Standard Library Log → InterceptHandler → Loguru → Console/File Output
# (PyTorch, Lightning)    (Interceptor)    (Logger)   (Handlers)

#     def emit(self, record: LogRecord) -> None:
#         # Get corresponding Loguru level if it exists.
#         level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno

#         # Find caller from where the log call was issued.
#         frame, depth = logging.currentframe(), 6
#         while frame and frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         # Log the message
#         logger.opt(
#             depth=depth,
#             exception=record.exc_info,
#         ).log(
#             level,
#             record.getMessage(),
#         )

# # Configure standard logging to pass through the interceptor
# logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
# for name in ["lightning.pytorch"]:
#     logging.getLogger(name).handlers = [InterceptHandler()]

# Configure loguru handlers
# log_file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# logger.configure(
#     handlers=[
#         {
#             "sink": sys.stdout,
#             "level": env.LOGGING_LEVEL,
#             "format": (
#                 "{time:YYYY-MM-DD HH:mm:ss} | {name} | "
#                 "<level>{level}: {message}</level> | {extra}"
#             ),
#             "colorize": True,
#             "enqueue": True,
#         },
#         {
#             "sink": env.BASE_DIR.joinpath(f"logs/{log_file_name}.log"),
#             "level": env.LOGGING_LEVEL,
#             "format": (
#                 "{time:YYYY-MM-DD HH:mm:ss} | {name} | "
#                 "<level>{level}: {message}</level> | {extra}"
#             ),
#             "colorize": True,
#             "enqueue": True,
#         }
#         if env.LOGGING_SINK_TO_FILE
#         else None,
#     ]
# )


console_handler = {
    "level": env.LOGGING_LEVEL,
    "sink": sys.stdout,
    "format": (
        "{time:YYYY-MM-DD HH:mm:ss} | {name} | "
        "<level>{level}: {message}</level> | {extra}"
    ),
    "colorize": True,
    "enqueue": True,
}

log_config = {"handlers": [console_handler]}
logger.configure(**log_config)
