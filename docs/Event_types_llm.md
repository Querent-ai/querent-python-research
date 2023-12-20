# EventType Class Documentation

This document provides detailed information about the `EventType` class used in the querent system. 

## Class: EventType

The `EventType` class contains predefined constants that represent different kinds of events which can occur in the querent system. These constants are used throughout the system to identify and handle events appropriately.

### Attributes

- **`Vector`**: Indicates event involving the sending of context embeddings generated from the system.
- **`Graph`**: Denotes event involving the sending of semantic triple data generated from the system.

### Usage Example (All event types generated from llm for now)

```python
current_state = EventState(EventType.Vector, 1.0, filtered_triples, filename)
current_state = EventState(EventType.Graph, 1.0, kgm.retrieve_triples(), filename)


Vector----------------------------------
  "payload":
    {"id":"gombasin_deposit_shaleinterval",
    "embeddings": [-0.0011837006313726306, -0.024518130347132683, 0.14961548149585724, -0.033723924309015274, -0.05840631201863289,.. ], 
    "size": 768
    "namespace": "deposit"
    }

GRAPH---------------------------------- 
  "payload":
    {
      "subject_name": "tectonic",
      "subject_type": "geo",
      "object_name": "shale interval",
      "object_type": "geo",
      "predicate": "deposit",
      "predicate_type": "location based",
      "sentence": """We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in 
the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom-
modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a 
considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin."""
}
