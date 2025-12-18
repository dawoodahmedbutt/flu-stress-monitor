import requests
from abc import ABC, abstractmethod
from src.log_config import logger

class IDataRepository(ABC):
    @abstractmethod
    def fetch_data(self):
        pass

class FluDataRepository(IDataRepository):
    # CORRECTED URL: 'r8kw-7aab' (Provisional COVID-19 Death Counts by Week & State)
    def __init__(self, api_url="https://data.cdc.gov/resource/r8kw-7aab.json"):
        self.url = api_url

    def fetch_data(self):
        logger.info(f"Fetching data from CDC API: {self.url}")
        try:
            params = {
                "$limit": 60000,
                "$order": "week_ending_date DESC",
                "$where": "week_ending_date >= '2023-10-01'"
            }
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning("API returned 0 records.")
            else:
                logger.info(f"Successfully retrieved {len(data)} records.")
                
            return data
        except Exception as e:
            logger.error(f"API Fetch Error: {e}")
            return []
