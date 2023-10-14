from abc import ABC
from rdflib import Literal, URIRef, BNode
from sqlalchemy import Column, Integer, String


class QuerentQuad(ABC):
    """
    A quad is a triple with a context.
    """

    __tablename__ = "querent_quad"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    predicate = Column(String)
    object = Column(String)
    context = Column(String)

    def __init__(self, subject, predicate, object, context):
        """
        Initialize a quad.

        Args:
            subject: The subject of the quad.
            predicate: The predicate of the quad.
            object: The object of the quad.
            context: The context or named graph associated with the quad.

        """
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.context = context

    def __repr__(self):
        """
        Return a string representation of the quad.

        Returns:
            str: A string representation of the quad.

        """
        return f"<QuerentQuad ({self.subject}, {self.predicate}, {self.object}, {self.context})>"

    def __eq__(self, other):
        """
        Check if two quads are equal.

        Args:
            other (QuerentQuad): The other quad to compare.

        Returns:
            bool: True if the quads are equal, False otherwise.

        """
        if isinstance(other, QuerentQuad):
            return (
                self.subject == other.subject
                and self.predicate == other.predicate
                and self.object == other.object
                and self.context == other.context
            )
        else:
            return False

    def __hash__(self):
        """
        Return a hash of the quad.

        Returns:
            int: A hash of the quad.

        """
        return hash((self.subject, self.predicate, self.object, self.context))

    def to_rdflib_quad(self):
        """
        Convert the quad to an rdflib quad.

        Returns:
            tuple: An rdflib quad.

        """
        if self.context.startswith("_:"):
            # Use BNode for blank node context
            # example: _:b0
            context = BNode(self.context[2:])
        else:
            context = URIRef(self.context)

        return (
            URIRef(self.subject),
            URIRef(self.predicate),
            URIRef(self.object),
            context,
        )
