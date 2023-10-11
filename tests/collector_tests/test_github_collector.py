import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector_config import GithubConfig
from querent.common.uri import Uri
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def github_config():
    return GithubConfig(
        github_username=os.getenv("GITHUB_USERNAME"),
        repository=os.getenv("GITHUB_REPOSITORY_NAME"),
        github_access_token=os.getenv("GITHUB_ACCESS_TOKEN"),
    )


@pytest.mark.asyncio
async def test_github_collector(github_config):
    uri = Uri("github://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, github_config)
    assert collector is not None

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk != "" or chunk is not None:
                counter += 1
        assert counter == 6

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_github_collector())
