from typing import Dict, Optional, Union
from querent.config.connector_config import ConnectorBackend
from querent.connectors.connector_base import Connector
from querent.connectors.connector_errors import ConnectorResolverError, ConnectorErrorKind
from querent.common.uri import Protocol, Uri
from querent.connectors.connector_factory import ConnectorFactory
class ConnectorResolver:
    def __init__(self):
        pass

    def resolve(self, src_uri: Uri, dest_uri: Uri) -> Optional[Connector]:
        src_backend = self._determine_backend(src_uri.protocol)
        dest_backend = self._determine_backend(src_dest.protocol)
        if backend in self.connector_factories:
            return self.connector_factories[src_backend].resolve(uri), 
        else:
            raise ConnectorResolverError(
                ConnectorErrorKind.NotSupported, backend, "Unsupported backend"
            )

    def _determine_backend(self, protocol: Protocol) -> ConnectorBackend:
        if protocol.is_file_Connector():
            return ConnectorBackend.LocalFile
        else:
            raise ConnectorResolverError(
                ConnectorErrorKind.NotSupported, "Unknown backend", "Unknown backend"
            )