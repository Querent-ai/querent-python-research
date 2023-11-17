from pydantic import BaseModel, Field

class RelationshipExtractorConfig(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"
    vector_store_path: str = "./querent/kg/rel_helperfunctions/vectorstores/"
    rel_model_path: str = './dev-env/llama-2-7b-chat.Q4_K_M.gguf'
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    faiss_index_path: str = "./querent/kg/rel_helperfunctions/vectorstores/my_FAISS_index"
    qa_template: str = """Use the following pieces of information to answer the user's question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            Context: {context}
            Question: {query}
            Only return the helpful answer below and nothing else.
            Helpful answer:
            """


