from pydantic import BaseModel, Field

class BERTLLMConfig(BaseModel):
    name: str = "BERTLLMEngine"
    description: str = "An engine for NER and knowledge graph operations using BERT"
    version: str = "0.0.1"
    logger: str = "BERTLLM.engine_config"
    ner_model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    enable_filtering: bool = False
    filter_params: dict = Field(default_factory=lambda: {
        'score_threshold': 0.6,
        'attention_score_threshold': 0.1,
        'similarity_threshold': 0.5,
        'min_cluster_size': 5,
        'min_samples': 3,
        'cluster_persistence_threshold': 0.4
    })


