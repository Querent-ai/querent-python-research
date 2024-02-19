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
