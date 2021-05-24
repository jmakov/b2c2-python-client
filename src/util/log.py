import logging
from logging import handlers

logger = logging.getLogger(__name__)


def configure_logger(target_logger: logging.Logger, log_path: str, log_level: str) -> None:
    target_logger.setLevel(logging.DEBUG)
    file_handler = handlers.RotatingFileHandler(log_path, backupCount=2, maxBytes=1000000)
    file_handler.setLevel(logging.getLevelName(log_level))
    formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(funcName)s:%(lineno)s:%(message)s")
    file_handler.setFormatter(formatter)
    target_logger.addHandler(file_handler)

    logger.info(f"Logger set to path: {log_path}, log_level: {log_level}")
