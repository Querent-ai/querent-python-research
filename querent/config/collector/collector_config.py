from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field, validator

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
    channel: Any

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


class FSCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.LocalFile
    id: str
    root_path: str
    chunk_size: int = 1024
    channel: Any

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
    chunk_size: int = 1024


class S3CollectConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.S3
    id: str
    bucket: str
    region: str
    access_key: str
    secret_key: str
    chunk: int = 1024


class GcsCollectConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Gcs
    id: str
    bucket: str
    credentials: str
    chunk: int = 1024


class SlackCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Slack
    id: str
    cursor: Optional[str]
    include_all_metadata: int
    inclusive: int
    latest: int
    limit: int
    channel_name: str
    access_token: str


class DropboxConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.DropBox
    id: str
    dropbox_app_key: str
    dropbox_app_secret: str
    folder_path: str
    chunk_size: int
    dropbox_refresh_token: str


class GithubConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Github
    id: str
    github_username: str
    github_access_token: str
    repository: str


class WebScraperConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.WebScraper
    id: str
    website_url: str = Field(..., description="The URL of the website to scrape.")


class DriveCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.Drive
    id: str
    drive_refresh_token: str
    drive_token: str
    drive_scopes: str
    drive_client_id: str
    drive_client_secret: str
    chunk_size: int
    specific_file_type: Optional[str] = None
    folder_to_crawl: Optional[str] = None


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
