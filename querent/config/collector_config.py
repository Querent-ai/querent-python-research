from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


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


class CollectorConfig(BaseModel):
    backend: CollectorBackend


class FSCollectorConfig(CollectorConfig):
    backend: CollectorBackend = CollectorBackend.LocalFile
    id: str
    root_path: str
    chunk_size: int = 1024


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
