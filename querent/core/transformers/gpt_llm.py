from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
from transformers import AutoTokenizer
from querent.config.core.gpt_llm_config import GPTConfig
from querent.core.transformers.bert_llm import BERTLLM
from querent.common.types.ingested_images import IngestedImages
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, List, Tuple
from querent.logging.logger import setup_logger
from querent.config.core.bert_llm_config import BERTLLMConfig
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.chat_models import ChatOpenAI
from querent.kg.rel_helperfunctions.gpt_pydantic_classes import Triples, TriplesList
from dotenv import load_dotenv, find_dotenv

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
            bert_llm_config = BERTLLMConfig(
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
            skip_inferences= True)
            print("going to initialize BERT")
            self.bert_instance = BERTLLM(input_queue, bert_llm_config)
            print("Bert Initialzed")
            # self.triples = convert_pydantic_to_openai_function(Triples)
            # self.triples_list = convert_pydantic_to_openai_function(TriplesList)
            self.gpt_llm = ChatOpenAI()
            # self.gpt_llm = self.gpt_llm.bind(
                # functions=[self.triples],
                # function_call={"name": "TriplesList"},
            # )
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
            raise Exception(f"Invalid {self.__class__.__name__} configuration. Unable to Initialize. {e}")
    
    def validate(self) -> bool:
        return isinstance(self.bert_instance, BERTLLM)

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

    async def get_triples(self, sentence: str):
        # print(right_answer_list)
        triples = self.gpt_llm.invoke(
            f"Extract subject, object and predicate from the given sentence. Sentence: {sentence}",
            functions=[self.triples, self.triples_list],
        )

        print(
            "Triples ------------------------------------------------------------------------------------------------"
        )
        print(type(triples.content))
        print(triples, "\n\n")
    
    async def process_tokens(self, data: IngestedTokens):
        try:
            print("Inside processssssssssssssssssssssssssssssssssss")
            filtered_triples = await self.bert_instance.process_tokens(data)
            print("filtered_triples--------------------------------------", filtered_triples)
            if not filtered_triples: return 
            else:
                print("Filtered_triples-------------------", filtered_triples[:1])
                # modified_data = GPT2LLM.remove_items_from_tuples(data)
                # # get the input text from the data which is a list of str
                # input_text_list = data.data

                # # concatenate the input text into a single string
                # input_text = " ".join(input_text_list)

                # model = GPT2LMHeadModel.from_pretrained(self.model_name)
                # tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)

                # input_ids = tokenizer.encode(input_text, return_tensors="pt")
                # output = model.generate(
                #     input_ids,
                #     max_length=50,
                #     num_return_sequences=1,
                #     no_repeat_ngram_size=2,
                # )
                # generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
                # return generated_text
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to extract predicates using GPT. {e}")
            raise Exception(f"An unexpected error occurred while extracting predicates using GPT: {e}")

    async def process_messages(self, data: IngestedMessages):
        raise NotImplementedError
