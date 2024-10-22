import json
from typing import Any, List, Tuple
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.kg.rel_helperfunctions.questionanswer_llama2 import QASystem
from querent.kg.rel_helperfunctions.rel_normalize import TextNormalizer
from querent.logging.logger import setup_logger
from querent.config.core.opensource_llm_config import Opensource_LLM_Config
from llama_cpp import LlamaGrammar

import ast

"""
    A class for extracting relationships from triples and processing them for various representations.

    This class includes methods for validating triples, generating embeddings, processing tokens, 
    normalizing and building indices for triples, creating semantic triples, extracting relationships, 
    and trimming triples.

    Attributes:
        config (Opensource_LLM_Config): Configuration settings for the relationship extractor.
        logger (Logger): Logger for logging messages and errors.
        create_emb (EmbeddingStore): An instance of EmbeddingStore for generating embeddings.
        qa_system (QASystem): A question-answering system for extracting relationships.
        rag_approach (bool): A flag indicating whether to use the RAG approach for retrieval.
        rag_retriever (RAGRetriever): A RAG retriever for document retrieval, used if rag_approach is True.
        sub_tasks (list): List of dynamic sub-tasks for processing.

    Methods:
        validate(data) -> bool:
            Validates the input data to ensure it's in the correct format for processing.
        generate_embeddings(payload):
            Generates embeddings for the given payload containing triples.
        process_tokens(payload):
            Processes tokens in the given payload and extracts relationships.
        normalizetriples_buildindex(triples):
            Normalizes the given triples and builds an index for them.
        create_semantic_triple(input1, input2):
            Creates a semantic triple from the given inputs.
        extract_relationships(triples):
            Extracts relationships from the given triples.
        trim_triples(data):
            Trims the given data to a more concise format.
    """

class RelationExtractor():
    def __init__(self, config: Opensource_LLM_Config, Embedding=None):  
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        try:
            super().__init__()
            self.config = config
            if Embedding is None:
                self.create_emb = EmbeddingStore()
            else:
                self.create_emb = Embedding
            self.qa_system = QASystem(
                rel_model_path=config.model_path,
                rel_model_type=config.model_type,
                )
            self.grammar = LlamaGrammar.from_file(file = config.grammar_file_path)
            self.is_confined_search = config.is_confined_search
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise Exception(f"Initialization failed: {e}")
        
    def validate(self, data) -> bool:
        try:
            if not data:
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Empty List Error"
                )
                return False

            if not isinstance(data, list):
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Not a list"
                )
                return False

            item = data[0]
            if not isinstance(item, tuple) or len(item) != 3:
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Item is not a triple"
                )
                return False

            if not (
                isinstance(item[0], str)
                and isinstance(item[2], str)
                and isinstance(item[1], str)
            ):
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Incorrect item format"
                )
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error in validation: {e}")
            return False
    
    def process_tokens(self, payload, fixed_entities = False):
        try:
            triples = payload
            trimmed_triples = self.normalizetriples_buildindex(triples)
            relationships = self.extract_relationships(triples, fixed_entities)
        
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
            
            return trimmed_triples
        
        except Exception as e:
            self.logger.error(f"Error in normalizing/building index: {e}")
            raise Exception(f"Error in normalizing/building index: {e}")
    
    def create_semantic_triple(self, input1, input2):
        try:   
            if not input1.get("predicate") or not input1.get("subject") or not input1.get("object"):
                raise ValueError("Missing 'subject', 'predicate', or 'object' in llm output") 
            input2_data = ast.literal_eval(input2)
            triple = (
                input1.get("subject",""),
                json.dumps({
                    "predicate": input1.get("predicate",""),
                    "predicate_type": input1.get("predicate_type","Unlabeled"),
                    "context": input2_data.get("context", ""),
                    "file_path": input2_data.get("file_path", ""),
                    "subject_type": input1.get("subject_type","Unlabeled"),
                    "object_type": input1.get("object_type","Unlabeled"),
                    "score":1
                }),
                input1.get("object","")
            )
            return triple
        except Exception as e:
            self.logger.error(f"Error in creating semantic triple: {e}")
            raise Exception(f"Error in creating semantic triple: {e}")
        
    def replace_entities(self, text, entity1, entity2):
        data = json.loads(text)
        if data.get("subject", "").strip() == "Entity 1":
            data["subject"] = entity1
        elif data.get("subject", "").strip() == "Entity 2":
            data["subject"] = entity2

        if data.get("object", "").strip() == "Entity 1":
            data["object"] = entity1
        elif data.get("object", "").strip() == "Entity 2":
            data["object"] = entity2

        return data

    def extract_relationships(self, triples, fixed_entities = False):
        try:
            self.logger.debug(f"Length of identified triples {len(triples)}")
            updated_triples = []
            for _, predicate_str, _ in triples:
                data = json.loads(predicate_str)
                context = data['context']
                predicate = predicate_str if isinstance(predicate_str, dict) else json.loads(predicate_str)
                if fixed_entities == False:
                    query = """Please analyze the provided context and two entities. Use this information to answer the users query below.
Context: {context}
Entity 1: {entity1} and Entity 2: {entity2}
Query:{question}
Answer:"""          
                    if not self.config.qa_template:
                        question = "In the context of a semantic triple framework, first identify which entity is subject and which is the object along with their respective types. Also determine the predicate and predicate type."   
                    else:
                        question = self.config.qa_template
                    query = query.format(question = question, context = context, entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', ''))
                else:
                    query = """Please analyze the provided context and two entities along with their identified labels. Use this information to answer the users query below.
Context: {context}
Entity 1: {entity1} and Entity 1_label: {entity1_label}
Entity 2: {entity2} and Entity 2_label: {entity2_label}
Query:{question}
Answer:"""          
                    if not self.config.qa_template:
                        question = "In the context of a semantic triple framework, first identify which entity is subject and which is the object, validate and output their respective types. Also determine the predicate and predicate type."      
                    else:
                        question = self.config.qa_template
                    query = query.format(question = question, 
                                                context = context, 
                                                entity1=predicate.get('entity1_nn_chunk', ''), 
                                                entity2=predicate.get('entity2_nn_chunk', ''),
                                                entity1_label=predicate.get('entity1_label', ''), 
                                                entity2_label=predicate.get('entity2_label', ''))
                answer_relation = self.qa_system.ask_question(prompt=query, llm=self.qa_system.llm, grammar=self.grammar)
                try:
                    choices_text = answer_relation['choices'][0]['text']
                    answer_relation = self.replace_entities(choices_text,entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk'))
                    updated_triple= self.create_semantic_triple(answer_relation, predicate_str)
                    updated_triples.append(updated_triple)
                except Exception as e:
                    continue
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
                    'entity2_label': predicate_dict.get('entity2_label', ''),
                    'file_path': predicate_dict.get('file_path', '')
                }
                trimmed_data.append((entity1, trimmed_predicate, entity2))

            return trimmed_data
        
        except Exception as e:
            self.logger.error(f"Error in trimming triples: {e}")
            raise Exception(f'Error in trimming triples: {e}')
  
