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
from querent.querent.resource_manager import ResourceManager
from querent.workflow._helpers import *


async def start_workflow(config_dict: dict):
    # Start the workflow
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
    collector_configs = config_dict.get("collectors", [])
    collectors = []
    for collector_config in collector_configs:
        collectors.append(CollectorConfig(config_source=collector_config).resolve())

    engine_configs = config_dict.get("engines", [])
    engines = []
    for engine_config in engine_configs:
        engine_config_source = engine_config.get("config", {})
        if engine_config["name"] == "knowledge_graph_using_openai":
            engines.append(GPTConfig(config_source=engine_config_source))
        elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config_source))
    config_dict["engines"] = engines
    config_dict["collectors"] = collectors
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)

    workflows = {
        "knowledge_graph_using_openai": start_gpt_workflow,
        "knowledge_graph_using_llama2_v1": start_llama_workflow,
    }

    workflow = workflows.get(config.workflow.name)
    result_queue = QuerentQueue()
    collector_tasks = asyncio.create_task(start_collectors(config))
    engine_tasks = asyncio.create_task(
        workflow(ResourceManager(), config, result_queue)
    )
    await asyncio.gather(collector_tasks, engine_tasks)
    print("Workflow is finished. All events have been released.")


async def start_ingestion(config_dict: dict):
    if not config_dict:
        return
    collectors = []
    collector_configs = config_dict.get("collectors", [])
    for collector_config in collector_configs:
        collectors.append(CollectorConfig(config_source=collector_config).resolve())
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
    config_dict["collectors"] = collectors
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)
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

    resource_manager = ResourceManager()
    
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
    check_message_states_task = asyncio.create_task(
        check_message_states(config, resource_manager, [ingest_task])
    )
    await asyncio.gather(ingest_task, check_message_states_task)

async def start_workflow_engine(config_dict: Config):
    if not config_dict:
        return
    workflow_config = config_dict.get("workflow")
    workflow = WorkflowConfig(config_source=workflow_config)
    engine_configs = config_dict.get("engines", [])
    engines = []
    for engine_config in engine_configs:
        engine_config_source = engine_config.get("config", {})
        if engine_config["name"] == "knowledge_graph_using_openai":
            engines.append(GPTConfig(config_source=engine_config_source))
        elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config_source))
    config_dict["engines"] = engines
    config_dict["collectors"] = None
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)
    workflows = {
        "knowledge_graph_using_openai": start_gpt_workflow,
        "knowledge_graph_using_llama2_v1": start_llama_workflow,
    }
    workflow = workflows.get(config.workflow.name)
    result_queue = QuerentQueue()
    resource_manager = ResourceManager()

    await workflow(resource_manager, config, result_queue)
