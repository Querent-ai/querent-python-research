import asyncio
from pathlib import Path
from typing import AsyncGenerator
import io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, DriveCollectorConfig
from querent.common import common_errors
import requests


class DriveCollector(Collector):
    def __init__(self, config: DriveCollectorConfig):
        self.items_to_ignore = []
        self.chunk_size = config.chunk_size
        self.refresh_token = config.drive_refresh_token
        self.token = config.drive_token
        self.scopes = config.drive_scopes
        self.client_id = config.drive_client_id
        self.client_secret = config.drive_client_secret
        self.creds = None
        self.drive_service = None
        self.chunk_size = config.chunk_size
        self.specific_file_type = config.specific_file_type
        self.folder_to_crawl = config.folder_to_crawl
        try:
            with open("./.gitignore", "r", encoding="utf-8") as gitignore_file:
                self.items_to_ignore = set(
                    gitignore_file.read().replace("/", "").replace("*", "").splitlines()
                )
        except Exception as e:
            self.items_to_ignore = []

    async def get_access_token(self):
        params = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        authorization_url = "https://oauth2.googleapis.com/token"

        r = requests.post(authorization_url, data=params)
        if r.ok:
            return r.json()["access_token"]
        else:
            return None

    async def connect(self):
        try:
            access_token = await self.get_access_token()
            self.creds = Credentials(
                token=access_token,
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
            raise common_errors.ConnectionError(
                "Failed to connect to Google Drive: {}".format(str(e))
            ) from e

    async def disconnect(self):
        try:
            if self.drive_service:
                # Close the Google Drive connection
                self.drive_service.close()
        except Exception as e:
            raise common_errors.ConnectionError(
                f"Failed to disconnect from Google Drive: {str(e)}"
            ) from e

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
                print("No files found.")
            for file in files:
                async for chunk in self.read_chunks(file["id"]):
                    yield CollectedBytes(data=chunk, file=file["name"])
        except Exception as e:
            raise common_errors.CollectorPollingError(
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
                raise common_errors.CollectorPollingError(
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
    def backend(self) -> CollectorBackend:
        return CollectorBackend.LocalFile

    def resolve(self, uri: Uri, config: DriveCollectorConfig) -> Collector:
        return DriveCollector(config)
