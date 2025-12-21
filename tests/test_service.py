import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.service import FluDashBoardService
from src.database import DatabaseAdapter

@pytest.fixture
def mock_repo():
    """Creates a fake API repository."""
    return MagicMock()

@pytest.fixture
def mock_db():
    """Creates a fake Database Adapter."""
    return MagicMock(spec=DatabaseAdapter)

@pytest.fixture
def service(mock_repo, mock_db):
    """Initializes the Service with the mocked dependencies."""
    return FluDashBoardService(repository=mock_repo, db_adapter=mock_db)


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


def test_get_dashboard_data_api_failure_fallback(service, mock_repo, mock_db):
    """
    Resilience Test: 
    If API returns None/Empty (simulating 503 Error), 
    Service should call db.load_data() instead.
    """
    # Simulate API Failure (Return empty list or None)
    mock_repo.fetch_data.return_value = [] 

    # Simulate DB having cached data
    mock_db.load_data.return_value = pd.DataFrame({
        'state': ['CachedState'],
        'Stress_Index': [50.0],
        'Risk_Level': ['High']
    })

    # Act
    result = service.get_dashboard_data()

    # Assert
    assert not result.empty
    assert result.iloc[0]['state'] == 'CachedState'
    
    # Verify that I tried to load from DB
    mock_db.load_data.assert_called_once()
    # Verify I did not save empty data
    mock_db.save_data.assert_not_called()