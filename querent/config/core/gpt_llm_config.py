from typing import Optional
from querent.config.core.llm_config import LLM_Config
import os

class GPTConfig(LLM_Config):
    id: str = ""
    name: str = "OPENAIEngine"
    description: str = "An engine for NER using BERT and knowledge graph operations using OPENAI"
    version: str = "0.0.1"
    logger: str = "OPENAI.engine_config"
    ner_model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    rel_model_name: str = "gpt-3.5-turbo"
    requests_per_minute: int = 3
    openai_api_key: str = ""
    user_context: str = None
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