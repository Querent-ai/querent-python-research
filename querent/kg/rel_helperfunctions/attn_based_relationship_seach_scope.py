import torch
import copy
from typing import List, Tuple, Dict
import numpy
    
class EntityPair:
    def __init__(self, head_entity: Dict, tail_entity: Dict, context: str, head_positions, tail_positions):
        self.head_entity = head_entity
        self.tail_entity = tail_entity
        self.context = context
        self.head_entity['start_idx'], self.head_entity['end_idx'] = head_positions[0]
        self.tail_entity['start_idx'], self.tail_entity['end_idx'] = tail_positions[0]

class SearchContextualRelationship:
    
    def __init__(self, initial_token_id):
        self.current_token = initial_token_id
        self.total_score = 0
        self.visited_tokens = [initial_token_id]
        self.relation_tokens = []

    def add_token(self, token_id, score):
        self.current_token = token_id
        self.visited_tokens.append(token_id)
        self.total_score += score
        self.relation_tokens.append(token_id)

    def has_relation(self) -> bool:
        return len(self.relation_tokens) > 0

    def finalize_path(self, score):
        self.total_score += score

    def mean_score(self) -> float:
        if len(self.relation_tokens) == 0:
            return 0
        return self.total_score / len(self.relation_tokens)


def sort_by_mean_score(path: SearchContextualRelationship) -> float:
    return path.mean_score()


def is_valid_token(token_id, pair: EntityPair, candidate_paths: List[SearchContextualRelationship], current_path: SearchContextualRelationship, score: float) -> bool:
    if pair.tail_entity['start_idx'] <= token_id <= pair.tail_entity['end_idx']:
        if current_path.has_relation():
            current_path.finalize_path(score)
            candidate_paths.append(current_path)
            return False

    return not (pair.head_entity['start_idx'] <= token_id <= pair.head_entity['end_idx'] or
                pair.tail_entity['start_idx'] <= token_id <= pair.tail_entity['end_idx'])



def perform_search(entity_start_index, attention_matrix: torch.Tensor, entity_pair: EntityPair, search_candidates: int, require_contiguous: bool, max_relation_length: int, num_initial_tokens: int) -> List[SearchContextualRelationship]:
    """
        Initialize the perform search function with the following parameters:
        :param attention_matrix :Mean attention score, average attention each token pays to every other token showing which tokens are most related to each other in the context of the given sentence(s).
        :param search_candidates: Number of candidates to select for the next iteration of the search
        :param contiguous_token: When generating relations, consider only those with contiguous tokens
        :param max_relation_length: Maximum quantity of tokens allowed in a relation.
        :patam num_initial_tokens: Different for different models. E.g. 'Bert' adds a '[CLS]' to the start of a sequence, so it is 1.
        
    """
    try:
        queue = [
            SearchContextualRelationship(entity_start_index)
        ]
        candidate_paths = []
        visited_paths = set()
        while len(queue) > 0:
            current_path = queue.pop(0)

            if len(current_path.relation_tokens) > max_relation_length:
                continue

            if require_contiguous and len(current_path.relation_tokens) > 1 and abs(current_path.relation_tokens[-2] - current_path.relation_tokens[-1]) != 1:
                continue

            new_paths = []
            
            # How all other tokens attend to an entity e.g. "Emily Stanton"
            # These scores indicate how much importance the model places on each token when considering "Emily Stanton."
            # The tokens which consider entity "Emily Stanton" important, highlight entity's relationships and relevance within the sentence.
            
            attention_scores = attention_matrix[:, current_path.current_token]
            for i in range(num_initial_tokens, len(attention_scores) - 1):
                next_path = tuple(current_path.visited_tokens + [i])
                if is_valid_token(i, entity_pair, candidate_paths, current_path, attention_scores[i].detach()) and next_path not in visited_paths and current_path.current_token != i:
                    new_paths.append(
                        copy.deepcopy(current_path)
                    )
                    new_paths[-1].add_token(i, attention_scores[i].detach())
                    visited_paths.add(next_path)
            new_paths.sort(key=sort_by_mean_score, reverse=True)
            queue += new_paths[:search_candidates]

        return candidate_paths
    except Exception as e:
        raise e
        

