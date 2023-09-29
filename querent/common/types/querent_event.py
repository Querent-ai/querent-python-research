from typing import Any, Literal


class EventType:
    """
    Custom type for representing event types in the querent system.

    Attributes:
        TOKEN_PROCESSED (Literal["token_processed"]): Event type for token processing completion.
        CHAT_COMPLETED (Literal["chat_completed"]): Event type for chat completion.
    """

    _STATE_TRANSITION = "state_transition"
    TOKEN_PROCESSED = "token_processed"
    CHAT_COMPLETED = "chat_completed"


class EventState:
    """
    Custom type for base class implementors to tie into the event system.
    EventState has a event_type, a timestamp, and a payload.

    Attributes:
        event_type (EventType): The type of event.
        timestamp (float): The timestamp of the event.
        payload (Any): The payload of the event.
    """

    def __init__(self, event_type: EventType, timestamp: float, payload: Any):
        self.event_type = event_type
        self.timestamp = timestamp
        self.payload = payload
