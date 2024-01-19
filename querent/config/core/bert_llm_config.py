import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class BERTLLMConfig(BaseModel):
    name: str = "BERTLLMEngine"
    description: str = "An engine for NER and knowledge graph operations using BERT"
    version: str = "0.0.1"
    logger: str = "BERTLLM.engine_config"
    ner_model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    user_context: Dict[str, Any] = Field(default_factory=dict, description="User-specific context information")
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
    
    def __init__(self, config_source=None, **kwargs):
        super().__init__(**kwargs) 
        declared_keys = set(self.__annotations__.keys())
        if config_source:
            config_data = self.load_config(config_source)
            super().__init__(**config_data)
            for config_key, config_value in config_data.items():
                if config_key in declared_keys:
                    setattr(self, config_key, config_value)

        # Apply any additional keyword arguments, if they are declared attributes
        for key, value in kwargs.items():
            if key in declared_keys:
                setattr(self, key, value)

    @classmethod
    def load_config(cls, config_source) -> dict:
        if isinstance(config_source, dict):
            # If config source is a dictionary, use it as the initial config data
            cls.config_data = config_source
        else:
            raise ValueError("Invalid config. Must be a valid dictionary")

        env_vars = dict(os.environ)
        cls.config_data.update(env_vars)  # Update config data with environment variables
        return cls.config_data

    

