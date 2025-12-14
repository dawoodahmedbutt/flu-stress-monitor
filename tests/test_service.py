import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.service import FluDashBoardService



def test_stress_index_calculation:
    """
    User Story 3: test merging API with CSV of capacity
    Scenario: Alabama has 10 deaths, 50 ICU beds
    Stress index = (10 / 50) * 100 = 20.0
    """
    mock_repo = MagicMock()
    mock_repo.fetch_data.return_value = [
        {
            "state": "AL",
            "flu_deaths": 10, 
            "date" : "2024-04-21"
        }]

    service.load_static_data = MagicMock(return_value=pd.DataFrame({
        'State': ['Alabama'],
        'Abbreviation': ['AL'],
        'Total_Hospital_Beds': [1000],
        'ICU_Beds': [50]
        #Expected stress level = (10/50)*100 = 20%
    }))

    result = service.get_dashboard_data()

    assert not result.empty
    row = result.iloc[0]
    assert row['State'] == 'Alabama'
    assert row ['Stress_Index'] == 20.0
    mock_repo.fetch_data.assert_called_once()