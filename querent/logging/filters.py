import logging


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class WarnLevelFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.WARNING
    

class ErrorLevelFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR
    

class CriticalLevelFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.CRITICAL
    

class InfoLevelFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO

class DebugLevelFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


