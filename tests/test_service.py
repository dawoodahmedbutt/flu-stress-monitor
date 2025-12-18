import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.service import FluDashBoardService
from src.database import DatabaseAdapter

def test_stress_index_calculation():
    """
    User Story 3: test merging API with CSV of capacity
    Scenario: Alabama has 10 deaths, 50 ICU beds
    Stress index = (10 / 50) * 100 = 20.0
    """
    # Mock the API Repository
    mock_repo = MagicMock()
    mock_repo.fetch_data.return_value = [
        {
            "state": "Alabama",
            "flu_deaths": 10, 
            "date" : "2024-04-21"
        }]
    
    # Mock the Database
    mock_db = MagicMock(spec=DatabaseAdapter)
    
    # Initialize Service
    service = FluDashBoardService(repository=mock_repo, db_adapter=mock_db)

    # Mock the Hospital CSV Data
    service.load_hospital_data = MagicMock(return_value=pd.DataFrame({
        'state': ['Alabama'],  
        'Abbreviation': ['AL'],
        'Total_Hospital_Beds': [1000],
        'ICU_Beds': [50]
    }))

    # Act
    result = service.get_dashboard_data()

    # Assert
    mock_db.save_data.assert_called_once()  
    row = result.iloc[0]
    assert row['state'] == 'Alabama'
    assert row['Stress_Index'] == 300.0
    mock_repo.fetch_data.assert_called_once()