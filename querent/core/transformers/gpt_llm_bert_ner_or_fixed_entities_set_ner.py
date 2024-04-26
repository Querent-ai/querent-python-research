import json
from querent.core.transformers.fixed_entities_set_opensourcellm import Fixed_Entities_LLM
from querent.kg.ner_helperfunctions.fixed_predicate import FixedPredicateExtractor
from querent.config.core.gpt_llm_config import GPTConfig
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.common.types.ingested_images import IngestedImages
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.kg.rel_helperfunctions.openai_functions import FunctionRegistry
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from typing import Any, List, Tuple
from querent.kg.rel_helperfunctions.triple_to_json import TripleToJsonConverter
from querent.logging.logger import setup_logger
from querent.config.core.llm_config import LLM_Config
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    wait_fixed
)
from dotenv import load_dotenv, find_dotenv
import json

_ = load_dotenv(find_dotenv())


class GPTLLM(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        config: GPTConfig
    ):
        self.logger = setup_logger(__name__, "OPENAILLM")
        try:
            super().__init__(input_queue)
            llm_config = LLM_Config(
            ner_model_name=config.ner_model_name,
            enable_filtering=config.enable_filtering,
            filter_params={
                'score_threshold': config.filter_params['score_threshold'],
                'attention_score_threshold': config.filter_params['attention_score_threshold'],
                'similarity_threshold': config.filter_params['similarity_threshold'],
                'min_cluster_size': config.filter_params['min_cluster_size'],
                'min_samples': config.filter_params['min_samples'],
                'cluster_persistence_threshold':config.filter_params['cluster_persistence_threshold']
            },
            sample_entities = config.sample_entities,
            fixed_entities = config.fixed_entities,
            skip_inferences= True,
            is_confined_search = config.is_confined_search,
            huggingface_token = config.huggingface_token,
            spacy_model_path = config.spacy_model_path,
            nltk_path = config.nltk_path)
            self.fixed_entities = config.fixed_entities
            self.is_confined_search = config.is_confined_search
            self.fixed_relationships = config.fixed_relationships
            self.sample_relationships = config.sample_relationships
            self.user_context = config.user_context
            self.nlp_model = NER_LLM.set_nlp_model(config.spacy_model_path)
            self.nlp_model = NER_LLM.get_class_variable()
            if self.fixed_relationships and not self.sample_relationships:
                raise ValueError("If specific predicates are provided, their types should also be provided.")
            if self.fixed_relationships and self.sample_relationships:
                self.predicate_context_extractor = FixedPredicateExtractor(fixed_predicates=self.fixed_relationships, predicate_types=self.sample_relationships,  model = self.nlp_model)
            elif self.sample_relationships:
                self.predicate_context_extractor = FixedPredicateExtractor(predicate_types=self.sample_relationships,  model = self.nlp_model)
            else:
                self.predicate_context_extractor = None
            self.create_emb = EmbeddingStore()
            if config.is_confined_search:
                self.llm_instance = Fixed_Entities_LLM(input_queue, llm_config, self.create_emb)
            else :
                self.llm_instance = BERTLLM(input_queue, llm_config, self.create_emb)
            self.rel_model_name = config.rel_model_name
            if config.openai_api_key:
                self.gpt_llm = OpenAI(api_key=config.openai_api_key)
            else:
                self.gpt_llm = OpenAI()
            self.function_registry = FunctionRegistry()
            
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
            raise Exception(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
    
    def validate(self) -> bool:
        return isinstance(self.llm_instance, BERTLLM) or isinstance(self.llm_instance, Fixed_Entities_LLM)

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    
    def process_images(self, data: IngestedImages):
        return super().process_messages(data)

    async def process_code(self, data: IngestedCode):
        return super().process_messages(data)

    @staticmethod
    def validate_ingested_tokens(data: IngestedTokens) -> bool:
        if data.is_error():
            
            return False

        return True
    def extract_semantic_triples(self, chat_completion):
    # Extract the message content from the ChatCompletion
        message_content = chat_completion.choices[0].message.content.replace('\n', '')

        # Parse the JSON content into a Python list
        try:
            triples_list = eval(message_content)
            if not isinstance(triples_list, list):
                raise ValueError("Content is not a list")
        except Exception as e:
            return []

        return triples_list

    @staticmethod
    def remove_items_from_tuples(data: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        result = []
        keys_to_remove = ['entity1_embedding', 'entity2_embedding', 'entity1_attnscore', 'entity2_attnscore', 'pair_attnscore']

        for tup in data:
            json_data = json.loads(tup[1])
            for key in keys_to_remove:
                json_data.pop(key, None)
            modified_json_str = json.dumps(json_data, ensure_ascii=False)
            modified_tuple = (tup[0], modified_json_str, tup[2])
            result.append(modified_tuple)

        return result
    
    async def process_triples(self, context, entity1, entity2, entity1_label, entity2_label):
        try: 
            if not self.user_context:
                identify_entity_message = f"""Please analyze the provided context below. Once you have understood the context, answer the user query using the specified output format.
        
                    Context: {context}
                    Entity 1: {entity1} and Entity 2: {entity2}
                    Output Format:
                    [
                        {{
                            'subject': 'Identified as the main entity in the context, typically the initiator or primary focus of the action or topic being discussed.',
                            'predicate': 'The relationship (predicate) between the subject and the object.',
                            'object': 'This parameter represents the entity in the context directly impacted by or involved in the action, typically the recipient or target of the main verb's action.',
                            'subject_type': 'The category of the subject entity e.g. location, person, event, material, process etc.',
                            'object_type': 'The category of the object entity e.g. location, person, event, material, process etc.',
                            'predicate_type': 'The category of the predicate e.g. causative, action, ownership, occurance etc.'
                        }},
                    ]
                    """
                messages_classify_entity = [
                    {"role": "user", "content": identify_entity_message},
                    {"role": "user", "content": "Query: First, identify all geological entities in the provided context. Then, create relevant semantic triples (Subject, Predicate, Object) and also categorize the respective the Subject, Object types (e.g. location, person, event, material, process etc.) and Predicate type. Use the above output format to provide all the relevant semantic triples."},
                ]
            elif self.user_context and self.fixed_entities :
                identify_entity_message = f"""Please analyze the provided context below. Once you have understood the context, answer the user query using the specified output format.
        
                    Context: {context}
                    Entity 1: {entity1} and Entity 2: {entity2}
                    Entity 1_Type: {entity1_label} and Entity 2_Type: {entity2_label}
                    Output Format:
                    [
                        {{
                            'subject': 'Identified as the main entity in the context, typically the initiator or primary focus of the action or topic being discussed.',
                            'predicate': 'The relationship (predicate) between the subject and the object.',
                            'object': 'This parameter represents the entity in the context directly impacted by or involved in the action, typically the recipient or target of the main verb's action.',
                            'subject_type': 'The category of the subject entity e.g. location, person, event, material, process etc.',
                            'object_type': 'The category of the object entity e.g. location, person, event, material, process etc.',
                            'predicate_type': 'The category of the predicate e.g. causative, action, ownership, occurance etc.'
                        }},
                    ]
                    """
                messages_classify_entity = [
                    {"role": "user", "content": identify_entity_message},
                    {"role": "user", "content": self.user_context},
                ]
            elif self.user_context and not self.fixed_entities :
                identify_entity_message = f"""Please analyze the provided context below. Once you have understood the context, answer the user query using the specified output format.
        
                    Context: {context}
                    Entity 1: {entity1} and Entity 2: {entity2}
                    Output Format:
                    [
                        {{
                            'subject': 'Identified as the main entity in the context, typically the initiator or primary focus of the action or topic being discussed.',
                            'predicate': 'The relationship (predicate) between the subject and the object.',
                            'object': 'This parameter represents the entity in the context directly impacted by or involved in the action, typically the recipient or target of the main verb's action.',
                            'subject_type': 'The category of the subject entity e.g. location, person, event, material, process etc.',
                            'object_type': 'The category of the object entity e.g. location, person, event, material, process etc.',
                            'predicate_type': 'The category of the predicate e.g. causative, action, ownership, occurance etc.'
                        }},
                    ]
                    """
                messages_classify_entity = [
                    {"role": "user", "content": identify_entity_message},
                    {"role": "user", "content": self.user_context},
                ]
            identify_predicate_response = self.generate_response(
                messages_classify_entity,
                "predicate_info"
            )
            semantic_triples = self.extract_semantic_triples(identify_predicate_response)
            if len(semantic_triples)>0:
                return {
                    'subject_type': semantic_triples[0]['subject_type'].lower().replace(" ", "_"),
                    'subject': semantic_triples[0]['subject'].lower(),
                    'object_type': semantic_triples[0]['object_type'].lower().replace(" ", "_"),
                    'object': semantic_triples[0]['object'].lower(),
                    'predicate': semantic_triples[0]['predicate'].lower(),
                    'predicate_type': semantic_triples[0]['predicate_type'].lower().replace(" ", "_")
                }   
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to process triples using GPT. {e}")

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(self, **kwargs):
        return self.gpt_llm.chat.completions.create(**kwargs)
    
    def generate_response(self, messages, name):
        response = self.completion_with_backoff(
            model=self.rel_model_name,
            messages=messages,
            temperature=0
        )
        return response

    def generate_output_tuple(self,result, context_json):
        context_data = json.loads(context_json)
        context = context_data.get("context", "")
        subject_type = result.get("subject_type", "Unlabeled")
        subject = result.get("subject", "")
        object_type = result.get("object_type", "Unlabeled")
        object = result.get("object", "")
        predicate = result.get("predicate", "")
        predicate_type = result.get("predicate_type", "Unlabled")
        output_tuple = (
            subject,
            f'{{"predicate": "{predicate}", "predicate_type": "{predicate_type}", "context": "{context}", "file": "{context_data.get("file_path", "")}", "subject_type": "{subject_type}", "object_type": "{object_type}"}}',
            object
        )

        return output_tuple
      
    async def process_tokens(self, data: IngestedTokens):
        try:
            if not GPTLLM.validate_ingested_tokens(data):
                    self.set_termination_event()                    
                    return 
            
            doc_source = data.doc_source
            relationships = []
            result = await self.llm_instance.process_tokens(data)
            if not result: return 
            else:
                filtered_triples, file = result
                modified_data = GPTLLM.remove_items_from_tuples(filtered_triples)
                for entity1, context_json, entity2 in modified_data:
                    context_data = json.loads(context_json)
                    context = context_data.get("context", "")
                    entity1_label = context_data.get("entity1_label", "")
                    entity2_label = context_data.get("entity2_label", "")
                    entity1_nn_chunk = context_data.get("entity1_nn_chunk","")
                    entity2_nn_chunk = context_data.get("entity2_nn_chunk","")
                    result = await self.process_triples(context, entity1_nn_chunk, entity2_nn_chunk, entity1_label, entity2_label)
                    if result:
                        output_tuple = self.generate_output_tuple(result, context_json)
                        relationships.append(output_tuple)
                if len(relationships) > 0:
                    embedding_triples = self.create_emb.generate_embeddings(relationships)
                    if self.sample_relationships:
                            embedding_triples = self.predicate_context_extractor.process_predicate_types(embedding_triples)
                    for triple in embedding_triples:
                        if not self.termination_event.is_set():
                            graph_json = json.dumps(TripleToJsonConverter.convert_graphjson(triple))
                            if graph_json:
                                    current_state = EventState(EventType.Graph,1.0, graph_json, file, doc_source=doc_source)
                                    await self.set_state(new_state=current_state)
                            vector_json = json.dumps(TripleToJsonConverter.convert_vectorjson(triple))
                            if vector_json:
                                    current_state = EventState(EventType.Vector,1.0, vector_json, file, doc_source=doc_source)
                                    await self.set_state(new_state=current_state)
                        else:
                            return
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to extract predicates using GPT. {e}")
            raise Exception(f"An error occurred while extracting predicates using GPT: {e}")

    async def process_messages(self, data: IngestedMessages):
        raise NotImplementedError