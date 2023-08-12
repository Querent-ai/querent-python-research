from abc import ABC, abstractmethod



class BaseDataCollector(ABC):
    """
    Base class for Data Collector
    """
    @abstractmethod
    def ingest_some_data():
        pass





class BaseAWSCollector(BaseDataCollector):
    def collect_some_data(self):
        pass




class BaseGCPCollector(BaseDataCollector):
    def collect_some_data(self):
        pass



class BaseWebScraperCollector(BaseDataCollector):
    def collect_some_data(self):
        pass


class BaseDataProcessor(ABC):
    """
    Base class for data tokenization 
    """
    @abstractmethod
    def process_some_data(self):
        pass



class BaseWebScraperProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass


class BaseAWSProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass


class BaseGCPProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass
