import json
import pytest
from querent.config.graph_config import GraphConfig
from querent.graph.subject import Subject
from querent.kg.querent_kg import QuerentKG
from querent.graph.utils import URI, BNode, Literal


@pytest.fixture
def schema():
    # Set up a sample ontology schema
    return json.dumps(
        {
            "fields": {
                "name": {"type": "string", "description": "Name of the person"},
                "location": {"type": "string", "description": "Location of the person"},
            }
        }
    )


@pytest.fixture
def querent_kg(schema):
    # Set up a QuerentKG instance for testing
    config = GraphConfig(
        identifier="test_kg",
        format="nt",
        store="default",
        schema=schema,
        flush_on_serialize=False,
    )
    return QuerentKG(config)


def test_add_knowledge(querent_kg: QuerentKG):
    # Create a Subject instance to represent knowledge about Alice
    alice = Subject(URI("http://example.org/Alice"))

    # Define properties for Alice
    alice.add_property(URI("http://example.org/hasLocation"), Literal("Paris"))

    # Add Alice's data to the knowledge graph
    querent_kg.add_subject_knowledge([alice])

    # Ensure that the knowledge graph is not empty
    serialized_data = querent_kg.serialize()
    assert serialized_data != ""

    # Verify that the correct data has been added
    triples = querent_kg.graph.triples((None, None, None))
    assert len(list(triples)) == 1

    # check the memory of graph
    expect_bytes = 119
    assert querent_kg.get_current_memory_usage == expect_bytes
