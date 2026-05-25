"""
One-time data preparation script.

Reads raw HHS hospital utilisation data (01_Data/raw_hospital_data.csv),
aggregates ICU and total bed counts to state level for the most recent
reporting week, and writes the cleaned output to 01_Data/us_states_capacity.csv.

The raw source file is not tracked in version control (see .gitignore).
Download it from the HHS Protect Public Data Hub before running this script.
"""
import pandas as pd
import os

INPUT_FILE = '01_Data/raw_hospital_data.csv'
OUTPUT_FILE = '01_Data/us_states_capacity.csv'


# Mapping states
STATE_MAP = {
    "AL": "Alabama", 
    "AK": "Alaska",
    "AZ": "Arizona", 
    "AR": "Arkansas", 
    "CA": "California",
    "CO": "Colorado", 
    "CT": "Connecticut", 
    "DE": "Delaware", 
    "FL": "Florida", 
    "GA": "Georgia",
    "HI": "Hawaii", 
    "ID": "Idaho", 
    "IL": "Illinois", 
    "IN": "Indiana", 
    "IA": "Iowa",
    "KS": "Kansas", 
    "KY": "Kentucky", 
    "LA": "Louisiana", 
    "ME": "Maine", 
    "MD": "Maryland",
    "MA": "Massachusetts", 
    "MI": "Michigan", 
    "MN": "Minnesota", 
    "MS": "Mississippi", 
    "MO": "Missouri",
    "MT": "Montana", 
    "NE": "Nebraska", 
    "NV": "Nevada", 
    "NH": "New Hampshire", 
    "NJ": "New Jersey",
    "NM": "New Mexico", 
    "NY": "New York", 
    "NC": "North Carolina", 
    "ND": "North Dakota", 
    "OH": "Ohio",
    "OK": "Oklahoma", 
    "OR": "Oregon", 
    "PA": "Pennsylvania", 
    "RI": "Rhode Island", 
    "SC": "South Carolina",
    "SD": "South Dakota", 
    "TN": "Tennessee", 
    "TX": "Texas", 
    "UT": "Utah", 
    "VT": "Vermont",
    "VA": "Virginia", 
    "WA": "Washington", 
    "WV": "West Virginia", 
    "WI": "Wisconsin", 
    "WY": "Wyoming",
    "DC": "District of Columbia",
    "PR": "Puerto Rico",
    "GU": "Guam",
    "VI": "Virgin Islands",
    "AS": "American Samoa"
}



def clean_hhs_data():
    print(f"Reading data from {INPUT_FILE}...")

    try:
        df = pd.read_csv(INPUT_FILE)
        
        # Normalize Columns
        df.columns = df.columns.str.lower().str.strip()
        
        col_date = 'collection_week'
        col_state = 'state'
        col_total_beds = 'inpatient_beds_7_day_avg'
        col_icu_beds = 'total_staffed_adult_icu_beds_7_day_avg'

        # force columns to numeric to avoid string concatenation during sum
        print("Forcing numeric conversion...")
        df[col_total_beds] = pd.to_numeric(df[col_total_beds], errors='coerce').fillna(0)
        df[col_icu_beds] = pd.to_numeric(df[col_icu_beds], errors='coerce').fillna(0)

        # Filter for latest date
        df[col_date] = pd.to_datetime(df[col_date])
        latest_date = df[col_date].max()
        print(f"Latest date found: {latest_date}")
        df_latest = df[df[col_date] == latest_date].copy()

        # Group by State 
        df_state = df_latest.groupby(col_state)[[col_total_beds, col_icu_beds]].sum().reset_index()

        # Rename columns
        df_state = df_state.rename(columns={
            col_state : 'Abbreviation',
            col_total_beds : 'Total_Hospital_Beds',
            col_icu_beds : 'ICU_Beds'
        })

        # Map Full Name
        df_state['State'] = df_state['Abbreviation'].map(STATE_MAP)

        # Data Cleanup
        df_final = df_state[['State', 'Abbreviation', 'Total_Hospital_Beds', 'ICU_Beds']]
        df_final = df_final.dropna(subset=['State'])

        # Convert to Integer
        df_final['Total_Hospital_Beds'] = df_final['Total_Hospital_Beds'].astype(int)
        df_final['ICU_Beds'] = df_final['ICU_Beds'].astype(int)

        # Save
        df_final.to_csv(OUTPUT_FILE, index=False)
        print(f"SUCCESS! Cleaned data saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clean_hhs_data()