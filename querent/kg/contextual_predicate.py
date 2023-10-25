from pydantic import BaseModel
from typing import List, Tuple, Dict

"""
    Represents a contextual predicate model that captures the relationship between two entities within a specific context.

    Attributes:
    - context (str): The context in which the relationship between the two entities is defined.
    - entity1_score (float): The confidence score of the first entity.
    - entity2_score (float): The confidence score of the second entity.
    - entity1_label (str): The label or category of the first entity.
    - entity2_label (str): The label or category of the second entity.
    - entity1_nn_chunk (str): The named entity recognition chunk for the first entity.
    - entity2_nn_chunk (str): The named entity recognition chunk for the second entity.
    - file_path (str): The path to the file containing the data.

    Methods:
    - from_tuple: A class method that constructs a ContextualPredicate object from a given tuple of data.
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

    @classmethod
    def from_tuple(cls, data: Tuple[str, str, str, Dict[str, str], str]) -> 'ContextualPredicate':
        return cls(
            context=data[1],
            entity1_score=data[3]['entity1_score'],
            entity2_score=data[3]['entity2_score'],
            entity1_label=data[3]['entity1_label'],
            entity2_label=data[3]['entity2_label'],
            entity1_nn_chunk=data[3]['entity1_nn_chunk'],
            entity2_nn_chunk=data[3]['entity2_nn_chunk'],
            file_path=data[4]
            
        )


    """
    Converts a list of tuples representing contextual predicates into a list of JSON strings.

    Args:
    - tuples_list (List[Tuple[str, str, str, Dict[str, str]]]): A list of tuples where each tuple contains entities, context, and associated metadata.

    Returns:
    - List[str]: A list of JSON strings representing the contextual predicates.

    Usage:
    This function is useful for converting raw data tuples into a structured JSON format using the ContextualPredicate model.
    """
    
def convert_tuples_to_json(tuples_list: List[Tuple[str, str, str, Dict[str, str], str]]) -> List[str]:
    return [ContextualPredicate.from_tuple(t).json() for t in tuples_list]

if __name__ == '__main__':
    sample_data = [
        ('eocene', 'ABSTRACT In this study...', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.99, 'entity1_label': 'B-GeoTime, B-GeoMeth', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico'},'dummy.txt'),

    ]
    json_list = convert_tuples_to_json(sample_data)
    for json_str in json_list:
        print(json_str)
        print(type(json_str))
