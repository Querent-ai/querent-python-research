from typing import Any, Optional
from pydantic import BaseModel, Field, validator

from querent.channel.channel_interface import ChannelCommandInterface


class EngineConfig(BaseModel):
    """Engine configuration."""

    id: str
    name: str

    num_workers: Optional[int] = 1
    max_retries: Optional[int] = 1
    retry_interval: Optional[int] = 2
    message_throttle_limit: Optional[int] = 1000
    message_throttle_delay: Optional[int] = 1
    # Use Field with allow_mutation=False to specify the type
    inner_channel: Optional[Any]
    channel: Optional[Any]
    logger: str = f"{__name__}.engine_config"
    state_queue: str = f"{__name__}.state_queue"
    workers: str = f"{__name__}.workers"

    # Custom validator for ChannelCommandInterface
    @validator("channel", pre=True, allow_reuse=True)
    def validate_channel(cls, value):
        if not hasattr(value, "receive_in_python") or not hasattr(
            value, "send_in_rust"
        ):
            raise ValueError(
                "Invalid type for channel. Must have 'receive_in_python' and 'send_in_rust' functions."
            )
        return value
