import asyncio
import json
from pathlib import Path
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType
from querent.common.uri import Uri
from querent.config.core.llm_config import LLM_Config
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid
from querent.core.transformers.bert_llm import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent

from dotenv import load_dotenv

from querent.config.collector.collector_config import (
    FSCollectorConfig,
    DriveCollectorConfig,
    SlackCollectorConfig,
)
from querent.common.uri import Uri
from querent.collectors.collector_resolver import CollectorResolver
import os

load_dotenv()


def drive_config():
    return DriveCollectorConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "drive_refresh_token": os.getenv("DRIVE_REFRESH_TOKEN"),
            "drive_token": os.getenv("DRIVE_TOKEN"),
            "drive_scopes": os.getenv("DRIVE_SCOPES"),
            "chunk_size": "1048576",
            "drive_client_id": os.getenv("DRIVE_CLIENT_ID"),
            "drive_client_secret": os.getenv("DRIVE_CLIENT_SECRET"),
            "specific_file_type": "application/pdf",
            "folder_to_crawl": "1BtLKXcYBrS16CX0R4V1X7Y4XyO9Ct7f8",
            "name": "Drive-config",
            "config": {},
            "uri": "drive://",
        }
    )


def slack_config():
    return SlackCollectorConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "channel_name": "C05TA5R7D88",
            "cursor": None,
            "include_all_metadata": 0,
            "inclusive": 0,
            "latest": 0,
            "limit": 100,
            "access_token": os.getenv("SLACK_ACCESS_KEY"),
            "name": "Slack-config",
            "config": {},
            "uri": "slack://",
        }
    )


@pytest.mark.asyncio
async def test_multiple_collectors_all_async():
    # Set up the collectors
    directories = ["./tests/data/llm/old_pdf", "./tests/data/llm/pdf"]
    collectors = [
        CollectorResolver().resolve(
            Uri("file://" + str(Path(directory).resolve())),
            FSCollectorConfig(config_source={
                    "id": str(uuid.uuid4()),
                    "root_path": directory,
                    "name": "Local-config",
                    "config": {},
                    "uri": "file://",
                }),
        )
        for directory in directories
    ]

    collectors.append(
        CollectorResolver().resolve(
            Uri("drive://"),
            drive_config(),
        )
    )

    collectors.append(
        CollectorResolver().resolve(
            Uri("slack://"),
            slack_config(),
        )
    )

    for collector in collectors:
        await collector.connect()

    # Set up the result queue
    result_queue = asyncio.Queue()

    # Create the IngestorFactoryManager
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    # Start the ingest_all_async in a separate task
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
    resource_manager = ResourceManager()
    bert_llm_config = LLM_Config(
        ner_model_name="botryan96/GeoBERT",
        enable_filtering=True,
        filter_params={
            "score_threshold": 0.5,
            "attention_score_threshold": 0.1,
            "similarity_threshold": 0.5,
            "min_cluster_size": 5,
            "min_samples": 3,
            "cluster_persistence_threshold": 0.1,
        },
        fixed_entities=["carbon isotope", "carbon stable isotope"],
        sample_entities=["B-GeoPetro", "B-GeoPetro"],
    )
    llm_instance = BERTLLM(result_queue, bert_llm_config)

    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            assert event_state.event_type == EventType.Graph
            triple = json.loads(event_state.payload)
            print("triple: {}".format(triple))
            assert isinstance(triple["subject"], str) and triple["subject"]

    llm_instance.subscribe(EventType.Graph, StateChangeCallback())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)


if __name__ == "__main__":
    asyncio.run(test_multiple_collectors_all_async())
