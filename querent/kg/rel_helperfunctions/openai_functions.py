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

    def get_predicate_info_function(self):
        return self._predicate_info_functions

    def get_classifyentity_function(self):
        return self._classifyentity_functions


