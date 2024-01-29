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
from querent.core.transformers.bert_llm import BERTLLM
from querent.core.transformers.gpt_llm import GPTLLM
from querent.common.types.querent_event import  EventState, EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager



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

    workflows = {"openai": start_gpt_workflow,
               "llama": start_llama_workflow}

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

    llm_instance = BERTLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    # token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=llm_instance.state_queue))
    await asyncio.gather(ingest_task, querent_task)
    # , token_feeder) # Loop and do config.workflow.channel for termination event messageType = "stop"



# async def main():
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             assert event_state.event_type == EventType.Graph
#             triple = json.loads(event_state.payload)
#             print("triple: {}".format(triple))
#             assert isinstance(triple['subject'], str) and triple['subject']
#     config_source={
#         "version": 1.0,
#         "id": "ahdbfvd",
#         "querent_id": 12345,
#         "querent_name": "llama",
#         "workflow": {
#         "name": "llama",
#         "id": str(uuid.uuid4()),
#         "config": {},
#         "event_handler": StateChangeCallback
#     },
#         "collectors": [{
#             "id": str(uuid.uuid4()),
#             "name": "Local-config",
#             "config": {
#                 "root_path": "./tests/data/llm/pdf",
#             },
#             "backend":"localfile",
#         },
#         {
#             "id": str(uuid.uuid4()),
#             "name": "Drive-config",
#             "config": {
#                 "drive_refresh_token": os.getenv("DRIVE_REFRESH_TOKEN"),
#                 "drive_token": os.getenv("DRIVE_TOKEN"),
#                 "drive_scopes": os.getenv("DRIVE_SCOPES"),
#                 "chunk_size": 1024 * 1024,
#                 "drive_client_id": os.getenv("DRIVE_CLIENT_ID"),
#                 "drive_client_secret": os.getenv("DRIVE_CLIENT_SECRET"),
#                 "specific_file_type": "application/pdf",
#                 "folder_to_crawl": "1BtLKXcYBrS16CX0R4V1X7Y4XyO9Ct7f8",
#             },
#             "backend": "drive",
#         }],
        
#         "engines": [{ 
#         #https://github.com/Querent-ai/querent-rs/blob/main/src/config/config.rs#L172 con
#         "id": str(uuid.uuid4()),
#         "name": "knowledge_graph_using_llama2_v1",
#         "config": {"ner_model_name":"botryan96/GeoBERT",
#         "enable_filtering": True,
#         "filter_params": {
#                 'score_threshold': 0.5,
#                 'attention_score_threshold': 0.1,
#                 'similarity_threshold': 0.5,
#                 'min_cluster_size': 5,
#                 'min_samples': 3,
#                 'cluster_persistence_threshold':0.1
#         }
#     }}],        
#     }

#     await start_workflow(config_source)
    
# asyncio.run(main())
