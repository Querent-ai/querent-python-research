from transformers import GPT2LMHeadModel, GPT2Tokenizer
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_llm import BaseLLM


class GPT2LLM(BaseLLM):
    def __init__(
        self,
        input_queue: QuerentQueue[str],
        output_queue: QuerentQueue[str],
        model_name="gpt2",
    ):
        super().__init__(input_queue, output_queue)
        self.model_name = model_name
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    async def process_tokens(self, data: str) -> str:
        try:
            input_text = data  # Assuming data is a string
            input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
            output = self.model.generate(
                input_ids, max_length=50, num_return_sequences=1, no_repeat_ngram_size=2
            )
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            return generated_text
        except Exception as e:
            # Log the error and return an informative error message
            error_message = f"Error in GPT2LLM: {str(e)}"
            print(error_message)
            return error_message

    def validate(self) -> bool:
        # You can add specific validation logic here
        # For example, check if the model is loaded successfully
        return hasattr(self, "model") and hasattr(self, "tokenizer")
