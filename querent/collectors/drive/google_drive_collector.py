import asyncio
from pathlib import Path
from typing import AsyncGenerator
import io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector.collector_config import (
    CollectorBackend,
    DriveCollectorConfig,
)
from querent.common import common_errors
import requests

from querent.logging.logger import setup_logger


class DriveCollector(Collector):
    def __init__(self, config: DriveCollectorConfig):
        self.items_to_ignore = []
        self.refresh_token = config.drive_refresh_token
        self.token = config.drive_token
        self.scopes = config.drive_scopes
        self.client_id = config.drive_client_id
        self.client_secret = config.drive_client_secret
        self.creds = None
        self.drive_service = None
        self.chunk_size = 1024
        if config.chunk_size and config.chunk_size.isdigit():
            self.chunk_size = int(config.chunk_size)
        self.specific_file_type = config.specific_file_type
        self.folder_to_crawl = config.folder_to_crawl
        self.logger = setup_logger(__name__, "DriveCollector")
        try:
            with open("./.gitignore", "r", encoding="utf-8") as gitignore_file:
                self.items_to_ignore = set(
                    gitignore_file.read().replace("/", "").replace("*", "").splitlines()
                )
        except Exception as e:
            self.items_to_ignore = []

    async def connect(self):
        try:
            self.creds = Credentials(
                token=self.token,
                refresh_token=self.refresh_token,
                scopes=[self.scopes],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

            self.drive_service = build("drive", "v3", credentials=self.creds)
        except Exception as e:
            self.logger.error(f"Error connecting to Google Drive: {e}")
            raise common_errors.ConnectionError(
                f"Failed to connect to Google Drive: {str(e)}"
            ) from e

    async def disconnect(self):
        try:
            if self.drive_service:
                # Close the Google Drive connection
                self.drive_service.close()
        except Exception as e:
            self.logger.error(f"Error disconnecting from Google Drive: {e}")

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            query = ""
            if self.specific_file_type:
                query = f"mimeType='{self.specific_file_type}'"
            if self.folder_to_crawl:
                if self.specific_file_type:
                    query += " and "
                query = f"'{self.folder_to_crawl}' in parents"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get("files", [])
            if not files:
                self.logger.info("No files found in Google Drive")
            for file in files:
                async for chunk in self.read_chunks(file["id"]):
                    yield CollectedBytes(data=chunk, file=file["name"])
                yield CollectedBytes(data=None, file=file["name"], eof=True)
        except Exception as e:
            raise common_errors.PollingError(
                f"Failed to poll Google Drive: {str(e)}"
            ) from e
        finally:
            await self.disconnect()

    async def read_chunks(self, file_id):
        file_metadata = (
            self.drive_service.files().get(fileId=file_id, fields="mimeType").execute()
        )
        mime_type = file_metadata.get("mimeType")

        if mime_type.startswith("application/vnd.google-apps."):
            if mime_type == "application/vnd.google-apps.document":
                export_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif mime_type == "application/vnd.google-apps.folder":
                return
            else:
                raise common_errors.PollingError(
                    f"Unsupported Google Docs file type: {mime_type}"
                )

            request = self.drive_service.files().export_media(
                fileId=file_id, mimeType=export_mime_type
            )
        else:
            # It's a binary file, we can proceed with normal download
            request = self.drive_service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request, chunksize=self.chunk_size)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                yield fh.getvalue()
                fh.seek(0)
                fh.truncate(0)


class DriveCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Drive

    def resolve(self, uri: Uri, config: DriveCollectorConfig) -> Collector:
        return DriveCollector(config)
