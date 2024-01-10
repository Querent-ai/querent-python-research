from pydantic import Field
from typing import List, Dict, Any
from querent.config.core.bert_llm_config import BERTLLMConfig

class GPTConfig(BERTLLMConfig):
    name: str = "OPENAIEngine"
    description: str = "An engine for NER using BERT and knowledge graph operations using OPENAI"
    version: str = "0.0.1"
    logger: str = "OPENAI.engine_config"
    ner_model_name: str = "botryan96/GeoBERT"
    rel_model_name: str = "gpt-3.5-turbo"
    requests_per_minute: int = 3

    

