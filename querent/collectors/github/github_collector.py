import requests
from typing import AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
import aiohttp


from querent.config.collector.collector_config import GithubConfig, CollectorBackend
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.uri import Uri
from querent.logging.logger import setup_logger


class GithubCollector(Collector):
    """Class for github collector"""

    def __init__(self, config: GithubConfig):
        self.user_name = config.github_username
        self.repository = config.repository
        self.access_token = config.github_access_token
        self.logger = setup_logger(__name__, "GithubCollector")

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        api_url = (
            f"https://api.github.com/repos/{self.user_name}/{self.repository}/contents/"
        )

        async for item in self.fetch_files_in_folder(api_url=api_url):
            yield item

    async def fetch_files_in_folder(self, api_url):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"token {self.access_token}"}
                async with session.get(api_url, headers=headers) as response:
                    response.raise_for_status()
                    contents = await response.json()
                    for item in contents:
                        if item["type"] == "file":
                            file_url = item["download_url"]
                            async with session.get(file_url, headers=headers) as file_response:
                                file_response.raise_for_status()
                                file_contents = await file_response.read()
                                # Assume process_data() is correctly implemented for your file type
                                yield CollectedBytes(file=item["name"], data=file_contents, doc_source=f"github://{self.repository}")

                            yield CollectedBytes(file = item["name"], data = None, eof = True, doc_source=f"github://{self.repository}")
                        elif item["type"] == "dir":
                            # Recursively fetch files in subfolders
                            async for sub_item in self.fetch_files_in_folder(item["url"]):
                                yield sub_item

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error connecting to Github: {e}")


class GithubCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.Slack

    def resolve(self, uri: Uri, config: GithubConfig) -> Collector:
        return GithubCollector(config)
