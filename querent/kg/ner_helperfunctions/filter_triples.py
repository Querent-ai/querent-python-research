import json
import numpy as np
import hdbscan
from scipy.spatial.distance import cosine
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

"""
    A class used to filter and cluster triples of (entity1, context, entity2) based on various scoring metrics and embedding similarities.

    Attributes
    ----------
    score_threshold : float
        The minimum score that both entities in a triple must have to be considered relevant.
    attention_score_threshold : float
        The minimum attention score that a triple must have to be considered relevant.
    similarity_threshold : float
        The minimum cosine similarity score between the embeddings of the entities to be considered relevant.
    min_cluster_size : int
        The minimum size of clusters to be formed by the HDBSCAN clustering algorithm.
    min_samples : int
        The number of samples in a neighborhood for a point to be considered a core point.

    Methods
    -------
    calculate_cosine_similarity(embedding1, embedding2):
        Calculates the cosine similarity between two embeddings.

    filter_by_score(data):
        Filters triples by checking if the entity scores meet the score threshold.

    filter_by_attention_score(data):
        Filters triples by checking if the pair attention score meets the attention score threshold.

    filter_by_embedding_similarity(data):
        Filters triples by checking if the cosine similarity between entity embeddings meets the similarity threshold.

    filter_triples(triples):
        Filters a list of triples by applying score, attention score, and embedding similarity filters.

    combine_embeddings(entity1_embedding, entity2_embedding):
        Combines two entity embeddings into a single embedding.

    cluster_triples(triples):
        Clusters the filtered triples using the HDBSCAN algorithm and returns the clusters along with the reduction count and the clusterer instance.

    Notes
    -----
    - The class expects triples in the form of (entity1, context, entity2), where 'context' is a JSON string containing various attributes including the embeddings.
    - The embeddings are expected to be in a format that can be converted to numpy arrays.
    - The class is designed to be flexible and allows for customization of the clustering process through various parameters.
"""

class TripleFilter:
    def __init__(self, score_threshold, attention_score_threshold, similarity_threshold, min_cluster_size=2, min_samples=None):
        self.score_threshold = score_threshold
        self.attention_score_threshold = attention_score_threshold
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples if min_samples is not None else self.min_cluster_size

    @staticmethod
    def calculate_cosine_similarity(embedding1, embedding2):
        try:
            embedding1 = np.asarray(embedding1)
            embedding2 = np.asarray(embedding2)
            if embedding1.ndim == 1:
                embedding1 = embedding1.reshape(1, -1)
            if embedding2.ndim == 1:
                embedding2 = embedding2.reshape(1, -1)
            if embedding1.shape[1] != embedding2.shape[1]:
                raise ValueError("Embeddings must have the same length")
            
            return cosine_similarity(embedding1, embedding2)[0, 0]
        
        except Exception as e:
            raise(f"Error calculating cosine similarity: {e}")


    def filter_by_score(self, data):
        try:
            return (data['entity1_score'] >= self.score_threshold and
                    data['entity2_score'] >= self.score_threshold)
            
        except KeyError as e:
            raise(f"Missing score in data: {e}")


    def filter_by_attention_score(self, data):
        try:
            return (data['pair_attnscore'] >= self.attention_score_threshold)
        
        except KeyError as e:
            raise(f"Missing attention score in data: {e}")
            
    def filter_by_embedding_similarity(self, data):
        try:
            similarity = self.calculate_cosine_similarity(data['entity1_embedding'], data['entity2_embedding'])
            
            return similarity >= self.similarity_threshold
        
        except Exception as e:
            raise(f"Error filtering by embedding similarity: {e}")

    def cosine_distance(u, v):
    
        return cosine(u, v)
    
    def filter_triples(self, triples):
        relevant_triples = []
        initial_count = len(triples)
        for triple in triples:
            try:
                entity1, json_data, entity2 = triple
                data = json.loads(json_data)
                
                if not self.filter_by_score(data):
                    continue
                if not self.filter_by_attention_score(data):
                    continue
                if not self.filter_by_embedding_similarity(data):
                    continue
                
                relevant_triples.append(triple)
            except (json.JSONDecodeError, KeyError) as e:
                raise(f"Error processing triple: {e}")
        reduction_count = initial_count - len(relevant_triples)
        
        return relevant_triples, reduction_count

    def combine_embeddings(self, entity1_embedding, entity2_embedding):
        try:
        
            return np.concatenate((entity1_embedding, entity2_embedding))
        
        except Exception as e:
            raise(f"Error combining embeddings: {e}")
            
    def cluster_triples(self, triples):
        try:
            combined_embeddings = np.array([
                self.combine_embeddings(
                    json.loads(triple[1])['entity1_embedding'],
                    json.loads(triple[1])['entity2_embedding']
                ) for triple in triples
            ])
            scaler = StandardScaler()
            normalized_embeddings = scaler.fit_transform(combined_embeddings)
            clusterer = hdbscan.HDBSCAN(metric=TripleFilter.cosine_distance, min_cluster_size=self.min_cluster_size, min_samples=self.min_samples, cluster_selection_method="leaf")
            cluster_labels = clusterer.fit_predict(normalized_embeddings)
            initial_count = len(triples)
            clustered_triples = list(zip(triples, cluster_labels))
            filtered_triples = [triple for triple, label in clustered_triples if label != -1]
            reduction_count = initial_count - len(filtered_triples)
            
            return filtered_triples, reduction_count, clusterer
        
        except Exception as e:
            raise(f"Error during clustering: {e}")

