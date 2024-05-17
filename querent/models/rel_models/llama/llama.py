from querent.models.model import Model
from querent.models.model_factory import ModelFactory

class LLAMA(Model):
    """ A specific implementation of a Model for LLAMA2 language processing. """
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_instance = None

    def return_model_name(self):
        """ Returns the specific model name for the LLAMA2 model. """
        self.model_instance = self.model_name
        return self.model_instance

class LLAMAFactory(ModelFactory):
    """ Factory for creating LLAMA v2 model instances. """
    def create(self, model_name: str) -> Model:
        return LLAMA(model_name)
    
    