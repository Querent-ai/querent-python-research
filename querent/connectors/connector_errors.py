from typing import List, Dict
from pathlib import Path
from enum import Enum

class ConnectorErrorKind(Enum):
    NotFound = "not_found"
    Unauthorized = "unauthorized"
    Service = "noincompatible"



class ConnectorResolverError(Exception):
    def __init__(self, kind: ConnectorErrorKind, message: str):
        super().__init__(message)
        self.kind = kind


class ConnectorError(Exception):
    def __init__(self, kind: ConnectorErrorKind, source: any):
        self.kind = kind
        self.source = source


class NotFoundError(ConnectorError):
    def __init__(self, message: str):
        super().__init__(ConnectorErrorKind.NotFound, message)

class unauthorizedError(ConnectorError):
    def __init__(self, message: str):
        super().__init__(ConnectorErrorKind.unauthorized, message)


class incompatibleError(ConnectorError):
    def __init__(self, message: str):
        super().__init__(ConnectorErrorKind.incompatible, message)
