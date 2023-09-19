from enum import Enum


class IngestorError(Enum):
    EOF = "End of File"
    ETCD = "ETCD Error"
    NETWORK = "Network Error"
    TIMEOUT = "Timeout"
    UNKNOWN = "Unknown Error"
    FILE_NOT_FOUND = "File Not Found"
    IOERROR = "IOError"
    UIE = "UnidentifiedImageError"


class IngestorErrorBase(Exception):
    def __init__(self, error_code, message=None) -> None:
        super().__init__(message)
        self.error_code = error_code


class FileNotFoundError(IngestorErrorBase):
    """Error function for file not found"""

    def __init__(self, message=None):
        super().__init__(message=message, error_code=IngestorError.FILE_NOT_FOUND)


class IOError(IngestorErrorBase):
    """Error function for I/O Errors"""

    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.IOERROR, message)


class UnidentifiedImageError(IngestorErrorBase):
    """Error function for UnidentifiedImageError"""

    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.UIE, message)
