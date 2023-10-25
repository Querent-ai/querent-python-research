from querent.graph.errors import InvalidParameter
from querent.kg.contextual_knowledge import ContextualKnowledge
import pytest
from querent.graph.utils import URI, BNode

"""
    Test the functionality of the ContextualKnowledge class.

    This test covers the following scenarios:
    1. Initialization of the ContextualKnowledge class with a subject.
    2. Adding properties (predicates and objects) to the knowledge using a BNode for contextual data.
    3. Ensuring that the property is correctly added to the knowledge.
    4. Removal of a property from the knowledge.
    5. Handling of invalid parameters during the addition of properties.
    6. Calculation of memory usage for the knowledge.

    Assertions:
    - Ensure that properties are correctly added to the knowledge.
    - Ensure that properties can be correctly removed from the knowledge.
    - Ensure that invalid parameters are handled with appropriate exceptions.
    - Ensure that memory usage calculation returns an integer value.
    """

def test_contextual_knowledge():
    s = URI("http://geodata.org/eocene")
    o = URI("http://geodata.org/mexico")
    data_for_p = '{"context": "ABSTRACT In this study...", "entity1_score": 1.0, "entity2_score": 0.99, "entity1_label": "B-GeoTime, B-GeoMeth", "entity2_label": "B-GeoLoc", "entity1_nn_chunk": "Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "Mexico"}'
    p = BNode(data_for_p)
    
    knowledge = ContextualKnowledge(s)
    knowledge.add_property(p, o)

    assert (s, p, o) in knowledge

    knowledge.remove_property(p, o)
    assert (s, p, o) not in knowledge

    with pytest.raises(InvalidParameter):
        knowledge.add_property("invalid_predicate", o)

    with pytest.raises(InvalidParameter):
        knowledge.add_property(p, "invalid_object")

    assert isinstance(knowledge._calculate_memory_usage(), int)

# Run the test
test_contextual_knowledge()

