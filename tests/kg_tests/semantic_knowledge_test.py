import pytest
from querent.graph.errors import InvalidParameter
from querent.graph.utils import URI, Literal
from querent.kg.semantic_knowledge import SemanticKnowledge

def test_semantic_knowledge():
    s1 = URI("http://geodata.org/eocene")
    o1 = URI("http://geodata.org/mexico")
    p1 = URI("http://relations.org/deep_marine_section")
    p2 = URI("http://relations.org/determined_using")

    knowledge1 = SemanticKnowledge(s1)

    knowledge1.add_context(p1, o1)
    knowledge1.add_context(p2, o1)
    assert (s1, p1, o1) in list(knowledge1)
    assert (s1, p2, o1) in list(knowledge1)

    # Testing removal of context
    knowledge1.remove_context(p1, o1)
    assert (s1, p1, o1) not in list(knowledge1)

    # Testing invalid parameters
    with pytest.raises(InvalidParameter):
        knowledge1.add_context("invalid_predicate", o1)
    with pytest.raises(InvalidParameter):
        knowledge1.add_context(p1, "invalid_object")

    # Test memory usage calculation
    assert isinstance(knowledge1._calculate_memory_usage(), int)

# Run the test
test_semantic_knowledge()

def test_semantic_knowledge_reification_and_metadata():
    s = URI("http://geodata.org/example")
    p = URI("http://relations.org/hasProperty")
    o = URI("http://geodata.org/value")
    metadata = {
        "accuracy": "high",
        "source": "sensor data"
    }

    knowledge = SemanticKnowledge(s)
    knowledge.add_context(p, o, metadata=metadata, reify=True)

    # Check if the original triple is present
    assert (s, p, o) in list(knowledge)

    # Check for the presence of metadata triples
    reified_subject = knowledge._generate_reified_subject(p, o)
    for meta_key, meta_value in metadata.items():
        meta_predicate = URI(f"http://metadata.org/{meta_key}")
        meta_object = Literal(meta_value)
        assert (reified_subject, meta_predicate, meta_object) in list(knowledge)

    # Test the removal of reified triples and metadata
    knowledge.remove_context(p, o)
    assert (s, p, o) not in list(knowledge)

    # After removal, check if the metadata is also removed
    for meta_key, meta_value in metadata.items():
        meta_predicate = URI(f"http://metadata.org/{meta_key}")
        meta_object = Literal(meta_value)
        assert (reified_subject, meta_predicate, meta_object) not in list(knowledge)

# Run the test
test_semantic_knowledge_reification_and_metadata()
