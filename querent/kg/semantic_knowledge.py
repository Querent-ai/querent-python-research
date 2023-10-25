from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, BNode, Literal
from querent.graph.subject import Reification, Subject

"""
    Represents a semantic knowledge graph node with properties and relationships.

    The class is designed to handle the storage and manipulation of semantic knowledge
    in the form of subjects, predicates, and objects. The subject and objects are represented 
    by URIs, while the predicates can be either URIs or Literals.

    Attributes:
        _resource (dict): A dictionary storing the relationships of the subject.
        _s (URI): The subject represented as a URI.

    Methods:
        add_semantics(p, o, reify=None): Adds a property (predicate-object relationship) to the subject.
        remove_semantics(p, o=None): Removes a property from the subject.
        get_properties(): Returns a list of all predicates associated with the subject.
        get_objects(p): Returns a list of all objects associated with a given predicate.
        _calculate_memory_usage(): Calculates the memory usage of the stored data.
"""
class SemanticKnowledge(Subject):
    def __init__(self, s):
        if not isinstance(s, URI):
            raise InvalidParameter("Subject needs to be a URI.")
        self._resource = dict()
        self._s = s

    def add_semantics(self, p, o, reify=None):
        if not isinstance(o, URI):
            raise InvalidParameter("Object needs to be a URI.")
        if not isinstance(p, (Literal, URI)):
            raise InvalidParameter("Predicate needs to be either a Literal or a URI.")

        if p not in self._resource:
            self._resource[p] = set([])
        self._resource[p].add(o)

        if reify:
            self.add_semantics(reify.p1, reify)
            if isinstance(reify, Reification):
                reify.add_property(reify.p2, o)
            return reify

    def remove_semantics(self, p, o=None):
        if not isinstance(p, (Literal, URI)):
            raise InvalidParameter("Predicate needs to be either a Literal or a URI.")
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

    def get_properties(self):
        return list(self._resource.keys())

    def get_objects(self, p):
        return list(self._resource.get(p, []))

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
