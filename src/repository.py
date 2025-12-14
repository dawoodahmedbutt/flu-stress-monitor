from abc import ABC, abstractmethod
import requests
import json

class IDataRepository(ABC):
    """define contract for fetching external health data sources"""
    @abstractmethod
    def fetch_data(self):
        """fetch and return cleaned data as a list of dictionaries"""
        pass


class CDCRepository(IDataRepository):
    """Concrete implementation for fetching flu data from CDC API"""
    def __init__(self):
        self.url = "https://data.cdc.gov/resource/ynw2-4viq.json"

    def fetch_data(self):
        params = {
            "$limit" : 2000, 
            "$order" : "week_ending_date DESC",
            "group" : "By Week",
            "age_group" : "All Ages"
        }

        try:
            response = requests.get(self_url, params = params, timeout = 10)
            response.raise_for_status()
            data = response.json()

            clean_data = []
            for row in data:
                if "jurisdiction" in row and "influenza_deaths" in row:
                    clean_data.append({
                        "state": row["jurisdiction"],
                        "flu_deaths": int(row.get("influenza_deaths") or 0),
                        "date": row.get("week_ending_date")
                    })
            return clean_data

        except requests.RequestException as e:
            print(f"Error fetching data from CDC API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []