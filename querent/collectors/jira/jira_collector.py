import json
from typing import AsyncGenerator

from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common import common_errors
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector.collector_config import (
    CollectorBackend,
    JiraCollectorConfig,
)
from jira import JIRA

from querent.logging.logger import setup_logger


class JiraCollector(Collector):
    def __init__(self, config: JiraCollectorConfig):
        self.config = config
        self.jira = None  # Initialize to None
        self.logger = setup_logger(__name__, "JiraCollector")

    def convert_to_boolean(self, val: str):
        if type(val) == str:
            return val.lower() == "true"
        return val

    def create_jira_client(self):
        self.config.jira_verify = self.convert_to_boolean(self.config.jira_verify)
        options = {
            "server": self.config.jira_server,
            "verify": self.config.jira_verify,
        }
        basic_auth = None
        token_auth = None
        if self.config.jira_api_token:
            basic_auth = (self.config.jira_username, self.config.jira_api_token)
        elif self.config.jira_password:
            token_auth = (self.config.jira_username, self.config.jira_password)
        elif self.config.jira_keyfile and self.config.jira_certfile:
            options["client_cert"] = (
                self.config.jira_certfile,
                self.config.jira_keyfile,
            )

        return JIRA(
            self.config.jira_server,
            basic_auth=basic_auth,
            token_auth=token_auth,
            options=options,
        )

    async def connect(self):
        try:
            self.jira = self.create_jira_client()
        except Exception as e:
            self.logger.error(f"Error connecting to Jira: {e}")
            raise common_errors.ConnectionError(
                f"Failed to connect to Jira: {str(e)}"
            ) from e

    async def disconnect(self):
        self.jira = None

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            if not self.jira:
                raise common_errors.ConnectionError(
                    "Jira client not initialized. Call connect() before polling."
                )

            issues = self.jira.search_issues(
                self.config.jira_query,
                startAt=self.config.jira_start_at,
                maxResults=self.config.jira_max_results,
                fields=self.config.jira_fields,
                expand=self.config.jira_expand,
                json_result=False,
            )

            for issue in issues:
                json_issue = json.dumps(issue.raw).encode("utf-8")
                yield CollectedBytes(
                    data=json_issue, file=f"jira_issue_{issue.key}.json.jira"
                )
                yield CollectedBytes(
                    data=None, file=f"jira_issue_{issue.key}.json.jira", eof=True
                )

        except common_errors.ConnectionError as e:
            self.logger.error(f"Error polling Jira issues: {e}")
            raise  # Re-raise ConnectionError without adding additional information
        except Exception as e:
            raise common_errors.ConnectionError(
                f"Failed to poll Jira issues: {str(e)}"
            ) from e
        finally:
            await self.disconnect()


class JiraCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Jira

    def resolve(self, uri: Uri, config: JiraCollectorConfig) -> Collector:
        return JiraCollector(config)
