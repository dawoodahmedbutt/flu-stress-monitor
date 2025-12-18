import streamlit as st
from src.repository import FluDataRepository
from src.database import DatabaseAdapter
from src.service import FluDashBoardService
from src.ui.dashboard import FluDashboardUI
from src.ui.admin import render_admin_panel
from src.log_config import logger

def main():
    # Initialise Layers
    
    repository = FluDataRepository(api_url="https://data.cdc.gov/resource/r8kw-7aab.json")
    db_adapter = DatabaseAdapter()
    service = FluDashBoardService(repository=repository, db_adapter=db_adapter)
    ui = FluDashboardUI()

    # Navigation
    st.sidebar.title("🛠️ System Control")
    page = st.sidebar.radio("Navigate to:", ["Dashboard", "Admin Panel"])

    # Routing
    if page == "Dashboard":
        logger.info("User navigated to Dashboard.")
        data = service.get_dashboard_data()
        ui.render(data)

    elif page == "Admin Panel":
        logger.info("User navigated to Admin Panel.")
        render_admin_panel(service)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.0 | Task 1 Complete")

if __name__ == "__main__":
    main()
