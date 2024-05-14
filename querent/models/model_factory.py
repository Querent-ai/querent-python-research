from abc import ABC, abstractmethod
from querent.models.model import Model


class ModelFactory(ABC):
    """ Abstract factory for creating models. """
    @abstractmethod
    def create(self, model_name) -> Model:
        """ Method to create model instances. """
        pass
    
    
