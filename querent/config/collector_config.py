from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CollectorBackend(str, Enum):
    LocalFile = "localfile"
    WebScraper = "webscraper"
    S3 = "s3"
    Gcs = "gs"


class CollectConfig(BaseModel):
    backend: CollectorBackend

    class Config:
        use_enum_values = True


class FSCollectorConfig(BaseModel):
    root_path: str
    chunk_size: int = 1024


class S3CollectConfig(BaseModel):
    bucket: str
    region: str
    access_key: str
    secret_key: str


class GcsCollectConfig(BaseModel):
    bucket: str
    region: str
    access_key: str
    secret_key: str

class WebScraperConfig(BaseModel):
    website_url: str = Field(
        ..., description="The URL of the website to scrape."
    )

class CollectConfigWrapper(BaseModel):
    backend: CollectorBackend
    config: Optional[BaseModel] = None

    @classmethod
    def from_collect_config(cls, collect_config: CollectConfig):
        if collect_config.backend == CollectorBackend.LocalFile:
            return cls(
                backend=CollectorBackend.LocalFile, config=FSCollectorConfig()
            )
        elif collect_config.backend == CollectorBackend.S3:
            return cls(backend=CollectorBackend.S3, config=S3CollectConfig())
        elif collect_config.backend == CollectorBackend.Gcs:
            return cls(backend=CollectorBackend.Gcs, config=GcsCollectConfig())
        elif collect_config.backend == CollectorBackend.WebScraper:
            return cls(
                backend=CollectorBackend.WebScraper, config=WebScraperConfig()
            )
        else:
            raise ValueError(f"Unsupported collector backend: {collect_config.backend}")