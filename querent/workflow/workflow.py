"""File to start workflow"""
import asyncio
import uuid

from querent.config.config import Config
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.bert_llm import BERTLLM
from querent.core.transformers.gpt_llm import GPTLLM
from querent.common.types.querent_event import  EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager



async def start_workflow(config_dict: dict):
    #Start the workflow
    config = Config(config_source=config_dict)

    workflows = {"openai": start_gpt_workflow,
               "bert_v1": start_bert_workflow}

    workflow = workflows.get(Config.workflow.name)
    await workflow(config)


async def start_gpt_workflow(config: Config):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.backend+"://")
        collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

    for collector in collectors:
        await collector.connect()

    result_queue = asyncio.Queue()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    resource_manager = ResourceManager()

    llm_instance = GPTLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=GPTLLM.state_queue))
    await asyncio.gather(ingest_task, querent_task, token_feeder)


#Config workflow channel for setting termination event
async def receive_token_feeder(resource_manager: ResourceManager, config: Config, result_queue: asyncio.Queue, state_queue: asyncio.Queue):
    while not resource_manager.querent_termination_event.is_set():
        tokens = config.workflow.tokens_feader.receive_tokens_in_python()
        message_state = config.workflow.channel.receive_in_python()
        if tokens is not None:
            await result_queue.put(tokens)
        if message_state is not None:
            await state_queue.put(message_state)

async def start_bert_workflow(config: Config):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.backend+"://")
        collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

    for collector in collectors:
        await collector.connect()

    result_queue = asyncio.Queue()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    resource_manager = ResourceManager()

    llm_instance = BERTLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=BERTLLM.state_queue))
    await asyncio.gather(ingest_task, querent_task, token_feeder)

