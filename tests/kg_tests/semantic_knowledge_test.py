import pytest
from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, Literal
from querent.kg.semantic_knowledge import SemanticKnowledge

"""
    Test the functionality of the SemanticKnowledge class.

    This test covers the following scenarios:
    1. Initialization of the SemanticKnowledge class with a subject.
    2. Adding properties (predicates and objects) to the knowledge.
    3. Ensuring that multiple relationships can be added between the same pair of entities.
    4. Testing the addition of a Literal as a predicate.
    5. Testing the addition of a common relationship type between different subject-object pairs.
    6. Removal of a property from the knowledge.
    7. Handling of invalid parameters during the addition of properties.
    8. Calculation of memory usage for the knowledge.

    Assertions:
    - Ensure that properties are correctly added to the knowledge.
    - Ensure that properties can be correctly removed from the knowledge.
    - Ensure that invalid parameters are handled with appropriate exceptions.
    - Ensure that memory usage calculation returns an integer value.
    """

def test_semantic_knowledge():
    s1 = URI("http://geodata.org/eocene")
    o1 = URI("http://geodata.org/mexico")
    p1 = URI("http://relations.org/deep marine section")
    p2 = URI("http://relations.org/determined using")
    p_literal = Literal("GeoTime Relationship")
    
    s2 = URI("http://geodata.org/mexico")
    o2 = URI("http://geodata.org/eocene")
    p_common = URI("http://relations.org/relatedTo")

    knowledge1 = SemanticKnowledge(s1)

    knowledge1.add_property(p1, o1)
    knowledge1.add_property(p2, o1)
    knowledge1.add_property(p_common, o1)
    knowledge1.add_property(p_literal, o1)

    assert (s1, p1, o1) in knowledge1
    assert (s1, p2, o1) in knowledge1
    assert (s1, p_common, o1) in knowledge1
    assert (s1, p_literal, o1) in knowledge1

    knowledge2 = SemanticKnowledge(s2)

    knowledge2.add_property(p_common, o2)

    assert (s2, p_common, o2) in knowledge2

    knowledge1.remove_property(p1, o1)
    assert (s1, p1, o1) not in knowledge1


    with pytest.raises(InvalidParameter):
        knowledge1.add_property("invalid_predicate", o1)

    with pytest.raises(InvalidParameter):
        knowledge1.add_property(p1, "invalid_object")


    assert isinstance(knowledge1._calculate_memory_usage(), int)
    assert isinstance(knowledge2._calculate_memory_usage(), int)

# Run the test
test_semantic_knowledge()
