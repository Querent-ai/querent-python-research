import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
from querent.config.engine.engine_config import EngineConfig

class LLM_Config(EngineConfig):
    id: str = ""
    name: str = "LLMEngine"
    description: str = "An engine for NER and knowledge graph operations."
    version: str = "0.0.1"
    logger: str = "LLM.engine_config"
    ner_model_name: str = "English"
    spacy_model_path: str = 'en_core_web_lg'
    nltk_path: str = '/model/nltk_data'
    rel_model_type: str = 'bert'
    rel_model_path: str = 'bert-base-uncased'
    grammar_file_path: str = './querent/kg/rel_helperfunctions/json.gbnf'
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    user_context: str = Field(default="In a semantic triple (Subject, Predicate & Object) framework, determine which of the above entity is the subject and which is the object based on the context along with the predicate between these entities. Please also identify the subject type, object type & predicate type.")
    enable_filtering: bool = False
    filter_params: dict = Field(default_factory=lambda: {
        'score_threshold': 0.6,
        'attention_score_threshold': 0.1,
        'similarity_threshold': 0.5,
        'min_cluster_size': 5,
        'min_samples': 3,
        'cluster_persistence_threshold': 0.4
    })
    sample_entities: List[str] = Field(default_factory=list, description="List of sample entities")
    fixed_entities: List[str] = Field(default_factory=list, description="List of fixed entities")
    is_confined_search: bool = False
    skip_inferences: bool = False
    fixed_relationships: List[str] = Field(default_factory=list, description="List of fixed relationships")
    sample_relationships: List[str] = Field(default_factory=list, description="List of sample relationships")
    huggingface_token: Optional[str] = None
    
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

    

