from typing import Any
from pydantic import BaseModel, validator


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    name: str
    id: str
    channel: Any
    event_handler: Any

    @validator("channel", pre=True, allow_reuse=True)
    def validate_channel(cls, value):
        # Perform any additional validation logic here
        return value

    @validator("event_handler", pre=True, allow_reuse=True)
    def validate_event_handler(cls, value):
        # Perform any additional validation logic here
        return value
