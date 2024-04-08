
import ast
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.querent_event import EventState, EventType
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.core.base_engine import BaseEngine
from typing import Any, Dict, List
from querent.kg.sentiment_helperfunctions.sentiment_analyzer import SentimentAnalyzer
from querent.kg.sentiment_helperfunctions.topic_classifier import TopicClassifier
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

class Sentiment_Graph(BaseEngine):
    def __init__(self, input_queue, config):
        super().__init__(input_queue)
        self.logger = setup_logger(__name__, "Sentiment_Graph")
        self.user_context = config.user_context
        self.nlp_model = NER_LLM.set_nlp_model(config.spacy_model_path)
        self.nlp_model = NER_LLM.get_class_variable()
        self.target_companies = config.target_companies
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.topic_classifier = TopicClassifier(config)

    def validate(self):
        return True

    def process_messages(self, data):
        return super().process_messages(data)

    def process_images(self, data):
        return super().process_messages(data)

    async def process_code(self, data):
        return super().process_messages(data)

    @staticmethod
    def validate_ingested_tokens(data):
        return not data.is_error()

    def preprocess_data(self, data)-> Dict[str, Any]:
        if not data or len(data) != 1 or not isinstance(data[0], str):
            raise ValueError("Data must be a list containing a single string element.")
        try:
            dict_data = ast.literal_eval(data[0])
        except (ValueError, SyntaxError) as e:
            raise ValueError("Could not convert string to dictionary.") from e
        
        return dict_data

    async def process_tokens(self, data):
        try:
            if not Sentiment_Graph.validate_ingested_tokens(data):
                self.set_termination_event()
                return
            else:
                print("Data parsed", data.data)
                if data.data[0].startswith('{\'source\''):
                    parsed_data = self.preprocess_data(data.data)
                    company_name = data.file.split('_')[0]
                    file = company_name
                    sentiment_result = self.sentiment_analyzer.analyze_sentiment(parsed_data["title"], self.user_context)
                    topic_result = self.topic_classifier.classify_topic(parsed_data["title"])
                    topic_result['topic_type'] = topic_result.pop('sentiment')
                    print("Sentiment result", sentiment_result)
                    print("Topic result", topic_result)
                    topic_result.pop('sentiment_score')
                    sentiment_result.update(topic_result)
                    sentiment_result['title'] = parsed_data["title"]
                    sentiment_result['author'] = parsed_data["author"]
                    sentiment_result['url'] = parsed_data["url"]
                    sentiment_result['publishedAt'] = parsed_data["publishedAt"]
                    sentiment_result['entity'] = company_name.lower()
                    sentiment_result['entity_type'] = "company"
                    sentiment_result['predicate'] = "has_sentiment"
                    sentiment_result['symbol'] = self.target_companies[company_name]
                    print("Sentiment result:",sentiment_result)
                else:
                    single_string = data.data
                    file = data.get_file_path()
                    sentiment_result = self.sentiment_analyzer.analyze_sentiment(single_string, self.user_context)
                    topic_result = self.topic_classifier.classify_topic(single_string)
                    topic_result['topic_type'] = topic_result.pop('sentiment')
                    topic_result.pop('sentiment_score')
                    sentiment_result.update(topic_result)
                    sentiment_result['title'] = single_string
                    sentiment_result['entity'] = file
                    sentiment_result['entity_type'] = "text"
                    sentiment_result['predicate'] = "has_sentiment"
                    print("Sentiment result:",sentiment_result)

                current_state = EventState(EventType.Sentiment, 1.0, json.dumps(sentiment_result), file)
                await self.set_state(new_state=current_state)
        except Exception as e:
            print("Exceptions caught",e)
            self.logger.debug(f"Invalid {self.__class__.__name__} configuration. Unable to extract sentiment. {e}")

    async def process_messages(self, data):
        raise NotImplementedError
