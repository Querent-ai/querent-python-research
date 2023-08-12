from abc import ABC, abstractmethod
from typing import Optional
from querent.storage.storage_base import Storage, StorageBackend, StorageResolverError

class StorageFactory(ABC):
    @abstractmethod
    def backend(self) -> StorageBackend:
        pass

    @abstractmethod
    async def resolve(self, uri: str) -> Optional[Storage]:
        pass
