from pydantic import BaseModel, Field
from typing import Dict

class RelationshipExtractorConfig(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"

    # Shared configurations for relationship extraction and BSM
    model_type = 'llama'
    # model_path: str = './tests/llama-2-7b-chat.Q4_K_M.gguf'  # Used as LLaMA model path in BSM
    model_path: str = './tests/llama-2-7b-chat.Q5_K_M.gguf'  # Used as LLaMA model path in BSM
    grammar_file_path = './querent/kg/rel_helperfunctions/json.gbnf'
    qa_template: str = None
        
    # Specific configurations for relationship extraction
    vector_store_path: str = "./querent/kg/rel_helperfunctions/vectorstores/"
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'

    # BSM specific configurations
    bsm_validator_model_path: str = "./tests/vicuna-13b-v1.5.Q4_K_M.gguf"
    bsm_validator_model_type='vicuna'
    bsm_max_new_tokens: int = -1
    bsm_temperature: float = 0.1
    bsm_repetition_penalty: float = 1.7
    bsm_context_length: int = 2000

    # Additional parameter for dynamic sub-tasks
    dynamic_sub_tasks: list = Field(default_factory=list)  # List of sub-tasks that user may provide
    
    rag_approach: bool = False
    
    def get_faiss_index_path(self):
        return self.vector_store_path + "my_FAISS_index"
