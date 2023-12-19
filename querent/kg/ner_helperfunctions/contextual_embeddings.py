from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.logging.logger import setup_logger
import torch
import umap
import numpy as np

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

    def __init__(self, model, tokenizer, number_entity_pairs, number_sentences):
        self.logger = setup_logger(__name__, "EntityEmbeddingExtractor")
        try:
            self.model = model
            self.tokenizer = tokenizer
            self.reducer = umap.UMAP(init='random',n_neighbors=min(15, number_entity_pairs), min_dist=0.1, n_components=10, metric='cosine')
            self.sentence_reducer = umap.UMAP(init='random', n_neighbors=min(15, number_sentences), min_dist=0.1, n_components=10, metric='cosine')
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


    def fit_umap(self, all_embeddings):
        try:
            if not all_embeddings:
                raise ValueError("Embedding lists are empty or contain invalid data.")
            self.reducer.fit(np.array(all_embeddings))
        except Exception as e:
            self.logger.error(f"Error fitting UMAP: {e}")
            raise Exception(f"Error fitting UMAP: {e}")

    
    def _get_relevant_context(self, entity1, entity2, full_context):
        sentences = NER_LLM.split_into_sentences(full_context)
        for sentence in sentences:
            if entity1.lower() in sentence.lower() and entity2.lower() in sentence.lower():
                return sentence
        return full_context
    
    def append_if_not_present(self,item, item_embedding, all_items, all_embeddings, sentence=None):
        if item not in all_items and sentence == None:
            all_items.append(item)
            all_embeddings.append(item_embedding.tolist())
        elif sentence is not None:
            if (item + " " + sentence) not in all_items:
                all_items.append(item + " " + sentence)
                all_embeddings.append(item_embedding.tolist())
            

    def _update_pairs_with_embeddings(self, doc_entity_pairs):
        updated_pairs = []
        for inner_list in doc_entity_pairs:
            updated_inner_list = []
            for pair in inner_list:
                entity1, full_context, entity2, pair_dict = pair
                context = self._get_relevant_context(entity1, entity2, full_context)
                entity1_embedding, _ = self.extract_entity_embedding(entity1, context)
                entity2_embedding, _ = self.extract_entity_embedding(entity2, context)
                pair_dict['entity1_embedding'] = self.reducer.transform([entity1_embedding.tolist()])[0]
                pair_dict['entity2_embedding'] = self.reducer.transform([entity2_embedding.tolist()])[0]
                updated_inner_list.append((entity1, full_context, entity2, pair_dict))
            updated_pairs.append(updated_inner_list)
        return updated_pairs

    def extract_and_append_entity_embeddings(self, doc_entity_pairs):
        all_embeddings = []
        all_entities = []
        try:
            for inner_list in doc_entity_pairs:
                for pair in inner_list:
                    entity1, full_context, entity2, _ = pair
                    context = self._get_relevant_context(entity1, entity2, full_context)
                    entity1_embedding, _ = self.extract_entity_embedding(entity1, context)
                    entity2_embedding, _ = self.extract_entity_embedding(entity2, context)
                    self.append_if_not_present(entity1, entity1_embedding, all_entities, all_embeddings, sentence=context)
                    self.append_if_not_present(entity2, entity2_embedding, all_entities, all_embeddings, sentence=context)

            self.fit_umap(all_embeddings=all_embeddings)
            return self._update_pairs_with_embeddings(doc_entity_pairs)
        
        except Exception as e:
            self.logger.error(f"Error extracting and appending entity embedding: {e}")
            raise Exception(f"Error extracting and appending entity embedding: {e}")

    


