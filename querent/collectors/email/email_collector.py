import asyncio
import imaplib
from typing import AsyncGenerator

from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.email.imap import ImapEmail
from querent.common import common_errors
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector.collector_config import (
    CollectorBackend,
    EmailCollectorConfig,
)
from querent.logging.logger import setup_logger


class EmailCollector(Collector):
    def __init__(self, config: EmailCollectorConfig):
        self.config = config
        self.imap_email = ImapEmail()
        self.logger = setup_logger(__name__, "EmailCollector")

    async def connect(self):
        try:
            # Open an IMAP connection using the provided configuration
            self.imap_connection = self.imap_email.imap_open(self.config)
            # Other connection-related setup can be done here if needed

        except imaplib.IMAP4.error as e:
            self.logger.error(f"Error connecting to IMAP server: {e}")
            raise common_errors.ConnectionError(
                "Failed to connect to the IMAP server: {}".format(str(e))
            ) from e

    async def disconnect(self):
        try:
            if self.imap_connection:
                # Close the IMAP connection
                await asyncio.get_event_loop().run_in_executor(
                    None, self.imap_connection.logout
                )
        except Exception as e:
            self.logger.error(f"Error disconnecting from IMAP server: {e}")

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            _, messages = self.imap_connection.select(self.config.imap_folder)
            num_of_messages = int(messages[0])

            # Fetch the emails
            for i in range(num_of_messages, 0, -1):
                _, data = self.imap_connection.fetch(str(i), "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        message = response_part[1]
                        yield CollectedBytes(
                            data=message,
                            file=f"{self.config.imap_username}:{self.config.imap_folder}/{i}.email",
                        )
                yield CollectedBytes(
                    data=None,
                    file=f"{self.config.imap_username}:{self.config.imap_folder}/{i}.email",
                    eof=True,
                )
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Error fetching emails from IMAP server: {e}")
            raise common_errors.ConnectionError(
                "Failed to fetch emails from the IMAP server: {}".format(str(e))
            ) from e
        finally:
            await self.disconnect()


class EmailCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Email

    def resolve(self, uri: Uri, config: EmailCollectorConfig) -> Collector:
        return EmailCollector(config)
