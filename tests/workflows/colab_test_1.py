import asyncio
import json
import pytest
from pathlib import Path
import uuid
import nltk

from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.config.core.llm_config import LLM_Config
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager

async def main():
    print("Inside main)")
# Setup directories for data collection and configure collectors.
    directories = ["/home/nishantg/querent-main/querent/tests/data/llm/case_study_files"]
    collectors = [
        # Resolve and configure each collector based on the provided directory and file system configuration.
        CollectorResolver().resolve(
            Uri("file://" + str(Path(directory).resolve())),
            FSCollectorConfig(
                config_source={
                    "id": str(uuid.uuid4()),
                    "root_path": directory,
                    "name": "Local-config",
                    "config": {},
                    "uri": "file://",
                }
            ),
        )
        for directory in directories
    ]

    # Connect each collector asynchronously.
    for collector in collectors:
        await collector.connect()

    # Setup the result queue for processing results from collectors.
    result_queue = asyncio.Queue()

    # Initialize the IngestorFactoryManager with the collectors and result queue.
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )


    # Start the asynchronous ingestion process and store the task.
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    # Initialize the ResourceManager.
    resource_manager = ResourceManager()

    # Set NLTK data path for natural language processing tasks.
    nltk.data.path=["/home/nishantg/querent-main/model/nltk_data"]

    # Configure the BERT language model for named entity recognition (NER) and filtering.
    bert_llm_config = LLM_Config(
        rel_model_path="/home/nishantg/querent-main/model/llama-2-7b-chat.Q5_K_M.gguf",
        grammar_file_path="/home/nishantg/querent-main/model/json.gbnf",
        spacy_model_path="/home/nishantg/querent-main/model/en_core_web_lg-3.7.1/en_core_web_lg/en_core_web_lg-3.7.1",
        ner_model_name="dbmdz/bert-large-cased-finetuned-conll03-english",
        nltk_path="/home/nishantg/querent-main/model/nltk_data",
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

    # Initialize the BERTLLM instance with the result queue and configuration.
    llm_instance = BERTLLM(result_queue, bert_llm_config)

    # Define a function to automatically terminate the task after 5 minutes
    async def terminate_querent(result_queue):
        await asyncio.sleep(180)
        await result_queue.put(None)
        await result_queue.put(None)

    # Define a callback class to handle state changes and print resulting triples.
    class StateChangeCallback(EventCallbackInterface):
        def handle_event(self, event_type: EventType, event_state: EventState):
            assert event_state['event_type'] == EventType.Graph
            triple = json.loads(event_state['payload'])
            print("triple: {}".format(triple))

    # Subscribe the BERTLLM instance to graph events using the StateChangeCallback.
    llm_instance.subscribe(EventType.Graph, StateChangeCallback())

    # Initialize Querent with the BERTLLM instance and ResourceManager.
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    # Start Querent and the ingestion task asynchronously and wait for both to complete.
    querent_task = asyncio.create_task(querent.start())
    terminate_task = asyncio.create_task(terminate_querent(result_queue))
    await asyncio.gather(querent_task, ingest_task, terminate_task)
if __name__ == "__main__":
    asyncio.run(main())