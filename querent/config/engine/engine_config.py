from typing import Any
from pydantic import BaseModel, Field, validator

from querent.channel.channel_interface import ChannelCommandInterface


class EngineConfig(BaseModel):
    """Engine configuration."""

    name: str
    description: str
    version: str

    num_workers: int = 1
    max_retries: int = 1
    retry_interval: float = 2.0
    message_throttle_limit: int = 1000
    message_throttle_delay: float = 0.001
    # Use Field with allow_mutation=False to specify the type
    channel: Any
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
