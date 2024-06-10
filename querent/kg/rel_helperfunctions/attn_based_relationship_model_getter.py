import torch
import transformers
from transformers import AutoTokenizer



class AttnRelationshipExtractor:
    def __init__(self, model_tokenizer, model):
        self.tokenizer = model_tokenizer
        self.model = model
        
    def init_token_idx_2_word_doc_idx(self) -> list[tuple[str, int]]:
        """
        This function initializes a dictionary of token index to spacy doc index. It should contain only the
        first token in a tokenized sentence, alongside its corresponding doc index in the sentence.
        For BERT, this is ('CLS', -1). We use -1 because the CLS does not correspond to a word in the sentence.
        :return: A list with the first tokenized item and its doc index.
        """
        pass

    def num_start_tokens(self) -> int:
        """
        This function returns the number of start tokens in a tokenized sentence.
        :return: Integer, representing the number of start tokens.
        """
        pass

    def append_last_token(self, listing: list[tuple[str, int]]):
        """
        Appends the last token of a tokenized sentence. In the case of BERT, this is only
        ('SEP', len(linsting)), as 'SEP' indicates the end of the sentence.
        :param listing: List of tokenized words and their corresponding Spacy doc index.
        """
        pass

    def model_input(self, tokenized_sequence: list[int]) -> dict[str, torch.Tensor]:
        """
        This function prepares the model input. It should correspond to the exact dictionary the model expects.
        :param tokenized_sequence: The sentence Havina has tokenized.
        :return: The dictionary the language model expects as inputs.
        """
        pass

    def tokenize(self, word: str):
        """
        Tokenize a word using the model's specific tokenizer.
        :param word: A word to tokenize.
        """
        pass

    def inference_attention(self, model_input: dict[str, torch.Tensor]):
        """
        Perform the inference and return the average of all the attention matrices in the model's last layer.
        :param model_input: The language model's input.
        :return:
        """
        pass

    def maximum_tokens(self) -> int:
        """
        Returns the maximum sequence length the language model can consume.
        :return: An integer, representing the maximum number of tokens the language model can handle.
        """
    pass

    def tokenize_sentence(self, sentence: str):
        pass

class BertBasedModel(AttnRelationshipExtractor):
    def __init__(self, model_tokenizer, model):
        super().__init__(model_tokenizer, model)

    def init_token_idx_2_word_doc_idx(self) -> list[tuple[str, int]]:
        return [('CLS', -1)]

    def num_start_tokens(self) -> int:
        return 1

    def append_last_token(self, listing: list[tuple[str, int]]):
        listing.append(('SEP', len(listing)))

    def model_input(self, tokenized_sentence: list[int]) -> dict[str, torch.Tensor]:
        tokenized_sentence = [self.tokenizer.cls_token_id] + tokenized_sentence + [self.tokenizer.sep_token_id]
        input_dict = {
            'input_ids': torch.tensor(tokenized_sentence, device='cpu').long().unsqueeze(0),
            'token_type_ids': torch.zeros(len(tokenized_sentence), device='cpu').long().unsqueeze(0),
            'attention_mask': torch.ones(len(tokenized_sentence), device='cpu').long().unsqueeze(0),
        }
        return input_dict

    def tokenize(self, word):
        return self.tokenizer(str(word), add_special_tokens=False)['input_ids']

    def inference_attention(self, model_input: dict[str, torch.Tensor]) -> torch.Tensor:
        output = self.model(**model_input, output_attentions=True)
        last_att_layer = output.attentions[-1]
        mean = torch.mean(last_att_layer, dim=1)
        return mean[0]

    def maximum_tokens(self) -> int:
        return 512
    
    def tokenize_sentence(self, sentence: str):
        return self.tokenizer.encode(sentence, add_special_tokens=False)


class LlamaBasedModel(AttnRelationshipExtractor):
    def __init__(self, model_tokenizer, model):
        super().__init__(model_tokenizer, model)

    def init_token_idx_2_word_doc_idx(self) -> list[tuple[str, int]]:
        return []

    def num_start_tokens(self) -> int:
        return 0

    def append_last_token(self, listing: list[tuple[str, int]]):
        pass

    def model_input(self, tokenized_sequence: list[int]) -> dict[str, torch.Tensor]:
        input_dict = {
            'input_ids': torch.tensor(tokenized_sequence, device=self.device).long().unsqueeze(0),
            'attention_mask': torch.ones(len(tokenized_sequence), device=self.device).long().unsqueeze(0)
        }
        return input_dict

    def tokenize(self, word: str):
        return self.tokenizer(str(word), add_special_tokens=False)['input_ids']

    def inference_attention(self, model_input: dict[str, torch.Tensor]):
        output = self.model(**model_input, output_attentions=True)
        last_att_layer = output.attentions[-1]
        mean = torch.mean(last_att_layer, dim=1)
        return mean[0]

    def maximum_tokens(self) -> int:
        return 2048
    
    def tokenize_sentence(self, sentence: str):
        return self.tokenizer.encode(sentence, add_special_tokens=False)


def get_model(model_name:str, model_tokenizer: str, model: str) -> AttnRelationshipExtractor:
    if model_name == 'bert':
        return BertBasedModel(model_tokenizer, model)
    elif model_name == 'llama':
        return LlamaBasedModel(model_tokenizer, model)

    raise Exception("Model not found")

