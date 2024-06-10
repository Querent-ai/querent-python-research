from pydantic import BaseModel, Field
from typing import Dict
import os

class Opensource_LLM_Config(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"
    model_type: str = 'llama'
    model_path: str = '' 
    grammar_file_path: str = './querent/kg/rel_helperfunctions/json.gbnf'
    qa_template: str = Field(default=None)
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    is_confined_search: bool = False
    spacy_model_path: str = 'en_core_web_lg'
    nltk_path: str = '/model/nltk_data'

    def __init__(self, config_source=None, **kwargs):
        config_data = {}
        config_data.update(kwargs)
        if config_source:
            config_data = self.load_config(config_source)
        if "config" in config_data:
            config_data.update(config_data["config"])
        super().__init__(**config_data)
        

    @classmethod
    def load_config(cls, config_source) -> dict:
        if isinstance(config_source, dict):
            # If config source is a dictionary, return a dictionary
            cls.config_data = config_source
        else:
            raise ValueError("Invalid config. Must be a valid dictionary")

        env_vars = dict(os.environ)
        cls.config_data.update(env_vars)
        return cls.config_data

    def get_faiss_index_path(self):
        return self.vector_store_path + "my_FAISS_index"