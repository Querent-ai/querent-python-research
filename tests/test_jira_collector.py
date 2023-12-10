import asyncio
import pytest
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import JiraCollectorConfig
from querent.common.uri import Uri
import uuid
from dotenv import load_dotenv
import os

load_dotenv()


@pytest.fixture
def jira_config():
    return JiraCollectorConfig(
        id=str(uuid.uuid4()),
        jira_server="https://querent.atlassian.net/",
        jira_username="puneet@querent.xyz",
        jira_api_token=os.getenv("JIRA_API_TOKEN"),
        jira_project="Querent1",
        jira_query="project=Querent1",
    )


@pytest.mark.asyncio
async def test_jira_collector(jira_config):
    uri = Uri("jira://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, jira_config)
    assert collector is not None
    await collector.connect()

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert result is not None
            chunk = result.unwrap()

            if chunk is not None:
                counter += 1
        assert counter == 1

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_jira_collector())
