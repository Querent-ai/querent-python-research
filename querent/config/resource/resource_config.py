from typing import Optional
from pydantic import BaseModel
import os

from querent.common.types.resource_config_keys import ResourceConfigKey


class ResourceConfig(BaseModel):
    id: str
    max_workers_allowed: Optional[int]
    max_workers_per_collector: Optional[int]
    max_workers_per_engine: Optional[int]
    max_workers_per_querent: Optional[int]

    def __init__(self, config_source=None, **kwargs):
        # if kwargs:
        #     raise ValueError(
        #         "Config values must be provided within a dictionary via 'config_source' parameter."
        #     )

        if config_source:
            config_data = self.load_config(config_source)
            for config_key in ResourceConfigKey:
                key = config_key.value
                if key in config_data:
                    setattr(self, key, config_data[key])

        # else:
        #     raise ValueError("Please pass config")

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
    def get(cls, key: ResourceConfigKey, default=None):
        """
        Get a specific configuration value by key.
        Args:
            key (ConfigKey): The key for the configuration value.
            default: The default value to return if the key is not found.
        Returns:
            The configuration value if found, otherwise the default value.
        """
        return cls.config_data.get(key, default)
