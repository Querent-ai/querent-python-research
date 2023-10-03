import os
from pydantic import BaseSettings
import yaml
from querent.common.types.config_keys import ConfigKey
from querent.lib.logger import logger


class Config(BaseSettings):
    def __init__(self, config_source=None, **kwargs):
        super().__init__(**kwargs)
        if config_source:
            self.config_data = self.load_config(config_source)
        else:
            self.config_data = {}

    @classmethod
    def load_config(cls, config_source) -> dict:
        if isinstance(config_source, str) and not os.path.exists(config_source):
            # If config source is a string, assume it's a YAML configuration string
            config_data = yaml.safe_load(config_source) or {}
        elif os.path.exists(config_source):
            # If config source is a file path, read it
            with open(config_source, "r") as file:
                config_data = yaml.safe_load(file) or {}
        else:
            raise ValueError(
                "Invalid config source. Must be a valid file path or YAML string."
            )

        # Merge environment variables and config data
        env_vars = dict(os.environ)
        config_data = {**config_data, **env_vars}

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
