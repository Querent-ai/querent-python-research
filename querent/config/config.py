import os
from pydantic import BaseSettings
import yaml
from querent.common.types.config_keys import ConfigKey


class Config(BaseSettings):
    def __init__(self, config_source=None, **kwargs):
        super().__init__(**kwargs)
        if config_source:
            self.config_data = self.load_config(config_source)
        else:
            self.config_data = {}

    @classmethod
    def load_config(cls, config_source) -> dict:
        if isinstance(config_source, dict):
            # If config source is a dictionary, return a dictionary
            config_data = config_source
        else:
            raise ValueError("Invalid config. Must be a valid dictionary")

        env_vars = dict(os.environ)
        config_data.update(env_vars)
        return config_data

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
