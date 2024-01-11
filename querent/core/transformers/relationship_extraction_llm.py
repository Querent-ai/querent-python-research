import json
from typing import Any, List, Tuple
from querent.kg.rel_helperfunctions.BSM_relationfilter import BSMBranch
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.kg.rel_helperfunctions.questionanswer_llama2 import QASystem
from querent.kg.rel_helperfunctions.rag_retriever import RAGRetriever
from querent.kg.rel_helperfunctions.rel_normalize import TextNormalizer
from querent.logging.logger import setup_logger
from querent.config.core.relation_config import RelationshipExtractorConfig
from langchain.docstore.document import Document
import ast

"""
    A class for extracting relationships from triples and processing them for various representations.

    This class includes methods for validating triples, generating embeddings, processing tokens, 
    normalizing and building indices for triples, creating semantic triples, extracting relationships, 
    and trimming triples.

    Attributes:
        config (RelationshipExtractorConfig): Configuration settings for the relationship extractor.
        logger (Logger): Logger for logging messages and errors.
        create_emb (EmbeddingStore): An instance of EmbeddingStore for generating embeddings.
        qa_system (QASystem): A question-answering system for extracting relationships.
        rag_approach (bool): A flag indicating whether to use the RAG approach for retrieval.
        rag_retriever (RAGRetriever): A RAG retriever for document retrieval, used if rag_approach is True.
        bsmbranch (BSMBranch): An instance of BSMBranch for handling BSM-related tasks.
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
    def __init__(self, config: RelationshipExtractorConfig):  
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        try:
            super().__init__()
            self.config = config
            self.create_emb = EmbeddingStore(vector_store_path=config.vector_store_path)
            self.qa_system = QASystem(
                rel_model_path=config.model_path,
                rel_model_type=config.model_type,
                )
            
            # self.qa_system_bsm_validator = QASystem(
            #     rel_model_path=config.bsm_validator_model_path,
            #     rel_model_type=config.bsm_validator_model_type,
            #     emb_model_name=config.emb_model_name,
            #     faiss_index_path=config.get_faiss_index_path()
            #     )
            self.rag_approach = config.rag_approach
            if  self.rag_approach == True:
                self.rag_retriever = RAGRetriever(
                faiss_index_path=config.get_faiss_index_path(),
                emb_model_name=config.emb_model_name,
                embedding_store=self.create_emb,
                logger=self.logger)
            self.bsmbranch = BSMBranch()
            self.sub_tasks = config.dynamic_sub_tasks
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
    
    def process_tokens(self, payload):
        try:
            triples = payload
            trimmed_triples = self.normalizetriples_buildindex(triples)
            if self.rag_approach == True:
                self.rag_retriever.build_faiss_index(trimmed_triples)
            relationships = self.extract_relationships(triples)
        
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
        input1_data = ast.literal_eval(input1)
        input2_data = ast.literal_eval(input2)
        triple = (
            input1_data.get("subject",""),
            json.dumps({
                "predicate": input1_data.get("predicate",""),
                "predicate_type": input1_data.get("predicate_type","Unlabeled"),
                "context": input2_data.get("context", ""),
                "file_path": input2_data.get("file_path", ""),
                "subject_type": input1_data.get("subject_type","Unlabeled"),
                "object_type": input1_data.get("object_type","Unlabeled")
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
                if self.rag_approach == True:
                    db = self.rag_retriever.load_faiss_index()
                    prompt=("What is the relationship between {entity1} and the Object is {entity2}.").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', ''))
                    top_docs = self.rag_retriever.retrieve_documents(db, prompt=prompt)
                    documents = top_docs
                else:
                    doc =  Document(page_content=context)
                    documents.append(doc)   
                all_tasks.append(("""Entity 1: {entity1} and Entity 2: {entity2}.
                    Determine which entity is the subject and which is the object in the context along with the predicate between the entities. Please also identify the subject type, predicate type and object type.""").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', '')))
                
                # all_tasks.append((" I want to define a semantic knowledge graph. The Subject is {entity1} and the Object is {entity2}. Please also identify the subject type, predicate type and object type").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', '')))
                # all_tasks.append(("I want to define a semantic knowledge graph where the subject is {entity1} and the object is {entity2}. Please also identify the subject type, predicate type and object type.").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', '')))
                sub_task_list_llm = self.bsmbranch.create_sub_tasks(llm = self.qa_system.llm, template=self.config.get_template("default1"), tasks=all_tasks,model_type=self.qa_system.rel_model_type)
                for task in sub_task_list_llm:  
                    answer_relation = self.qa_system.ask_question(prompt=task[2], top_docs=documents, llm_chain=task[0])
                    print("Answer relation------------------------", answer_relation)
                    try:
                        updated_triple= self.create_semantic_triple(answer_relation, predicate_str)
                        updated_triples.append(updated_triple)
                    except:
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
                    'file_path': predicate_dict.get('file_path', '')
                }
                trimmed_data.append((entity1, trimmed_predicate, entity2))

            return trimmed_data
        
        except Exception as e:
            self.logger.error(f"Error in trimming triples: {e}")
            raise Exception(f'Error in trimming triples: {e}')
  
