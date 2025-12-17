import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.service import FluDashBoardService
from src.database import DatabaseAdapter

def test_service_keeps_history_and_calculates_risk():
    """
    Enhancement Test:
    1. Should return data for MULTIPLE dates (History), not just the latest.
    2. Should calculate 'Risk_Level' based on Stress Index.
    """
    # Mock API with 2 weeks of data
    mock_repo = MagicMock()
    mock_repo.fetch_data.return_value = [
        {"state": "Alabama", "flu_deaths": 10, "date": "2024-01-01"}, # Week 1
        {"state": "Alabama", "flu_deaths": 50, "date": "2024-01-08"}  # Week 2 (Higher deaths)
    ]
    
    # Mock Database
    mock_db = MagicMock(spec=DatabaseAdapter)
    
    service = FluDashBoardService(repository=mock_repo, db_adapter=mock_db)

    # Mock CSV for hospital capacity
    # Note: Capacity is static, but merged with time-series data
    service.load_hospital_data = MagicMock(return_value=pd.DataFrame({
        'state': ['Alabama'],
        'Total_Hospital_Beds': [100],
        'ICU_Beds': [50] 
    }))

    # Act
    df = service.get_dashboard_data()

    # Assert 1: History Check
    # sent 2 weeks of data, expect 2 rows back. 
    # (Current logic might drop one or fail to handle dates)
    assert len(df) == 2, "Service should keep history, but it returned fewer rows."

    # Assert 2: Feature Engineering Check
    # expect a new column 'Risk_Level'
    assert 'Risk_Level' in df.columns, "Risk_Level column is missing."
    
    # Check logic: 
    # Week 1: 10 deaths / 50 beds = 20% (Medium/High?). Logic yet to be defined
    # Week 2: 50 deaths / 50 beds = 100% (Critical/High)
    # check the column exists and has values 
    assert not df['Risk_Level'].isnull().any()