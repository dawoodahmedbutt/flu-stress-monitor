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
        try:
            df = pd.read_csv(HOSPITAL_DATA)

            if 'State' in df.columns:
                df.rename(columns={'State': 'state'}, inplace=True)
            return df
        
        except Exception as e:
            logger.error(f"Critical: Failed to load hospital CSV: {e}")
            return pd.DataFrame()


    def get_dashboard_data(self):
        api_data = self.repository.fetch_data()

        if not api_data: 
            logger.warning("API returned no data.")
            return pd.DataFrame()

        hospital_data = self.load_hospital_data()
        if hospital_data.empty: 
            return pd.DataFrame()

        df_api = pd.DataFrame(api_data)
        if 'date' in df_api.columns:
            df_api['date'] = pd.to_datetime(df_api['date'])
        
        # Trend Analysis 
        df_api = df_api.sort_values(by=['state', 'date'], ascending=False)


        try:
            df_merged = pd.merge(df_api, hospital_data, on='state', how='inner')

        except KeyError as e:
            logger.error(f"Merge error: {e}")
            return pd.DataFrame()


        if not df_merged.empty:
            # Feature Engineering: Calculate Stress and Risk
            df_merged['Stress_Index'] = df_merged.apply(self._calculate_stress, axis=1)
            df_merged['Risk_Level'] = df_merged['Stress_Index'].apply(self._categorise_risk)

          
            try:
                self.db_adapter.save_data(df_merged)

            except Exception as e:
                logger.error(f"Database persistence failed: {e}")
            
            return df_merged
        
        return df_merged

    def _calculate_stress(self, row):
        """
        Calculate stress using UKHSA 2024/25 mortality-to-admission ratio (1:15).
        Formula: (Deaths * 15 / ICU_Beds) * 100
        """
        beds = row['ICU_Beds']
        deaths = row['flu_deaths']
        if beds == 0: return 0.0
        
        estimated_occupancy = deaths * 15
        stress_index = (estimated_occupancy / beds) * 100
        return round(stress_index, 2)

    def _categorise_risk(self, stress_index):
        """
        Risk Logic:
        Maps UKHSA-derived occupancy to CDC IRAT risk categories.
        """
        if stress_index < 10.0:
            return "Low"
        elif stress_index < 40.0:
            return "Moderate"
        elif stress_index < 70.0:
            return "High"
        else:
            return "Critical"