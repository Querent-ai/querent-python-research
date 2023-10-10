from transformers import AutoTokenizer, AutoModelForTokenClassification,AutoModelForQuestionAnswering,pipeline
import torch
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, List, Tuple
from querent.common.types.file_buffer import FileBuffer
import os, re


class BERTLLM(BaseEngine):
    """
    A specialized engine for processing tokens using BERT-based models for Named Entity Recognition (NER) 
    and Relationship Extraction.

    This engine utilizes pre-trained BERT models to extract entities and relationships from given text. 
    It manages file content in chunks and processes them using an LRU cache. The engine is designed to handle 
    tokenized content that comes in chunks and to extract meaningful information from them.

    Attributes:
        file_buffer (FileBuffer): Buffer to manage and store file content in chunks.
        ner_tokenizer (AutoTokenizer): Tokenizer for the NER model.
        ner_model (AutoModelForTokenClassification): Pre-trained BERT model for NER.
        rel_tokenizer (AutoTokenizer): Tokenizer for the Relationship model.
        rel_model (AutoModelForQuestionAnswering): Pre-trained BERT model for Relationship extraction.
        nlp_ner (pipeline): NER pipeline for entity extraction.
        nlp_rel (pipeline): Relationship extraction pipeline.

    Methods:
        _load_model(model_name: str, model_type: str) -> Union[AutoModelForTokenClassification, AutoModelForQuestionAnswering]:
            Load the specified model, handling potential TensorFlow weights.

        validate() -> bool:
            Validate the BERT models.

        process_messages(data: IngestedMessages) -> None:
            Process the given messages.

        split_into_sentences(text: str) -> List[str]:
            Split the given text into sentences.

        validate_ingested_tokens(data: IngestedTokens) -> bool:
            Validate the ingested tokens.

        combine_subword_entities(entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
            Combine entities that are split into subwords.

        _tokenize_and_chunk(data: str) -> List[List[str]]:
            Tokenize the given data and split it into chunks.

        _extract_entities_from_chunks(token_chunks: List[List[str]]) -> List[Tuple[str, str]]:
            Extract entities from the given token chunks.

        _extract_relationships(context: str, entity1: str, entity2: str) -> List[str]:
            Extract relationships between the given entities.

        process_tokens(data: IngestedTokens) -> None:
            Process the given tokens and extract entities and relationships.
    """
    def __init__(self, input_queue = QuerentQueue ,  
                 ner_model_name="dbmdz/bert-large-cased-finetuned-conll03-english", 
                 rel_model_name="deepset/roberta-base-squad2",
                 ):
        
        super().__init__(input_queue)

        self.file_buffer = FileBuffer()

