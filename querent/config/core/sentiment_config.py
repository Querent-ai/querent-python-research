from typing import Optional
from pydantic import BaseModel, Field
import os

class Sentiment_Config(BaseModel):
    id: str = ""
    name: str = "Sentiment Configuration"
    openai_model_name: str = "gpt-3.5-turbo"
    requests_per_minute: int = 3
    openai_api_key: str = ""
    user_context: str = None
    huggingface_token: Optional[str] = None
    huggingface_api_url: Optional[str] = None
    spacy_model_path: str = 'en_core_web_lg'
    nltk_path: str = '/model/nltk_data'
    sentiment_model_name: str = "mr8488/distilroberta-finetuned-financial-news-sentiment-analysis-v2"
    topic_type_model_name: str = "nickmuchi/finbert-tone-finetuned-finance-topic-classification"
    target_companies: Optional[dict]= {
    'Nvidia Corporation': 'NVDA',
    'Advanced Micro Devices': 'AMD',
    'Meta Platforms, Inc.': 'META',
    'Alphabet Inc.': 'GOOGL',
    'Amazon.com, Inc.': 'AMZN',
    'Intel Corporation': 'INTC',
    'Microsoft Corporation': 'MSFT',
    'Apple Inc.': 'AAPL',
    'International Business Machines Corporation': 'IBM',
    'Oracle Corporation': 'ORCL',
    'Salesforce.com, inc.': 'CRM',
    'Tesla, Inc.': 'TSLA',
    'Uber Technologies, Inc.': 'UBER',
    'Baidu, Inc.': 'BIDU',
    'Qualcomm Incorporated': 'QCOM',
    'Square, Inc.': 'SQ',
    'Palantir Technologies Inc.': 'PLTR',
    'Adobe Inc.': 'ADBE',
    'Zoom Video Communications, Inc.': 'ZM',
    'Splunk Inc.': 'SPLK',
    'Shopify Inc.': 'SHOP',
    'ServiceNow, Inc.': 'NOW',
    'Snowflake Inc.': 'SNOW',
    'Twilio Inc.': 'TWLO',
    'DocuSign, Inc.': 'DOCU',
    'CrowdStrike Holdings, Inc.': 'CRWD',
    'Okta, Inc.': 'OKTA',
    'Pinterest, Inc.': 'PINS',
    'Broadcom Inc.': 'AVGO',
    'Texas Instruments Incorporated': 'TXN'
}



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