from querent.models.ner_models.english.english import EnglishFactory
from querent.models.ner_models.geobert.geobert import GeoBERTFactory
from querent.models.rel_models.llama.llama import LLAMAFactory

class ModelManager:
    def __init__(self):
        # Maps model identifiers to their corresponding factory classes
        self.factory_map = {
            "English": EnglishFactory,
            "GeoBERT": GeoBERTFactory,
            "llama" : LLAMAFactory,
        }

    def get_model(self, model_identifier, model_path = None):
        factory_class = self.factory_map.get(model_identifier)
        if not factory_class:
            raise Exception(f"No factory available for the model identifier: {model_identifier}")
        factory = factory_class()
        model = factory.create(model_identifier)
        if not model_path:
            return model.return_model_name()
        else:
            if model.return_model_name():
                return model_path
            else:
                raise Exception("No factory available for the model identifier: {model_identifier} and model path : {model_path}")
