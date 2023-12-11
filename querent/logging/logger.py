import logging
from logging.handlers import RotatingFileHandler
from querent.config.logger.logger_config import (
    LOGGING_LEVEL,
    LOGGING_FORMAT,
    LOGGING_DATE_FORMAT,
    LOGGING_FILE,
)


def setup_logger(logger_name: str, log_file_id: str) -> logging.Logger:
    """
    Setup a logger with a given name and log file id.
    """
    try:
        log_file_name = LOGGING_FILE % log_file_id
        logger = logging.getLogger(logger_name)
        logger.setLevel(LOGGING_LEVEL)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(LOGGING_FORMAT, LOGGING_DATE_FORMAT)
        )
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            log_file_name, maxBytes=1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter(LOGGING_FORMAT, LOGGING_DATE_FORMAT)
        )
        logger.addHandler(file_handler)

        return logger
    except Exception as e:
        logger.error(f"Error while setting up logger: {e}")
        return None
