import pytest
from querent.common.types.querent_quad import QuerentQuad
from querent.config.graph_config import GraphConfig
from querent.kg.querent_kg import QuerentKG


@pytest.fixture
def querent_kg():
    # Set up a QuerentKG instance for testing
    config = GraphConfig(
        graph_identifier="test_graph",
        store="default",
        memory_threshold=10,
        flush_on_serialize=False,
        graph_format="nt",
    )
    return QuerentKG(config)


def test_add_knowledge(querent_kg: QuerentKG):
    # Test adding knowledge to the graph
    quad = QuerentQuad(
        subject="http://example.org/subject",
        predicate="http://example.org/predicate",
        object="Value",
        context="http://example.org/context",
    )
    querent_kg.add_quad(quad)
    dict_value = querent_kg.value
    assert len(dict_value) > 0  # Check if the graph is populated


def test_stream_graph(querent_kg: QuerentKG):
    # Test streaming the graph
    quad = QuerentQuad(
        subject="http://example.org/subject",
        predicate="http://example.org/predicate",
        object="Value",
        context="http://example.org/context",
    )
    querent_kg.add_quad(quad)

    serialized_graph = querent_kg.serialize()
    assert len(serialized_graph) > 0  # Check if the graph is serialized
