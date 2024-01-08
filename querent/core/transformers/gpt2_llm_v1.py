from transformers import GPT2LMHeadModel, GPT2Tokenizer
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from querent.core.base_engine import BaseEngine
from querent.logging.logger import setup_logger


class GPT2LLM(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        model_name="gpt2",
    ):
        self.logger = setup_logger(__name__, "OPENAI")
        super().__init__(input_queue)
        self.model_name = model_name
    
    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

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
