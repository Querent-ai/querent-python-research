from typing import Dict, Optional, Union
from querent.config.storage_config import StorageBackend
from querent.callback.storage.storage_base import Storage
from querent.callback.storage.storage_errors import (
    StorageResolverError,
    StorageErrorKind,
)
from querent.common.uri import Protocol, Uri
from querent.callback.storage.storage_factory import StorageFactory
from querent.callback.storage.local.local_file_storage import LocalStorageFactory


class StorageResolver:
    def __init__(self):
        self.storage_factories: Dict[StorageBackend, StorageFactory] = {
            StorageBackend.LocalFile: LocalStorageFactory(),
        }

    def resolve(self, uri: Uri) -> Optional[Storage]:
        backend = self._determine_backend(uri.protocol)
        if backend in self.storage_factories:
            return self.storage_factories[backend].resolve(uri)
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
