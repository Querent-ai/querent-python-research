import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

# Make sure to download the required NLTK data:
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')


class TextNormalizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def lowercase(self, text):
        return text.lower()

    def lemmatize(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(lemmatized_tokens)

    def remove_stop_words(self, text):
        tokens = word_tokenize(text)
        filtered_tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(filtered_tokens)

    def normalize(self, text):
        text = self.lowercase(text)
        text = self.lemmatize(text)
        text = self.remove_stop_words(text)
        return text
    
    def normalize_triples(self, triples):
        normalized_triples = []
        for triple in triples:
            entity1, context_json, entity2 = triple
            context_dict = json.loads(context_json)  # Assuming context_json is a JSON string
            normalized_context = self.normalize(context_dict['context'])
            context_dict['context'] = normalized_context  # Replace the context with the normalized one
            normalized_context_json = json.dumps(context_dict)  # Convert back to JSON string if needed
            normalized_triples.append((entity1, normalized_context_json, entity2))
        return normalized_triples
