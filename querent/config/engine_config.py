from pydantic import BaseModel

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
    channel: ChannelCommandInterface
    logger: str = f"{__name__}.engine_config"
    state_queue: str = f"{__name__}.state_queue"
    workers: str = f"{__name__}.workers"
