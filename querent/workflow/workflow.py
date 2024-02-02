"""File to start workflow"""
import asyncio
import json
from typing import Any
import uuid
import os
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.channel.channel_interface import ChannelCommandInterface
from querent.common.types.ingested_tokens import IngestedTokens
from querent.config.config import Config
from querent.config.workflow.workflow_config import WorkflowConfig
from querent.config.collector.collector_config import CollectorConfig
from querent.config.core.llm_config import LLM_Config
from querent.config.core.gpt_llm_config import GPTConfig
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.gpt_llm import GPTLLM
from querent.common.types.querent_event import  EventState, EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_messages import IngestedMessages
from querent.core.base_engine import BaseEngine
from querent.common.types.querent_queue import QuerentQueue

class MockLLMEngine(BaseEngine):
    def __init__(self, input_queue: QuerentQueue):
        super().__init__(input_queue)

    async def process_tokens(self, data: IngestedTokens):
        if data is None or data.is_error():
            self.set_termination_event()
            return

        current_state = EventState(EventType.Graph, 1.0, "anything", "dummy.txt")
        await self.set_state(new_state=current_state)

    async def process_code(self, data: IngestedCode):
        pass

    async def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    async def process_images(self, data: IngestedImages):
        return super().process_images(data)

    def validate(self):
        return True


async def start_workflow(config_dict: dict):
    #Start the workflow
    # print("----------------------------------------------------------------Print the configuration :", config_dict)
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
    collector_configs = config_dict.get("collectors", [])
    collectors = []
    for collector_config in collector_configs: 
        collectors.append(CollectorConfig(config_source=collector_config).resolve())

    engine_configs = config_dict.get("engines", [])
    engines = []
    for engine_config in engine_configs:
        engine_config_source = engine_config.get("config",{})
        if engine_config["name"] == "knowledge_graph_using_openai_v1":
            engines.append(GPTConfig(config_source = engine_config_source))
        elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config_source))
    config_dict["engines"] = engines 
    config_dict["collectors"] = collectors 
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)

    workflows = {"knowledge_graph_using_openai_v1": start_gpt_workflow,
               "knowledge_graph_using_llama2_v1": start_llama_workflow}

    workflow = workflows.get(config.workflow.name)
    await workflow(config)


async def start_gpt_workflow(config: Config):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.uri)
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
            #we will get a dictionary here
            result_queue.put_nowait(tokens)
        if message_state is not None:
            state_queue.put_nowait(message_state)

async def start_llama_workflow(config: Config):
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.uri)
        collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

    for collector in collectors:
        await collector.connect()

    result_queue = asyncio.Queue()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    resource_manager = ResourceManager()
    llm_instance = MockLLMEngine(result_queue)

    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    querent_task = asyncio.create_task(querent.start())
    
    #token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=llm_instance.state_queue))
    await asyncio.gather(ingest_task, querent_task)
    #, token_feeder) # Loop and do config.workflow.channel for termination event messageType = "stop"
