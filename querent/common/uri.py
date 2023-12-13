import re
import enum
from pathlib import Path
from typing import Optional, Union


class Protocol(enum.Enum):
    Azure = "azure"
    File = "file"
    Gcs = "gs"
    PostgreSQL = "postgresql"
    Ram = "ram"
    S3 = "s3"
    Webscraper = "https"
    Slack = "slack"
    DropBox = "dropbox"
    Github = "github"
    Drive = "drive"
    Email = "email"
    Jira = "jira"

    def is_azure(self) -> bool:
        return self == Protocol.Azure

    def is_file(self) -> bool:
        return self == Protocol.File

    def is_gcs(self) -> bool:
        return self == Protocol.Gcs

    def is_postgresql(self) -> bool:
        return self == Protocol.PostgreSQL

    def is_ram(self) -> bool:
        return self == Protocol.Ram

    def is_s3(self) -> bool:
        return self == Protocol.S3

    def is_file_storage(self) -> bool:
        return self in {Protocol.File, Protocol.Ram}

    def is_object_storage(self) -> bool:
        return self in {Protocol.Azure, Protocol.S3}

    def is_database(self) -> bool:
        return self == Protocol.PostgreSQL

    def is_webscraper(self) -> bool:
        return self == Protocol.Webscraper

    def is_azure_blob_storage(self) -> bool:
        return self == Protocol.Azure

    def is_slack(self) -> bool:
        return self == Protocol.Slack

    def is_dropbox(self) -> bool:
        return self == Protocol.DropBox

    def is_github(self) -> bool:
        return self == Protocol.Github

    def is_drive(self) -> bool:
        return self == Protocol.Drive

    def is_email(self) -> bool:
        return self == Protocol.Email

    def is_jira(self) -> bool:
        return self == Protocol.Jira


class Uri:
    PROTOCOL_SEPARATOR = "://"
    DATABASE_URI_PATTERN = re.compile(
        r"(?P<before>^.*://.*)(?P<password>:.*@)(?P<after>.*)"
    )

    def __init__(self, uri: str):
        self.uri = uri
        self.protocol_idx = uri.find(self.PROTOCOL_SEPARATOR)
        self.protocol = Protocol(uri[: self.protocol_idx])

    @classmethod
    def from_well_formed(cls, uri: str) -> "Uri":
        protocol_idx = uri.find(cls.PROTOCOL_SEPARATOR)
        protocol_str = uri[:protocol_idx]
        Protocol(protocol_str)
        return cls(uri)

    @property
    def extension(self) -> Optional[str]:
        return Path(self.uri).suffix.lstrip(".")

    @property
    def path(self) -> str:
        return self.uri[self.protocol_idx + len(self.PROTOCOL_SEPARATOR) :]

    def as_str(self) -> str:
        return self.uri

    def is_redacted(self) -> bool:
        return self.protocol.is_database()

    def as_redacted_str(self) -> str:
        if self.protocol.is_database():
            return self.DATABASE_URI_PATTERN.sub(
                r"\g<before>:***redacted***@\g<after>", self.uri
            )
        return self.uri

    def __str__(self) -> str:
        return self.as_redacted_str()

    def __eq__(self, other: Union[str, "Uri"]) -> bool:
        if isinstance(other, Uri):
            return self.uri == other.uri
        return self.uri == other

    def __hash__(self) -> int:
        return hash(self.uri)


# Usage example
if __name__ == "__main__":
    uri_str = "s3://bucket/key"
    uri = Uri(uri_str)
    print(f"Original URI: {uri}")
    print(f"Extension: {uri.extension}")
    print(f"Protocol: {uri.protocol}")
    print(f"Is Azure: {uri.protocol.is_azure()}")
    print(f"Is Redacted: {uri.is_redacted()}")
    print(f"Redacted URI: {uri.as_redacted_str()}")
    print(f"URI == 's3://bucket/key': {uri == 's3://bucket/key'}")
