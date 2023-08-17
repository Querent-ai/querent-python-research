import asyncio
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.aws.aws_collector import AWSCollectorFactory
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend
import pytest


@pytest.fixture
def aws_config():
    return {
        "bucket": "pstreamsbucket1",
        "region": "Asia Pacific (Mumbai) ap-south-1",
        "access_key": "AKIA5ZFZH6CA6LDWIPV5",
        "secret_key": "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",
    }


def test_aws_collector_factory():
    factory = AWSCollectorFactory()
    assert factory.backend() == CollectorBackend.S3

# Modify this function to test the AWS collector


async def test_aws_collector(aws_config):
    uri = Uri("s3://" + aws_config["bucket"] + "/prefix/")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri)
    assert collector is not None

    await collector.connect()

    async def poll_and_print():
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None

    # Modify this function to add files to S3 bucket
    async def add_files():
        # Add files to your S3 bucket here
        pass

    async def main():
        await asyncio.gather(add_files(), poll_and_print())

    asyncio.run(main())


if __name__ == "__main__":
    # Modify this line to call the appropriate test function
    pytest.main(["-k", "test_aws_collector"])
