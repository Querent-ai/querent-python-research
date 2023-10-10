from collections import defaultdict
from typing import Any, List
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType


class EventCallbackDispatcher:
    def __init__(self):
        self.callbacks: dict[EventType, List[EventCallbackInterface]] = defaultdict(
            list
        )

    def register_callback(
        self, event_type: EventType, callback: EventCallbackInterface
    ):
        """
        Register a callback.
        Args:
            callback (EventCallbackInterface): An event callback instance.
        """
        self.callbacks[event_type].append(callback)

    async def dispatch_event(self, event_type: EventType, event_data: EventState):
        """
        Dispatch an event to all registered callbacks.
        Args:
            event_data (Any): Data associated with the event.
        """
        for callback in self.callbacks[event_type]:
            await callback.handle_event(event_type, event_data)
