import time

import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

class MilvusDBConnection:
    
    def create_collection(self,collection_name, dim):
        # if utility.has_collection(collection_name):
        #     utility.drop_collection(collection_name)
        connections.connect("default", host="localhost", port="19530")
        has = utility.has_collection(collection_name)
        fields = [
        FieldSchema(name='knowledge', dtype=DataType.VARCHAR, descrition='ids (subject_predicate_object)', max_length=500, is_primary=True, auto_id=False),
        FieldSchema(name='relationship', dtype=DataType.VARCHAR, max_length=500, descrition='namespace',default_value="Unknown"),
        FieldSchema(name='embeddings', dtype=DataType.FLOAT_VECTOR, descrition='embedding vectors', dim=dim),
        FieldSchema(name='document', dtype=DataType.VARCHAR, max_length=500, default_value="Unknown")
        ]
        schema = CollectionSchema(fields=fields, description='semantic search')
        if not utility.has_collection(collection_name):
            collection = Collection(name=collection_name, schema=schema)
            # create IVF_FLAT index for collection.
            # index_params = {
            #     'metric_type':'L2',
            #     'index_type':"IVF_FLAT",
            #     'params':{"nlist":2048}
            # }
            # collection.create_index(field_name="embedding", index_params=index_params)
        else:
            collection = Collection(name=collection_name)

        return collection
    
    def insert_vector_event(self, id, embedding, namespace, document, collection):
        if collection is not None:
            try:
                insert_result = collection.insert(
                                                    [
                                                        [id],
                                                        [namespace],
                                                        [embedding],
                                                        [document] 
                                                        
                                                    ]
                                                )
                
            except Exception as e:
                raise("An error occurred while inserting the data:")

    def vectorsearch_db(self, collection, vector_search_query):
        collection.load()
        vectors_to_search = vector_search_query
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10},
        }

        start_time = time.time()
        result = collection.search(vectors_to_search, "embeddings", search_params, limit=3)
        end_time = time.time()

        return result
        