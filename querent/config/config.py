import os
from pydantic import BaseSettings
import yaml
from pydantic import BaseModel
from typing import Optional, List

from querent.common.types.config_keys import ConfigKey
from querent.config.workflow.workflow_config import WorkflowConfig
from querent.config.collector.collector_config import CollectorConfig
from querent.config.engine.engine_config import EngineConfig
from querent.config.resource.resource_config import ResourceConfig


class Config(BaseModel):
    version: float
    querent_id: str
    querent_name: str
    workflow: WorkflowConfig
    collectors: Optional[List[CollectorConfig]]
    engines: Optional[List[EngineConfig]]
    resource: Optional[ResourceConfig]

    def __init__(self, config_source=None, **kwargs):
        # if kwargs:
        #     raise ValueError(
        #         "Config values must be provided within a dictionary via 'config_source' parameter."
        #     )

        if config_source:
            config_data = self.load_config(config_source)
            super().__init__(**config_data)
            for config_key in ConfigKey:
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
    def get(cls, key: ConfigKey, default=None):
        """
        Get a specific configuration value by key.
        Args:
            key (ConfigKey): The key for the configuration value.
            default: The default value to return if the key is not found.
        Returns:
            The configuration value if found, otherwise the default value.
        """
        return cls.config_data.get(key, default)

    @classmethod
    def has(cls, key: ConfigKey):
        """
        Check if a specific configuration key exists.
        Args:
            key (ConfigKey): The key to check.
        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in cls.config_data
