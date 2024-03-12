import asyncio
import json
import logging
from typing import Dict, Any, List, Callable, Optional

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
from querent.workflow._helpers import check_message_states, start_collectors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def parse_json_config(json_str: str) -> Optional[Dict[str, Any]]:
    """Attempt to parse a JSON string and return the dictionary representation.

    Args:
        json_str (str): The JSON string to parse.

    Returns:
        Optional[Dict[str, Any]]: The dictionary representation of the JSON string, or None if parsing fails.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Got error while loading JSON: {e}")
        return None


def load_configuration(
    config_dict: dict, engine_params: Optional[Dict[str, Any]] = None
) -> Config:
    """Load and return a configuration object from a dictionary.

    Args:
        config_dict (dict): The dictionary containing configuration.
        engine_params (Optional[Dict[str, Any]]): Optional engine parameters to update the engine config with.

    Returns:
        Config: The configuration object.
    """
    # Process workflow configuration
    workflow = WorkflowConfig(config_source=config_dict.get("workflow"))

    # Process collector configurations
    collectors = [
        CollectorConfig(config_source=collector_config).resolve()
        for collector_config in config_dict.get("collectors", [])
    ]

    # Process engine configurations
    engines = []
    for engine_config in config_dict.get("engines", []):
        if engine_params:
            engine_config.update(engine_params)
        if engine_config["name"] == "knowledge_graph_using_openai":
            engines.append(GPTConfig(config_source=engine_config))
        elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
            engines.append(LLM_Config(config_source=engine_config))

    # Assemble the final configuration
    final_config_dict = {
        "workflow": workflow,
        "collectors": collectors,
        "engines": engines,
    }

    return Config(config_source=final_config_dict)


async def start_workflow(config_dict: dict):
    """Start the main workflow asynchronously.

    Args:
        config_dict (dict): Configuration dictionary for the workflow.
    """
    engine_params_json = (
        config_dict.get("workflow", {}).get("config", {}).get("engine_params")
    )
    engine_params = (
        parse_json_config(engine_params_json) if engine_params_json else None
    )

    config = load_configuration(config_dict, engine_params)

    # Retrieve the appropriate workflow function based on the workflow name
    workflow_func: Callable = globals().get(f"start_{config.workflow.name}_workflow")

    if not workflow_func:
        logger.error(f"Workflow function for '{config.workflow.name}' not found.")
        return

    result_queue = QuerentQueue()
    collector_tasks = asyncio.create_task(start_collectors(config))
    engine_tasks = asyncio.create_task(
        workflow_func(ResourceManager(), config, result_queue)
    )

    await asyncio.gather(collector_tasks, engine_tasks)
    logger.info("Workflow is finished. All events have been released.")


async def start_ingestion(config_dict: dict):
    """Start the ingestion process asynchronously.

    Args:
        config_dict (dict): Configuration dictionary for the ingestion.
    """
    if not config_dict:
        logger.error("Configuration for ingestion is empty.")
        return

    config = load_configuration(config_dict)

    # Initialize collectors based on the configuration
    collectors: List[CollectorResolver] = [
        CollectorResolver().resolve(
            uri=Uri(collector_config.uri), config=collector_config
        )
        for collector_config in config.collectors
    ]

    for collector in collectors:
        await collector.connect()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors,
        result_queue=None,  # Assuming there's logic to handle the result queue
        tokens_feader=config.workflow.tokens_feader,
    )

    resource_manager = ResourceManager()

    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
    check_message_states_task = asyncio.create_task(
        check_message_states(config, resource_manager, [ingest_task])
    )

    await asyncio.gather(ingest_task, check_message_states_task)
