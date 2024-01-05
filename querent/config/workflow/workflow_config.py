from typing import Any, Optional, Dict
from pydantic import BaseModel, validator


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    name: str
    id: str
    config: Dict[str, str]
    inner_channel: Optional[Any]
    channel: Optional[Any]
    inner_channel_handler: Optional[Any]
    event_handler: Optional[Any]

    @validator("channel", pre=True, allow_reuse=True)
    def validate_channel(cls, value):
        if not hasattr(value, "receive_in_python") or not hasattr(
            value, "send_in_rust"
        ):
            raise ValueError(
                "Invalid type for channel. Must have 'receive_in_python' and 'send_in_rust' functions."
            )
        return value

    @validator("event_handler", pre=True, allow_reuse=True)
    def validate_event_handler(cls, value):
        # value must have handle_event function
        if not hasattr(value, "handle_event"):
            raise ValueError(
                "Invalid type for event_handler. Must have 'handle_event' function."
            )
