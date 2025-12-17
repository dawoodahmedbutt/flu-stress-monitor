import pytest
from unittest.mock import MagicMock
import pandas as pd
from src.ui.dashboard import render_dashboard
from src.ui.admin import render_admin_panel

@pytest.fixture
def mock_service():
    service = MagicMock()
    df = pd.DataFrame({
        'state': ['Test State'], 
        'flu_deaths':[10],
        'Total_Hospital_Beds':[100],
        'ICU_Beds': [10], 
        'Stress_Index' : [10.0],
        'date': ['2023-10-01']
    })
    service.get_dashboard_data.return_value = df
    return service

@patch('src.ui.dashboard.st')
def test_dashboard_renders_and_calls_service (mock_st, mock_service):
    render_dashboard(mock_service)

    #Assert
    mock_service.get_dashboard_data.assert_called_once()

    mock_st.header.assert_called()

@ patch('src.ui.admin.st')
def test_admin_panel_loads_data (mock_st, mock_service):
    render_admin_table(mock_service)

    #assert
    mock_service.get_dashboard_data.assert_called_once()
    mock_st.header.assert_called()