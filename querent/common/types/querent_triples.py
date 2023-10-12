from pydantic import BaseModel
from sqlalchemy import Column, Integer, String


class QuerentTriple(BaseModel):
    """
    A triple in the graph.
    """

    __tablename__ = "querent_triples"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    predicate = Column(String)
    object = Column(String)

    def __init__(self, subject, predicate, object):
        """
        Initialize a triple.

        Args:
            subject: The subject of the triple.
            predicate: The predicate of the triple.
            object: The object of the triple.

        """
        self.subject = subject
        self.predicate = predicate
        self.object = object

    def __repr__(self):
        """
        Return a string representation of the triple.

        Returns:
            str: A string representation of the triple.

        """
        return "<QuerentTriple(%s, %s, %s)>" % (
            self.subject,
            self.predicate,
            self.object,
        )

    def __eq__(self, other):
        """
        Check if two triples are equal.

        Args:
            other (QuerentTriple): The other triple to compare.

        Returns:
            bool: True if the triples are equal, False otherwise.

        """
        return (
            self.subject == other.subject
            and self.predicate == other.predicate
            and self.object == other.object
        )

    def __hash__(self):
        """
        Return a hash of the triple.

        Returns:
            int: A hash of the triple.

        """
        return hash((self.subject, self.predicate, self.object))
