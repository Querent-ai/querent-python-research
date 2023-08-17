from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from querent.collectors.collector_base import Collector
from querent.collectors.collector_errors import CollectorResolverError, CollectorErrorKind
from querent.config.collector_config import CollectConfig, CollectorBackend


class CollectorFactory(ABC):
    @abstractmethod
    def backend(self) -> CollectorBackend:
        pass

    @abstractmethod
    async def resolve(self, uri: str, config: CollectConfig) -> Optional[CollectorBackend]:
        pass


class UnsupportedCollector(CollectorFactory):
    def __init__(self, backend: CollectorBackend, message: str):
        self.backend = backend
        self.message = message

    async def resolve(self, uri: str, config: CollectConfig) -> Optional[Collector]:
        raise CollectorResolverError(
            CollectorErrorKind.NotSupported, self.backend, self.message
        )
