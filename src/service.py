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
        """Main pipeline: Fetch, Filter, Normalize, Merge."""
        api_data = self.repository.fetch_data()
        if not api_data: 
            return pd.DataFrame()

        df_api = pd.DataFrame(api_data)
        
       
        if 'group' in df_api.columns:
            df_api = df_api[df_api['group'] == 'By Week']

        # Filter out national totals 
        if 'state' in df_api.columns:
            df_api = df_api[df_api['state'] != 'United States']

    
        column_map = {
            'state': 'state',                
            'week_ending_date': 'date',      
            'influenza_deaths': 'flu_deaths' 
        }
        df_api.rename(columns=column_map, inplace=True)
        
        if 'state' not in df_api.columns:
            logger.error(f"Missing 'state' column. Available: {df_api.columns}")
            return pd.DataFrame()

        # clean and convert
        if 'flu_deaths' not in df_api.columns:
            df_api['flu_deaths'] = 0
        
        df_api['flu_deaths'] = pd.to_numeric(df_api['flu_deaths'], errors='coerce').fillna(0)
        
        if 'date' in df_api.columns:
            df_api['date'] = pd.to_datetime(df_api['date'])

        hospital_data = self.load_hospital_data()
        if hospital_data.empty: return pd.DataFrame()

        try:
            df_merged = pd.merge(df_api, hospital_data, on='state', how='inner')
        except KeyError:
            return pd.DataFrame()

        if not df_merged.empty:
            df_merged['Stress_Index'] = df_merged.apply(self._calculate_stress, axis=1)
            df_merged['Risk_Level'] = df_merged['Stress_Index'].apply(self._categorize_risk)
            
            # Save to DB
            self.db_adapter.save_data(df_merged)
            return df_merged
        
        return df_merged

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