import asyncio
from asyncio import Queue
import json
from pathlib import Path
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.common.types.querent_event import EventState, EventType
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.config.core.llm_config import LLM_Config
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import uuid
import numpy as np
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent
from postgres_utility import DatabaseManager

async def ingest_all_async():
    db_manager = DatabaseManager(
        dbname="querent_test",
        user="querent",
        password="querent",
        host="localhost",
        port="5432"
    )
    
    db_manager.connect_db()
    db_manager.create_tables()
    directories = ["/home/nishantg/querent-main/querent/tests/data/readme_assets"]
    collectors = [
        FSCollectorFactory().resolve(
            Uri("file://" + str(Path(directory).resolve())),
            FSCollectorConfig(config_source={
                    "id": str(uuid.uuid4()),
                    "root_path": directory,
                    "name": "Local-config",
                    "config": {},
                    "backend": "localfile",
                    "uri": "file://",
                }),
        )
        for directory in directories
    ]

    result_queue = asyncio.Queue()

    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
    resource_manager = ResourceManager()
    bert_llm_config = LLM_Config(
        # ner_model_name="English",
    rel_model_type = "bert",
        rel_model_path = 'bert-base-uncased',
        fixed_entities = [
            "university", "greenwood", "liam zheng", "department", "Metroville",
            "Emily Stanton", "Coach", "health", "training", "athletes"
        ],
        sample_entities = [
            "organization", "organization", "person", "department", "city",
            "person", "person", "method", "method", "person"
        ],
        is_confined_search = True
    )
    llm_instance = BERTLLM(result_queue, bert_llm_config)
    
    class StateChangeCallback(EventCallbackInterface):
        def handle_event(self, event_type: EventType, event_state: EventState):
            if event_state['event_type'] == EventType.Graph:
                triple = json.loads(event_state['payload'])
                db_manager.insert_metadata(
    event_id=triple['event_id'],
    subject=triple['subject'],
    subject_type=triple['subject_type'],
    predicate=triple['predicate'],
    object=triple['object'],
    object_type=triple['object_type'],
    sentence=triple['sentence'],
    file=event_state['file'],
    doc_source=event_state['doc_source'],
    score=triple['score']
)
            elif event_state['event_type'] == EventType.Vector:
                triple_v = json.loads(event_state['payload'])
                db_manager.insert_embedding(
        event_id=triple_v['event_id'],
        embeddings=triple_v['embeddings'],
    )
    
    llm_instance.subscribe(EventType.Graph, StateChangeCallback())
    llm_instance.subscribe(EventType.Vector, StateChangeCallback())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )
    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)

if __name__ == "__main__":
    asyncio.run(ingest_all_async())
