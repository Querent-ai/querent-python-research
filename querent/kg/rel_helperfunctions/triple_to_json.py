import json
import re
import numpy as np
"""
    A class to convert triples into different JSON formats.

    This class provides static methods to convert triples (a tuple of subject, predicate, and object)
    into specific JSON structures suitable for graph and vector space representations.

    Methods:
    - _normalize_text(text, replace_space=False): Normalizes the text by converting it to lowercase
      and optionally replacing spaces with underscores.
    - _parse_json_str(json_str): Parses a JSON string and returns a Python dictionary.
    - convert_graphjson(triple): Converts a triple into a JSON object suitable for graph representation.
    - convert_vectorjson(triple): Converts a triple into a JSON object suitable for vector space representation.
    """

class TripleToJsonConverter:
    @staticmethod
    def _normalize_text(text, replace_space=False):
        normalized_text = text.lower()
        if replace_space:
            normalized_text = TripleToJsonConverter.replace_special_chars_with_underscore(normalized_text)
        return normalized_text

    @staticmethod
    def _parse_json_str(json_str):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")

    @staticmethod
    def convert_graphjson(triple):
        try:
            subject, json_str, object_ = triple
            predicate_info = TripleToJsonConverter._parse_json_str(json_str)
            if predicate_info is None:
                return {}

            json_object = {
                "subject": TripleToJsonConverter._normalize_text(subject, replace_space=True),
                "subject_type": TripleToJsonConverter._normalize_text(predicate_info.get("subject_type", "Unlabeled"), replace_space=True),
                "object": TripleToJsonConverter._normalize_text(object_, replace_space=True),
                "object_type": TripleToJsonConverter._normalize_text(predicate_info.get("object_type", "Unlabeled"), replace_space=True),
                "predicate": TripleToJsonConverter._normalize_text(predicate_info.get("predicate", ""), replace_space=True),
                "predicate_type": TripleToJsonConverter._normalize_text(predicate_info.get("predicate_type", "Unlabeled"), replace_space=True),
                "sentence": predicate_info.get("context", "").lower(),
                "score": predicate_info.get("score", 1)
            }

            return json_object
        except Exception as e:
            raise Exception(f"Error in convert_graphjson: {e}")
        
    def dynamic_weighted_average_embeddings(embeddings, base_weights, normalize_weights=True):
            embeddings = [np.array(emb) for emb in embeddings]
            weights = np.array(base_weights, dtype=float)

            if normalize_weights:
                weights /= np.sum(weights)  # Normalize weights to sum to 1

            weighted_sum = np.zeros_like(embeddings[0])
            for emb, weight in zip(embeddings, weights):
                weighted_sum += emb * weight

            return weighted_sum

    @staticmethod
    def convert_vectorjson(triple, blob = None, embeddings=None):
        try:
            subject, json_str, object_ = triple
            data = TripleToJsonConverter._parse_json_str(json_str)
            if data is None:
                return {}

            id_format = f"{TripleToJsonConverter._normalize_text(subject,replace_space=True)}-{TripleToJsonConverter._normalize_text(data.get('predicate', ''),replace_space=True)}-{TripleToJsonConverter._normalize_text(object_,replace_space=True)}"
            json_object = {
                "id": TripleToJsonConverter._normalize_text(id_format),
                "embeddings": embeddings.tolist(),
                "size": len(embeddings.tolist()),
                "namespace": TripleToJsonConverter._normalize_text(data.get("predicate", ""),replace_space=True),
                "sentence": data.get("context", "").lower(),
                "blob": blob,
            }

            return json_object
        except Exception as e:
            raise Exception(f"Error in convert_vectorjson: {e}")
        

    @staticmethod
    def replace_special_chars_with_underscore(data):
        # This pattern will match anything that is not a letter, number, or underscore
        pattern = r'[^a-zA-Z0-9_]'
        # Replace matched patterns with an underscore
        return re.sub(pattern, '_', data)
        
        
