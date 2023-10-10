from abc import ABC, abstractmethod
from typing import Any

from querent.common.types.querent_event import EventState, EventType


class EventCallbackInterface(ABC):
    @abstractmethod
    async def handle_event(self, event_type: EventType, event_data: EventState):
        """
        Handle an event.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            event_data (EventState): Data associated with the event.
        """
        raise NotImplementedError
