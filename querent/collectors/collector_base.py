from abc import ABC, abstractmethod
from typing import AsyncGenerator
import asyncio

from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import CollectorConfig
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_message import MessageState, MessageType


class Collector(ABC):
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.message_queue = QuerentQueue()

    @abstractmethod
    async def connect(self):
        """
        Establishes an asynchronous connection to the data source.
        Args:
            None.
        Returns:
            None. This method should establish the connection but does not return it.
        """
        raise NotImplementedError

    @abstractmethod
    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        """
        Asynchronously polls data from the connected source.
        Args:
            None.
        Returns:
            AsyncGenerator[CollectedBytes, None]: An asynchronous generator yielding collected data.
        """
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self):
        """
        Asynchronously closes the connection to the data source.
        Args:
            None.
        Returns:
            None. This method handles the disconnection process but does not return anything.
        """
        raise NotImplementedError
