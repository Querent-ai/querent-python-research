## Notes
# similar to start_workflow we have start_graph_query_engine
# Which takes a config as input and has neo4j storage info Neo4jGraphStore
# implement 
# graph_rag_retriever = KnowledgeGraphRAGRetriever(
#     storage_context=storage_context,
#     verbose=True,
# )

# query_engine = RetrieverQueryEngine.from_args(
#     graph_rag_retriever,
# )

# input config also has our token feader where the input query will come
# whenever a query is received in token feader we pass it through the query engine
# and the result is sent via event_handler as EventType- QueryResult
# where file = actual query and payload is the result from query engine

## So this will expose querent's capability to do graph queries via neo4j using graphRag