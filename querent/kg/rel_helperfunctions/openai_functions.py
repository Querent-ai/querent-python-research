class FunctionRegistry:
    def __init__(self):
        self._predicate_info_functions = [
            {
                "type": "function",
                "function": {
                    'name': 'predicate_info',
                    'description': 'Identify the predicate (relationship) and its type based on the context and the subject-object',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'predicate': {
                                'type': 'string',
                                'description': 'The relationship (predicate) between the subject and the object.'
                            },
                            'predicate_type': {
                                'type': 'string',
                                'description': 'The type of the relationship (predicate type).'
                            },

                        }, "required": ["predicate", "predicate_type"],
                    }
                }
            }
        ]

        self._classifyentity_functions = [
        {
            "type": "function",
            "function": {
                'name': 'classify_entities',
                'description': 'This function identifies and classifies two provided entities as either the subject or the object within a given context. It also categorizes these entities based on their types, providing a clear semantic understanding of their roles.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'subject': {
                            'type': 'string',
                            'description': 'Identified as the main entity in the context, this is typically the initiator or the primary focus of the action or topic being discussed.'
                        },
                        'subject_type': {
                            'type': 'string',
                            'description': 'The subject type.'
                        },
                        'object': {
                            'type': 'string',
                            'description': 'This parameter represents the entity in the context that is directly impacted by or involved in the action. It is typically the recipient or target of the main verbs action.'
                        },
                        
                        'object_type': {
                            'type': 'string',
                            'description': 'The type of the object entity.'
                        }
                    
                    }, "required": ["subject","subject_type", "object", "object_type"],
                }
            }    
        }
    ]

        self._identify_entities_functions = [
                {
                    "type": "function",
                    "function": {
                        'name': 'identify_entities',
                        'description': 'Identify all the entities and their respective Named Entity Recognition type/label based on the context.',
                        'parameters': {
                            "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "entity": {
                            "type": "string",
                            "description": "The extracted entity."
                        },
                        "label": {
                            "type": "string",
                            "description": "The type or category of the entity (e.g., GeoEvent, GeoLoc)."
                        },
                        "score": {
                            "type": "number",
                            "description": "The confidence score of the entity extraction and classification."
                        },
                        "start_idx": {
                            "type": "integer",
                            "description": "The start index of the entity in the provided text."
                        }
                    }, "required": ["entity", "label", "score", "start_idx"]},
                
                        }
                    }
                }
            ]

    def get_predicate_info_function(self):
        return self._predicate_info_functions

    def get_classifyentity_function(self):
        return self._classifyentity_functions
    
    def get_identifyentities_function(self):
        return self._identify_entities_functions


