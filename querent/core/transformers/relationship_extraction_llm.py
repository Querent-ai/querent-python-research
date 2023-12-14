import json
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.querent_event import EventState, EventType
from typing import Any, List, Tuple
from querent.kg.ner_helperfunctions.graph_manager_semantic import Semantic_KnowledgeGraphManager
from querent.kg.rel_helperfunctions.BSM_relationfilter import BSMBranch
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.kg.rel_helperfunctions.questionanswer_llama2 import QASystem
from querent.kg.rel_helperfunctions.rel_normalize import TextNormalizer
from querent.logging.logger import setup_logger
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.common.types.querent_queue import QuerentQueue
from langchain.docstore.document import Document
import ast

"""
    A class that extends the EventCallbackInterface to extract relationships between entities in a contextual triple(s) to create semantic triples for a Knowledge Graph.

    The RelationExtractor is responsible for handling events, particularly updates to a Named Entity Recognition (NER)
    graph, and extracting relationships between entities. It uses an embedding store for efficient similarity searches
    and a QA system for relationship extraction.

    Attributes:
        logger (Logger): A logging instance for recording events and errors.
        config (RelationshipExtractorConfig): Configuration settings for the relationship extractor.
        create_emb (EmbeddingStore): An instance of EmbeddingStore for handling vector storage and retrieval.
        template (str): The template string for QA prompts.
        qa_system (QASystem): An instance of QASystem for asking questions about relationships.

    Methods:
        handle_event(event_type: EventType, event_state: EventState): Handles the event based on the type and state.
        validate(data) -> bool: Validates the input data format for relationship extraction.
        process_event(event_state: EventState): Processes the event and extracts relationships.
        normalizetriples_buildindex(triples): Normalizes triples and builds a FAISS index for them.
        extract_relationships(triples): Extracts relationships from triples using QA prompts.
        trim_triples(data): Trims triples to a required format.
        build_faiss_index(data): Builds a FAISS index from the provided data.
    """

class RelationExtractor():
    def __init__(self, config: RelationshipExtractorConfig):  
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        try:
            super().__init__()
            self.config = config
            self.create_emb = EmbeddingStore(vector_store_path=config.vector_store_path)
            self.qa_system = QASystem(
                rel_model_path=config.model_path,
                rel_model_type=config.model_type,
                emb_model_name=config.emb_model_name,
                faiss_index_path=config.faiss_index_path
                )
            self.qa_system_bsm_validator = QASystem(
                rel_model_path=config.bsm_validator_model_path,
                rel_model_type=config.bsm_validator_model_type,
                emb_model_name=config.emb_model_name,
                faiss_index_path=config.faiss_index_path
                )
            self.bsmbranch = BSMBranch()
            self.sub_tasks = config.dynamic_sub_tasks
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise Exception(f"Initialization failed: {e}")
    
    def validate(self, data) -> bool:
        try:
            if not data:
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Empty List Error")
                return False

            if not isinstance(data, list):
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Not a list")
                return False

            item = data[0]
            if not isinstance(item, tuple) or len(item) != 3:
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Item is not a triple")
                return False

            if not (isinstance(item[0], str) and isinstance(item[2], str) and isinstance(item[1], str)):
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Incorrect item format")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error in validation: {e}")
            return False

    def process_tokens(self, event_state: EventState):
        try:
            triples = event_state.payload
            trimmed_triples = self.normalizetriples_buildindex(triples)
            relationships = self.extract_relationships(triples)
            graph_manager = Semantic_KnowledgeGraphManager()
            graph_manager.feed_input(relationships)
            final_triples = graph_manager.retrieve_triples()
        
            return final_triples
        
        except Exception as e:
            self.logger.error(f"Error in processing event: {e}")
            raise Exception(f"Invalid in processing event: {e}")

    def normalizetriples_buildindex(self, triples):
        try:
            if not self.validate(triples):
                self.logger.error("Invalid triples for relationship extractor")
                raise ValueError("Invalid triples for relationship extractor")
            normalizer = TextNormalizer()
            normalized_triples = normalizer.normalize_triples(triples)
            trimmed_triples = self.trim_triples(normalized_triples)
            self.build_faiss_index(trimmed_triples)
            return trimmed_triples
        except Exception as e:
            self.logger.error(f"Error in normalizing/building index: {e}")
            raise Exception(f"Error in normalizing/building index: {e}")
    
    def create_semantic_triple(self, input1, input2):
        input1_data = ast.literal_eval(input1)
        input2_data = ast.literal_eval(input2)
        print()
        triple = (
            input1_data.get("subject",""),
            json.dumps({
                "predicate": input1_data.get("predicate",""),
                "predicate_type": input1_data.get("predicate_type",""),
                "context": input2_data.get("context", ""),
                "file_path": input2_data.get("file_path", "")
            }),
            input1_data.get("object","")
        )
        return triple

    def extract_relationships(self, triples):
        try:
            updated_triples = []
            for _, predicate_str, _ in triples:
                all_tasks = []
                documents=[]
                data = json.loads(predicate_str)
                context = data['context']
                predicate = predicate_str if isinstance(predicate_str, dict) else json.loads(predicate_str)
                doc =  Document(page_content=context)
                documents.append(doc)
                all_tasks.append((" I want to define a semantic knowledge graph triple (Subject, Predicate, Object). The Subject is {entity1} and the Object is {entity2}.").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', '')))
                sub_task_list_llm = self.bsmbranch.create_sub_tasks(llm = self.qa_system.llm, template=self.config.get_template("default"), tasks=all_tasks,model_type=self.qa_system.rel_model_type)
                for task in sub_task_list_llm:    
                    answer_relation = self.qa_system.ask_question(prompt=task[2], top_docs=documents, llm_chain=task[0])
                    try:
                        updated_triple= self.create_semantic_triple(answer_relation, predicate_str)
                        updated_triples.append(updated_triple)
                    except Exception as e:
                        print("Error : ", e)
            return updated_triples
        except Exception as e:
            self.logger.error(f"Error in extracting relationships: {e}")

    def trim_triples(self, data):
        try:
            trimmed_data = []
            for entity1, predicate, entity2 in data:
                predicate_dict = json.loads(predicate)
                trimmed_predicate = {
                    'context': predicate_dict.get('context', ''),
                    'entity1_nn_chunk': predicate_dict.get('entity1_nn_chunk', ''),
                    'entity2_nn_chunk': predicate_dict.get('entity2_nn_chunk', ''),
                    'file_path': predicate_dict.get('file_path', '')
                }
                trimmed_data.append((entity1, trimmed_predicate, entity2))

            return trimmed_data
        except Exception as e:
            self.logger.error(f"Error in trimming triples: {e}")
            raise Exception(f'Error in trimming triples: {e}')
    
    def build_faiss_index(self, data):
        try:
            contexts = set()
            for _, predicate, _ in data:
                context = predicate.get('context', '')
                context = context.encode().decode('unicode_escape')
                contexts.add(context)
            self.create_emb.create_index(texts=contexts, verbose=True)
            self.create_emb.save_index('my_FAISS_index')
        except Exception as e:
            self.logger.error(f"Error in building FAISS index: {e}")
            raise Exception(f'Error in building FAISS Index : {e}')