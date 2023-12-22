import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
from querent.logging.logger import setup_logger

"""
    A utility class for normalizing text data using various natural language processing (NLP) techniques.

    This class provides methods to lowercase, lemmatize, remove stopwords, and fully normalize text data.
    It is also equipped to normalize the context within triples typically used in knowledge graph scenarios.

    Attributes:
        logger (Logger): A logger instance for logging activities and errors.
        lemmatizer (WordNetLemmatizer): An NLTK lemmatizer for converting words to their base or root form.
        stop_words (set): A set of English stopwords from NLTK's corpus.

    Methods:
        lowercase(text): Converts all characters in the text to lowercase.
            Parameters:
                text (str): The text to be lowercased.
            Returns:
                str: The lowercased text.

        lemmatize(text): Lemmatizes the given text.
            Parameters:
                text (str): The text to be lemmatized.
            Returns:
                str: The lemmatized text.

        remove_stop_words(text): Removes stopwords from the given text.
            Parameters:
                text (str): The text from which stopwords are to be removed.
            Returns:
                str: The text with stopwords removed.

        normalize(text): Fully normalizes the text by lowercasing, lemmatizing, and removing stopwords.
            Parameters:
                text (str): The text to be normalized.
            Returns:
                str: The normalized text.

        normalize_triples(triples): Normalizes the context within each triple in the given list of triples.
            Parameters:
                triples (list of tuples): The list of triples to be normalized. Each triple should be in the
                                          format (entity1, context_json, entity2), where context_json is a JSON
                                          string containing the context to be normalized.
            Returns:
                list of tuples: The list of normalized triples.
    """


class TextNormalizer:
    def __init__(self):
        self.logger = setup_logger("TextNormalizer_config", "TextNormalizer")
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def lowercase(self, text):
        try:
            return text.lower()
        except Exception as e:
            self.logger.error(f"Error in lowercasing text: {e}")

    def lemmatize(self, text):
        try:
            tokens = word_tokenize(text)
            lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            return ' '.join(lemmatized_tokens)
        except Exception as e:
            self.logger.error(f"Error in lemmatizing text: {e}")

    def remove_stop_words(self, text):
        try:
            tokens = word_tokenize(text)
            filtered_tokens = [token for token in tokens if token not in self.stop_words]
            return ' '.join(filtered_tokens)
        except Exception as e:
            self.logger.error(f"Error in removing stop words: {e}")

    def normalize(self, text):
        try:
            #text = self.lowercase(text)
            #text = self.lemmatize(text)
            #text = self.remove_stop_words(text)
            return text
        except Exception as e:
            self.logger.error(f"Error in normalizing text: {e}")
            raise Exception(f'Error in normalizing text: {e}')

    def normalize_triples(self, triples):
        try:
            normalized_triples = []
            for triple in triples:
                entity1, context_json, entity2 = triple
                context_dict = json.loads(context_json)
                normalized_context = self.normalize(context_dict['context'])
                context_dict['context'] = normalized_context
                normalized_context_json = json.dumps(context_dict)
                normalized_triples.append((entity1, normalized_context_json, entity2))
            return normalized_triples
        except Exception as e:
            self.logger.error(f"Error in normalizing triples: {e}")
            raise Exception(f"Error in normalizing triples: {e}")
