# EventType Class Documentation

This document provides detailed information about the `EventType` class used in the querent system. 

## Class: EventType

The `EventType` class contains predefined constants that represent different kinds of events which can occur in the querent system. These constants are used throughout the system to identify and handle events appropriately.

### Attributes

- **`Vector Event`**: lists embeddings for text we find linked to our semantic knowledge, this will be sent to VectorDB where id will be file path, metadata will be id set in payload and namespace will be predicate for better clustering of vectors and ofcourse respective vector array.
- **`Graph`**: lists subject, subject type, object, object type predicate and predicate type which defines our semantic knowledge, Ideally in a realistic use case, a user will specify types  of sop  or release p  they are interested in so it becomes easier to upsert in graphDB.

### Usage Example (All event types generated from llm for now)

```python
current_state = EventState(EventType.Vector, 1.0, filtered_triples, filename)
current_state = EventState(EventType.Graph, 1.0, filtered_triples, filename)


Vector----------------------------------
{'id': 'gom_basin_accommodate_shale_interval', 'embeddings': [-0.0011837006313726306, -0.024518130347132683, ..],
 'size': 384, 'namespace': 'accommodate'}

GRAPH---------------------------------- 
{'subject': 'gom basin', 'subject_type': 'geological_feature', 'object': 'shale interval', 'object_type': 'sedimentary_rock', 'predicate': 'accommodate', 'predicate_type': 'geological_process', 'sentence': 'we suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom. this relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the gom basin.'}
