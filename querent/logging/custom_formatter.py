import logging

class CustomFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)
