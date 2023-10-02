from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import AsyncGenerator
import os

from querent.collectors.collector_factory import CollectorFactory
from querent.config.collector_config import CollectorBackend, SlackCollectorConfig
from querent.collectors.collector_base import Collector
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.common import common_errors


class SlackCollector(Collector):
    def __init__(self, config: SlackCollectorConfig):
        self.cursor = config.cursor
        self.include_all_metadata = (
            config.include_all_metadata if config.include_all_metadata else 0
        )
        self.inclusive = config.inclusive if config.inclusive else 0
        self.latest = config.latest if config.latest else 0
        self.limit = config.limit if config.limit else 100
        self.channel = config.channel_name
        self.access_token = config.access_token

        self.client = WebClient()

    async def connect(self):
        pass

    async def disconnect(self):
        # Add your cleanup logic here if needed
        pass

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            self.client = WebClient(token=self.access_token)
            response = self.client.conversations_join(channel=self.channel)
            if not response["ok"]:
                print(
                    f"Failed to join channel: {self.channel}, Error: {response['error']}"
                )
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
                        yield CollectedBytes(
                            file=f"slack://{self.channel}",
                            data=bytes(message["text"] + "\n\n", "utf-8"),
                        )

                    if not response["has_more"]:
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


class SlackCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.Slack

    def resolve(self, uri: Uri, config: SlackCollectorConfig) -> Collector:
        return SlackCollector(config)
