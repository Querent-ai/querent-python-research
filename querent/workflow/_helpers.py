"""Helper Functions for Workflow"""

import asyncio
from typing import List, Optional
from querent.common.types.querent_queue import QuerentQueue
from querent.config.config import Config
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.core.transformers.gpt_llm_gpt_ner import GPTNERLLM
from querent.common.types.querent_event import EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.common.types.ingested_tokens import IngestedTokens
from querent.workflow._helpers import *
import os
import nltk

async def start_collectors(config: Config):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.uri)
        collectors.append(CollectorResolver().resolve(uri=uri, config=collector_config))

    for collector in collectors:
        await collector.connect()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors,
        result_queue=None,
        tokens_feader=config.workflow.tokens_feader,
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    await ingest_task


async def start_llama_workflow(
    resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue
):
    # Specify the directory you want to search
    search_directory = '/model/'
    # Specify the file extension you're interested in, e.g., '.txt'. Leave empty ('') for all files.
    file_extension = '.gguf'
    nltk.data.path.append(config.engines[0].nltk_path)
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
    print("--------------------------------", config.engines[0].spacy_model_path)
    config.engines[0].spacy_model_path = '/model/en_core_web_lg-3.7.1/en_core_web_lg/en_core_web_lg-3.7.1'
    print("--------------------------------", config.engines[0].spacy_model_path)
    llm_instance = BERTLLM(result_queue, config.engines[0])
    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler)
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


async def start_gpt_workflow(
    resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue
):
    nltk.data.path.append(config.engines[0].nltk_path)
    config.engines[0].spacy_model_path = '/model/en_core_web_lg-3.7.1/en_core_web_lg/en_core_web_lg-3.7.1'
    llm_instance = GPTNERLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler)
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
    await asyncio.sleep(180)
    while not resource_manager.querent_termination_event.is_set():
        tokens = config.workflow.tokens_feader.receive_tokens_in_python()
        if tokens is not None:
            ingested_tokens = IngestedTokens(
                file=tokens.get("file", None), data=tokens.get("data", None)
            )
            # we will get a dictionary here
            await result_queue.put(ingested_tokens)

        else:
            ## wait 1 minute for system to process and then set termination event
            await asyncio.sleep(60)
            resource_manager.querent_termination_event.set()
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
                print("🛑 Received stop signal. Exiting...")
                resource_manager.querent_termination_event.set()
                if tasks_to_kill is not None:
                    for task in tasks_to_kill:
                        task.cancel()
                break
            else:
                print("📬 Received message of type: " + message_type)
                # Handle other message types...
        await asyncio.sleep(60)
    print("🛑 Received stop signal. Exiting...")