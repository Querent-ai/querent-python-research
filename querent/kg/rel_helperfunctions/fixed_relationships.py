import re
from typing import List
from nltk.corpus import wordnet as wn
"""
    A class designed to extract sentences from text that contain specified fixed relationships,
    taking into account synonyms for more comprehensive matching.

    This class utilizes regular expressions, spaCy's NLP capabilities, and the WordNet 
    database to identify and extract sentences from a given text which include any of the 
    user-specified relationships or their synonyms. It's particularly useful for focusing on
    specific types of relationships within large volumes of text.

    Attributes:
        nlp (spacy.Language): An instance of spaCy's language model.
        fixed_relationships (List[str]): A list of relationships (as strings) to search for in the text.
        relationship_patterns (List[re.Pattern]): Compiled regex patterns for the fixed relationships and their synonyms, 
                                                  enabling case-insensitive searching.

    Methods:
        create_patterns_with_synonyms(relationships: List[str]) -> List[re.Pattern]:
            Generates and compiles regex patterns that include synonyms of the specified relationships.

        find_relationship_sentences(text: str) -> str:
            Identifies and returns sentences from the provided text that contain any of the 
            fixed relationships or their synonyms.

        measure_reduction(original_text: str, reduced_text: str) -> float:
            Calculates the percentage reduction in text length after extracting relevant sentences.
"""

class FixedRelationshipExtractor:
    def __init__(self, fixed_relationships: List[str], model=None):
        self.nlp = model
        self.fixed_relationships = fixed_relationships
        self.relationship_pattern = self.create_combined_pattern_with_synonyms(fixed_relationships)

    def create_combined_pattern_with_synonyms(self, relationships):
        all_synonyms = set()
        for relationship in relationships:
            all_synonyms.add(relationship)
            for syn in wn.synsets(relationship, pos=wn.VERB):
                for l in syn.lemmas():
                    all_synonyms.add(l.name().replace('_', ' '))
        combined_pattern = '|'.join(map(re.escape, all_synonyms))
        return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)

    def find_relationship_sentences(self, text: str, chunk_size=1000) -> str:
        doc = self.nlp(text)
        relevant_sentences = set()
        prev_sentence = None

        for i in range(0, len(doc), chunk_size):
            chunk = doc[i:i+chunk_size]
            sentences = list(chunk.sents)

            for j, sentence in enumerate(sentences):
                sentence_text = sentence.text
                if self.relationship_pattern.search(sentence_text):
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
