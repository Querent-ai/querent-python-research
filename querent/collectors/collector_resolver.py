from typing import Optional
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.collectors.webscaper.web_scraper_collector import WebScraperFactory
from querent.config.collector_config import CollectConfig, CollectorBackend
from querent.collectors.collector_base import Collector
from querent.collectors.collector_errors import CollectorResolverError, CollectorErrorKind
from querent.common.uri import Protocol, Uri

class CollectorResolver:
    def __init__(self):
        self.collector_factories = {
            CollectorBackend.LocalFile: FSCollectorFactory(),
            CollectorBackend.WebScraper: WebScraperFactory(),
            # Add other collector factories as needed
        }

    def resolve(self, uri: Uri, config: CollectConfig) -> Optional[Collector]:
        backend = self._determine_backend(uri.protocol)
        
        if backend in self.collector_factories:
            factory = self.collector_factories[backend]
            return factory.resolve(uri, config)
        else:
            raise CollectorResolverError(
                CollectorErrorKind.NotSupported, backend, "Unsupported backend"
            )

    def _determine_backend(self, protocol: Protocol) -> CollectorBackend:
        if protocol.is_file_storage():
            return CollectorBackend.LocalFile
        else:
            raise CollectorResolverError(
                CollectorErrorKind.NotSupported, "Unknown backend", "Unknown backend"
            )