# Initialize NER model and tokenizer
        self.ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
        self.ner_model = self._load_model(ner_model_name, "NER")

        # Initialize Relationship model and tokenizer
        self.rel_tokenizer = AutoTokenizer.from_pretrained(rel_model_name)
        self.rel_model = self._load_model(rel_model_name, "Relationship")

        # Create pipelines for NER and Relationship extraction
        self.nlp_ner = pipeline("ner", model=self.ner_model, tokenizer=self.ner_tokenizer, aggregation_strategy="simple")
        self.nlp_rel = pipeline('question-answering', model=self.rel_model, tokenizer=self.rel_tokenizer)

    def _load_model(self, model_name, model_type):
        """Load the model, handling potential TensorFlow weights."""
        try:
            if model_type == "NER":
                return AutoModelForTokenClassification.from_pretrained(model_name)
            return AutoModelForQuestionAnswering.from_pretrained(model_name)
        except OSError as e:
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU if there's an issue
            if "file named pytorch_model.bin" in str(e) and "file for TensorFlow weights" in str(e):
                # Attempt to load model from TensorFlow weights
                if model_type == "NER":
                    return AutoModelForTokenClassification.from_pretrained(model_name, from_tf=True)
                return AutoModelForQuestionAnswering.from_pretrained(model_name, from_tf=True)
            raise OSError(f"Failed to load {model_type} model from {model_name}. Error: {e}")

    def validate(self) -> bool:
            """
            Validate the BERT model.
            Returns:
                bool: True if the BERT model is loaded properly, False otherwise.
            """
            #return (self.ner_model is not None and self.ner_tokenizer is not None) and (self.rel_model is not None and self.rel_tokenizer is not None)
            return True
    
    
    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    

    @staticmethod
    def split_into_sentences(text):

        # Split text by sentence delimiters and remove empty strings
        sentences = [s.strip() for s in re.split('[.!?]', text) if s]
        
        
        return sentences

    
    @staticmethod
    def validate_ingested_tokens(data: IngestedTokens) -> bool:
        # Validate that the input data is not an empty string
        if not data.data or data.is_error():
            return False
        
        return True
    
    def combine_subword_entities(self, entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        combined_entities = []
        current_entity = []
        current_label = None

        for word, label in entities:
            if word.startswith('##'):
                if current_label == label:
                    current_entity.append(word[2:])  # remove '##' and append
                else:
                    if current_entity:
                        combined_entities.append((''.join(current_entity), current_label))
                    current_entity = [word[2:]]
                    current_label = label
            else:
                if current_entity:
                    combined_entities.append((''.join(current_entity), current_label))
                    current_entity = []
                current_entity.append(word)
                current_label = label

        if current_entity:
            combined_entities.append((''.join(current_entity), current_label))

        return combined_entities

    
    def _tokenize_and_chunk(self, data: str) -> List[List[str]]:
             # Split the text into sentences
        sentences = BERTLLM.split_into_sentences(data)


        token_chunks = []  # List to store chunks of tokens

        for sentence in sentences:

            sentence_tokens = self.ner_tokenizer.tokenize(sentence)


            # If the sentence tokens exceed the max_chunk_size, split them into multiple chunks
            k = 0
            max_chunk_size = 510
            while k < len(sentence_tokens):
                end = min(k + max_chunk_size, len(sentence_tokens))
                while end > k and end < len(sentence_tokens) and sentence_tokens[end].startswith('##'):
                    end -= 1
                token_chunks.append(sentence_tokens[k:end])
                k = end
        
        return token_chunks

    def _extract_entities_from_chunks(self, token_chunks: List[List[str]]) -> List[Tuple[str, str]]:

         

            all_entities = []

            for chunk in token_chunks:
                    chunk_text = self.ner_tokenizer.convert_tokens_to_string(chunk)
                    entities = self.nlp_ner(chunk_text)
                    formatted_entities = [(entity['word'], entity['entity_group']) for entity in entities]
                    all_entities.extend(formatted_entities)


            combined_entities = self.combine_subword_entities(all_entities)

            return combined_entities
    
    def _extract_relationships(self, context: str, entity1: str, entity2: str) -> List[str]:
        # Frame the question based on the two entities
        question = f"What is the relationship between {entity1} and {entity2}?"

        # Use the QnA pipeline to extract the answer (relationship)
        QA_input = {
            'question': question,
            'context': context
        }
        res = self.nlp_rel(QA_input)

        # For simplicity, we're assuming the answer is a list of relationships. 
        # This can be adjusted based on the actual structure of the returned answer.

        relationships = [res['answer']]  # Convert the answer to a list
        return relationships

    async def process_tokens(self, data: IngestedTokens):
        if data is None or data.is_error():
            # the LLM developer can raise an error here or do something else
            # the developers of Querent can customize the behavior of Querent
            # to handle the error in a way that is appropriate for the use case
            self.set_termination_event()
            return
    # Add chunk to FileBuffer and check if the file has ended
        content = self.file_buffer.add_chunk(data.get_file_path(), data.data)
        
        
        # If content is returned, it means the file has ended
        if content:
            # Execute relationship extraction logic on 'content'

            token_chunks = self._tokenize_and_chunk(content)
            all_entities = self._extract_entities_from_chunks(token_chunks)

            # Dictionary to store relationships
            relationships_dict = {}
        
            # Extract relationships for each pair of entities
            for i in range(len(all_entities)):
                for j in range(i+1, len(all_entities)):
                    entity1 = all_entities[i][0]  # Extracting the entity name from the tuple
                    entity2 = all_entities[j][0]
                    relationship_list = self._extract_relationships(context=content, entity1=entity1, entity2=entity2)
                    relationships_dict[(entity1, entity2)] = relationship_list

            for entities, rel_list in relationships_dict.items():
                print(f"Relationships between {entities[0]} and {entities[1]}: {', '.join(rel_list)}")

        else:
            # If the file hasn't ended, continue with the regular process
            if not BERTLLM.validate_ingested_tokens(data):
                self.set_termination_event()
            
            token_chunks = self._tokenize_and_chunk(data.data)
            all_entities = self._extract_entities_from_chunks(token_chunks)



        current_state = EventState(EventType.TOKEN_PROCESSED, 1.0, all_entities)
        
        await self.set_state(new_state=current_state)

