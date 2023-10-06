import logging
from querent.logging.custom_formatter import CustomFormatter

def create_console_handler(log_format, date_format):
    console_handler = logging.StreamHandler()
    formatter = CustomFormatter(fmt=log_format, datefmt=date_format)
    console_handler.setFormatter(formatter)
    return console_handler


def create_file_handler(log_file, log_format, date_format):
    file_handler = logging.FileHandler(log_file)
    formatter = CustomFormatter(fmt=log_format, datefmt=date_format)
    file_handler.setFormatter(formatter)
    return file_handler
