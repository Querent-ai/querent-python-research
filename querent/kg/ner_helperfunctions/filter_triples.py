import json
import numpy as np
import hdbscan
from scipy.spatial.distance import cosine
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from querent.logging.logger import setup_logger
from typing import List, Tuple, Dict

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
    
    filter_by_cluster_persistence:
        Filter triples by cluster persistence to retain only those belonging to clusters with high persistence values.
        
    Notes
    -----
    - The class expects triples in the form of (entity1, context, entity2), where 'context' is a JSON string containing various attributes including the embeddings.
    - The embeddings are expected to be in a format that can be converted to numpy arrays.
    - The class is designed to be flexible and allows for customization of the clustering process through various parameters.
"""

class TripleFilter:
    def __init__(self, score_threshold, attention_score_threshold, similarity_threshold, min_cluster_size=2, min_samples=None, cluster_persistence_threshold=-1):
        self.score_threshold = score_threshold
        self.attention_score_threshold = attention_score_threshold
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.logger = setup_logger(__name__, "TripleFilter")
        self.min_samples = min_samples if min_samples is not None else self.min_cluster_size
        self.cluster_persistence_threshold = cluster_persistence_threshold

    @staticmethod
    def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        
        return cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0, 0]

    def filter_by_score(self, data: dict) -> bool:
        
        return data['entity1_score'] >= self.score_threshold and data['entity2_score'] >= self.score_threshold

    def filter_by_attention_score(self, data: dict) -> bool:
        
        return data['pair_attnscore'] >= self.attention_score_threshold

    def filter_by_embedding_similarity(self, data: dict) -> bool:
        similarity = self.calculate_cosine_similarity(data['entity1_embedding'], data['entity2_embedding'])
        
        return similarity >= self.similarity_threshold

    def filter_triples(self, triples: List[Tuple[str, str, str]]) -> Tuple[List[Tuple[str, str, str]], int]:
        relevant_triples = []
        initial_count = len(triples)
        for triple in triples:
            try:
                entity1, json_data, entity2 = triple
                data = json.loads(json_data)                
                if not self.filter_by_score(data) or not self.filter_by_attention_score(data) or not self.filter_by_embedding_similarity(data):
                    continue

                relevant_triples.append(triple)
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to filter triples {e}")
                raise Exception(f"Unable to filter triples: {e}")
        reduction_count = initial_count - len(relevant_triples)
        
        return relevant_triples, reduction_count

    @staticmethod
    def combine_embeddings(entity1_embedding: np.ndarray, entity2_embedding: np.ndarray) -> np.ndarray:
        # Check if the two embeddings are the same
        if np.array_equal(entity1_embedding, entity2_embedding):
            return entity1_embedding
        else:
            return np.concatenate((entity1_embedding, entity2_embedding))

    def cluster_triples(self, triples: List[Tuple[str, str, str]]) -> Dict[str, any]:
        try:
            combined_embeddings = np.array([
                self.combine_embeddings(
                    json.loads(triple[1])['entity1_embedding'],
                    json.loads(triple[1])['entity2_embedding']
                ) for triple in triples
            ])
            scaler = StandardScaler()
            normalized_embeddings = scaler.fit_transform(combined_embeddings)
            distance_matrix = 1 - cosine_similarity(normalized_embeddings)
            clusterer = hdbscan.HDBSCAN(
                metric='precomputed',
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                cluster_selection_method="leaf"
            )
            cluster_labels = clusterer.fit_predict(distance_matrix)
            cluster_persistence = clusterer.cluster_persistence_

            filtered_triples = [triples[index] for index, label in enumerate(cluster_labels) if label != -1]
            cluster_output = {
                'filtered_triples': filtered_triples,
                'reduction_count': len(triples) - len(filtered_triples),
                'cluster_labels': cluster_labels,
                'cluster_persistence': cluster_persistence
            }

            return cluster_output

        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to apply clustering on triples {e}")
            raise Exception(f"Error during clustering: {e}")

    def filter_by_cluster_persistence(self, triples: List[Tuple[str, str,str]], cluster_persistence, cluster_labels) -> List[Tuple[str, str, str]]:
        if self.cluster_persistence_threshold != -1:
            high_persistence_triples = []
            high_persistence_clusters = [index for index, persistence in enumerate(cluster_persistence) if persistence > self.cluster_persistence_threshold]
            for i, (triple, label) in enumerate(zip(triples, cluster_labels)):
                if label in high_persistence_clusters:
                    high_persistence_triples.append(triple)
                    
            return high_persistence_triples
        
        else:
            
            return None