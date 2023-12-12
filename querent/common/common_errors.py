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
    WRONGPPTFILE = "Wrong PPt file"
    INVALIDXMLERROR = "Invalid Xml Error"
    BADZIPFILE = "BadZipFile"
    UNICODEDECODEERROR = "UnicodeDecodeError"
    LOOKUPERROR = "LookupError"
    TYPEERROR = "TypeError"
    UNKNOWNVALUEERROR = "UnknownValueError"
    REQUESTERROR = "RequestError"
    INDEXERROR = "IndexError"
    CSVERROR = "CsvError"
    RUNTIMEERROR = "RuntimeError"
    JSONDECODEERROR = "JsonDecodeError"
    DOCUMENTERROR = "DocumentError"
    SHELLERROR = "ShellError"
    PERMISSIONERROR = "PermissionError"
    OSERROR = "OSError"
    CONNECTIONERROR = "ConnectionError"
    SLACKERROR = "SlackAPIError"
    POLLINGERROR = "PollingError"


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


class WrongPptFileError(IngestorErrorBase):
    """Error function if ppt file is not being passed into ppt ingestor"""

    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.WRONGPPTFILE, message)


class InvalidXmlError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.INVALIDXMLERROR, message)


class BadZipFile(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.BADZIPFILE, message)


class UnicodeDecodeError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.UNICODEDECODEERROR, message)


class LookupError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.LOOKUPERROR, message)


class TypeError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.TYPEERROR, message)


class UnknownValueError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.UNKNOWNVALUEERROR, message)


class RequestError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.REQUESTERROR, message)


class IndexErrorException(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.INDEXERROR, message)


class UnknownError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.UNKNOWN, message)


class CsvError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.CSVERROR, message)


class RuntimeError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.RUNTIMEERROR, message)


class JsonDecodeError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.JSONDECODEERROR, message)


class DocumentError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.DOCUMENTERROR, message)


class ShellError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.SHELLERROR, message)


class PermissionError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.PERMISSIONERROR, message)


class OSError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.OSERROR, message)


class ConnectionError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.CONNECTIONERROR, message)


class SlackApiError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.SLACKERROR, message)


class PollingError(IngestorErrorBase):
    def __init__(self, message=None) -> None:
        super().__init__(IngestorError.POLLINGERROR, message)
