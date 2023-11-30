from abc import ABC, abstractmethod
from typing import Any

from querent.common.types.querent_event import EventState, EventType
from querent.logging.logger import setup_logger

logger = setup_logger(__name__, "EventCallbackInterface")


class EventCallbackInterface(ABC):
    @abstractmethod
    def handle_event(self, event_type: EventType, event_data: EventState):
        """
        Handle an event.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            event_data (EventState): Data associated with the event.

        """

        raise NotImplementedError
