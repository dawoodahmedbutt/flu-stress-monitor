import pandas as pd
from src.repository import IDataRepository
from src.database import DatabaseAdapter
from src.log_config import logger 

HOSPITAL_DATA = '01_Data/us_states_capacity.csv'

class FluDashBoardService:
    def __init__(self, repository: IDataRepository, db_adapter: DatabaseAdapter):
        self.repository = repository
        self.db_adapter = db_adapter

    def load_hospital_data(self):
        """Loads static state capacity data from CSV."""
        try:
            df = pd.read_csv(HOSPITAL_DATA)
            if 'State' in df.columns:
                df.rename(columns={'State': 'state'}, inplace=True)
            return df
        except Exception as e:
            logger.error(f"Critical: Failed to load hospital CSV: {e}")
            return pd.DataFrame()


    def get_dashboard_data(self):
        """
        Main ETL Method:
        1. Tries to fetch live data from API.
        2. If successful: Merges with CSV, Calculates Stress, Saves to DB.
        3. If API fails (returns empty): LOADS FROM LOCAL DB instead.
        """
        # Attempt to fetch live data
        api_data = self.repository.fetch_data()
        
        # Check if API is working
        if api_data:
            logger.info(f"API Success: Fetched {len(api_data)} records. Processing...")
            
            # Convert to DataFrame
            df_api = pd.DataFrame(api_data)
            
            # Load static Hospital Capacity CSV
            df_capacity = self.load_hospital_data()
            
            # Merge Datasets (Left Join on State)
            merged_df = pd.merge(
                df_api, 
                df_capacity, 
                left_on="state", 
                right_on="state", 
                how="inner"
            )
            
            # Calculate Logic
            merged_df['Stress_Index'] = merged_df.apply(self._calculate_stress, axis=1)
            merged_df['Risk_Level'] = merged_df['Stress_Index'].apply(self._categorize_risk)
            
            # Save to Database (Cache for next time)
            if not merged_df.empty:
                self.db_adapter.save_data(merged_df)
                
            return merged_df

        # FALLBACK: API failed or returned empty -> Load from Database
        else:
            logger.warning("API returned no data. Falling back to Local Database Cache.")
            cached_df = self.db_adapter.load_data()
            
            if cached_df.empty:
                logger.error("Cache is also empty! System has no data to display.")
            else:
                logger.info(f"Loaded {len(cached_df)} records from Local Cache.")
                
            return cached_df


    def _calculate_stress(self, row):
        """Calculates stress using UKHSA 1:15 ratio."""
        beds = row['ICU_Beds']
        deaths = row['flu_deaths']
        if beds == 0: return 0.0
        
        estimated_occupancy = deaths * 15
        stress_index = (estimated_occupancy / beds) * 100
        return round(stress_index, 2)

    def _categorize_risk(self, stress_index):
        if stress_index < 10.0: return "Low"
        elif stress_index < 40.0: return "Moderate"
        elif stress_index < 70.0: return "High"
        else: return "Critical"