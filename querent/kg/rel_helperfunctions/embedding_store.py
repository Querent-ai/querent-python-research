import json
from fastembed import TextEmbedding
from querent.logging.logger import setup_logger


class EmbeddingStore:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.logger = setup_logger("EmbeddingStore_config", "EmbeddingStore")
        try:
            self.model_name = model_name
            self.embeddings = TextEmbedding(model_name=model_name)
        except Exception as e:
            self.logger.error(
                f"Invalid {self.__class__.__name__} configuration. Failed to initialize EmbeddingStore: {e}"
            )
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
    
    def generate_embeddings(self, payload, relationship_finder=False, generate_embeddings_with_fixed_relationship = False):
        try:
            triples = payload
            processed_pairs = []
            for entity, json_string, related_entity in triples:
                try:
                    json_string = json_string.replace("\n", "")
                    data = json.loads(json_string)
                    context = data.get("context", "").replace('"', '\\"')
                    predicate = data.get("predicate","").replace('"', '\\"')
                    predicate_type = data.get("predicate_type","Unlabeled").replace('"', '\\"')
                    subject_type = data.get("subject_type","Unlabeled").replace('"', '\\"')
                    object_type = data.get("object_type","Unlabeled").replace('"', '\\"')
                    score = data.get("score")
                    context_embeddings = None
                    predicate_embedding = None
                    context_embeddings = self.get_embeddings([context])[0]
                    if relationship_finder and generate_embeddings_with_fixed_relationship:
                        predicate_embedding = self.get_embeddings([predicate + " ("+predicate_type+")"])[0]
                    elif relationship_finder:
                        predicate_embedding = self.get_embeddings([predicate_type])[0]
                    essential_data = {
                        "context": context,
                        "context_embeddings": context_embeddings,
                        "predicate_type": predicate_type,
                        "predicate": predicate,
                        "subject_type": subject_type,
                        "object_type": object_type,
                        "predicate_emb": predicate_embedding if predicate_embedding is not None else "Not Implemented",
                        "score":score
                    }
                    updated_json_string = json.dumps(essential_data)
                    processed_pairs.append(
                        (entity, updated_json_string, related_entity)
                    )
                except json.JSONDecodeError as e:
                    self.logger.debug(
                        f"JSON parsing error: {e} in string: {json_string}"
                    )

            return processed_pairs

        except Exception as e:
            self.logger.error(f"Error in extracting embeddings: {e}")

    def generate_relationship_embeddings(self, payload):
        try:
            relationships = payload
            processed_pairs = []

            for relation in relationships:
                try:
                    data = json.loads(relation)
                    predicate_value = data.get("predicate_value", "").replace('"', '\\"')
                    relationship = data.get("relationship","unlabelled").replace('"', '\\"')
                    relationship_type = data.get("type").replace('"', '\\"')
                    predicate_embedding = None
                    predicate_embedding = self.get_embeddings([predicate_value])[0]
                    essential_data = {
                        "predicate_value": predicate_value,
                        "predicate_emb" : predicate_embedding,
                        "relationship" : relationship,
                        "type" : relationship_type
                    }
                    updated_json_string = json.dumps(essential_data)
                    processed_pairs.append((updated_json_string))
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON parsing error while generating embeddings for fixed realtionships: {e} in string.")
                    
            return processed_pairs

        except Exception as e:
            self.logger.debug(f"Error in extracting embeddings for fixed realtionships: {e}")
