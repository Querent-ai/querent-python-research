import asyncio

from querent.config.collector_config import S3CollectConfig
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.aws.aws_collector import AWSCollectorFactory
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend
import pytest
import os
from dotenv import load_dotenv

load_dotenv()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


@pytest.fixture
def aws_config():
    config = S3CollectConfig(
        bucket="pstreamsbucket1",
        region="ap-south-1",
        access_key=aws_access_key_id,
        secret_key=aws_secret_access_key,
        chunk=1024,
    )
    return config


def test_aws_collector_factory():
    factory = AWSCollectorFactory()
    assert factory.backend() == CollectorBackend.S3


# Modify this function to test the AWS collector


@pytest.mark.asyncio
async def test_aws_collector(aws_config):
    config = aws_config
    uri = Uri("s3://" + config.bucket)
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, config)
    assert collector is not None

    await collector.connect()

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk != "" or chunk is not None:
                counter += 1
        assert counter == 5392

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_aws_collector())
