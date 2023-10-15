from abc import ABC, abstractmethod
from typing import Any

from querent.common.types.querent_event import EventState, EventType
from querent.logging.logger import setup_logger

logger = setup_logger(__name__, "EventCallbackInterface")


class EventCallbackInterface(ABC):
    @property
    async def adapter(self) -> Any:
        """
        Adapter to convert event state to a respective type.
        """
        logger.warn("Adapter not implemented")
        logger.warn("Returning None")
        return None

    @abstractmethod
    async def handle_event(self, event_type: EventType, event_data: EventState):
        """
        Handle an event.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            event_data (EventState): Data associated with the event.

        """

        if self.adapter is None:
            logger.error("Adapter not implemented")
            raise NotImplementedError

        raise NotImplementedError
