from typing import Optional
from querent.collectors.azure.azure_collector import AzureCollectorFactory
from querent.collectors.email.email_collector import EmailCollectorFactory
from querent.collectors.gcs.gcs_collector import GCSCollectorFactory
from querent.collectors.aws.aws_collector import AWSCollectorFactory
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.collectors.jira.jira_collector import JiraCollectorFactory
from querent.collectors.webscaper.web_scraper_collector import WebScraperFactory
from querent.collectors.slack.slack_collector import SlackCollectorFactory
from querent.collectors.dropbox.dropbox_collector import DropBoxCollectorFactory
from querent.collectors.github.github_collector import GithubCollectorFactory
from querent.collectors.drive.google_drive_collector import DriveCollectorFactory
from querent.config.collector.collector_config import CollectorConfig, CollectorBackend
from querent.collectors.collector_base import Collector
from querent.collectors.collector_errors import (
    CollectorResolverError,
    CollectorErrorKind,
)
from querent.common.uri import Protocol, Uri


class CollectorResolver:
    def __init__(self):
        self.collector_factories = {
            CollectorBackend.LocalFile: FSCollectorFactory(),
            CollectorBackend.S3: AWSCollectorFactory(),
            CollectorBackend.WebScraper: WebScraperFactory(),
            CollectorBackend.Gcs: GCSCollectorFactory(),
            CollectorBackend.AzureBlobStorage: AzureCollectorFactory(),
            CollectorBackend.Slack: SlackCollectorFactory(),
            CollectorBackend.DropBox: DropBoxCollectorFactory(),
            CollectorBackend.Github: GithubCollectorFactory(),
            CollectorBackend.Drive: DriveCollectorFactory(),
            CollectorBackend.Email: EmailCollectorFactory(),
            CollectorBackend.Jira: JiraCollectorFactory(),
            # Add other collector factories as needed
        }

    def resolve(self, uri: Uri, config: CollectorConfig) -> Optional[Collector]:
        backend = config.backend
        backendFromUri = self._determine_backend(uri.protocol)

        if backend != backendFromUri:
            raise CollectorResolverError(
                CollectorErrorKind.NotSupported,
                "Backend in the config does not match the backend the protocol",
            )

        if backend in self.collector_factories:
            factory = self.collector_factories[backend]
            return factory.resolve(uri, config)
        else:
            raise CollectorResolverError(
                CollectorErrorKind.NotSupported, "Unsupported backend"
            )

    def _determine_backend(self, protocol: Protocol) -> CollectorBackend:
        if protocol.is_file_storage():
            return CollectorBackend.LocalFile
        elif protocol.is_s3():
            return CollectorBackend.S3
        elif protocol.is_webscraper():
            return CollectorBackend.WebScraper
        elif protocol.is_gcs():
            return CollectorBackend.Gcs
        elif protocol.is_webscraper():
            return CollectorBackend.WebScraper
        elif protocol.is_azure_blob_storage():
            return CollectorBackend.AzureBlobStorage
        elif protocol.is_slack():
            return CollectorBackend.Slack
        elif protocol.is_dropbox():
            return CollectorBackend.DropBox
        elif protocol.is_github():
            return CollectorBackend.Github
        elif protocol.is_drive():
            return CollectorBackend.Drive
        elif protocol.is_email():
            return CollectorBackend.Email
        elif protocol.is_jira():
            return CollectorBackend.Jira
        else:
            raise CollectorResolverError(
                CollectorErrorKind.NotSupported, "Unknown backend"
            )
