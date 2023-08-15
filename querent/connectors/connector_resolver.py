from typing import Dict, Optional, Union
from querent.config.connector_config import ConnectorBackend
from querent.connectors.connector_base import Connector
from querent.connectors.connector_errors import ConnectorResolverError, ConnectorErrorKind
from querent.common.uri import Protocol, Uri
from querent.connectors.connector_factory import ConnectorFactory
class ConnectorResolver:
    def __init__(self):
        self.connector_factories: Dict[ConnectorBackend, ConnectorFactory] = {}

    def register_connector_factory(self, backend: ConnectorBackend, factory: ConnectorFactory):
        self.connector_factories[backend] = factory

    def resolve(self, src_uri: Uri, dest_uri: Uri) -> Optional[Connector]:
        src_backend = self._determine_backend(src_uri.protocol)
        dest_backend = self._determine_backend(dest_uri.protocol)
        if src_backend in self.connector_factories:
            return self.connector_factories[src_backend].resolve(src_uri), 
        else:
            raise ConnectorResolverError(
                ConnectorErrorKind.NotSupported, src_backend, "Unsupported backend"
            )

    def _determine_backend(self, protocol: Protocol) -> ConnectorBackend:
        if protocol.is_file():
            return ConnectorBackend.LocalFile
        
        if protocol.is_grpc():
            return ConnectorBackend.Grpc

        if protocol.is_azure():
            return ConnectorBackend.Azure
        
        if protocol.is_postgresql():
            return ConnectorBackend.PostgreSQL
        
        if protocol.is_ram():
            return ConnectorBackend.Ram
        
        if protocol.is_s3():
            return ConnectorBackend.S3
        
        if protocol.is_file_storage():
            return ConnectorBackend.FileStorage
        
        if protocol.is_object_storage():
            return ConnectorBackend.ObjectStorage
        
        if protocol.is_database():
            return ConnectorBackend.Database
        else:
            raise ConnectorResolverError(
                ConnectorErrorKind.NotSupported, "Unknown backend", "Unknown backend"
            )