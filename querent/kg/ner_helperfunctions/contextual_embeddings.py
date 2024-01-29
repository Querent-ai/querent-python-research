from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.logging.logger import setup_logger
import torch
import numpy as np
import time

"""
    EntityEmbeddingExtractor: A class designed to extract embeddings for entities within a given context.

    Attributes:
        model (torch.nn.Module): A pre-trained model used for generating embeddings.
        tokenizer (Tokenizer): A tokenizer compatible with the model for tokenizing input text.
        reducer (umap.UMAP): A UMAP reducer for dimensionality reduction of embeddings.
        logger (logging.Logger): Logger for capturing and reporting errors.

    Methods:
        setup_logger() -> logging.Logger:
            Sets up a logger for the class.
        
        extract_entity_embedding(entity: str, context: str) -> torch.Tensor:
            Extracts the combined embedding of an entity and its context.
        
        fit_umap(all_embeddings: List[List[float]]):
            Fits the UMAP reducer on the collected embeddings.
        
        extract_and_append_entity_embeddings(doc_entity_pairs: List[Tuple[str, str, str, Dict[str, Any]]]) -> List[List[Tuple[str, str, str, Dict[str, Any]]]]:
            Extracts embeddings for entities in the provided document-entity pairs and appends them to the pairs.
    """

class EntityEmbeddingExtractor:

    def __init__(self, model, tokenizer):
        self.logger = setup_logger(__name__, "EntityEmbeddingExtractor")
        try:
            self.model = model
            self.tokenizer = tokenizer
        except Exception as e:
            self.logger.error(f"Error Initializing Entity Embedding Extractor Class: {e}")

    def extract_entity_embedding(self, entity, context):
        try:
            
            inputs = self.tokenizer(context, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                all_hidden_states = outputs.hidden_states  # Tuple of hidden states at each layer
                last_hidden_state = all_hidden_states[-1][0]  # Take the last layer's hidden state
            entity_token_ids = self.tokenizer.encode(entity, add_special_tokens=False)
            entity_positions = [i for i, token_id in enumerate(inputs["input_ids"][0]) if token_id in entity_token_ids]
            entity_embedding = last_hidden_state[entity_positions].mean(dim=0)
            sentence_embedding = last_hidden_state.mean(dim=0)
            combined_embedding = torch.cat((entity_embedding, sentence_embedding), dim=0)

            return combined_embedding, sentence_embedding
        
        except Exception as e:
            self.logger.error(f"Error extracting entity embedding: {e}")
            raise   Exception("Error extracting entity embedding: {}".format(e))

    
    def _get_relevant_context(self, entity1, entity2, full_context):
        sentences = NER_LLM.split_into_sentences(full_context)
        for sentence in sentences:
            if entity1.lower() in sentence.lower() and entity2.lower() in sentence.lower():
                return sentence
        return full_context
    
            

    def extract_and_append_entity_embeddings(self, doc_entity_pairs):
        try:
            for inner_list_index, inner_list in enumerate(doc_entity_pairs):
                to_remove = []  # List to hold indices of pairs to remove
                for pair_index, pair in enumerate(inner_list):
                    entity1, full_context, entity2, pair_dict = pair
                    context = self._get_relevant_context(entity1, entity2, full_context)
                    entity1_embedding, _ = self.extract_entity_embedding(entity1, context)
                    entity2_embedding, _ = self.extract_entity_embedding(entity2, context)

                    is_nan_entity1 = np.isnan(entity1_embedding).any()
                    is_nan_entity2 = np.isnan(entity2_embedding).any()

                    if is_nan_entity1 or is_nan_entity2:
                        # Record the index of the pair that needs to be removed
                        to_remove.append(pair_index)
                    if not is_nan_entity1:
                        pair_dict['entity1_embedding'] = entity1_embedding.tolist()
                    if not is_nan_entity2:
                        pair_dict['entity2_embedding'] = entity2_embedding.tolist()
                doc_entity_pairs[inner_list_index] = [pair for i, pair in enumerate(inner_list) if i not in to_remove]

            return doc_entity_pairs
        
        except Exception as e:
            self.logger.error(f"Error extracting and appending entity embedding: {e}")
            raise Exception(f"Error extracting and appending entity embedding: {e}")
