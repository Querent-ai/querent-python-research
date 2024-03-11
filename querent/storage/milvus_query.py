# from pymilvus import connections, Collection, utility

# # Connect to the Milvus server
# connections.connect("default", host="localhost", port="19530")

# # List all collections
# collections = utility.list_collections()
# print("Collections in Milvus:", collections)
# print("------------------------------------------------------------------------")

# # for collection_name in collections:
# #     collection = Collection(name=collection_name)

# #     index_params = {
# #         "metric_type": "L2",  # or "IP" for inner product
# #         "index_type": "IVF_FLAT",  # Choose based on your specific needs
# #         "params": {"nlist": 100}  # Adjust based on dataset size and available resources
# #     }

# #     # Create an index on the embeddings field
# #     collection.create_index(field_name="embeddings", index_params=index_params)





# for collection_name in collections:
#     collection = Collection(name=collection_name)

#     schema = collection.schema
#     print(f"Schema for collection '{collection_name}':")
#     for field in schema.fields:
#         print(f"  Field Name: {field.name}, Field Type: {field.dtype}, Params: {field.params}")
#     print("---------------------------------------------------------------")
#     collection.load()


#     print("collection.primary_field --------------",collection.primary_field)         # Return the schema.FieldSchema of the primary key field.
#     print("collection.partitions-------------------",collection.partitions)            # Return the list[Partition] object.
#     print("collection.partitions-----------------",collection.indexes)               # Return the list[Index] object.

#     num_entities = collection.num_entities
#     print(f"The collection '{collection_name}' contains {num_entities} entities.")

#     results = collection.query(expr="", output_fields=["knowledge", "relationship", "document", "embeddings"], partition_names=[], limit=10)
#     print(results[0])
#     print("--------------------------------------------------------------------------------------------")



# # Disconnect from the server
# connections.disconnect("default")
