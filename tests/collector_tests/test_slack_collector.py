import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector_config import SlackCollectorConfig
from querent.common.uri import Uri


@pytest.fixture
def slack_config():
    return SlackCollectorConfig(
        channel_name="C05TA5R7D88",
        cursor=None,
        include_all_metadata=0,
        inclusive=0,
        latest=0,
        limit=100,
        access_token=os.getenv("SLACK_ACCESS_KEY"),
    )


@pytest.mark.asyncio
async def test_slack_collector(slack_config):
    uri = Uri("slack://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, slack_config)
    assert collector is not None

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk != "" or chunk is not None:
                counter += 1
        assert counter == 15

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_slack_collector())
