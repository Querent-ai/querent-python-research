import logging
from querent.config.logger.logger_config import (
    LOGGING_LEVEL,
    LOGGING_FORMAT,
    LOGGING_DATE_FORMAT,
    LOGGING_FILE,
)
from querent.logging.handlers import create_console_handler, create_file_handler


def setup_logger(logger_name: str, log_file_id: str) -> logging.Logger:
    """
    Setup a logger with a given name and log file id.
    """
    try:
        log_file_name = LOGGING_FILE % log_file_id
        logger = logging.getLogger(logger_name)
        logger.setLevel(LOGGING_LEVEL)

        console_handler = create_console_handler(LOGGING_FORMAT, LOGGING_DATE_FORMAT)
        file_handler = create_file_handler(
            log_file_name, LOGGING_FORMAT, LOGGING_DATE_FORMAT
        )

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
    except Exception as e:
        print(f"Error while setting up logger: {e}")
        return None
