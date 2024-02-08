import json
from pydantic import BaseModel
from typing import List, Tuple, Dict

"""
    A model representing contextual information about a predicate in a knowledge graph.

    Attributes:
    -----------
    context : str
        The context in which the predicate is used.
    entity1_score, entity2_score : float
        Scores associated with the two entities involved in the predicate.
    entity1_label, entity2_label : str
        Labels associated with the two entities.
    entity1_nn_chunk, entity2_nn_chunk : str
        Nearest neighbor chunks for the two entities.
    file_path : str
        Path to the file where the predicate information is stored.
    entity1_attnscore, entity2_attnscore : float
        Attention scores for the two entities.
    entity1_embedding, entity2_embedding : List[float]
        Embeddings for the two entities.

    Methods:
    --------
    from_tuple(data: Tuple[str, str, str, Dict[str, str], str]) -> 'ContextualPredicate':
        Class method to create an instance of ContextualPredicate from a tuple.
    """

class ContextualPredicate(BaseModel):
    context: str
    entity1_score: float
    entity2_score: float
    entity1_label: str
    entity2_label: str
    entity1_nn_chunk: str
    entity2_nn_chunk: str
    file_path: str
    entity1_attnscore: float
    entity2_attnscore: float
    pair_attnscore: float
    entity1_embedding: List[float]
    entity2_embedding: List[float]
    
    
    @classmethod
    def from_tuple(cls, data: Tuple[str, str, str, Dict[str, str], str]) -> 'ContextualPredicate':
        try:
            entity1_embedding = data[3].get('entity1_embedding', []) if 'entity1_embedding' in data[3] else []
            entity2_embedding = data[3].get('entity2_embedding', []) if 'entity2_embedding' in data[3] else []

            return cls(
                context=data[1],
                entity1_score=float(data[3].get('entity1_score', 0.0)),
                entity2_score=float(data[3].get('entity2_score', 0.0)),
                entity1_label=data[3].get('entity1_label'),
                entity2_label=data[3].get('entity2_label'),
                entity1_nn_chunk=data[3].get('entity1_nn_chunk'),
                entity2_nn_chunk=data[3].get('entity2_nn_chunk'),
                entity1_attnscore=data[3].get('entity1_attnscore',1),
                entity2_attnscore=data[3].get('entity2_attnscore',1), 
                pair_attnscore=data[3].get('pair_attnscore',1), 
                entity1_embedding=entity1_embedding,
                entity2_embedding=entity2_embedding,
                file_path=data[4]
            )
        except Exception as e:
            raise ValueError(f"Error creating ContextualPredicate from tuple: {e}")



def process_data(data: List[List[Tuple[str, str, str, Dict[str, float], str]]], file_path: str) -> List[Tuple[str, str, str]]:
    result = []
    try:
        for inner_list in data:
            for tup in inner_list:
                if tup:  # Check if tuple is not empty
                    extended_tup = (*tup, file_path)
                    # Convert extended tuple to ContextualPredicate object and then to JSON string
                    context_metadata_str = ContextualPredicate.from_tuple(extended_tup)
                    context_metadata_str = json.dumps(context_metadata_str.dict(), ensure_ascii=False)
                    result.append((tup[0], context_metadata_str, tup[2]))
                    
        return result
    
    except Exception as e:
        raise ValueError(f"Error processing data: {e}")

