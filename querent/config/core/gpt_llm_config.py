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
    

