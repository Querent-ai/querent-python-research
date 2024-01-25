import asyncio
import json
from pathlib import Path
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.common.types.querent_event import EventState, EventType
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent
from querent.config.core.gpt_llm_config import GPTConfig
from querent.core.transformers.gpt_llm import GPTLLM

@pytest.mark.asyncio
async def test_ingest_all_async():
    # Set up the collectors
    directories = [ "./tests/data/llm/pdf/"]
    collectors = [
        FSCollectorFactory().resolve(
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

    # Set up the result queue
    result_queue = asyncio.Queue()

    # Create the IngestorFactoryManager
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
    resource_manager = ResourceManager()
    gpt_llm_config = GPTConfig(
        enable_filtering=True,
        filter_params={
            'score_threshold': 0.5,
            'attention_score_threshold': 0.1,
            'similarity_threshold': 0.5,
            'min_cluster_size': 5,
            'min_samples': 3,
            'cluster_persistence_threshold':0.2
        }
    )
    llm_instance = GPTLLM(result_queue, gpt_llm_config)
    class StateChangeCallback(EventCallbackInterface):
        def handle_event(self, event_type: EventType, event_state: EventState):
            print("StateChange---------------------------")
            assert event_state.event_type == EventType.Graph
            triple = json.loads(event_state.payload)
            print("triple: {}".format(triple))
            assert isinstance(triple['subject'], str) and triple['subject']
    llm_instance.subscribe(EventType.Graph, StateChangeCallback())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)

if __name__ == "__main__":

    # Run the async function
    asyncio.run(test_ingest_all_async())
