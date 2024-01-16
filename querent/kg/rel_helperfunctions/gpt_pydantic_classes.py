from pydantic import BaseModel, validator, Field
from typing import List

class ClassifyEntities(BaseModel):
    """A data structure for classifying entities within a sentence.

    Args:
        subject (str): The main entity or topic of the sentence.
            Example: "The cat" in the sentence "The cat chased the mouse."
        object (str): The entity that is acted upon or affected by the verb.
            Example: "the mouse" in the sentence "The cat chased the mouse."
        subject_type (str): The category or type of the subject as identified by Named Entity Recognition (NER).
            Example: "Animal" for the subject "The cat."
        object_type (str): The category or type of the object as identified by Named Entity Recognition (NER).
            Example: "Animal" for the object "the mouse."
    """
    
    subject: str = Field(description="The main entity or topic of the sentence.")
    object: str = Field(description="The entity that is acted upon or affected by the verb.")
    subject_type: str = Field(description="The category or type of the subject as identified by NER.")
    object_type: str = Field(description="The category or type of the object as identified by NER.")



class TriplesList(BaseModel):
    """Call this to get list of triples extracted from a single sentence"""

    triples: List[ClassifyEntities] = Field(description="list of objects of type Triples")


