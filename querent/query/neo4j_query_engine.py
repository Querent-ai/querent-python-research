import asyncio
from typing import List, Optional
import time

from querent.common.types.querent_queue import QuerentQueue
from querent.querent.resource_manager import ResourceManager
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.ingested_tokens import IngestedTokens
from querent.query.neo4j_query import Neo4jConnection
from querent.logging.logger import setup_logger

logger = setup_logger(__name__, "Neo4jQueryEngine")

async def start_graph_query_engine(config_dict: dict):
    query_queue = QuerentQueue()
    resource_manager = ResourceManager()
    receive_token_feeder_task = asyncio.create_task(receive_token_feeder(config=config_dict, resource_manager=resource_manager, query_queue=query_queue))
    check_message_states_task = asyncio.create_task(check_message_states(config=config_dict, resource_manager=resource_manager, query_queue=query_queue))

    rag_task = asyncio.create_task(process_query1(config_dict, resource_manager, query_queue))
    await asyncio.gather(rag_task, receive_token_feeder_task, check_message_states_task)


async def receive_token_feeder(
    config: dict,
    resource_manager: ResourceManager,
    query_queue: QuerentQueue
):
    #for this to terminate, channel input
    while not resource_manager.querent_termination_event.is_set():
        query = config["tokens_feader"].receive_tokens_in_python()
        if query is not None:
            ingested_tokens = IngestedTokens(
                file=query.get("file", None), data=query.get("data", None), is_token_stream= query.get("is_token_stream"), 
            )
            await query_queue.put(ingested_tokens)
        else:
            await asyncio.sleep(10)



async def check_message_states(
    config: dict,
    resource_manager: ResourceManager,
    tasks_to_kill: Optional[List[asyncio.Task]] = None,
):
    while not resource_manager.querent_termination_event.is_set():
        message_state = config["channel"].receive_in_python()
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



async def process_query1(config_dict: dict, resource_manager: ResourceManager, query_queue: QuerentQueue):
    uri = config_dict.get("uri")
    user = config_dict.get("user")
    pwd = config_dict.get("pwd")
    while not resource_manager.querent_termination_event.is_set():
        try:
            data = await asyncio.wait(query_queue.get(), timeout=300)

            neo4j_conn = Neo4jConnection(uri, user, pwd)
            if isinstance(data, IngestedTokens):
                # Execute the query
                results = neo4j_conn.query(data.data)

                event_state = EventState(EventType.QueryResult, timestamp=time.time(), payload=results, file= data.file)
                config_dict["event_handler"].handle_event(EventType.QueryResult, event_state)
        
        except asyncio.TimeoutError:
            logger.error("Got timeout error while waiting for data from queue ")
            resource_manager.querent_termination_event.set()

    neo4j_conn.close()
