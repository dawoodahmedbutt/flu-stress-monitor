import streamlit as st
from src.repository import CDCRepository
from src.database import DatabaseAdapter
from src.service import FluDashBoardService
from src.ui.dashboard import render_dashboard
from src.ui.admin import render_admin_panel

# Page configuration
st.set_page_config(page_title="Flu Stress Dashboard", page_icon="🏥", layout="wide")

# Dependency
@st.cache_resource
def get_service():
    API_URL = "https://data.cdc.gov/resource/ynw2-4viq.json"
    DB_PATH = 'health_dashboard.db'
    DB_TABLE = 'dashboard_data'
    
    repository = CDCRepository(api_url=API_URL)
    db_adapter = DatabaseAdapter(db_path=DB_PATH, table_name=DB_TABLE)
    return FluDashBoardService(repository=repository, db_adapter=db_adapter)

def main():
    try:
        service = get_service()
    except Exception as e:
        st.error(f"Critical Error: Failed to initialize services. {e}")
        st.stop()

    # navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Admin Panel"])
    
    st.sidebar.markdown("---")
    
    # routing
    if page == "Dashboard":
        render_dashboard(service)
    elif page == "Admin Panel":
        render_admin_panel(service)

if __name__ == "__main__":
    main()