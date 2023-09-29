from typing import Literal


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
