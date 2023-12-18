# EventType Class Documentation

This document provides detailed information about the `EventType` class used in the querent system. 

## Class: EventType

The `EventType` class contains predefined constants that represent different kinds of events which can occur in the querent system. These constants are used throughout the system to identify and handle events appropriately.

### Attributes

- **`ContextualTriples`**: Indicates event involving the generation of contextual triples (text) in the system.
- **`RdfContextualTriples`**: Denotes event involving the generation of (Resource Description Framework) graph formatted contextual triples in the system.
- **`RdfSemanticTriples`**: Used for events involving the creation of (Resource Description Framework) graph formatted semantic triples.
- **`ContextualEmbeddings`**: Used for events involving creation of Vector embeddings of context.

### Usage Example (All event types generated from llm for now)

```python
current_state = EventState(EventType.ContextualTriples, 1.0, filtered_triples)
current_state = EventState(EventType.RdfContextualTriples, 1.0, kgm.retrieve_triples())
current_state = EventState(EventType.RdfSemanticTriples, 1.0, semantic_triples)
