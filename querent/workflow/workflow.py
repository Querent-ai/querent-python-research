"""File to start workflow"""
import asyncio
import json
import threading
from typing import Any
import uuid
import os
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.channel.channel_interface import ChannelCommandInterface
from querent.common.types.ingested_tokens import IngestedTokens
from querent.config.config import Config
from querent.config.workflow.workflow_config import WorkflowConfig
from querent.config.resource.resource_config import ResourceConfig
from querent.config.collector.collector_config import CollectorConfig
from querent.config.core.llm_config import LLM_Config
from querent.config.core.gpt_llm_config import GPTConfig
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM
from querent.common.types.querent_event import  EventState, EventType
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager

import asyncio

# async def task1():
#     print("Task 1 started")
#     # Simulate a task
#     # await asyncio.sleep(1)
#     print("Task 1 completed")


# async def task2():
#     # result_queue = asyncio.Queue()
#     print("Task 2 started")
#     # llm_config = LLM_Config(rel_model_path = "/tests/llama-2-7b-chat.Q5_K_M.gguf", grammar_file_path = "/tests/json.gbnf")
#     print("Task 2 completed")
#     # BERTLLM(result_queue, llm_config)
#     # Simulate a task
#     # await asyncio.sleep(1)
#     print("Task 2 completed")

# from transformers import AutoTokenizer, AutoModelForTokenClassification

# async def start_workflow(config_dict: dict):
#     print("Starting workflow with configuration:", config_dict)
#     # loop = asyncio.get_running_loop()

#     # Function to load tokenizer
#     def load_tokenizer():
#         print("Loading tokenizer")
#         # return AutoTokenizer.from_pretrained('dbmdz/bert-large-cased-finetuned-conll03-english')
#         AutoModelForTokenClassification.from_pretrained('/GeoBERT/', output_attentions=True, from_tf=True)
#         print("Ending Tokenizer----------------------------------")
        
#     # Run the synchronous function in an executor
#     # await asyncio.to_thread(load_tokenizer)
#     load_tokenizer()
#     print("Ending Tokenizer----------------------------------")



async def start_workflow(config_dict: dict):
    print("Starting workflow with configuration:", config_dict)
    from huggingface_hub import InferenceClient
    client = InferenceClient(model = "botryan96/GeoBERT", token="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")

    tokens = client.token_classification("In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe.")
    print ("Tokens Produced ------------------------------------", tokens)

    
    # Create tasks
    # task_1 = asyncio.create_task(task1())
    # task_2 = asyncio.create_task(task2())
    # task2()
    # Gather and run tasks concurrently
    # await asyncio.gather(task_1, task_2)

    print("Workflow completed. Results:")





# async def start_workflow(config_dict: Any):
#     #Start the workflow
#     print("----------------------------------------------------------------Print the configuration :", config_dict)
#     print(f"In Workflow thread11111111111111: {threading.current_thread().name}")
#     workflow_config = config_dict.get("workflow")
#     workflow = WorkflowConfig(config_source=workflow_config)
#     collector_configs = config_dict.get("collectors", [])
#     collectors = []
#     for collector_config in collector_configs: 
#         collectors.append(CollectorConfig(config_source=collector_config).resolve())

#     engine_configs = config_dict.get("engines", [])
#     engines = []
#     for engine_config in engine_configs:
#         engine_config_source = engine_config.get("config",{})
#         if engine_config["name"] == "knowledge_graph_using_openai_v1":
#             engines.append(GPTConfig(config_source = engine_config_source))
#         elif engine_config["name"] == "knowledge_graph_using_llama2_v1":
#             engines.append(LLM_Config(config_source=engine_config_source))
#     # resource_config = config_dict.get("resource")
#     # print("Resource config acquired---------", type(resource_config))
#     # resource = ResourceConfig(config_source=resource_config)
#     # config_dict["resource"] = resource
#     config_dict["engines"] = engines 
#     config_dict["collectors"] = collectors 
#     config_dict["workflow"] = workflow
#     config = Config(config_source=config_dict)
#     print(f"In Workflow thread22222222222222: {threading.current_thread().name}")
#     # while True :
#     #     print("⌛ Waiting for querent to start...sending dummy events")
#     #     message_state = config.workflow.channel.receive_in_python()
#     #     tokens_received = config.workflow.tokens_feader.receive_tokens_in_python()

#     #     if tokens_received is not None:
#     #         print("📜 Received tokens: " + str(tokens_received['data']))

#     #     if message_state is not None:
#     #         message_type = message_state['message_type']

#     #         if message_type.lower() == "stop":
#     #             print("🛑 Received stop signal. Exiting...")
#     #             break
#     #         else:
#     #             print("📬 Received message of type: " + message_type)
#     #             # Handle other message types...

