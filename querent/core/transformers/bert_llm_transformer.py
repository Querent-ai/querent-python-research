from transformers import AutoTokenizer, AutoModelForTokenClassification,pipeline
import torch
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from typing import Any, List, Tuple
import os, re

"""
    BERTLLM: A class for Named Entity Recognition (NER) using BERT-based models.

    This class provides functionalities to tokenize input text, chunk them into manageable sizes,
    and extract named entities using a BERT-based model.

    Attributes:
        tokenizer (AutoTokenizer): Tokenizer associated with the BERT model.
        model (AutoModelForTokenClassification): BERT model for token classification.
        nlp (pipeline): HuggingFace's NER pipeline.

    Methods:
        validate() -> bool:
            Validates if the BERT model and tokenizer are loaded properly.

        split_into_sentences(text: str) -> List[str]:
            Splits the input text into sentences.

        validate_ingested_tokens(data: IngestedTokens) -> bool:
            Validates the input data.

        _tokenize_and_chunk(data: IngestedTokens) -> List[List[str]]:
            Tokenizes the input data and chunks them into manageable sizes.

        _extract_entities_from_chunks(token_chunks: List[List[str]]) -> List[Tuple[str, str]]:
            Extracts named entities from token chunks.

        process_tokens(data: IngestedTokens) -> None:
            Processes the input tokens and extracts named entities.
"""


class BERTLLM(BaseEngine):
    def __init__(self, input_queue,  model_name="dbmdz/bert-large-cased-finetuned-conll03-english"):
        super().__init__(input_queue)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        #self.model = AutoModelForTokenClassification.from_pretrained(model_name)

                # Try to load the model normally first
        try:
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        except OSError as e:
            #need to update gpu availability
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            # If an OSError occurs, check if it's related to TensorFlow weights

            if "file named pytorch_model.bin" in str(e) and "file for TensorFlow weights" in str(e):
                # If so, try loading the model from TensorFlow weights
                self.model = AutoModelForTokenClassification.from_pretrained(model_name, from_tf=True)
            else:
                # If the error is not related to TensorFlow weights, raise the original error
                raise e

        #create a ner pipeline
        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer,aggregation_strategy="simple")

    def validate(self) -> bool:
            """
            Validate the BERT model.
            Returns:
                bool: True if the BERT model is loaded properly, False otherwise.
            """
            return self.model is not None and self.tokenizer is not None
    

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
    
    def _tokenize_and_chunk(self, data: IngestedTokens) -> List[List[str]]:
            # Split the text into sentences
            sentences = BERTLLM.split_into_sentences(data.data[0])

            # Tokenize each sentence separately and collect all tokens
            tokens = []
            for sentence in sentences:
                tokens.extend(self.tokenizer.tokenize(sentence))

            # Define the maximum chunk size (512 - 2 to account for [CLS] and [SEP] tokens)
            max_chunk_size = 510 
            token_chunks = []  
            k = 0

            while k < len(tokens):
                end = min(k + max_chunk_size, len(tokens))
                while end > k and end < len(tokens) and tokens[end].startswith('##'):
                    end -= 1
                
                token_chunks.append(tokens[k:end])
                k = end
            
            return token_chunks

    def _extract_entities_from_chunks(self, token_chunks: List[List[str]]) -> List[Tuple[str, str]]:
            all_entities = []

            for chunk in token_chunks:
                chunk_text = self.tokenizer.convert_tokens_to_string(chunk)
                entities = self.nlp(chunk_text)
                formatted_entities = [(entity['word'], entity['entity_group']) for entity in entities]
                all_entities.extend(formatted_entities)

            return all_entities

    async def process_tokens(self, data: IngestedTokens):
            if not BERTLLM.validate_ingested_tokens(data):
                self.set_termination_event()
            
            token_chunks = self._tokenize_and_chunk(data)
            
            all_entities = self._extract_entities_from_chunks(token_chunks)

            current_state = EventState(EventType.TOKEN_PROCESSED, 1.0, all_entities)

            await self.set_state(new_state=current_state)