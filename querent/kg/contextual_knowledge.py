from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, BNode, Literal
from querent.graph.subject import Reification, Subject


"""
    Represents a contextual knowledge graph node with properties and relationships.

    The class is designed to handle the storage and manipulation of contextual knowledge
    in the form of subjects, predicates, and objects. The subject and objects are represented 
    by URIs, while the predicates will be of type B-Nodes.

    Attributes:
        _resource (dict): A dictionary storing the RDF triples.
        _s (URI): The subject of the RDF triple.
        _size_len (int): A size length variable (its purpose needs to be defined further).

    Methods:
        add_property(p, o, reify=None): Adds a property (predicate-object pair) to the resource.
        remove_property(p, o=None): Removes a property (predicate-object pair) from the resource.
        subject: Returns the subject of the RDF triple.
        __is_valid_object(o): Checks if the object is valid (either URI, BNode, Literal, or Subject).
        __iter__(): Returns an iterator over the RDF triples.
        __next__(): Returns the next item from the iterator.
        _calculate_memory_usage(): Calculates the memory usage based on the length of the strings in the RDF triples.

    Raises:
        InvalidParameter: If the provided parameters do not match the expected types (e.g., subject not being a URI).

    """
    
class ContextualKnowledge(Subject):
    def __init__(self, s):
        if not isinstance(s, URI):
            raise InvalidParameter("Subject needs to be a URI.")
        self._resource = dict()
        self._s = s
        self._size_len = 0

    def add_property(self, p, o, reify=None):
        if not isinstance(o, URI):
            raise InvalidParameter("Object needs to be a URI.")
        if not isinstance(p, BNode):
            raise InvalidParameter("Predicate needs to be a BNode.")
        if p not in self._resource:
            self._resource[p] = set([])
        self._resource[p].add(o)

        if reify:
            self.add_property(reify.p1, reify)
            if isinstance(reify, Reification):
                reify.add_property(reify.p2, o)
            return reify

    def remove_property(self, p, o=None):
        if not isinstance(p, BNode):
            raise InvalidParameter("Predicate needs to be a BNode.")
        if o and not isinstance(o, URI):
            raise InvalidParameter("Object needs to be a URI.")

        try:
            if not o:
                del self._resource[p]
            else:
                self._resource[p].remove(o)
                if not self._resource[p]:
                    del self._resource[p]
        except KeyError:
            return False

        return True

    @property
    def subject(self):
        return self._s

    @staticmethod
    def __is_valid_object(o):
        return isinstance(o, (URI, BNode, Literal, Subject))

    def __iter__(self):
        for p, os in self._resource.items():
            for o in os:
                yield self._s, p, o

    def __next__(self):
        return self.__iter__()

    def _calculate_memory_usage(self):
        return sum(
            [
                len(str(self._s)),
                sum(
                    [
                        len(str(p)) + len(str(o))
                        for p, os in self._resource.items()
                        for o in os
                    ]
                ),
            ]
        )

