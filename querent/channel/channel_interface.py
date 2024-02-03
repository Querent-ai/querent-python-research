from abc import ABC, abstractmethod
from typing import Any

from querent.common.types.querent_event import EventState, EventType
from querent.common.types.ingested_tokens import IngestedTokens
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
    
    @abstractmethod
    def receive_tokens_in_python(self) -> IngestedTokens:
        """Receive tokens in Python from Rust."""
        raise NotImplementedError
    
    @abstractmethod
    def send_tokens_in_rust(self, tokens: IngestedTokens) -> None:
        """Send tokens in Rust from Python."""
        raise NotImplementedError
