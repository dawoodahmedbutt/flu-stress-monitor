from abc import ABC, abstractmethod

class IDataRepository(ABC):
    """define contract for fetching external health data sources"""
    @abstractmethod
    def fetch_data(self):
        """fetch and return cleaned data as a list of dictionaries"""
        pass