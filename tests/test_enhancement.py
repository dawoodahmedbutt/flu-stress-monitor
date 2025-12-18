import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.service import FluDashBoardService
from src.database import DatabaseAdapter

def test_service_logic_with_ukhsa_and_cdc_thresholds():
    """
    Enhancement Test:
    Validates that:
    1. 1:15 Multiplier works correctly.
    2. Thresholds trigger the correct CDC/Critical labels.
    - 0 deaths -> 0% Stress -> Low
    - 1 death  -> 15% Stress -> Moderate (Threshold 10-40)
    - 3 deaths -> 45% Stress -> High (Threshold 40-70)
    - 6 deaths -> 90% Stress -> Critical (Threshold > 70)
    using UKHSA data with 1:15 deaths to ICU bed ratio - ref and further explanation in the report
    """
    # Mock Repository with specific mortality counts
    mock_repo = MagicMock()
    mock_repo.fetch_data.return_value = [
        {"state": "Alabama", "flu_deaths": 0, "date": "2024-01-01"}, 
        {"state": "Alabama", "flu_deaths": 1, "date": "2024-01-08"}, 
        {"state": "Alabama", "flu_deaths": 3, "date": "2024-01-15"}, 
        {"state": "Alabama", "flu_deaths": 6, "date": "2024-01-22"}  
    ]
    
    # Mock DB
    mock_db = MagicMock(spec=DatabaseAdapter)
    
    # Initialise Service
    service = FluDashBoardService(repository=mock_repo, db_adapter=mock_db)

    # Mock Capacity (100 ICU beds for easy math)
    service.load_hospital_data = MagicMock(return_value=pd.DataFrame({
        'state': ['Alabama'],
        'Total_Hospital_Beds': [500],
        'ICU_Beds': [100]
    }))

    # Act
    df = service.get_dashboard_data()

    # Assertions
    assert len(df) == 4
    
    # Verify Low (0 * 15 / 100 = 0%)
    assert df[df['flu_deaths'] == 0]['Risk_Level'].iloc[0] == "Low"
    
    # Verify Moderate (1 * 15 / 100 = 15%)
    assert df[df['flu_deaths'] == 1]['Risk_Level'].iloc[0] == "Moderate"

    # Verify High (3 * 15 / 100 = 45%)
    assert df[df['flu_deaths'] == 3]['Risk_Level'].iloc[0] == "High"

    # Verify Critical (6 * 15 / 100 = 90%)
    assert df[df['flu_deaths'] == 6]['Risk_Level'].iloc[0] == "Critical"