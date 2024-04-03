
import ast
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.querent_event import EventState, EventType
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, Dict, List, Tuple
from querent.logging.logger import setup_logger
from querent.config.core.sentiment_config import Sentiment_Config
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


class Sentiment_Graph(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        config: Sentiment_Config,
    ):
        super().__init__(input_queue)
        self.logger = setup_logger(__name__, "Sentiment_Graph")
        self.user_context = config.user_context
        self.nlp_model = NER_LLM.set_nlp_model(config.spacy_model_path)
        self.nlp_model = NER_LLM.get_class_variable()
        self.openai_model_name = config.openai_model_name
        self.sentiment_model_name = config.sentiment_model_name
        self.openai_api_key = config.openai_api_key
        self.target_companies = config.target_companies
        self.huggingface_token = config.huggingface_token
        self.api_url = config.huggingface_api_url
        self.gpt_llm = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        self.sentiment_classifier = self.initialize_classifier(self.sentiment_model_name)
        self.article_type_classifier = self.initialize_classifier(config.topic_type_model_name)

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
            self.logger.debug(f"Failed to classify text using Hugging Face API: {response.text}")
            return None
        
    
    @staticmethod
    def load_model(model_name, huggingface_token=None):
        token = huggingface_token if huggingface_token else None
        return pipeline("text-classification", model=model_name, token=token)

    def validate(self) -> bool:
        return True

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    
    def process_images(self, data: IngestedImages):
        return super().process_messages(data)

    async def process_code(self, data: IngestedCode):
        return super().process_messages(data)

    @staticmethod
    def validate_ingested_tokens(data: IngestedTokens) -> bool:
        return not data.is_error()
    
    def preprocess_data(self, data)-> Dict[str, Any]:
        if not data or len(data) != 1 or not isinstance(data[0], str):
            raise ValueError("Data must be a list containing a single string element.")
        try:
            dict_data = ast.literal_eval(data[0])
        except (ValueError, SyntaxError) as e:
            raise ValueError("Could not convert string to dictionary.") from e
        
        return dict_data
    
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
            messages_classify_entity = [
                    {"role": "user", "content": identify_entity_message},
                    {"role": "user", "content": data["title"]},
                    {"role": "user", "content": "Target Company: " + company_name},
                ]
            response = self.generate_response(messages_classify_entity)
            return response
        except Exception as e:
            self.logger.debug(f"Invalid {self.__class__.__name__} configuration. Unable to process triples using GPT. {e}")
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

    def extract_sentiment_info(self, output):
        print("Type of output: {0}".format(type(output)))
        print("Output: {0}".format(output))
        if isinstance(output, list):
            return {"sentiment": output[0]['label'].lower(), "sentiment_score": round(output[0]['score'], 1)}
        elif hasattr(output, 'choices'):
            try:
                sentiment_info = json.loads(output.choices[0].message.content)
                return {"sentiment": sentiment_info["sentiment"].lower(), "sentiment_score": sentiment_info["sentiment_score"]}
            except Exception:
                return None
        return None
        
      
    async def process_tokens(self, data: IngestedTokens):
        try:
            if not Sentiment_Graph.validate_ingested_tokens(data):
                    self.set_termination_event()                    
                    return
            else :
                print("Token Stream Value:", data.is_token_stream)
                if data.data[0].startswith('{\'source\''):
                    parsed_data = self.preprocess_data(data.data)
                    company_name = data.file.split('_')[0]
                    file = company_name
                    if len(self.openai_api_key) > 0:
                        result = self.process_triples(parsed_data, company_name) 
                        parsed_result = self.extract_sentiment_info(result)
                    else:
                        result = self.sentiment_classifier(parsed_data["title"])
                        if self.api_url is not None:
                            print("Result from api is {}",result)
                            flat_list = [item for sublist in result for item in sublist]
                            max_score_dict = max(flat_list, key=lambda x: x['score'])
                            result = [max_score_dict]
                        parsed_result = self.extract_sentiment_info(result)         
                    if not parsed_result: return 
                    else:
                        news_type = self.article_type_classifier(parsed_data["title"])
                        if self.api_url is not None:
                            print("Result from api is {}",result)
                            flat_list = [item for sublist in news_type for item in sublist]
                            max_score_dict = max(flat_list, key=lambda x: x['score'])
                            news_type = [max_score_dict]
                        parsed_news_type = self.extract_sentiment_info(news_type)
                        parsed_news_type['news_type'] = parsed_news_type.pop('sentiment')
                        parsed_news_type['news_type_score'] = parsed_news_type.pop('sentiment_score')
                        parsed_result.update(parsed_news_type)
                        parsed_result['title'] = parsed_data["title"]
                        parsed_news_type['author'] = parsed_data["author"]
                        parsed_result['url'] = parsed_data["url"]
                        parsed_result['publishedAt'] = parsed_data["publishedAt"]
                        parsed_result['company'] = company_name.lower()
                        parsed_result['company_ticker'] = self.target_companies[company_name]
                else:
                    # single_string = ' '.join(data.data)
                    print("Data for------------------------", data.data)
                    single_string = data.data
                    file = data.get_file_path()
                    if len(self.openai_api_key) > 0:
                        if not self.user_context:
                            identify_entity_message = f"""Forget all your previous instructions. I will offer you text and your task is to:
                                1. Determine the sentiments of the text: positive, negative, or neutral.
                                2. Determine the sentiment score based on the potential impact of text. With 0 being no impact and 1 being the highest.
                                3. Only provide responses in JSON format.
                                4. Example output: {{sentiment: “positive”, sentiment_score:0.9}}
                                Text:
                                """
                        else:
                            identify_entity_message = self.user_context
                        messages_classify_entity = [
                                {"role": "user", "content": identify_entity_message},
                                {"role": "user", "content": single_string},
                            ]
                        result = self.generate_response(messages_classify_entity)
                        # print("User Message-------------", response)
                        parsed_result = self.extract_sentiment_info(result)
                    else:
                        result = self.sentiment_classifier(single_string)
                        parsed_result = self.extract_sentiment_info(result)
                    if not parsed_result: return 
                    else:
                        topic_type = self.article_type_classifier(single_string)
                        parsed_topic_type = self.extract_sentiment_info(topic_type)
                        parsed_topic_type['topic_type'] = parsed_topic_type.pop('sentiment')
                        parsed_topic_type['topic_type_score'] = parsed_topic_type.pop('sentiment_score')
                        parsed_result.update(parsed_topic_type)
                        parsed_result['title'] = single_string
            current_state = EventState(EventType.Sentiment,1.0, json.dumps(parsed_result), file)
            await self.set_state(new_state=current_state) 
        except Exception as e:
            self.logger.debug(f"Invalid {self.__class__.__name__} configuration. Unable to extract sentiment. {e}")

    async def process_messages(self, data: IngestedMessages):
        raise NotImplementedError