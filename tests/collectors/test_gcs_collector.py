import asyncio
import json
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.gcs.gcs_collector import GCSCollectorFactory
from querent.common.uri import Uri
from querent.config.collector.collector_config import CollectorBackend, GcsCollectConfig
import pytest
import uuid
from dotenv import load_dotenv

load_dotenv()
import os


@pytest.fixture
def gcs_config():
    cred_file = "/tmp/.config/gcloud/application_default_credentials.json"
    credentials_info = {
        "type": "service_account",
        "project_id": "protocolstreams-ai",
        "private_key_id": os.getenv("GOOGLE_BUCKET_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_BUCKET_PRIVATE_KEY"),
        "client_email": "gcs-test-querent@protocolstreams-ai.iam.gserviceaccount.com",
        "client_id": os.getenv("GOOGLE_BUCKET_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gcs-test-querent%40protocolstreams-ai.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    credential_json_str = json.dumps(credentials_info)
    return GcsCollectConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "bucket": "querent-test",
            "credentials": credential_json_str,
            "chunk": "1024",
            "config": {},
            "name": "GCS-config",
            "uri": "gs://",
        }
    )


def test_gcs_collector_factory():
    factory = GCSCollectorFactory()
    assert factory.backend() == CollectorBackend.Gcs


# Modify this function to test the GCS collector

# To do: uncomment the following code when you have the bucket name and the credentials.json file for testing.


@pytest.mark.asyncio
async def test_gcs_collector(gcs_config):
    config = gcs_config
    uri = Uri("gs://" + config.bucket)
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, config)
    assert collector is not None

    await collector.connect()

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()

            if chunk is not None:
                counter += 1
        assert counter == 3996

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_gcs_collector())
