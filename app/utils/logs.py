from loguru import logger

logger.add(
    "info.log",
    rotation="10 MB",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="INFO",
)
logger.add(
    "errors.log",
    rotation="10 MB",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
)
# Remove the logging print out to standard error
# logger.remove(0)

logger = logger
