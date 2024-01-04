import json

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
            normalized_text = normalized_text.replace(" ", "_")
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
                "subject": TripleToJsonConverter._normalize_text(subject),
                "subject_type": TripleToJsonConverter._normalize_text(predicate_info.get("subject_type", ""), replace_space=True),
                "object": TripleToJsonConverter._normalize_text(object_),
                "object_type": TripleToJsonConverter._normalize_text(predicate_info.get("object_type", ""), replace_space=True),
                "predicate": TripleToJsonConverter._normalize_text(predicate_info.get("predicate", "")),
                "predicate_type": TripleToJsonConverter._normalize_text(predicate_info.get("predicate_type", ""), replace_space=True),
                "sentence": predicate_info.get("context", "").lower()
            }

            return json_object
        except Exception as e:
            raise Exception(f"Error in convert_graphjson: {e}")

    @staticmethod
    def convert_vectorjson(triple):
        try:
            subject, json_str, object_ = triple
            data = TripleToJsonConverter._parse_json_str(json_str)
            if data is None:
                return {}

            id_format = f"{TripleToJsonConverter._normalize_text(subject)}_{TripleToJsonConverter._normalize_text(data.get('predicate', ''))}_{TripleToJsonConverter._normalize_text(object_)}"
            json_object = {
                "id": TripleToJsonConverter._normalize_text(id_format,replace_space=True),
                "embeddings": data.get("context_embeddings", []),
                "size": len(data.get("context_embeddings", [])),
                "namespace": TripleToJsonConverter._normalize_text(data.get("predicate", ""),replace_space=True)
            }

            return json_object
        except Exception as e:
            raise Exception(f"Error in convert_vectorjson: {e}")
        
        
        
