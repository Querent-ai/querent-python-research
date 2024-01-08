from pydantic import BaseModel, validator, Field
from typing import List

class Triples(BaseModel):
    """Call this to get triples extracted from a single sentence"""

    subject: str = Field(description="What (or Whom) the sentence is about")
    object: str = Field(
        description="Whom (or upon) Which action of the verb is carried out."
    )
    predicate: str = Field(
        description="Contains the verb that represents the action done by the subject"
    )

    subject_type: str = Field(description="Type of subject as per NER")
    object_type: str = Field(description="Type of object as per NER")
    predicate_type: str = Field(description="Type of predicate as per NER")


class TriplesList(BaseModel):
    """Call this to get list of triples extracted from a single sentence"""

    triples: List[Triples] = Field(description="list of objects of type Triples")
