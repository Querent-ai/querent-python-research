class FunctionRegistry:
    def __init__(self):
        self._predicate_info_functions = [
            {
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

                    }
                }
            }
        ]

        self._classifyentity_functions = [
        {
            'name': 'classify_entities',
            'description': 'Classify provided entities into subject and object and determine their types based on the provided context.',
            'parameters': {
                'type': 'object',
                'properties': {
                     'subject': {
                        'type': 'string',
                        'description': 'The main entity or topic of the sentence.'
                    },
                    'object': {
                        'type': 'string',
                        'description': 'The entity that is acted upon or affected by the verb.'
                    },
                    'subject_type': {
                        'type': 'string',
                        'description': 'The type of the subject.'
                    },
                    'object_type': {
                        'type': 'string',
                        'description': 'The type of the object.'
                    }
                   
                },
            }
        }
    ]

    def get_predicate_info_function(self):
        return self._predicate_info_functions

    def get_classifyentity_function(self):
        return self._classifyentity_functions
