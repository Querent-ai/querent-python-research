from pydantic import BaseModel, Field
from typing import Dict

class Opensource_LLM_Config(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"
    model_type: str = 'llama'
    model_path: str = './tests/llama-2-7b-chat.Q5_K_M.gguf' 
    grammar_file_path: str = './querent/kg/rel_helperfunctions/json.gbnf'
    qa_template: str = Field(default=None)
    vector_store_path: str = "./querent/kg/rel_helperfunctions/vectorstores/"
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    rag_approach: bool = False
    is_confined_search: bool = False

    def __init__(self, config_source=None, **kwargs):
        declared_keys = set(self.__annotations__.keys())

        # Initialize BaseModel with kwargs
        super().__init__(**kwargs)

        if config_source:
            config_data = self.load_config(config_source)
            for config_key, config_value in config_data.items():
                if config_key in declared_keys:
                    setattr(self, config_key, config_value)

        # Apply any additional keyword arguments, if they are declared attributes
        for key, value in kwargs.items():
            if key in declared_keys:
                setattr(self, key, value)

    @staticmethod
    def load_config(config_source):
        if isinstance(config_source, dict):
            return config_source
        else:
            raise ValueError("Invalid config. Must be a valid dictionary")

    def get_faiss_index_path(self):
        return self.vector_store_path + "my_FAISS_index"