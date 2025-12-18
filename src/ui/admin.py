import streamlit as st
import pandas as pd
from src.log_config import logger

def render_admin_panel(service):
    """
    Unified Admin Interface: Sync Data AND Edit Capacity (CRUD).
    """
    st.header("⚙️ Administrative Controls")

    # Data sync
    st.subheader("🔄 Data Synchronization")
    st.info("Pull latest 2024 mortality data from CDC API.")
    
    if st.button("Trigger Data Sync"):
        with st.spinner("Fetching and processing data..."):
            df = service.get_dashboard_data()
            if not df.empty:
                st.success(f"✅ Sync Complete! {len(df)} records processed.")
                logger.info("Manual data sync triggered successfully.")
            else:
                st.error("Data sync failed. Check logs.")

    st.divider()

    # CRUD
    st.subheader("🏥 Hospital Capacity Management (CRUD)")
    st.info("Manually update hospital bed capacity for a specific state.")

    # Load Data for Selection
    df = service.get_dashboard_data()
    if df.empty:
        st.warning("Sync data first to enable editing.")
        return

    # Select State
    all_states = sorted(df['state'].unique())
    selected_state = st.selectbox("Select State to Update", all_states)

    # Get Current Values
    state_data = df[df['state'] == selected_state].iloc[0]
    current_beds = int(state_data.get('Total_Hospital_Beds', 0))
    current_icu = int(state_data.get('ICU_Beds', 0))

    # Edit Form
    with st.form(key='capacity_form'):
        col1, col2 = st.columns(2)
        new_beds = col1.number_input("Total Beds", min_value=0, value=current_beds)
        new_icu = col2.number_input("ICU Beds", min_value=0, value=current_icu)
        
        submit = st.form_submit_button("💾 Save Changes to Database")

    # Handle Submission
    if submit:
        try:
            # Update CSV 
            csv_path = '01_Data/us_states_capacity.csv'
            df_csv = pd.read_csv(csv_path)
            if 'State' in df_csv.columns: df_csv.rename(columns={'State': 'state'}, inplace=True)
            
            mask = df_csv['state'] == selected_state
            df_csv.loc[mask, 'Total_Hospital_Beds'] = new_beds
            df_csv.loc[mask, 'ICU_Beds'] = new_icu
            df_csv.to_csv(csv_path, index=False)
            
            # Trigger Logic Refresh (Update DB immediately)
            service.get_dashboard_data()
            
            st.success(f"Updated {selected_state}: Beds={new_beds}, ICU={new_icu}")
            logger.info(f"CRUD Update: {selected_state} updated by admin.")
            
        except Exception as e:
            st.error(f"Update failed: {e}")