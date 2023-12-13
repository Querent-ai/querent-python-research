from typing import Any


class MessageType:
    """Custom type for messages sent to and received from rust
    Attribute :
        START - start the given entity
        STOP - stop the given entity
        RESTART - restart the given entity
    """

    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "resume"
    STATUS = "status"
    METRICS = "metrics"


class MessageState:
    """
    Custom type for base class implementors to listen or send messages from and to rust.
    MessageState has a message_type, a timestamp, and a payload.

    Attributes:
        message_type (MessageType): The type of message.
        timestamp (float): The timestamp of the message.
        payload (Any): The payload of the message.
    """

    def __init__(self, message_type: MessageType, timestamp: float, payload: Any):
        self.message_type = message_type
        self.timestamp = timestamp
        self.payload = payload
