import streamlit as st
import pandas as pd
from src.log_config import logger

def render_admin_table(service):
    """
    Render the Admin interface for CRUD operations on Hospital Data.
    """
    st.header("🛠️ Admin Panel: Hospital Capacity Management")
    st.info("Update the ICU or Hospital Bed capacity for a specific state.")

    # Load data to get the list of states
    df = service.get_dashboard_data()
    
    if df.empty:
        st.error("Could not load data for editing.")
        return

    # choose state to edit
    all_states = sorted(df['state'].unique())
    selected_state = st.selectbox("Select State to Update", all_states)

    # Get current values for chosen state
    current_row = df[df['state'] == selected_state].iloc[0]
    current_beds = int(current_row['Total_Hospital_Beds'])
    current_icu = int(current_row['ICU_Beds'])

    # edit
    with st.form(key='edit_hospital_form'):
        col1, col2 = st.columns(2)
        new_beds = col1.number_input("Total Hospital Beds", min_value=0, value=current_beds)
        new_icu = col2.number_input("ICU Beds", min_value=0, value=current_icu)
        
        submit_button = st.form_submit_button(label="💾 Update Records")

    # submission
    if submit_button:
        try:
            # Load the raw CSV to update it permanently
            csv_path = '01_Data/us_states_capacity.csv'
            df_csv = pd.read_csv(csv_path)
            
            # Standardise column name if needed
            if 'State' in df_csv.columns:
                df_csv.rename(columns={'State': 'state'}, inplace=True)
            
            # Update data
            mask = df_csv['state'] == selected_state
            df_csv.loc[mask, 'Total_Hospital_Beds'] = new_beds
            df_csv.loc[mask, 'ICU_Beds'] = new_icu
            
            # Save  to CSV
            df_csv.to_csv(csv_path, index=False)
            
            logger.info(f"User updated capacity for {selected_state}: Beds={new_beds}, ICU={new_icu}")
            st.success(f"✅ Successfully updated records for {selected_state}!")
            
            # Force a cache clear so dashboard sees new data immediately
            st.cache_data.clear()
            
        except Exception as e:
            st.error(f"Failed to update records: {e}")
            logger.error(f"Admin update failed: {e}")