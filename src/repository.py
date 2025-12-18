from abc import ABC, abstractmethod
import requests
import json
from src.log_config import logger

class IDataRepository(ABC):
    """define contract for fetching external health data sources"""
    @abstractmethod
    def fetch_data(self):
        """fetch and return cleaned data as a list of dictionaries"""
        pass


class FluDataRepository(IDataRepository):
    """Concrete implementation for fetching flu data from CDC API"""
    def __init__(self, api_url:str):
        self.api_url = api_url
        logger.info(f"CDCRepo initialised with API URL: {self.api_url}")


    def fetch_data(self):
        
        params = {
            "$limit" : 2000, 
            "$order" : "week_ending_date DESC",
            "group" : "By Week",
            "age_group" : "All Ages"
        }

        try:
            response = requests.get(self.api_url, timeout = 30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} records from CDC API.")

            clean_data = []
            for row in data:
                if "jurisdiction" in row and "influenza_deaths" in row:
                    clean_data.append({
                        "state": row["jurisdiction"],
                        "flu_deaths": int(row.get("influenza_deaths") or 0),
                        "date": row.get("week_ending_date")
                    })
            return clean_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to CDC API: {e}")
            print(f"Error fetching data from CDC API: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error during data processing: {e}")
            print(f"Unexpected error: {e}")
            return []