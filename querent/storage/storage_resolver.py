from typing import Dict, Optional, Union
from querent.config.storage_config import StorageBackend
from querent.storage.storage_base import Storage
from querent.storage.storage_errors import StorageResolverError, StorageErrorKind
from querent.common.uri import Uri

class StorageResolver:
    def __init__(self):
        self.storage_factories: Dict[StorageBackend, StorageFactory] = {
            StorageBackend.LocalFile: LocalFileStorageFactory(),
        }

    def resolve(self, uri_str: str) -> Optional[Storage]:
        uri = Uri(uri_str)
        backend = self._determine_backend(uri.protocol)
        if backend in self.storage_factories:
            return self.storage_factories[backend].resolve(uri_str)
        else:
            raise StorageResolverError(
                StorageErrorKind.NotSupported, backend, "Unsupported backend"
            )

    def _determine_backend(self, protocol: Protocol) -> StorageBackend:
        if protocol.is_file_storage():
            return StorageBackend.LocalFile
        else:
            raise StorageResolverError(
                StorageErrorKind.NotSupported, "Unknown backend", "Unknown backend"
            )