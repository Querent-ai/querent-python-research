from typing import List, Dict
from pathlib import Path
from enum import Enum


class CollectorErrorKind(Enum):
    NotFound = "not_found"
    Unauthorized = "unauthorized"
    incompatible = "incompatible"
    NotSupported = "not_supported"


class CollectorResolverError(Exception):
    def __init__(self, kind: CollectorErrorKind, message: str):
        super().__init__(message)
        self.kind = kind


class CollectorError(Exception):
    def __init__(self, kind: CollectorErrorKind, source: any):
        self.kind = kind
        self.source = source


class NotFoundError(CollectorError):
    def __init__(self, message: str):
        super().__init__(CollectorErrorKind.NotFound, message)


class UnauthorizedError(CollectorError):
    def __init__(self, message: str):
        super().__init__(CollectorErrorKind.unauthorized, message)


class IncompatibleError(CollectorError):
    def __init__(self, message: str):
        super().__init__(CollectorErrorKind.incompatible, message)
