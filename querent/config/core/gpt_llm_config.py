from pydantic import BaseModel, Field
from typing import List, Dict, Any
from typing import List, Dict, Any


class GPTLLMConfig(BaseModel):
    name: str = "GPTLLMEngine"
    description: str = "An engine for NER and knowledge graph operations using GPT"
    version: str = "0.0.1"
    logger: str = "GPTLLM.engine_config"
    ner_model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    enable_filtering: bool = False
    filter_params: dict = Field(
        default_factory=lambda: {
            "score_threshold": 0.6,
            "attention_score_threshold": 0.1,
            "similarity_threshold": 0.5,
            "min_cluster_size": 5,
            "min_samples": 3,
            "cluster_persistence_threshold": 0.4,
        }
    )
