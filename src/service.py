import pandas as pd
from src.repository import IDataRepository

HOSPITAL_DATA = '01_Data/us_states_capacity.csv'

class FluDashBoardService:
    """main logic
    responsible for merging data and calculating stress index"""

    def __init__ (self, repository: IDataRepository):
        self.repository = repository

    def load_hospital_data(self):
        try: 
            return pd.read_csv(HOSPITAL_DATA)
        except FileNotFoundError:
            print (f"File {HOSPITAL_DATA} not found.")
            return pd.DataFrame()
        
    def get_dashboard_data (self):

        # get api data 
        api_data = self.repository.fetch_data()
        if not api_data:
            print("No data fetched from repository.")
            return pd.DataFrame()
    
        df_api = pd.DataFrame(api_data)
    
        #Load hospital data 
        df_hospital = self.load_hospital_data()
        if df_hospital.empty:
            print("Hospital data is empty.")
            return pd.DataFrame()
        
        # Merge data
        df_merged = pd.merge(
            df_api,
            df_hospital, 
            left_on = 'state', 
            right_on = 'State', 
            how = 'inner'
        )
    
        # 1. DEFINE final_cols here (FIX 1)
        final_cols = ['state', 'flu_deaths', 'Total_Hospital_Beds', 'ICU_Beds', 'Stress_Index', 'date']

        # Calculate Stress Index
        # 2. FIX DataFrame name typo: df.merged -> df_merged (FIX 2)
        df_merged['Stress_Index'] = df_merged.apply(self._calculate_stress, axis=1)
        
        # 3. Use the defined final_cols (FIX 1, Cont.)
        return df_merged[final_cols].sort_values(by='Stress_Index', ascending = False)
    
    def _calculate_stress(self, row):
        beds = row['ICU_Beds']
        deaths = row['flu_deaths']
        if beds == 0:
            return 0.0
        return round((deaths / beds) * 100, 2)