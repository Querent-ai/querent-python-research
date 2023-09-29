import asyncio
import pytest
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector_config import CollectorBackend, SlackCollectorConfig
from querent.common.uri import Uri


@pytest.mark.asyncio
async def test_slack_collector():
    uri = Uri("slack://")
    resolver = CollectorResolver()
    file_config = SlackCollectorConfig(
        channel_name="C05MRBR192L",
        cursor=None,
        include_all_metadata=0,
        inclusive=0,
        latest=0,
        limit=100,
    )
    collector = resolver.resolve(uri, file_config)
    assert collector is not None

    async for result in collector.poll():
        assert not result.is_error()
        chunk = result.unwrap()
        assert chunk is not None


if __name__ == "__main__":
    asyncio.run(test_slack_collector())
