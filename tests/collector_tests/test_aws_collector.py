import asyncio
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.aws.aws_collector import AWSCollectorFactory
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend
import pytest
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def aws_config():
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    aws_bucket_name = os.getenv('AWS_BUCKET_NAME')
    return {
        "bucket": aws_bucket_name,
        "region": aws_region,
        "access_key": aws_access_key_id,
        "secret_key": aws_secret_access_key,
    }


def test_aws_collector_factory():
    factory = AWSCollectorFactory()
    assert factory.backend() == CollectorBackend.S3

# Modify this function to test the AWS collector


@pytest.mark.asyncio
async def test_aws_collector(aws_config):
    uri = Uri("s3://" + aws_config["bucket"] + "/prefix/")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, aws_config)
    assert collector is not None

    await collector.connect()

    async def poll_and_print():
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None

    await poll_and_print()

    # Modify this function to add files to S3 bucket
    async def add_files():
        # Add files to your S3 bucket here
        pass

    async def main():
        await asyncio.gather(add_files(), poll_and_print())

    # asyncio.run(main())


if __name__ == "__main__":
    # Modify this line to call the appropriate test function
    pytest.main(["-k", "test_aws_collector"])
