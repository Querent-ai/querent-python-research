import asyncio
import json
import re

import spacy
from querent.core.transformers.fixed_entities_set_opensourcellm import Fixed_Entities_LLM
from querent.kg.ner_helperfunctions.fixed_predicate import FixedPredicateExtractor
from querent.config.core.gpt_llm_config import GPTConfig
from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
from querent.common.types.ingested_images import IngestedImages
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
from querent.common.types.file_buffer import FileBuffer
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from dotenv import load_dotenv, find_dotenv
import json

_ = load_dotenv(find_dotenv())


class GPTNERLLM(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        config: GPTConfig
    ):
        self.logger = setup_logger(__name__, "OPENAINERLLM")
        try:
            self.nlp = spacy.load('en_core_web_lg')
            super().__init__(input_queue)
            self.file_buffer = FileBuffer()
            self.rel_model_name = config.rel_model_name
            if config.openai_api_key:
                self.gpt_llm = OpenAI(api_key=config.openai_api_key)
            else:
                self.gpt_llm = OpenAI()
            self.function_registry = FunctionRegistry()
            self.create_emb = EmbeddingStore(inference_api_key=config.huggingface_token)
            self.user_context = config.user_context
            
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
            raise Exception(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
    
    def validate(self) -> bool:
        return True

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
    
    def get_context(self, sentences):
        contexts = []
        for i, sentence in enumerate(sentences):
            # Previous sentence or empty string if current sentence is the first
            prev_sentence = sentences[i-1] if i > 0 else ''
            # Next sentence or empty string if current sentence is the last
            next_sentence = sentences[i+1] if i < len(sentences)-1 else ''
            # Current context
            context = f"{prev_sentence} {sentence} {next_sentence}".strip()
            contexts.append(context)
        return contexts
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(self, **kwargs):
        return self.gpt_llm.chat.completions.create(**kwargs)
    
    def generate_response(self, messages):
        response = self.completion_with_backoff(
            model=self.rel_model_name,
            messages=messages,
            temperature=0,
        )
        return response

    def extract_semantic_triples(self, chat_completion):
    # Extract the message content from the ChatCompletion
        message_content = chat_completion.choices[0].message.content.replace('\n', '')

        # Parse the JSON content into a Python list
        try:
            triples_list = eval(message_content)
            if not isinstance(triples_list, list):
                raise ValueError("Content is not a list")
        except Exception as e:
            raise ValueError(f"Error parsing content: {e}")

        return triples_list

    def filter_relevant_triples(self, triples, context, max_distance):
        def tokenize_text(text):
            # Tokenize the text while ignoring common filler words
            filler_words = ["the", "and", "in", "of", "a", "an", "to", "with"]
            tokens = re.findall(r'\b\w+\b', text)
            tokens = [token.lower() for token in tokens if token.lower() not in filler_words]
            return tokens

        def calculate_distance(tokenized_text, subject, object):
            # Find the start index of subject and object in tokenized_text
            subject_tokens = tokenize_text(subject)
            object_tokens = tokenize_text(object)
            
            subject_start_index = None
            object_start_index = None
            
            for i in range(len(tokenized_text)):
                if tokenized_text[i:i+len(subject_tokens)] == subject_tokens:
                    subject_start_index = i
                    break
            
            for i in range(len(tokenized_text)):
                if tokenized_text[i:i+len(object_tokens)] == object_tokens:
                    object_start_index = i
                    break
            
            if subject_start_index is not None and object_start_index is not None:
                return abs(subject_start_index - object_start_index)
            else:
                return float('inf')  # Return a large distance if either subject or object is not found

        tokenized_context = tokenize_text(context.lower())  # Convert context to lowercase
        relevant_triples = []
        
        for triple in triples:
            subject = triple['subject'].lower()  # Convert subject to lowercase
            object = triple['object'].lower()    # Convert object to lowercase
            
            distance = calculate_distance(tokenized_context, subject, object)
            
            if distance <= max_distance:
                triple['subject'] = subject
                triple['object'] = object
                triple['subject_type'] = triple['subject_type'].lower().replace(" ", "_")
                triple['object_type'] = triple['object_type'].lower().replace(" ", "_")
                triple['predicate'] = triple['predicate'].lower()
                triple['predicate_type'] = triple['predicate_type'].lower().replace(" ", "_")
                triple['sentence'] = context  # Add the context as a key-value pair
                relevant_triples.append(triple)
        
        return relevant_triples
    
    def remove_duplicate_triplets(self,input_list):
        seen = set()
        result = []

        for item in input_list:
            triplet = (item['subject'], item['predicate'], item['object'])
            if triplet not in seen:
                result.append(item)
                seen.add(triplet)

        return result
      
    async def process_tokens(self, data: IngestedTokens):
        try:
            if not GPTNERLLM.validate_ingested_tokens(data):
                    self.set_termination_event()                    
                    return 

            if data.data:
                single_string = ' '.join(data.data)
                clean_text = single_string.replace('\n', ' ')
            else:
                clean_text = data.data
            if not data.is_token_stream : 
                file, content = self.file_buffer.add_chunk(
                data.get_file_path(), clean_text)
            else:
                content = clean_text
                file = data.get_file_path()
            if content: 
                doc = self.nlp(content)
                sentences = [sent.text for sent in doc.sents]
                contexts = self.get_context(sentences)
                final_triples = []
                for context in contexts:
                    identify_entity_message = f"""Please analyze the provided context below. Once you have understood the context, answer the user query using the specified output format.
        
                    Context: {contexts[0]}

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
                        {{}},  # Additional triples go here
                        {{}},  # Additional triples go here
                        # ...  # Additional triples go here
                    ]
                    """
                    if not self.user_context:
                        messages_classify_entity = [
                            {"role": "user", "content": identify_entity_message},
                            {"role": "user", "content": "Query: First, identify all geological entities in the provided context. Then, create relevant semantic triples (Subject, Predicate, Object) and also categorize the respective the Subject, Object types (e.g. location, person, event, material, process etc.) and Predicate type. Use the above output format to provide all the relevant semantic triples."},
                        ]
                    else :
                        messages_classify_entity = [
                            {"role": "user", "content": identify_entity_message},
                            {"role": "user", "content": self.user_context},
                        ]
                    identify_entity_response = self.generate_response(messages_classify_entity)
                    try:
                        semantic_triples = self.extract_semantic_triples(identify_entity_response)
                        relevant_triples = self.filter_relevant_triples(semantic_triples, context, 10)
                    except Exception as e:
                        self.logger.info(f"Error extracting semantic triples in GPT NER & LLM Class: {e}")
                        continue
                    if len(relevant_triples)>0:
                        final_triples.extend(relevant_triples)
                #final_triples = [{'subject': 'paleocene–eocene thermal maximum (petm) record', 'predicate': 'is present in', 'object': '543-m-thick (1780 ft) deep-marine section in the gulf of mexico (gom)', 'subject_type': 'event', 'object_type': 'location', 'predicate_type': 'occurrence', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.'}, {'subject': 'climate and tectonic perturbations', 'predicate': 'can induce', 'object': 'a substantial response', 'subject_type': 'process', 'object_type': 'event', 'predicate_type': 'causative', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.'}, {'subject': 'gulf coastal plain', 'predicate': 'is', 'object': 'ultimately in the gom', 'subject_type': 'location', 'object_type': 'location', 'predicate_type': 'ownership', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.'}, {'subject': 'paleocene–eocene thermal maximum (petm) record', 'predicate': 'is present in', 'object': '543-m-thick (1780 ft) deep-marine section in the gulf of mexico (gom)', 'subject_type': 'event', 'object_type': 'location', 'predicate_type': 'occurrence', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.'}, {'subject': 'climate and tectonic perturbations', 'predicate': 'can induce', 'object': 'a substantial response', 'subject_type': 'process', 'object_type': 'event', 'predicate_type': 'causative', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.'}, {'subject': 'upstream north american catchments', 'predicate': 'can induce', 'object': 'a substantial response', 'subject_type': 'location', 'object_type': 'event', 'predicate_type': 'causative', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.'}, {'subject': 'downstream sectors of the gulf coastal plain', 'predicate': 'can be impacted by', 'object': 'upstream north american catchments', 'subject_type': 'location', 'object_type': 'location', 'predicate_type': 'causative', 'sentence': 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.'}, {'subject': 'climate and tectonic perturbations', 'predicate': 'can induce', 'object': 'a substantial response', 'subject_type': 'process', 'object_type': 'event', 'predicate_type': 'causative', 'sentence': 'We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin. Despite other thick PETM sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions.'}, {'subject': 'upstream north american catchments', 'predicate': 'can induce', 'object': 'a substantial response', 'subject_type': 'location', 'object_type': 'event', 'predicate_type': 'causative', 'sentence': 'We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin. Despite other thick PETM sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions.'}]
                final_triples = self.remove_duplicate_triplets(final_triples)
                if len(final_triples) > 0:
                    for triple in final_triples:
                        graph_json = json.dumps(triple)
                        if graph_json:
                            current_state = EventState(EventType.Graph,1.0, graph_json, file)
                            await self.set_state(new_state=current_state)
                        context_embeddings = self.create_emb.get_embeddings([triple['sentence']])[0]
                        triple['context_embeddings'] = context_embeddings
                        triple['context'] = triple['sentence']
                        vector_json = json.dumps(TripleToJsonConverter.convert_vectorjson((triple['subject'],json.dumps(triple), triple['object'])))
                        if vector_json:
                                current_state = EventState(EventType.Vector,1.0, vector_json, file)
                                await self.set_state(new_state=current_state)

        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to extract predicates using GPT NER LLM class. {e}")
            raise Exception(f"An error occurred while extracting predicates using GPT NER LLM class: {e}")
    
    async def process_messages(self, data: IngestedMessages):
        raise NotImplementedError
