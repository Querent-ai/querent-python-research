from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

class SemanticTripleFilter:
    def __init__(self, similarity_threshold=0.3, max_predicate_words=5):
        self.similarity_threshold = similarity_threshold
        self.max_predicate_words = max_predicate_words
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_predicate_embedding(self, predicate: str):
        return self.model.encode(predicate, convert_to_tensor=True).numpy()

    def is_similar(self, embedding1, embedding2):
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return similarity > self.similarity_threshold

    def filter_triples(self, triples):
        # Store unique triples
        unique_triples = []
        # Keep track of embeddings for comparison
        embeddings_dict = {}

        for triple in triples:
            subject, json_string, obj = triple
            data = json.loads(json_string)
            predicate = data.get("predicate","")
            # subject, predicate, obj = triple
            triple_key = (subject, obj)

            # Skip processing for long predicates, assuming they're unique
            if len(predicate.split()) > self.max_predicate_words:
                unique_triples.append(triple)
                continue

            # Generate or retrieve embedding
            if predicate not in embeddings_dict:
                embeddings_dict[predicate] = self.generate_predicate_embedding(predicate)
            predicate_embedding = embeddings_dict[predicate]

            # Check against existing triples
            if triple_key not in embeddings_dict:
                embeddings_dict[triple_key] = predicate_embedding
                unique_triples.append(triple)
            else:
                existing_embedding = embeddings_dict[triple_key]
                if not self.is_similar(existing_embedding, predicate_embedding):
                    unique_triples.append(triple)
                    # Update the embedding to represent the most recent addition
                    embeddings_dict[triple_key] = predicate_embedding

        return unique_triples
