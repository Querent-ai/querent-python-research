from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.logging.logger import setup_logger
import torch
import umap

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

    def __init__(self, model, tokenizer, number_entity_pairs):
        self.logger = setup_logger(__name__, "EntityEmbeddingExtractor")
        self.model = model
        self.tokenizer = tokenizer
        self.reducer = umap.UMAP(n_neighbors=min(15, number_entity_pairs), min_dist=0.1, n_components=10, metric='cosine')


    def extract_entity_embedding(self, entity, context):
        try:
            inputs = self.tokenizer(context, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                all_hidden_states = outputs.hidden_states  # Tuple of hidden states at each layer
                last_hidden_state = all_hidden_states[-1][0]  # Take the last layer's hidden state

            entity_token_ids = self.tokenizer.encode(entity, add_special_tokens=False)
            entity_positions = [i for i, token_id in enumerate(inputs["input_ids"][0]) if token_id in entity_token_ids]

            # Get the average embedding for the entity tokens
            entity_embedding = last_hidden_state[entity_positions].mean(dim=0)
            sentence_embedding = last_hidden_state.mean(dim=0)
            combined_embedding = torch.cat((entity_embedding, sentence_embedding), dim=0)
            
            return combined_embedding
        
        except Exception as e:
            self.logger.error(f"Error extracting entity embedding: {e}")
            raise   Exception("Error extracting entity embedding: {}".format(e))
    
    def get_embedding(self, entity, context, task_type="cls_embedding"):
        try:
            inputs = self.tokenizer(context, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                all_hidden_states = outputs.hidden_states
                last_hidden_state = all_hidden_states[-1][0]

            entity_token_ids = self.tokenizer.encode(entity, add_special_tokens=False)
            entity_positions = [i for i, token_id in enumerate(inputs["input_ids"][0]) if token_id in entity_token_ids]

            #Bad Results
            if task_type == "average":
                return last_hidden_state[entity_positions].mean(dim=0)

            # Bad Results 
            elif task_type == "layerwise_average":
                layers = [-1, -2, -3, -4]
                return torch.stack([all_hidden_states[layer][0][entity_positions].mean(dim=0) for layer in layers]).mean(dim=0)
            
            #not good for geobert
            elif task_type == "concatenate":
                layers = [-1, -2]
                return torch.cat([all_hidden_states[layer][0][entity_positions].mean(dim=0) for layer in layers], dim=0)
            
            #not good for geobert
            elif task_type == "max_pooling":
                return last_hidden_state[entity_positions].max(dim=0)[0]

            #not good for geobert but best for colln model
            elif task_type == "difference":
                sentence_embedding = last_hidden_state.mean(dim=0)
                entity_embedding = last_hidden_state[entity_positions].mean(dim=0)
                return entity_embedding - sentence_embedding
            
            #only pass the entity and get the embeddings on the cls token or the embedding itself
            elif task_type == "cls_embedding":
                print("entity :", entity)
                self.model.eval()
                inputs1 = self.tokenizer(entity, return_tensors="pt", truncation=True, padding=True, max_length=512)
                tokenized_text = self.tokenizer.tokenize(entity)
                print(tokenized_text)

                with torch.no_grad():
                    outputs1 = self.model(**inputs1, output_hidden_states=True)
                last_hidden_state = outputs1['hidden_states'][-1]
                cls_embedding = last_hidden_state[0, 0, :]
                return cls_embedding
                  

            else:
                raise ValueError(f"Unsupported task_type: {task_type}")
        
        except Exception as e:
            self.logger.error(f"Error extracting entity embedding: {e}")
            raise   Exception("Error extracting entity embedding: {}".format(e))


    def fit_umap(self, all_embeddings):
        """Fit UMAP on all embeddings."""
        try:
            self.reducer.fit(all_embeddings)
        except Exception as e:
            self.logger.error(f"Error fitting UMAP: {e}")
            raise Exception (f"Error fitting UMAP: {e}")
    
    def _get_relevant_context(self, entity1, entity2, full_context):
        sentences = NER_LLM.split_into_sentences(full_context)
        for sentence in sentences:
            if entity1.lower() in sentence.lower() and entity2.lower() in sentence.lower():
                return sentence
        return full_context

    def _update_pairs_with_embeddings(self, doc_entity_pairs):
        updated_pairs = []
        for inner_list in doc_entity_pairs:
            updated_inner_list = []
            for pair in inner_list:
                entity1, full_context, entity2, pair_dict = pair
                context = self._get_relevant_context(entity1, entity2, full_context)
                entity1_embedding = self.extract_entity_embedding(entity1, context)
                entity2_embedding = self.extract_entity_embedding(entity2, context)
                pair_dict['entity1_embedding'] = self.reducer.transform([entity1_embedding.tolist()])[0]
                pair_dict['entity2_embedding'] = self.reducer.transform([entity2_embedding.tolist()])[0]
                updated_inner_list.append((entity1, full_context, entity2, pair_dict))
            updated_pairs.append(updated_inner_list)
        #print("updated pairs with embeddings", updated_pairs)    
        return updated_pairs

    def extract_and_append_entity_embeddings(self, doc_entity_pairs):
        all_embeddings = []
        try:
            for inner_list in doc_entity_pairs:
                for pair in inner_list:
                    entity1, full_context, entity2, _ = pair
                    context = self._get_relevant_context(entity1, entity2, full_context)
                    entity1_embedding = self.extract_entity_embedding(entity1, context)
                    entity2_embedding = self.extract_entity_embedding(entity2, context)
                    all_embeddings.extend([entity1_embedding.tolist(), entity2_embedding.tolist()])

            self.fit_umap(all_embeddings)
            return self._update_pairs_with_embeddings(doc_entity_pairs)
        
        except Exception as e:
            self.logger.error(f"Error extracting and appending entity embedding: {e}")
            raise Exception(f"Error extracting and appending entity embedding: {e}")

    


