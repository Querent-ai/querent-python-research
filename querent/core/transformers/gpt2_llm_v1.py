from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
from typing import List, Tuple
from transformers import AutoTokenizer
from querent.kg.ner_helperfunctions.fixed_predicate import FixedPredicateExtractor
from querent.common.types.ingested_images import IngestedImages
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.kg.contextual_predicate import process_data
from querent.kg.ner_helperfunctions.contextual_embeddings import EntityEmbeddingExtractor
from querent.kg.ner_helperfunctions.fixed_entities import FixedEntityExtractor
from querent.kg.ner_helperfunctions.fixed_entities import FixedEntityExtractor
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, List, Tuple
from querent.common.types.file_buffer import FileBuffer
from querent.logging.logger import setup_logger
from querent.kg.querent_kg import QuerentKG
from querent.graph.graph import QuerentGraph
from querent.config.graph_config import GraphConfig
from querent.kg.ner_helperfunctions.attn_scores import EntityAttentionExtractor
from querent.kg.ner_helperfunctions.filter_triples import TripleFilter
from querent.config.core.bert_llm_config import BERTLLMConfig
from querent.kg.rel_helperfunctions.triple_to_json import TripleToJsonConverter
import time
import psutil


class GPT2LLM(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        model_name="gpt2",
    ):
        self.logger = setup_logger(__name__, "OPENAI")
        super().__init__(input_queue)
        self.model_name = model_name
        self.ner_model_name = "botryan96/GeoBERT"
        self.file_buffer = FileBuffer()
        self.ner_tokenizer = AutoTokenizer.from_pretrained(self.ner_model_name)
        self.ner_model = NER_LLM.load_model(self.ner_model_name, "NER")
        self.ner_llm_instance = NER_LLM(provided_tokenizer=self.ner_tokenizer, provided_model=self.ner_model)
    
    def validate(self) -> bool:
        return self.model_name is not None and self.ner_tokenizer is not None

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
    
    async def process_tokens(self, data: IngestedTokens) -> str:
        try:
            # get the input text from the data which is a list of str
            input_text_list = data.data

            # concatenate the input text into a single string
            input_text = " ".join(input_text_list)

            model = GPT2LMHeadModel.from_pretrained(self.model_name)
            tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)

            input_ids = tokenizer.encode(input_text, return_tensors="pt")
            output = model.generate(
                input_ids,
                max_length=50,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
            )
            generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
            return generated_text
        except Exception as e:
            # Log the error and return an informative error message
            error_message = f"Error in GPT2LLM: {str(e)}"
            print(error_message)
            return error_message

    async def process_messages(self, data: IngestedMessages):
        raise NotImplementedError

    def validate(self) -> bool:
        # You can add specific validation logic here
        # For example, check if the model is loaded successfully
        return hasattr(self, "model") and hasattr(self, "tokenizer")
