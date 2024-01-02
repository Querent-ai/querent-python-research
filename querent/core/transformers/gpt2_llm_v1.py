from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import AutoTokenizer
from langchain.utils.openai_functions import convert_pydantic_to_openai_function

from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.kg.ner_helperfunctions.gpt_pydantic_classes import Triples, TriplesList

from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.core.base_engine import BaseEngine
from querent.common.types.file_buffer import FileBuffer
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_code import IngestedCode
from querent.config.core.gpt_llm_config import GPTLLMConfig
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


class GPT2LLM(BaseEngine):
    def __init__(self, input_queue: QuerentQueue, config: GPTLLMConfig):
        super().__init__(input_queue)
        self.ner_tokenizer = AutoTokenizer.from_pretrained(config.ner_model_name)
        self.ner_model = NER_LLM.load_model(config.ner_model_name, "NER")
        self.ner_llm_instance = NER_LLM(
            provided_tokenizer=self.ner_tokenizer, provided_model=self.ner_model
        )
        self.file_buffer = FileBuffer()
        self.triples = convert_pydantic_to_openai_function(Triples)
        self.triples_list = convert_pydantic_to_openai_function(TriplesList)
        self.gpt_llm = ChatOpenAI()
        self.gpt_llm = self.gpt_llm.bind(
            functions=[self.triples],
            function_call={"name": "TriplesList"},
        )

    async def process_tokens(self, data: IngestedTokens) -> str:
        doc_entity_pairs = []
        number_sentences = 0
        try:
            if data is None or data.is_error():
                self.set_termination_event()

                return

            file, content = self.file_buffer.add_chunk(data.get_file_path(), data.data)
            print("--------------------------------", content)

            # Get content
            if content:
                # Get sentences
                sentences = content.replace("\n", " ")
                sentences = sentences.split(".")
                print("tokens: ", sentences)

                # Pass to GPT to handle
                for sentence in sentences:
                    await self.get_triples(sentence)

        except Exception as e:
            # Log the error and return an informative error message
            error_message = f"Error in GPT2LLM: {str(e)}"
            print(error_message)
            return error_message

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

    async def process_images(self, data: IngestedImages):
        return super().process_messages(data)

    async def process_code(self, data: IngestedCode):
        return super().process_messages(data)

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None
