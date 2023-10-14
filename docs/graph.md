# **Key Components of the Graph Package:**

1. `QuerentKG` Class:
   - `QuerentKG` is a class that represents a Querent Knowledge Graph. It's a part of the `querent.kg` module.
   - It is backed by a default schema and stores knowledge in RDF format.
   - `QuerentKG` provides methods for adding knowledge, serializing the graph, binding namespaces, and validating the graph against a schema.

2. `QuerentGraph` Class:
   - `QuerentGraph` is the base class for `QuerentKG`. It manages and manipulates RDF graphs with memory management features.
   - It provides methods for adding and removing knowledge, serializing the graph, parsing RDF data, and more.

3. `NamespaceManager` Class:
   - The `NamespaceManager` class manages namespaces used in the graph. It's responsible for binding prefixes to namespaces.

**Key Features of the `Subject` Class:**

1. `Subject` Class:
   - The `Subject` class is a fundamental component of the package that represents subjects in the RDF graph.
   - A subject can have multiple properties, each consisting of a predicate (`URI`) and an object (`URI`, `BNode`, `Literal`, or another `Subject`).
   - It provides methods for adding and removing properties, as well as reification.

2. Reification:
   - The `Subject` class supports reification, which is the process of making statements about statements. Reification can be used to express metadata about RDF triples.

3. Memory Usage Tracking:
   - The `Subject` class has a feature to track the memory usage of the properties added. This allows users to estimate the size of the graph and potentially manage memory efficiently.

**Example of How a Graph Appears:**
In the example provided, a Querent Knowledge Graph (`QuerentKG`) is created with a default schema. RDF knowledge is added using the `Subject` class, representing knowledge about a person named "Alice" and her location. The `add_property` method of the `Subject` class is used to add properties to the `alice` subject, and this knowledge is added to the `QuerentKG`. The `serialize` method of `QuerentKG` is used to obtain the serialized RDF data. In this way, the graph appears as an RDF structure that can be serialized for storage or further processing.

In summary, the graph package provides a structured and memory-efficient way to work with RDF data and construct knowledge graphs. The `Subject` class allows users to represent knowledge about entities and properties within the graph, and the `QuerentKG` class manages the overall RDF graph. This package is useful for tasks involving RDF data and semantic knowledge representation.
