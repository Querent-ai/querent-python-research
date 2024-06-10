"""File to start workflow"""

import asyncio
import json
from querent.common.types.querent_queue import QuerentQueue
from querent.config.config import Config
from querent.config.workflow.workflow_config import WorkflowConfig
from querent.config.collector.collector_config import CollectorConfig
from querent.config.core.llm_config import LLM_Config
from querent.querent.resource_manager import ResourceManager
from querent.workflow._helpers import *

from querent.logging.logger import setup_logger
logger = setup_logger(__name__, "Workflows")

async def start_workflow(config_dict: dict):
    # Start the workflow
    workflow_config = config_dict.get("workflow")
    engine_params = workflow_config.get("config", None)
    is_engine_params = False
    try:
        if engine_params is not None:
            engine_params_json = {}
            
            if engine_params.get("fixed_entities") is not None:
                engine_params_json["fixed_entities"] = [x for x in engine_params.get("fixed_entities").split(",")]
            
            if engine_params.get("sample_entities") is not None:
                engine_params_json["sample_entities"] = [x for x in engine_params.get("sample_entities").split(",")]
            
            if engine_params.get("ner_model_name") is not None:
                engine_params_json["ner_model_name"] = engine_params.get("ner_model_name")
            
            if engine_params.get("enable_filtering") is not None:
                engine_params_json["enable_filtering"] = engine_params.get("enable_filtering")
            
            if engine_params.get("fixed_relationships") is not None:
                engine_params_json["fixed_relationships"] = [x for x in engine_params.get("fixed_relationships").split(",")]
            
            if engine_params.get("sample_relationships") is not None:
                engine_params_json["sample_relationships"] = [x for x in engine_params.get("sample_relationships").split(",")]
            
            
            engine_params_json["filter_params"] = {
                "score_threshold": float(engine_params.get("score_threshold")) if engine_params.get("score_threshold") is not None else None,
                "attention_score_threshold": float(engine_params.get("attention_score_threshold")) if engine_params.get("attention_score_threshold") is not None else None,
                "similarity_threshold": float(engine_params.get("similarity_threshold")) if engine_params.get("similarity_threshold") is not None else None,
                "min_cluster_size": int(engine_params.get("min_cluster_size")) if engine_params.get("min_cluster_size") is not None else None,
                "min_samples": int(engine_params.get("min_samples")) if engine_params.get("min_samples") is not None else None,
                "cluster_persistence_threshold": float(engine_params.get("cluster_persistence_threshold")) if engine_params.get("cluster_persistence_threshold") is not None else None,
            }

            if engine_params.get("is_confined_search") is not None:
                engine_params_json["is_confined_search"] = engine_params.get("is_confined_search")

            if engine_params.get("user_context") is not None:
                engine_params_json["user_context"] = engine_params.get("user_context")
            is_engine_params = True
    except Exception as e:
        logger.error("Got error while loading engine params: ", e)
    workflow = WorkflowConfig(config_source=workflow_config)
    collector_configs = config_dict.get("collectors", [])
    collectors = []
    for collector_config in collector_configs:
        collectors.append(CollectorConfig(config_source=collector_config).resolve())
    engine_configs = config_dict.get("engines", [])
    engines = []
    for engine_config in engine_configs:
        if is_engine_params:
            engine_config.update(engine_params_json)
        engine_config_source = engine_config.get("config", {})
        if engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config))
    config_dict["engines"] = engines
    config_dict["collectors"] = collectors
    config_dict["workflow"] = workflow
    config = Config(config_source=config_dict)

    workflows = {
        "knowledge_graph_using_llama2_v1": start_llama_workflow,
    }

    workflow = workflows.get(config.workflow.name)
    result_queue = QuerentQueue()
    collector_tasks = asyncio.create_task(start_collectors(config, result_queue))
    engine_tasks = asyncio.create_task(
        workflow(ResourceManager(), config, result_queue)
    )
    await asyncio.gather(collector_tasks, engine_tasks)
    logger.info("Workflow is finished. All events have been released.")

