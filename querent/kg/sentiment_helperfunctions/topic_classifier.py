from typing import Any, Dict, List, Tuple
from transformers import pipeline
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    wait_fixed
)
from dotenv import load_dotenv, find_dotenv
import json

_ = load_dotenv(find_dotenv())
import requests

class TopicClassifier:
    def __init__(self, config):
        self.topic_type_model_name = config.topic_type_model_name
        self.huggingface_token = config.huggingface_token
        self.api_url = config.huggingface_api_url
        self.topic_classifier = self.initialize_classifier(self.topic_type_model_name)


    def initialize_classifier(self, model_name):
        if self.api_url:
            return lambda text: self.classify_text_with_hf_api(text, model_name)
        else:
            return self.load_model(model_name)

    def classify_text_with_hf_api(self, text, model_name):
        headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        payload = {"inputs": text}
        url = f"{self.api_url}/{model_name}"
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    
    @staticmethod
    def load_model(model_name, huggingface_token=None):
        token = huggingface_token if huggingface_token else None
        return pipeline("text-classification", model=model_name, token=token)
    
    def extract_topic_info(self, output):
        if isinstance(output, list):
            if all(isinstance(sublist, list) for sublist in output):
                flat_list = [item for sublist in output for item in sublist]
                if all(isinstance(item, dict) for item in flat_list):
                    max_score_dict = max(flat_list, key=lambda x: x['score'])
                    return {"sentiment": max_score_dict['label'].lower(), "sentiment_score": round(max_score_dict['score'], 1)}
            elif all(isinstance(item, dict) for item in output):
                max_score_dict = max(output, key=lambda x: x['score'])
                return {"sentiment": max_score_dict['label'].lower(), "sentiment_score": round(max_score_dict['score'], 1)}
            else:
                return {"sentiment": output[0]['label'].lower(), "sentiment_score": round(output[0]['score'], 1)}
        elif hasattr(output, 'choices'):
            try:
                sentiment_info = json.loads(output.choices[0].message.content)
                return {"sentiment": sentiment_info["sentiment"].lower(), "sentiment_score": sentiment_info["sentiment_score"]}
            except Exception as e:
                return None
        return None
    
    def classify_topic(self, text):
        result = self.topic_classifier(text)
        return self.extract_topic_info(result)