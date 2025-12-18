import streamlit as st
from src.repository import FluDataRepository
from src.database import DatabaseAdapter
from src.service import FluDashBoardService
from src.ui.dashboard import FluDashboardUI
from src.log_config import logger

def main():
    # Initialise Infrastructure
    db_adapter = DatabaseAdapter()
    repository = FluDataRepository()
    
    # Initialize Service Layer
    service = FluDashBoardService(repository=repository, db_adapter=db_adapter)
    
    # Initialize UI Layer
    ui = FluDashboardUI()

    # navigation
    st.sidebar.title("🛠️ System Control")
    page = st.sidebar.radio("Navigate to:", ["Dashboard", "Admin Panel"])


    if page == "Dashboard":
        logger.info("User navigated to Dashboard.")
        data = service.get_dashboard_data()
        ui.render(data)

    elif page == "Admin Panel":
        logger.info("User navigated to Admin Panel.")
        st.header("⚙️ Administrative Controls")
        st.info("Use this panel to refresh data from the API and update the local database.")
        
        if st.button("🔄 Trigger Data Sync"):
            with st.spinner("Fetching latest data..."):
                df = service.get_dashboard_data()
                if not df.empty:
                    st.success(f"Successfully synced {len(df)} records!")
                    logger.info("Manual data sync triggered successfully.")
                else:
                    st.error("Data sync failed. Check app.log for details.")
        

        st.markdown("---")
        st.subheader("System Logs")
        st.text("Latest activity is recorded in the project root as 'app.log'.")

if __name__ == "__main__":
    main()