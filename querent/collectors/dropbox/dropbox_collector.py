from typing import AsyncGenerator

import dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector_config import DropboxConfig
from querent.collectors.collector_base import Collector
from querent.config.collector_config import CollectorBackend
from querent.collectors.collector_factory import CollectorFactory
from querent.common import common_errors
from querent.common.uri import Uri


class DropboxCollector(Collector):
    def __init__(self, config: DropboxConfig):
        self.dropbox_app_key = config.dropbox_app_key
        self.dropbox_app_secret = config.dropbox_app_secret
        self.folder_path = config.folder_path
        self.chunk_size = config.chunk_size
        self.refresh_token = config.dropbox_refresh_token

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        # access_token = self.get_access_token()
        dbx = dropbox.Dropbox(
            app_key=self.dropbox_app_key,
            app_secret=self.dropbox_app_secret,
            oauth2_refresh_token=self.refresh_token,
        )
        try:
            files_list = dbx.files_list_folder(self.folder_path).entries
            for entry in files_list:
                name = f"/{entry.name}"
                file_metadata, response = dbx.files_download(name)
                file_content_bytes = response.content
                async for chunk in self.stream_blob(file_content_bytes):
                    yield CollectedBytes(file=entry.name, data=chunk)
        except dropbox.exceptions.ApiError as e:
            print(f"Error listing files: {e}")

    async def stream_blob(self, content_bytes):
        offset = 0
        while offset < len(content_bytes):
            yield content_bytes[offset : offset + self.chunk_size]
            offset = offset + self.chunk_size


class DropBoxCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Gcs

    def resolve(self, uri: Uri, config: DropboxConfig) -> Collector:
        return DropboxCollector(config=config)