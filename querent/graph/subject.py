from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, BNode, Literal


class Subject:
    def __init__(self, s):
        if not isinstance(s, (URI, BNode)):
            raise InvalidParameter("Subject needs to be URI or BNode")
        self._resource = dict()
        self._s = s
        self._size_len = 0

    def add_property(self, p, o, reify=None):
        """

        :param p: URI, predicate
        :param o: [URI, BNode, Literal, Subject], object
        :param reify: Optional[Reification, Tuple[URI, Optional[URI or BNode],
                        Tuple[URI, URI, Optional[URI, BNode]]
                    None -> don't reify
                    Reification -> reify with Reification specification
                    URI -> reify with specific predicate
                    (URI, Optional[Term]) -> reify, and use provided statement term or BNode
                    (URI, URI, Optional[Term]) -> reify with two predicates, statement term or BNode
        :return: statement term if reify else None
        """
        if not isinstance(p, URI):
            raise InvalidParameter("Predict needs to be URI")
        if not self.__is_valid_object(o):
            raise InvalidParameter(
                "Object needs to be URI or BNode or Literal or Triple"
            )

        if p not in self._resource:
            self._resource[p] = set([])
        self._resource[p].add(o)

        if reify:
            self.add_property(reify.p1, reify)
            if isinstance(reify, Reification):
                reify.add_property(reify.p2, o)
            return reify

    def remove_property(self, p, o=None):
        if not isinstance(p, URI):
            raise InvalidParameter("Predicate needs to be URI")
        if o and not self.__is_valid_object(o):
            raise InvalidParameter(
                "Object needs to be URI or BNode or Literal or Triple"
            )

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


class Reification(Subject):
    def __init__(self, p1, p2=None, statement=None):
        """
        Make reification.

        :param p1: URI, predicate for reification
        :param p2: Optional[URI],
                    URI -> second predicate for reification
                    None -> reuse p1 as second predicate
        :param statement: Optional[Union[URI, BNode]],
                    URI or BNode -> use provided node as statement term
                    None -> generate a new BNode as statement term
        """
        if isinstance(p1, URI):
            self.p1 = p1
        else:
            raise InvalidParameter("Reification predicate needs to be a valid URI")

        if p2 is None:
            self.p2 = p1
        elif isinstance(p2, URI):
            self.p2 = p2
        else:
            raise InvalidParameter(
                "Reification second predicate needs to be a valid URI or None"
            )

        if statement is None:
            self.statement = BNode()
        elif isinstance(statement, (URI, BNode)):
            self.statement = statement
        else:
            raise InvalidParameter(
                "Reification statement term needs to be a valid URI or BNode or None"
            )
        super().__init__(self.statement)
