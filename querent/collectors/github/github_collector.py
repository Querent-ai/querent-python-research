import requests
from typing import AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes


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
            headers = {"Authorization": f"token {self.access_token}"}
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            contents = response.json()
            for item in contents:
                if item["type"] == "file":
                    file_url = item["download_url"]
                    try:
                        file_response = requests.get(
                            file_url, timeout=5, headers=headers
                        )
                        file_response.raise_for_status()
                        file_contents = (file_response.text).encode("utf-8")
                        yield CollectedBytes(file=item["name"], data=file_contents)
                        yield CollectedBytes(
                            file=item["name"], data=None, error=None, eof=True
                        )
                    except requests.exceptions.RequestException as file_error:
                        self.logger.error(f"Error connecting to Github: {file_error}")
                        yield CollectedBytes(
                            file=item["name"], data=None, error=file_error
                        )
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
