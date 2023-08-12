from typing import Dict
from querent.storage.storage_base import Storage, StorageBackend, StorageResolverError

class StorageResolver:
    def __init__(self):
        self.storage_factories: Dict[StorageBackend, StorageFactory] = {}

    def register_factory(self, backend: StorageBackend, factory: StorageFactory):
        self.storage_factories[backend] = factory

    async def resolve(self, uri: str) -> Optional[Storage]:
        # Parse the URI and determine the backend
        backend = ...
        if backend in self.storage_factories:
            return await self.storage_factories[backend].resolve(uri)
        else:
            raise StorageResolverError("Unsupported backend")

# Usage example
resolver = StorageResolver()
resolver.register_factory(StorageBackend.LocalFile, LocalFileStorageFactory())
resolver.register_factory(StorageBackend.Ram, RamStorageFactory())
# Add more factories for other backends

# Resolve a storage instance
uri = "localfile:///path/to/file"
storage = resolver.resolve(uri)
