from enum import Enum
from typing import Any, List, Optional, Union, Dict
from pydantic import BaseModel, Field, validator
import os
from querent.common.types.collector_config_keys import CollectorConfigKey

from querent.channel.channel_interface import ChannelCommandInterface


class CollectorBackend(str, Enum):
    LocalFile = "localfile"
    WebScraper = "webscraper"
    S3 = "s3"
    Gcs = "gs"
    AzureBlobStorage = "azure"
    Slack = "slack"
    DropBox = "dropbox"
    Github = "github"
    Drive = "drive"
    Email = "email"
    Jira = "jira"

class CollectorConfig(BaseModel):
    backend: CollectorBackend
    # Use Field with allow_mutation=False to specify the type
    channel: Optional[Any]
    id: str
    name: str
    uri: Optional[Any]
    config: Dict[str, str]
    inner_channel: Optional[Any]
    config_source: Optional[Any]

    def __init__(self, config_source=None, **kwargs):
         
         if config_source:
            config_data = self.load_config(config_source)

            if "uri" not in config_data or not config_data["uri"]:
                config_data["uri"] = uri_backend_mapping[config_data.get("backend")]

            super().__init__(**config_data)
            self.config_source = config_source
            for config_key in CollectorConfigKey:
                key = config_key.value
                if key in config_data:
                    setattr(self, key, config_data[key])

        # else:
        #     raise ValueError("Please pass config")
    
    def resolve(self):
        if self.config_source and isinstance(self.config_source, dict):
            backend_type = self.config_source.get('backend')
            if backend_type in colectorconfig_factories:
                collector_class = colectorconfig_factories[backend_type]
                return collector_class(self.config_source)
            else:
                raise ValueError(f"Unsupported backend type: {backend_type}")
        else:
            raise ValueError("Invalid or missing config source")

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
    def get(cls, key: CollectorConfigKey, default=None):
        """
        Get a specific configuration value by key.
        Args:
            key (ConfigKey): The key for the configuration value.
            default: The default value to return if the key is not found.
        Returns:
            The configuration value if found, otherwise the default value.
        """
        return cls.config_data.get(key, default)


class FSCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.LocalFile
    id: str
    root_path: str
    chunk_size: str = "1024"
    channel: Any

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    # Custom validator for ChannelCommandInterface
    @validator("channel", pre=True, allow_reuse=True)
    def validate_channel(cls, value):
        if (
            value is None
            or not hasattr(value, "receive_in_python")
            or not hasattr(value, "send_in_rust")
        ):
            raise ValueError(
                "Invalid type for channel. Must have 'receive_in_python' and 'send_in_rust' functions."
            )
        return value


class AzureCollectConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.AzureBlobStorage
    id: str
    connection_string: str
    account_url: str
    credentials: str
    container: str
    prefix: str
    chunk_size: str = "1024"

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class S3CollectConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.S3
    id: str
    bucket: str
    region: str
    access_key: str
    secret_key: str
    chunk: str = "1024"

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class GcsCollectConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Gcs
    id: str
    bucket: str
    credentials: str
    chunk: str = "1024"

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class SlackCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Slack
    id: str
    cursor: Optional[str]
    include_all_metadata: Optional[bool]
    inclusive: Optional[bool]
    latest: Optional[str]
    limit: Optional[int]
    channel_name: str
    access_token: str

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class DropboxConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.DropBox
    id: str
    dropbox_app_key: str
    dropbox_app_secret: str
    folder_path: str
    chunk_size: str = "1024"
    dropbox_refresh_token: str

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class GithubConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Github
    id: str
    github_username: str
    github_access_token: str
    repository: str

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class WebScraperConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.WebScraper
    id: str
    website_url: str = Field(..., description="The URL of the website to scrape.")

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class DriveCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Drive
    id: str
    drive_refresh_token: str
    drive_token: str
    drive_scopes: str
    drive_client_id: str
    drive_client_secret: str
    chunk_size: str = "1024"
    specific_file_type: Optional[str] = None
    folder_to_crawl: Optional[str] = None

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class EmailCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Email
    id: str
    imap_server: str
    imap_port: int
    imap_username: str
    imap_password: str
    imap_folder: str
    imap_keyfile: Optional[str] = None
    imap_certfile: Optional[str] = None

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class JiraCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Jira
    id: str
    jira_server: str
    jira_username: str
    jira_project: str
    jira_query: str
    jira_password: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_start_at: Optional[int] = 0
    jira_max_results: Optional[int] = 50
    jira_fields: Optional[Union[str, List[str]]] = ("*all",)
    jira_expand: Optional[str] = None
    jira_keyfile: Optional[str] = None
    jira_certfile: Optional[str] = None
    jira_verify: Optional[bool] = True

    def __init__(self, config_source=None, **kwargs):
        if config_source and "config" in config_source:
            extended_config = config_source["config"]
            config_source.update(extended_config) 
            super().__init__(config_source=config_source, **kwargs)
            for key, value in extended_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)


colectorconfig_factories = {
        CollectorBackend.LocalFile: FSCollectorConfig,
        CollectorBackend.Drive: DriveCollectorConfig,
        CollectorBackend.AzureBlobStorage: AzureCollectConfig,
        CollectorBackend.DropBox: DropboxConfig,
        CollectorBackend.Email: EmailCollectorConfig,
        CollectorBackend.Gcs: GcsCollectConfig,
        CollectorBackend.Github: GithubConfig,
        CollectorBackend.Jira: JiraCollectorConfig,
        CollectorBackend.S3: S3CollectConfig,
        CollectorBackend.WebScraper: WebScraperConfig,
        CollectorBackend.Slack: SlackCollectorConfig,
    }

uri_backend_mapping = {
    "localfile": "file://",
    "webscraper": "https://",
    "s3": "s3://",
    "gs": "gs://",
    "azure": "azure://",
    "slack": "slack://",
    "dropbox": "dropbox://",
    "github": "github://",
    "drive": "drive://",
    "email": "email://",
    "jira": "jira://",
}