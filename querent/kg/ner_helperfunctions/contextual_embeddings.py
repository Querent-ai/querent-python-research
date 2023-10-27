from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.logging.logger import setup_logger
import torch
import umap

class EntityEmbeddingExtractor:
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
        
            return None

    def fit_umap(self, all_embeddings):
        """Fit UMAP on all embeddings."""
        try:
            self.reducer.fit(all_embeddings)
        except Exception as e:
            raise Exception (f"Error fitting UMAP: {e}")

    def extract_and_append_entity_embeddings(self, doc_entity_pairs):
        all_embeddings = []
        try:
            # First, collect all embeddings without reducing dimensions
            for inner_list in doc_entity_pairs:
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
                    entity1_embedding = self.extract_entity_embedding(entity1, context)
                    entity2_embedding = self.extract_entity_embedding(entity2, context)
                    all_embeddings.append(entity1_embedding.tolist())
                    all_embeddings.append(entity2_embedding.tolist())

            # Fit UMAP on all collected embeddings
            self.fit_umap(all_embeddings)        
            updated_pairs = []
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
                    entity1_embedding = self.extract_entity_embedding(entity1, context)
                    entity2_embedding = self.extract_entity_embedding(entity2, context)
                    pair_dict = pair[3]
                    pair_dict['entity1_embedding'] = self.reducer.transform([entity1_embedding.tolist()])[0]
                    pair_dict['entity2_embedding'] = self.reducer.transform([entity2_embedding.tolist()])[0]
                    updated_inner_list.append((entity1, full_context, entity2, pair_dict))
                updated_pairs.append(updated_inner_list)
                
            return updated_pairs
        
        except Exception as e:
            self.logger.error(f"Error extracting and appending entity embedding: {e}")
            raise Exception("Error extracting and appending entity embedding: {}".format(e))


