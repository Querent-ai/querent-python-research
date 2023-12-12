import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import JiraCollectorConfig
from querent.common.uri import Uri
import uuid
from dotenv import load_dotenv

from querent.ingestors.ingestor_manager import IngestorFactoryManager

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
async def test_jira_ingestor(jira_config):
    uri = Uri("jira://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, jira_config)
    assert collector is not None
    await collector.connect()

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("jira")
    ingestor = await ingestor_factory.create("jira", [])
    ingested_call = ingestor.ingest(collector.poll())

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested is not "" or ingested is not None:
                counter += 1
        # 1 extra ingestedToken signifying end of file
        assert counter == 2

    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_jira_ingestor())
