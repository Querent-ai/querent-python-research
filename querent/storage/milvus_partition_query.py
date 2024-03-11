# from pymilvus import connections, Collection

# # Connect to the Milvus server
# connections.connect("default", host="localhost", port="19530")

# # Specify your collection and partition name
# collection_name = "_b2d2e7547bca4459978ac17fad130697"
# partition_name = "is_one_of_the_more_exciting_shale_plays_in_the_united_states_at_the_current_time"

# collection = Collection(name=collection_name)

# # Load the collection into memory to query it
# collection.load()

# # Specify the partition names as a list
# partition_names = [partition_name]

# # Now, assuming you want to retrieve all entities from the partition
# # Specify the actual field names you wish to retrieve
# output_fields = ["id", "knowledge", "relationship", "document", "embeddings"]

# # Specify a limit to the number of results you want to retrieve
# limit = 100  # Adjust this number based on your needs

# # Use the partition_names parameter to specify which partitions to query, along with the limit
# results = collection.query(expr="", partition_names=partition_names, output_fields=output_fields, limit=limit)

# print("Printing results", results)
# # Print the retrieved entities
# for result in results:
#     print(result)

# # Disconnect from the server
# connections.disconnect("default")
