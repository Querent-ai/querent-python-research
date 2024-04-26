from typing import Any, Dict, List, Tuple
from querent.logging.logger import setup_logger
from openai import OpenAI
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

class SentimentAnalyzer:
    def __init__(self, config):
        self.openai_model_name = config.openai_model_name
        self.sentiment_model_name = config.sentiment_model_name
        self.user_context = config.user_context
        self.openai_api_key = config.openai_api_key
        self.huggingface_token = config.huggingface_token
        self.api_url = config.huggingface_api_url
        self.gpt_llm = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        self.sentiment_classifier = self.initialize_classifier(self.sentiment_model_name)

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
    
    def extract_sentiment_info(self, output):
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
    
    def analyze_sentiment(self, text, user_context=None):
        if self.openai_api_key:
            result = self.process_triples(text, user_context)
        else:
            result = self.sentiment_classifier(text)

        return self.extract_sentiment_info(result)
    
    def process_triples(self, data, company_name):
        try:
            if not self.user_context:
                identify_entity_message = f"""Forget all your previous instructions. I want you to act as an experienced financial engineer. I will offer you
                    financial news headlines in one day. Your task is to:
                    1. Identify whether the target company will be impacted by the news headline.
                    2. Determine the sentiments of the affected company: positive, negative, or neutral.
                    3. Determine the sentiment score based on the potential impact of news headline on the target company stock price. With 0 being no impact and 1 being the highest.
                    4. Only provide responses in JSON format.
                    5. Example output: {{sentiment: “positive”, sentiment_score:0.9}}
                    News Headline:
                    """
            else:
                identify_entity_message = self.user_context
            if isinstance (data,dict):
                messages_classify_entity = [
                        {"role": "user", "content": identify_entity_message},
                        {"role": "user", "content": data["title"]},
                        {"role": "user", "content": "Target Company: " + company_name},
                    ]
            else:
                messages_classify_entity = [
                    {"role": "user", "content": identify_entity_message},
                    {"role": "user", "content": data}
                ]
            response = self.generate_response(messages_classify_entity)
            return response
        except Exception as e:
            return

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(self, **kwargs):
        return self.gpt_llm.chat.completions.create(**kwargs)
    
    def generate_response(self, messages):
        response = self.completion_with_backoff(
            model=self.openai_model_name,
            messages=messages,
            temperature=0
        )
        return response
    