import json
from fastembed import TextEmbedding
from querent.logging.logger import setup_logger

class EmbeddingStore:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.logger = setup_logger("EmbeddingStore_config", "EmbeddingStore")
        try:
            self.model_name = model_name
            self.embeddings = TextEmbedding(model_name=model_name)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize EmbeddingStore: {e}")
            raise Exception(f"Failed to initialize EmbeddingStore: {e}")
    
    def get_embeddings(self, texts):
        try:
            embeddings = []
            for text in texts:
                embedding_generator = self.embeddings.embed(text)
                embedding = list(embedding_generator)[0]
                embeddings.append(embedding.tolist())
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise Exception(f"Failed to generate embeddings: {e}")
    
    
    def generate_embeddings(self, payload):
        try:
            triples = payload
            processed_pairs = []
            for entity, json_string, related_entity in triples:
                try:
                    data = json.loads(json_string)
                    context = data.get("context", "").replace('"', '\\"')
                    predicate = data.get("predicate","").replace('"', '\\"')
                    predicate_type = data.get("predicate_type","Unlabeled").replace('"', '\\"')
                    subject_type = data.get("subject_type","Unlabeled").replace('"', '\\"')
                    object_type = data.get("object_type","Unlabeled").replace('"', '\\"')
                    context_embeddings = self.get_embeddings([context])[0]
                    essential_data = {
                        "context": context,
                        "context_embeddings" : context_embeddings,
                        "predicate_type": predicate_type,
                        "predicate" : predicate,
                        "subject_type": subject_type,
                        "object_type": object_type
                    }
                    updated_json_string = json.dumps(essential_data)
                    processed_pairs.append((entity, updated_json_string, related_entity))
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON parsing error: {e} in string: {json_string}")

            return processed_pairs

        except Exception as e:
            self.logger.error(f"Error in extracting embeddings: {e}")

    