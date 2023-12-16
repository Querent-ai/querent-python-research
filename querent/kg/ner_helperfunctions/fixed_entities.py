import spacy
import re
from typing import List

class EntityContextExtractor:
    def __init__(self, fixed_entities: List[str], model="en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.fixed_entities = fixed_entities
        # Precompile regex patterns for faster searching
        self.entity_patterns = [re.compile(re.escape(entity), re.IGNORECASE) for entity in self.fixed_entities]

    def find_entity_sentences(self, text: str) -> str:
        doc = self.nlp(text)
        sentences = list(doc.sents)
        relevant_sentences = set()

        for i, sentence in enumerate(sentences):
            sentence_text = sentence.text
            if any(pattern.search(sentence_text) for pattern in self.entity_patterns):
                relevant_sentences.add(max(i - 1, 0))
                relevant_sentences.add(i)
                relevant_sentences.add(min(i + 1, len(sentences) - 1))

        return ' '.join(sentences[index].text for index in sorted(relevant_sentences))

    def measure_reduction(self, original_text: str, reduced_text: str) -> float:
        original_length = len(original_text)
        reduced_length = len(reduced_text)
        reduction_percentage = ((original_length - reduced_length) / original_length) * 100
        return reduction_percentage
