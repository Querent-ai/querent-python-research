from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from querent.storage.storage_base import Storage
from querent.storage.storage_errors import StorageResolverError, StorageErrorKind
from querent.config.storage_config import StorageBackend


class StorageFactory(ABC):
    @abstractmethod
    def backend(self) -> StorageBackend:
        pass

    @abstractmethod
    async def resolve(self, uri: str) -> Optional[Storage]:
        pass


class UnsupportedStorage(StorageFactory):
    def __init__(self, backend: StorageBackend, message: str):
        self.backend = backend
        self.message = message

    async def resolve(self, uri: str) -> Optional[Storage]:
        raise StorageResolverError(
            StorageErrorKind.NotSupported, self.backend, self.message
        )
