import spacy
import re
from typing import List
"""
    A class for extracting sentences from a text that contain specified fixed entities.

    This class utilizes regular expressions and spaCy's NLP capabilities to identify and 
    extract sentences from a given text which include any of the user-specified entities. 
    It is useful in scenarios where focus is required on specific entities within large 
    volumes of text.

    Attributes:
        nlp (spacy.Language): An instance of spaCy's language model.
        fixed_entities (List[str]): A list of entities (as strings) to search for in the text.
        entity_patterns (List[re.Pattern]): Compiled regex patterns for the fixed entities, 
                                            enabling case-insensitive searching.

    Methods:
        find_entity_sentences(text: str) -> str:
            Identifies and returns sentences from the provided text that contain any of the 
            fixed entities.

        measure_reduction(original_text: str, reduced_text: str) -> float:
            Calculates the percentage reduction in text length after extracting relevant sentences.

    """

class FixedEntityExtractor:
    def __init__(self, fixed_entities: List[str], model="en_core_web_lg"):
        self.nlp = spacy.load(model)
        self.fixed_entities = fixed_entities
        self.entity_pattern = self.create_combined_pattern(fixed_entities)

    def create_combined_pattern(self, entities):
        combined_pattern = '|'.join(map(re.escape, entities))
        return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)

    def find_entity_sentences(self, text: str, chunk_size=1000) -> str:
        doc = self.nlp(text)
        relevant_sentences = set()
        prev_sentence = None

        for i in range(0, len(doc), chunk_size):
            chunk = doc[i:i+chunk_size]
            sentences = list(chunk.sents)

            for j, sentence in enumerate(sentences):
                sentence_text = sentence.text
                if self.entity_pattern.search(sentence_text):
                    # Add the previous, current, and next sentences
                    if prev_sentence:
                        relevant_sentences.add(prev_sentence.text)
                    relevant_sentences.add(sentence_text)
                    if j < len(sentences) - 1:  # Check if there is a next sentence
                        relevant_sentences.add(sentences[j + 1].text)

                prev_sentence = sentence

        return ' '.join(sorted(relevant_sentences))

    def measure_reduction(self, original_text: str, reduced_text: str) -> float:
        original_length = len(original_text)
        reduced_length = len(reduced_text)
        reduction_percentage = ((original_length - reduced_length) / original_length) * 100
        return reduction_percentage
