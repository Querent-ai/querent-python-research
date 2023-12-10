from abc import ABC, abstractmethod
from typing import Any

from querent.common.types.querent_event import EventState, EventType
from querent.logging.logger import setup_logger

logger = setup_logger(__name__, "ChannelCommandInterface")


class ChannelCommandInterface(ABC):
    @abstractmethod
    def receive_in_python(self) -> EventState:
        """Receive a message in Python from Rust."""
        raise NotImplementedError

    @abstractmethod
    def send_in_rust(self, message_type: EventType, message_data: Any) -> None:
        """Send a message in Rust from Python."""
        raise NotImplementedError
