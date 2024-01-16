from pydantic import BaseModel, Field
from typing import Dict

class RelationshipExtractorConfig(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"
    model_type = 'llama'
    # model_path: str = './tests/llama-2-7b-chat.Q4_K_M.gguf'
    model_path: str = './tests/llama-2-7b-chat.Q5_K_M.gguf' 
    grammar_file_path = './querent/kg/rel_helperfunctions/json.gbnf'
    qa_template: str = None
    vector_store_path: str = "./querent/kg/rel_helperfunctions/vectorstores/"
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    rag_approach: bool = False
    def get_faiss_index_path(self):
        return self.vector_store_path + "my_FAISS_index"
