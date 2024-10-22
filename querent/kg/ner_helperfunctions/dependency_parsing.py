import spacy
from querent.logging.logger import setup_logger

"""
    A class to perform dependency parsing on a given sentence using SpaCy.

    Attributes:
    -----------
    entities : list
        A list of entities to be processed.
    sentence : str
        The input sentence for dependency parsing.
    nlp : SpaCy Language object
        The SpaCy model loaded for processing.
    doc : SpaCy Doc object
        The processed document after applying the SpaCy model on the sentence.
    noun_chunks : list
        List of noun chunks identified in the sentence.
    filtered_chunks : list
        Filtered noun chunks based on certain criteria.
    noun_chunks : list
        Entities merged based on overlapping criteria.
    
    Methods:
    --------
    load_spacy_model():
        Loads the specified SpaCy model.
    compare_entities_with_chunks():
        Compares the entities with the noun chunks and updates the entity details.
    process_entities():
        Processes the entities, groups them by noun chunks, and calculates average scores.
    """

class Dependency_Parsing():
    def __init__(self, entities=None, sentence=None, model=None):
        try:
            self.entities = entities
            self.sentence = sentence.replace("\n", " ")
            self.nlp = model
            self.doc = self.nlp(self.sentence)
            self.noun_chunks = list(self.doc.noun_chunks)
            self.noun_chunks = list(self.doc.noun_chunks)
            self.compare_entities_with_chunks()
            self.entities = self.process_entities()
        except Exception as e:
            raise Exception(f"Error Initializing Dependency Parsing Class: {e}")

    def compare_entities_with_chunks(self):
        try:
            for entity in self.entities:
                for chunk in self.noun_chunks:
                    if entity['entity'].lower() in chunk.text.lower():
                        entity['noun_chunk'] = chunk.text
                        entity['noun_chunk_length'] = len(chunk.text.split())
                        break
        except Exception as e:
            raise Exception(f"Error comparing entities with chunks: {e}")
        
    def process_entities(self):
        try:
            grouped_entities = {}
            for entity in self.entities:
                # Use both chunk and start index as the key to differentiate entities at different positions
                chunk = entity.get('noun_chunk', entity['entity'])
                start_idx = entity.get('start_idx', -1)  # Use a default value if start_idx is not present
                key = (chunk, start_idx)

                if key not in grouped_entities:
                    grouped_entities[key] = []
                grouped_entities[key].append(entity)
            processed_entities = []
            for key, chunk_entities in grouped_entities.items():
                if len(chunk_entities) == 1:
                    chunk_entities[0]['score'] = round(chunk_entities[0]['score'], 2)
                    chunk_entities[0].setdefault('noun_chunk', chunk_entities[0]['entity'])
                    chunk_entities[0].setdefault('noun_chunk_length', len(chunk_entities[0]['entity'].split()))
                    processed_entities.append(chunk_entities[0])
                else:
                    labels = set([e['label'] for e in chunk_entities])
                    avg_score = sum([e['score'] for e in chunk_entities]) / len(chunk_entities)
                    avg_score = round(avg_score, 2)
                    processed_entity = {
                        'entity': chunk_entities[0]['entity'],
                        'label': ', '.join(labels),
                        'score': avg_score,
                        'noun_chunk': chunk,
                        'noun_chunk_length':chunk_entities[0]['noun_chunk_length'],
                        'start_idx': chunk_entities[0]['start_idx']
                    }
                    processed_entities.append(processed_entity)

            return processed_entities
        except Exception as e:
            raise Exception(f"Error processing entities: {e}")

