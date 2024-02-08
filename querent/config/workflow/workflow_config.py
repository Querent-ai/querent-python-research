from typing import Any, Optional, Dict
from pydantic import BaseModel, validator
from querent.common.types.workflow_config_keys import WorkflowConfigKey
import os


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    name: str
    id: str
    config: Dict[str, str]
    inner_channel: Optional[Any]
    channel: Optional[Any]
    inner_channel_handler: Optional[Any]
    event_handler: Optional[Any]
    inner_tokens_feader: Optional[Any]
    tokens_feader: Optional[Any]

    def __init__(self, config_source=None, **kwargs):
        # if kwargs:
        #     raise ValueError(
        #         "Config values must be provided within a dictionary via 'config_source' parameter."
        #     )

        if config_source:
            config_data = self.load_config(config_source)
            super().__init__(**config_data) 
            for config_key in WorkflowConfigKey:
                key = config_key.value
                if key in config_data:
                    setattr(self, key, config_data[key])

        # else:
        #     raise ValueError("Please pass config")

    @validator("channel", pre=True, allow_reuse=True)
    def validate_channel(cls, value):
        if not hasattr(value, "receive_in_python") or not hasattr(
            value, "send_in_rust"
        ):
            raise ValueError(
                "Invalid type for channel. Must have 'receive_in_python' and 'send_in_rust' functions."
            )
        return value
    
    @validator("tokens_feader", pre=True, allow_reuse=True)
    def validate_tokens_feader(cls, value):
        if not hasattr(value, "receive_tokens_in_python") or not hasattr(
            value, "send_tokens_in_rust"
        ):
            raise ValueError(
                "Invalid type for tokens_feader. Must have 'receive_tokens_in_python' and 'send_tokens_in_rust' functions."
            )
        return value

    @validator("event_handler", pre=True, allow_reuse=True)
    def validate_event_handler(cls, value):
        # value must have handle_event function
        if not hasattr(value, "handle_event"):
            raise ValueError(
                "Invalid type for event_handler. Must have 'handle_event' function."
            )

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
    def get(cls, key: WorkflowConfigKey, default=None):
        """
        Get a specific configuration value by key.
        Args:
            key (ConfigKey): The key for the configuration value.
            default: The default value to return if the key is not found.
        Returns:
            The configuration value if found, otherwise the default value.
        """
        return cls.config_data.get(key, default)
