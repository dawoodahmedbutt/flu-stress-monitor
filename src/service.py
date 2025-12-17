import pandas as pd
from src.repository import IDataRepository
from src.database import DatabaseAdapter

HOSPITAL_DATA = '01_Data/us_states_capacity.csv'

class FluDashBoardService:
    """main logic
    responsible for merging data and calculating stress index"""

    def __init__ (self, repository: IDataRepository, db_adapter : DatabaseAdapter):
        self.repository = repository
        self.db_adapter = db_adapter

    def load_hospital_data(self):

        try:
            df = pd.read_csv(HOSPITAL_DATA)
            
            # Standardise Column Names 
            if 'State' in df.columns:
                df.rename(columns={'State': 'state'}, inplace=True)
            
            # Ensure  required columns exist after renaming
            required_columns = ['state', 'Total_Hospital_Beds', 'ICU_Beds']

            if not all(col in df.columns for col in required_columns):
                # Logs missing columns for debugging
                missing = [c for c in required_columns if c not in df.columns]
                print(f"Error: CSV is missing columns: {missing}")
                return pd.DataFrame()
            
            return df
        except FileNotFoundError:
            print(f"Error: File {HOSPITAL_DATA} not found.")
            return pd.DataFrame()
        
        except Exception as e:
            print(f"Error loading hospital data: {e}")
            return pd.DataFrame()



    def get_dashboard_data(self):
        # Fetch data from repository (API)
        api_data = self.repository.fetch_data()
        if not api_data:
            print("DEBUG: API returned no data.") # <--- DEBUG
            return pd.DataFrame()

        # Load static data (CSV)
        hospital_data = self.load_hospital_data()
        if hospital_data.empty:
            print("DEBUG: Hospital CSV data is empty.") # <--- DEBUG
            return pd.DataFrame()

        # Convert API data to DataFrame
        df_api = pd.DataFrame(api_data)
        print(f"DEBUG: Rows from API: {len(df_api)}") # <--- DEBUG


        # convert to datetime
        df_api['date'] = pd.to_datetime(df_api['date'])
        
        
        # Sort by date
        df_api = df_api.sort_values(by='date', ascending = False)

        # Delete duplicates, keeping only the latest entry
        df_api = df_api.drop_duplicates(subset = ['state'], keep='first')
        print(f"DEBUG: Rows from API after deduplication: {len(df_api)}")


        # Merge Data
        try:
            df_merged = pd.merge(df_api, hospital_data, left_on = 'state', right_on = 'state', how = 'inner')
            print(f"DEBUG: Rows after merge: {len(df_merged)}")

        except KeyError as e:
            print (f"Merge error: column not found. {e}")
            return pd.DataFrame()


        # Calculate Stress Index
        if not df_merged.empty:
            df_merged['Stress_Index'] = df_merged.apply(self._calculate_stress, axis=1)
            self.db_adapter.save_data(df_merged)
            
            final_cols = ['state', 'flu_deaths', 'Total_Hospital_Beds', 'ICU_Beds', 'Stress_Index', 'date']
            return df_merged[final_cols].sort_values(by='Stress_Index', ascending=False)
        
        return df_merged



    def _calculate_stress(self, row):
        beds = row['ICU_Beds']
        deaths = row['flu_deaths']
        if beds == 0:
            return 0.0
        return round((deaths / beds) * 100, 2)