from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.logging.logger import setup_logger
import torch

"""
EntityAttentionExtractor Class:

This class is designed to extract attention weights from a given transformer model for specific entities within a context. 
The primary purpose is to determine the significance or relevance of entities in the context based on the attention mechanism of the transformer model.

Attributes:
    model (torch.nn.Module): The transformer model used for extracting attention weights.
    tokenizer (Tokenizer): The tokenizer associated with the transformer model.

Methods:
    extract_attention_weight(entity, context):
        Extracts the attention weight for a given entity within a context.
        
    extract_and_append_attention_weights(doc_entity_pairs):
        Processes a list of document-entity pairs, extracts attention weights for each entity, 
        and appends the attention weights to the respective pairs.

Dependencies:
    - torch
    - NER_LLM from querent.kg.ner_helperfunctions.ner_llm_transformer
    - setup_logger from querent.logging.logger

Example:
    model = ... # Load a transformer model
    tokenizer = ... # Load the corresponding tokenizer
    extractor = EntityAttentionExtractor(model, tokenizer)
    attention_weight = extractor.extract_attention_weight("apple", "Apple Inc. is a tech company.")
    ...

Note:
    Ensure that the transformer model and tokenizer are compatible. 
    The model should be capable of returning attention weights (e.g., BERT, RoBERTa).

"""

class EntityAttentionExtractor:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.logger = setup_logger(__name__, "EntityAttentionExtractor")

    def extract_attention_weight(self, entity, context):
        try:
            inputs = self.tokenizer(context, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs, output_attentions=True)
                attentions = outputs.attentions[-1][0] 
            entity_token_ids = self.tokenizer.encode(entity, add_special_tokens=False)
            entity_positions = [i for i, token_id in enumerate(inputs["input_ids"][0]) if token_id in entity_token_ids]

            # # Get the average attention weight for the entity tokens
            # attention_weight = attentions[0, entity_positions].mean().item()

            attention_weight = attentions[0, entity_positions].max().item()
            
            return attention_weight
        
        except Exception as e:
            self.logger.error(f"Error extracting attention weights : {e}")
            raise Exception("Error extracting attention weights : {}".format(e))

    def extract_and_append_attention_weights(self, doc_entity_pairs):
        updated_pairs = []
        try:
            for inner_list in doc_entity_pairs:
                updated_inner_list = []
                for pair in inner_list:
                    full_context = pair[1]
                    entity1 = pair[0]
                    entity2 = pair[2]
                    sentences = NER_LLM.split_into_sentences(full_context)
                    context = None
                    for sentence in sentences:
                        if entity1.lower() in sentence.lower() and entity2.lower() in sentence.lower():
                            context = sentence
                            break
                    if not context:
                        context = full_context
                    entity1_attnscore = self.extract_attention_weight(entity1, context)
                    entity2_attnscore = self.extract_attention_weight(entity2, context)
                    pair_dict = pair[3]
                    pair_dict['entity1_attnscore'] = round(entity1_attnscore,2)
                    pair_dict['entity2_attnscore'] = round(entity2_attnscore,2)
                    updated_inner_list.append((entity1, full_context, entity2, pair_dict))
                updated_pairs.append(updated_inner_list)
                
            return updated_pairs
        
        except Exception as e:
            self.logger.error(f"Error extracting and appending attention weights : {e}")
            raise Exception("Error extracting and appending attention weights : {}".format(e))