#     #     # Continue sending events
#     #     if config_dict['workflow'] is not None:
#             # event_type = "Graph"  # Replace with the desired event type
#             # payload = {
#             #     "subject": "Querent AI LLCA",
#             #     "subject_type": "Organization",
#             #     "object": "Querent",
#             #     "object_type": "Software",
#             #     "predicate": "developed by",
#             #     "predicate_type": "ownership",
#             #     "sentence": "Querent is developed by Querent AI LLC"
#             # }
#             # event_data = {
#             #     "event_type": event_type,
#             #     "timestamp": 123.45,  # Replace with the actual timestamp
#             #     "payload": json.dumps(payload),
#             #     "file": "file_name"  # Replace with the actual file name
#             # }
#             # config.workflow.event_handler.handle_event(event_type, event_data)

#     #     await asyncio.sleep(1)
#     workflows = {"knowledge_graph_using_openai_v1": start_gpt_workflow,
#                "knowledge_graph_using_llama2_v1": start_llama_workflow}
#     print("Workflow name captured.............................")
#     workflow = workflows.get(config.workflow.name)
#     print("Workflow name captured.............................AGAIN")
#     await workflow(config)
#     print(f"In Workflow thread433333333333333333: {threading.current_thread().name}")


# async def start_gpt_workflow(config: Config):
#     collectors = []
#     for collector_config in config.collectors:
#         uri = Uri(collector_config.uri)
#         collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

#     for collector in collectors:
#         await collector.connect()

#     result_queue = asyncio.Queue()

#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue
#     )

#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

#     resource_manager = ResourceManager()

#     llm_instance = GPTLLM(result_queue, config.engines[0])

#     llm_instance.subscribe(EventType.Graph, config.workflow.event_handler())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
#     token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=GPTLLM.state_queue))
#     await asyncio.gather(ingest_task, querent_task, token_feeder)


# #Config workflow channel for setting termination event
# async def receive_token_feeder(resource_manager: ResourceManager, config: Config, result_queue: asyncio.Queue, state_queue: asyncio.Queue):
#     while not resource_manager.querent_termination_event.is_set():
#         tokens = config.workflow.tokens_feader.receive_tokens_in_python()
#         message_state = config.workflow.channel.receive_in_python()
#         if tokens is not None:
#             #we will get a dictionary here
#             result_queue.put_nowait(tokens)
#         if message_state is not None:
#             state_queue.put_nowait(message_state)

# async def start_llama_workflow(config: Config):
#     print("Inside llama Configuration ------------------", config)
#     collectors = []
#     for collector_config in config.collectors:
#         uri = Uri(collector_config.uri)
#         collectors.append(CollectorResolver().resolve(uri=uri, config = collector_config))

#     for collector in collectors:
#         await collector.connect()
#         print("Inside llama Collector ------------------")

#     result_queue = asyncio.Queue()

#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue
#     )
#     print("Ingestor Factory Manager Intialized")
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
#     await asyncio.gather(ingest_task)
#     print("Workflow Ingest Task Created.......................")
#     # resource_manager = config.resource
#     resource_manager = ResourceManager()
#     config.engines[0].rel_model_path = "/tests/llama-2-7b-chat.Q5_K_M.gguf"
#     config.engines[0].grammar_file_path = "/tests/json.gbnf"
#     config.engines[0].ner_model_name = "/GeoBERT/"
#     print("-----------------------", config.engines[0])
#     llm_instance = BERTLLM(result_queue, config.engines[0])
#     print("Initialized------------------------------------------------------------------------")
#     # event_type = "Graph"  # Replace with the desired event type
#     # payload = {
#     #             "subject": "Querent AI LLCA",
#     #             "subject_type": "Organization",
#     #             "object": "Querent",
#     #             "object_type": "Software",
#     #             "predicate": "developed by",
#     #             "predicate_type": "ownership",
#     #             "sentence": "Querent is developed by Querent AI LLC"
#     #         }
#     # event_data = {
#     #             "event_type": event_type,
#     #             "timestamp": 123.45,  # Replace with the actual timestamp
#     #             "payload": json.dumps(payload),
#     #             "file": "file_name"  # Replace with the actual file name
#     #         }
#     print("Type of Event Handler--------------------------------", type(config.workflow.event_handler))
#     # config.workflow.event_handler.handle_event(event_type, event_data)
#     print("Retrieve event handler and subscribe to graph event ---------------------------")
#     print(f"In Workflow thread5555555555555: {threading.current_thread().name}")
#     # llm_instance.subscribe(EventType.Graph, config.workflow.event_handler)
#     # querent = Querent(
#     #     [llm_instance],
#     #     resource_manager=resource_manager,
#     # )
#     print("Querent Initializeddddddddddddddddddddddddddddddddddddddddddddddddddddd")
#     # querent_task = asyncio.create_task(querent.start())
#     # await asyncio.gather(querent_task)
#     token_feeder = asyncio.create_task(receive_token_feeder(resource_manager=resource_manager, config=config, result_queue=result_queue, state_queue=llm_instance.state_queue))
#     # await asyncio.gather(ingest_task, querent_task, token_feeder) # Loop and do config.workflow.channel for termination event messageType = "stop"
#     await asyncio.gather(token_feeder) # Loop and do config.workflow.channel for termination event messageType = "stop"

#      # Adjust the sleep duration as needed