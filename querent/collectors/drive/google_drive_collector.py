import asyncio
import re
from pathlib import Path
from typing import AsyncGenerator
import aiofiles
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, DriveCollectorConfig
from querent.common import common_errors


# AIzaSyCjrL7jYQFJuxhmaYRCdgqADQXj3ugPIAs
class DriveCollector(Collector):
    def __init__(self, config: DriveCollectorConfig):
        self.items_to_ignore = []
        self.chunk_size = config.chunk_size
        self.refresh_token = config.drive_refresh_token
        self.token = config.drive_token
        self.scopes = config.drive_scopes
        self.creds = None
        self.drive_service = None
        self.chunk_size = config.chunk_size
        try:
            with open("./.gitignore", "r", encoding="utf-8") as gitignore_file:
                self.items_to_ignore = set(
                    gitignore_file.read().replace("/", "").replace("*", "").splitlines()
                )
        except Exception as e:
            self.items_to_ignore = []

    async def connect(self):
        self.creds = Credentials(
            token=self.token, refresh_token=self.refresh_token, scopes=self.scopes
        )
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())

        self.drive_service = build("drive", "v3", credentials=self.creds)

    async def disconnect(self):
        self.creds = None

    # collect those files

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        results = self.drive_service.files().list().execute()
        files = results.get("files", [])
        if not files:
            print("No files found.")
        for file in files:
            yield self.read_chunks(file["id"])

    async def read_chunks(self, file_id):
        request = self.drive_service.files().get_media(fileId=file_id)

        downloader = request.get(downloader_options={"chunk_size": self.chunk_size})
        for chunk in downloader:
            if chunk:
                yield chunk

    async def walk_files(self, root: Path) -> AsyncGenerator[Path, None]:
        for item in root.iterdir():
            item_split = set(str(item).split("/"))
            item_split.remove("")
            if item_split.intersection(self.items_to_ignore):
                print(item_split, "\n\n", self.items_to_ignore)
                continue
            if item.is_file():
                yield item
            elif item.is_dir():
                async for file_path in self.walk_files(item):
                    yield file_path


class DriveCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.LocalFile

    def resolve(self, uri: Uri, config: DriveCollectorConfig) -> Collector:
        return DriveCollector(config)
