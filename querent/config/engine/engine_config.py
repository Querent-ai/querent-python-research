from typing import Any, Optional
from pydantic import validator
import os
from pydantic import BaseModel

from querent.common.types.engine_config_keys import EngineConfigKey


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

    def __init__(self, config_source=None, **kwargs):
        # if kwargs:
        #     raise ValueError(
        #         "Config values must be provided within a dictionary via 'config_source' parameter."
        #     )

        if config_source:
            config_data = self.load_config(config_source)
            super().__init__(**config_data)
            for config_key in EngineConfigKey:
                key = config_key.value
                if key in config_data:
                    setattr(self, key, config_data[key])

        # else:
        #     raise ValueError("Please pass config")

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

    @classmethod
    def load_config(cls, config_source) -> dict:
        if isinstance(config_source, dict):
            # If config source is a dictionary, return a dictionary
            cls.config_data = config_source
        else:
            raise ValueError("Invalid config. Must be a valid dictionary")

        env_vars = dict(os.environ)
        cls.config_data.update(env_vars)
        return cls.config_data

    @classmethod
    def get_full_config(cls):
        return cls.config_data

    @classmethod
    def get(cls, key: EngineConfigKey, default=None):
        """
        Get a specific configuration value by key.
        Args:
            key (ConfigKey): The key for the configuration value.
            default: The default value to return if the key is not found.
        Returns:
            The configuration value if found, otherwise the default value.
        """
        return cls.config_data.get(key, default)
