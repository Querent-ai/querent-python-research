from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, BNode, Literal
from querent.graph.subject import Reification, Subject
import hashlib

class SemanticKnowledge(Subject):
    def __init__(self, s):
        if not isinstance(s, URI):
            raise InvalidParameter("Subject needs to be a URI.")
        self._resource = dict()
        self._reified_subjects = dict()
        self._s = s
        self._size_len = 0

    def add_context(self, p, o, metadata=None, reify=None, base_uri="http://geodata.org/"):
        if not isinstance(o, URI):
            raise InvalidParameter("Object needs to be a URI.")
        if not isinstance(p, URI):
            raise InvalidParameter("Predicate needs to be a URI.")
        if p not in self._resource:
            self._resource[p] = set()
        self._resource[p].add(o)
        if reify and metadata:
            reified_subject = self._generate_reified_subject(p, o)

            rdf_type_stmt = URI(base_uri + "type")
            rdf_statement = URI(base_uri + "Statement")
            rdf_subject = URI(base_uri + "subject")
            rdf_predicate = URI(base_uri + "predicate")
            rdf_object = URI(base_uri + "object")

            self._resource.setdefault(reified_subject, set()).add((rdf_type_stmt, rdf_statement))
            self._resource.setdefault(reified_subject, set()).add((rdf_subject, self._s))
            self._resource.setdefault(reified_subject, set()).add((rdf_predicate, p))
            self._resource.setdefault(reified_subject, set()).add((rdf_object, o))
            if reified_subject not in self._reified_subjects:
                self._reified_subjects[reified_subject] = []

            for meta_key, meta_value in metadata.items():
                meta_predicate = URI(f"http://metadata.org/{meta_key}")
                meta_object = Literal(meta_value)
                self._resource.setdefault(reified_subject, set()).add((meta_predicate, meta_object))
            represents_literal = Literal(f"{self._s} {p} {o}")
            self._reified_subjects[reified_subject].append((URI("http://represents.org/represents"), represents_literal))


    def remove_context(self, p, o=None):
        if not isinstance(p, URI):
            raise InvalidParameter("Predicate needs to be a URI.")
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
    
    def _generate_reified_subject(self, p, o):
        hash_input = str(self._s) + str(p) + str(o)
        hash_output = hashlib.sha1(hash_input.encode()).hexdigest()[:8]

        return URI(f"http://geodata.org/reified/{hash_output}")

    @property
    def subject(self):
        return self._s

    @staticmethod
    def __is_valid_object(o):
        return isinstance(o, (URI, Subject))

    def __iter__(self):       
        for subject, triples in self._resource.items():
            for item in triples:
                if isinstance(item, tuple):
                    p, o = item
                    yield subject, p, o
                else:
                    o = item
                    yield self._s, subject, o

    def __next__(self):
        return self.__iter__()

    def _calculate_memory_usage(self):
        return sum(
            [
                len(str(self._s)),
                sum([   len(str(p)) + len(str(o)) + len(str(self._metadata.get((p, o), '')))
                        for p, os in self._resource.items()
                        for o in os]),])
