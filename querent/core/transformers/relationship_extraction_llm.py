import json
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.querent_event import EventState, EventType
from typing import Any, List, Tuple
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.kg.rel_helperfunctions.questionanswer_llama2 import QASystem
from querent.kg.rel_helperfunctions.rel_normalize import TextNormalizer
from querent.logging.logger import setup_logger
from querent.config.core.relation_config import RelationshipExtractorConfig

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

class RelationExtractor(EventCallbackInterface):
    def __init__(self, config: RelationshipExtractorConfig):  
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        try:
            super().__init__()
            self.config = config
            self.create_emb = EmbeddingStore(vector_store_path=config.vector_store_path)
            self.template = config.qa_template
            self.qa_system = QASystem(
                rel_model_path=config.rel_model_path,
                rel_model_type='llama',
                emb_model_name=config.emb_model_name,
                faiss_index_path=config.faiss_index_path,
                template=self.template
            )
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise Exception(f"Initialization failed: {e}")

    async def handle_event(self, event_type: EventType, event_state: EventState):
        try:
            if event_type == EventType.NER_GRAPH_UPDATE:
                await self.process_event(event_state)
        except Exception as e:
            self.logger.error(f"Error in handling event: {e}")

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

    async def process_event(self, event_state: EventState):
        try:
            triples = event_state.payload
            trimmed_triples = self.normalizetriples_buildindex(triples)
            relationships = self.extract_relationships(trimmed_triples)
            
            return relationships
        
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

    def extract_relationships(self, triples):
        try:
            question_entities_validate = "I would like to define a knowledge graph triple, do {entity1} and {entity2} show relationship ? Just give a yes or no answer."
            question_entities_relation = "Please find possible relationships between {entity1} and {entity2}"
            updated_triples = []
            for entity1, predicate_str, entity2 in triples:
                predicate = predicate_str if isinstance(predicate_str, dict) else json.loads(predicate_str)
                # Ask the first question
                validation_prompt = question_entities_validate.format(entity1=entity1, entity2=entity2)
                answer_validate = self.qa_system.ask_question(prompt=validation_prompt, search_kwargs={'k': 3})

                if "yes" in answer_validate.lower():
                    # Ask the second question
                    relation_prompt = question_entities_relation.format(entity1=entity1, entity2=entity2)
                    answer_relation = self.qa_system.ask_question(prompt=relation_prompt, search_kwargs={'k': 3})
                    predicate['relationship'] = answer_relation
                updated_predicate_str = json.dumps(predicate)
                updated_triples.append((entity1, updated_predicate_str, entity2))

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
                    'entity1_label': predicate_dict.get('entity1_label', ''),
                    'entity2_label': predicate_dict.get('entity2_label', '')
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
            self.create_emb.create_index(texts=contexts, verbose=False)
            self.create_emb.save_index('my_FAISS_index')
        except Exception as e:
            self.logger.error(f"Error in building FAISS index: {e}")
            raise Exception(f'Error in building FAISS Index : {e}')