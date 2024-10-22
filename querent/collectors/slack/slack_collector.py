import base64
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import AsyncGenerator
import os

from querent.collectors.collector_factory import CollectorFactory
from querent.config.collector.collector_config import CollectorBackend, SlackCollectorConfig
from querent.collectors.collector_base import Collector
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.common import common_errors
from querent.logging.logger import setup_logger


class SlackCollector(Collector):
    def __init__(self, config: SlackCollectorConfig):
        self.cursor = config.cursor
        self.include_all_metadata = (
            self.convert_to_boolean(config.include_all_metadata) if config.include_all_metadata else 0
        )
        self.inclusive = self.convert_to_boolean(config.inclusive) if config.inclusive else False
        self.latest = config.latest if config.latest else 0
        self.limit = 100
        if config.limit and type(config.limit) == str and config.limit.isdigit():
            self.limit = int(config.limit)
        self.channel = config.channel_name
        self.access_token = config.access_token

        self.client = WebClient()
        self.logger = setup_logger(__name__, "SlackCollector")

    async def connect(self):
        pass

    async def disconnect(self):
        # Add your cleanup logic here if needed
        pass

    def convert_to_boolean(self, val: str):
        if type(val) == str:
            return val.lower() == "true"
        return val

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            self.client = WebClient(token=self.access_token)
            response = self.client.conversations_join(channel=self.channel)
            if not response["ok"]:
                self.logger.error(f"Error connecting to Slack: {response['error']}")
        except SlackApiError as exc:
            raise common_errors.SlackApiError(
                f"Slack API Error: {exc.response['error']}"
            ) from exc
        while True:
            try:
                # Get list of all the conversation history
                response = self.client.conversations_history(
                    channel=self.channel, cursor=self.cursor, limit=self.limit
                )
                if response["ok"]:
                    messages = response["messages"]
                    for message in messages:
                        if 'files' in message:  # Check if the message contains files
                            for file in message['files']:
                                file_url = file['url_private']
                                # Assuming `self.download_file` is a method to download files using the URL
                                file_bytes = await self.fetch_file_bytes(file_url)
                                yield CollectedBytes(
                                    file=f"slack://{self.channel}/{file['name']}",
                                    data=file_bytes,
                                    doc_source=f"slack://{self.channel}"
                                )
                        else:
                            yield CollectedBytes(
                                file=f"slack://{self.channel}.slack",
                                data=bytes(message["text"] + "\n\n", "utf-8"),
                                doc_source = f"slack://{self.channel}"
                            )

                    if not response["has_more"]:
                        yield CollectedBytes(
                            file=f"slack://{self.channel}.slack",
                            data=None,
                            error=None,
                            eof=True,
                            doc_source = f"slack://{self.channel}"
                        )
                        break
                else:
                    raise common_errors.SlackApiError(
                        f"Slack API Error: {response['error']}"
                    )

                self.cursor = response["response_metadata"]["next_cursor"]

            except SlackApiError as exc:
                raise common_errors.SlackApiError(
                    f"Slack API Error: {exc.response['error']}"
                ) from exc
    
    async def fetch_file_bytes(self, url):
        """Fetch image bytes directly without downloading the image to disk."""
        headers = {'Authorization': f'Bearer {self.client.token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch image, status code: {response.status_code}")
            return None


class SlackCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.Slack

    def resolve(self, uri: Uri, config: SlackCollectorConfig) -> Collector:
        return SlackCollector(config)
