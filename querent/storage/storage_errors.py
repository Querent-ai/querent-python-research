from typing import List, Dict
from pathlib import Path
from enum import Enum

class StorageErrorKind(Enum):
    NotFound = "not_found"
    Unauthorized = "unauthorized"
    Service = "service"
    InternalError = "internal_error"
    Timeout = "timeout"
    Io = "io"
    NotSupported = "not_supported"


class StorageResolverError(Exception):
    def __init__(self, kind: StorageErrorKind, message: str):
        super().__init__(message)
        self.kind = kind


class StorageError(Exception):
    def __init__(self, kind: StorageErrorKind, source: any):
        self.kind = kind
        self.source = source


class NotFoundError(StorageError):
    def __init__(self, message: str):
        super().__init__(StorageErrorKind.NotFound, message)


class ConnectionError(StorageError):
    def __init__(self, message: str):
        super().__init__(StorageErrorKind.ConnectionError, message)


class ReadError(StorageError):
    def __init__(self, message: str):
        super().__init__(StorageErrorKind.ReadError, message)


class WriteError(StorageError):
    def __init__(self, message: str):
        super().__init__(StorageErrorKind.WriteError, message)


class DeleteError(StorageError):
    def __init__(self, message: str):
        super().__init__(StorageErrorKind.DeleteError, message)


class BulkDeleteError(StorageError):
    def __init__(self, successes: List[Path], failures: Dict[Path, "DeleteFailure"], unattempted: List[Path]):
        self.successes = successes
        self.failures = failures
        self.unattempted = unattempted

    def __str__(self):
        return f"Bulk delete error ({len(self.successes)} success(es), {len(self.failures)} failure(s), {len(self.unattempted)} unattempted)"


class DeleteFailure:
    def __init__(self, error: StorageError = None, code: str = None, message: str = None):
        self.error = error
        self.code = code
        self.message = message


class StorageErrorFactory:
    @staticmethod
    def from_io_error(io_error: Exception) -> StorageError:
        io_error_kind = None
        if isinstance(io_error, FileNotFoundError):
            io_error_kind = StorageErrorKind.NotFound
        else:
            io_error_kind = StorageErrorKind.Io
        return StorageError(io_error_kind, io_error)

    @staticmethod
    def from_bulk_delete_error(error: BulkDeleteError) -> StorageError:
        return StorageError(StorageErrorKind.Io, error)
