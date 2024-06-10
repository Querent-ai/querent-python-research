"""Helper Functions for Workflow"""

import asyncio
from typing import List, Optional
from querent.common.types.querent_queue import QuerentQueue
from querent.config.config import Config
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.common.types.querent_event import EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.common.types.ingested_tokens import IngestedTokens
from querent.workflow._helpers import *
from querent.processors.text_cleanup_processor import TextCleanupProcessor
from querent.processors.text_processor import TextProcessor
import os
import nltk
from querent.logging.logger import setup_logger
logger = setup_logger(__name__, "Helpers")


def setup_nltk_and_spacy_paths(config, search_directory):
    """
    Sets up NLTK and spaCy paths using the provided search directory.
    """
    # Set NLTK path
    config.engines[0].nltk_path = os.path.join(search_directory, 'nltk_data')
    nltk.data.path=[config.engines[0].nltk_path]
    # nltk.data.path.append(config.engines[0].nltk_path)
    
    # Set spaCy model path
    spacy_model_path = os.path.join(search_directory, 'en_core_web_lg-3.7.1/en_core_web_lg/en_core_web_lg-3.7.1')
    config.engines[0].spacy_model_path = spacy_model_path

    
async def start_collectors(config: Config, result_queue: QuerentQueue):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.uri)
        collectors.append(CollectorResolver().resolve(uri=uri, config=collector_config))

    for collector in collectors:
        await collector.connect()

    text_cleanup_processor = TextCleanupProcessor()
    text_processor = TextProcessor()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors,
        result_queue=result_queue,
        tokens_feader=None,
        processors=[text_cleanup_processor, text_processor]
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    await ingest_task


async def start_llama_workflow(
    resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue
):
    # Specify the directory you want to search
    
    search_directory = os.getenv('MODEL_PATH', '/model/')
    setup_nltk_and_spacy_paths(config, search_directory)
    # Specify the file extension you're interested in, e.g., '.txt'. Leave empty ('') for all files.
    file_extension = '.gguf'
    def find_first_file(directory, extension):
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if file ends with the specified extension (if any)
                if file.endswith(extension) or not extension:
                    return os.path.join(root, file)
        return None

    # Calling the function and printing the result
    first_file_path = find_first_file(search_directory, file_extension)
    if first_file_path:
        model_path = first_file_path
    else:
        raise Exception("No file found matching the criteria.")
    config.engines[0].rel_model_path = model_path
    second_file_path = find_first_file(search_directory, '.gbnf')
    config.engines[0].grammar_file_path = second_file_path
    llm_instance = BERTLLM(result_queue, config.engines[0])
    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler)
    llm_instance.subscribe(EventType.Vector, config.workflow.event_handler)
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    token_feeder = asyncio.create_task(
        receive_token_feeder(
            resource_manager=resource_manager,
            config=config,
            result_queue=result_queue,
        )
    )

    check_message_states_task = asyncio.create_task(
        check_message_states(config, resource_manager, [querent_task, token_feeder])
    )

    await asyncio.gather(querent_task, token_feeder, check_message_states_task)


# Config workflow channel for setting termination event
async def receive_token_feeder(
    resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue
):
    while not resource_manager.querent_termination_event.is_set():
        tokens = config.workflow.tokens_feader.receive_tokens_in_python()
        if tokens is not None:
            ingested_tokens = IngestedTokens(
                file=tokens.get("file", None), data=tokens.get("data", None), is_token_stream= tokens.get("is_token_stream"), doc_source=tokens.get("doc_source", "")
            )
            await result_queue.put(ingested_tokens)
        else:
            await asyncio.sleep(10)
    await result_queue.put(None)


async def check_message_states(
    config: Config,
    resource_manager: ResourceManager,
    tasks_to_kill: Optional[List[asyncio.Task]] = None,
):
    while not resource_manager.querent_termination_event.is_set():
        message_state = config.workflow.channel.receive_in_python()
        if message_state is not None:
            message_type = message_state["message_type"]
            if message_type.lower() == "stop" or message_type.lower() == "terminate":
                logger.info("🛑 Received stop signal. Exiting...")
                resource_manager.querent_termination_event.set()
                if tasks_to_kill is not None:
                    for task in tasks_to_kill:
                        task.cancel()
                break
            else:
                logger.info("📬 Received message of type: " + message_type)
                # Handle other message types...
        await asyncio.sleep(60)
    logger.info("🛑 Received stop signal. Exiting...")
