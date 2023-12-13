import asyncio
from pathlib import Path
from querent.collectors.github.github_collector import GithubCollectorFactory
from querent.config.collector.collector_config import GithubConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import os
import uuid
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.asyncio
async def test_collect_and_ingest_code():
    collector_factory = GithubCollectorFactory()
    config = GithubConfig(
        id=str(uuid.uuid4()),
        github_username=os.getenv("USERNAME_GITHUB"),
        repository=os.getenv("REPOSITORY_NAME_GITHUB"),
        github_access_token=os.getenv("ACCESS_TOKEN_GITHUB"),
    )
    uri = Uri("github://")

    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("github")
    ingestor = await ingestor_factory.create("github", [])

    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested is not "" or ingested is not None:
                counter += 1

        # 6 extra IngestedTokens signifying end of file
        assert counter == 12

    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_code())
