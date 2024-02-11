from typing import AsyncGenerator

import dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import DropboxConfig
from querent.collectors.collector_base import Collector
from querent.config.collector.collector_config import CollectorBackend
from querent.collectors.collector_factory import CollectorFactory
from querent.common import common_errors
from querent.common.uri import Uri
from querent.logging.logger import setup_logger


class DropboxCollector(Collector):
    def __init__(self, config: DropboxConfig):
        self.dropbox_app_key = config.dropbox_app_key
        self.dropbox_app_secret = config.dropbox_app_secret
        self.folder_path = config.folder_path
        self.chunk_size = 1024
        if config.chunk_size and config.chunk_size.isdigit():
            self.chunk_size = int(config.chunk_size)
        self.refresh_token = config.dropbox_refresh_token
        self.logger = setup_logger(__name__, "DropboxCollector")
        self.dbx = None

    async def connect(self):
        try:
            if not self.dbx:
                # If the Dropbox SDK already has a valid access token, it won't refresh unnecessarily
                self.dbx = dropbox.Dropbox(
                    app_key=self.dropbox_app_key,
                    app_secret=self.dropbox_app_secret,
                    oauth2_refresh_token=self.refresh_token,
                )
        except dropbox.exceptions.AuthError as auth_error:
            self.logger.error(
                f"Authentication error during Dropbox connection: {auth_error}"
            )
            raise common_errors.ConnectionError(
                "Failed to authenticate with Dropbox."
            ) from auth_error
        except Exception as e:
            self.logger.error(f"Error connecting to Dropbox: {e}")
            raise common_errors.ConnectionError(
                "Failed to connect to Dropbox: {}".format(str(e))
            ) from e

    async def disconnect(self):
        try:
            if self.dbx:
                self.dbx.close()
        except Exception as e:
            self.logger.error(f"Error disconnecting from Dropbox: {e}")

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            files_list = self.dbx.files_list_folder(self.folder_path).entries
            for entry in files_list:
                name = f"/{entry.name}"
                try:
                    file_metadata, response = self.dbx.files_download(name)
                except dropbox.exceptions.AuthError as auth_error:
                    self.logger.warning(
                        f"Token expired. Refreshing access token and retrying."
                    )
                    self.connect()  # Attempt to refresh access token
                    file_metadata, response = self.dbx.files_download(name)

                file_content_bytes = response.content
                async for chunk in self.stream_blob(file_content_bytes):
                    yield CollectedBytes(file=entry.name, data=chunk)
                yield CollectedBytes(file=entry.name, data=None, eof=True)
        except dropbox.exceptions.ApiError as e:
            self.logger.error(f"Error polling Dropbox: {e}")
            raise common_errors.PollingError(
                "Failed to poll Dropbox: {}".format(str(e))
            ) from e
        finally:
            await self.disconnect()

    async def stream_blob(self, content_bytes):
        offset = 0
        while offset < len(content_bytes):
            yield content_bytes[offset : offset + self.chunk_size]
            offset = offset + self.chunk_size


class DropBoxCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.DropBox

    def resolve(self, uri: Uri, config: DropboxConfig) -> Collector:
        return DropboxCollector(config=config)
