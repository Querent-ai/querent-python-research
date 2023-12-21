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
{'id': 'deposition_occurred in_upstream', 'embeddings': [-0.0011837006313726306, -0.024518130347132683, 0.14961548149585724, -0.033723924309015274, -0.05840631201863289, -0.06296741962432861, -0.1140032485127449, -0.0032285358756780624, -0.01215912215411663, -0.06379254162311554, -0.06848873198032379, ....], 'size': 384, 'namespace': 'occurred in'}

GRAPH---------------------------------- 
{'subject': 'deposition', 'subject_type': 'location', 'object': 'upstream', 'object_type': 'catchment', 'predicate': 'occurred in', 'predicate_type': 'location', 'sentence': 'we suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom. this relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the gom basin.'}


