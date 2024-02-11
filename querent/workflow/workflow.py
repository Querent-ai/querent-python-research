"""File to start workflow"""
import asyncio
from querent.common.types.querent_queue import QuerentQueue
from querent.config.config import Config
from querent.config.workflow.workflow_config import WorkflowConfig
from querent.config.collector.collector_config import CollectorConfig
from querent.config.core.llm_config import LLM_Config
from querent.config.core.gpt_llm_config import GPTConfig
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM
from querent.common.types.querent_event import EventType
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

    workflows = {"knowledge_graph_using_openai_v1": start_gpt_workflow,
               "knowledge_graph_using_llama2_v1": start_llama_workflow}

    workflow = workflows.get(config.workflow.name)
    result_queue = QuerentQueue()
    state_queue = QuerentQueue()
    await workflow(ResourceManager(), config, result_queue, state_queue)


async def start_gpt_workflow(resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue,  state_queue: QuerentQueue):
    llm_instance = GPTLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=llm_instance.state_queue))
    await asyncio.gather(querent_task, token_feeder)


#Config workflow channel for setting termination event
async def receive_token_feeder(resource_manager: ResourceManager, config: Config, result_queue: asyncio.Queue, state_queue: asyncio.Queue):
    while not resource_manager.querent_termination_event.is_set():
        tokens = config.workflow.tokens_feader.receive_tokens_in_python()
        message_state = config.workflow.channel.receive_in_python()
        if tokens is not None:
            #we will get a dictionary here
            result_queue.put_nowait(tokens)
            print("Type of token: ", type(tokens))
            print("is data stream true ", tokens.is_data_stream)
        if message_state is not None:
            state_queue.put_nowait(message_state)

async def start_llama_workflow(resource_manager: ResourceManager, config: Config, result_queue: QuerentQueue,  state_queue: QuerentQueue):
    llm_instance = BERTLLM(result_queue, config.engines[0])

    llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=llm_instance.state_queue))
    await asyncio.gather(querent_task, token_feeder)

async def start_ingestion(config_dict: dict):
    collectors = []
    collector_configs = config_dict.get("collectors", [])
    for collector_config in collector_configs: 
        collectors.append(CollectorConfig(config_source=collector_config).resolve())
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
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
    collectors = []
    for collector_config in config.collectors:
        uri = Uri(collector_config.uri)
        collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

    for collector in collectors:
        await collector.connect()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=None,
        tokens_feader= config.workflow.tokens_feader
    )

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    await ingest_task
    
    
async def start_workflow_engine(config_dict: Config):
    result_queue = QuerentQueue()
    state_queue = QuerentQueue()
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
    engine_configs = config_dict.get("engines", [])
    engines = []
    for engine_config in engine_configs:
        engine_config_source = engine_config.get("config",{})
        if engine_config["name"] == "knowledge_graph_using_openai_v1":
            engines.append(GPTConfig(config_source = engine_config_source))
        elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config_source))
    config_dict["engines"] = engines 
    config_dict["collectors"] = None 
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)
    workflows = {"knowledge_graph_using_openai_v1": start_gpt_workflow,
               "knowledge_graph_using_llama2_v1": start_llama_workflow}
    
    workflow = workflows.get(config.workflow.name)
    await workflow(ResourceManager(), config, result_queue, state_queue)