import pytest
import pandas as pd
from src.ui.dashboard import FluDashboardUI

def test_ui_renders_risk_indicators():
    """
    UI Test: Ensure the UI logic can process the new 
    enhanced columns (Risk_Level and Stress_Index).
    """
    # Mock Data including UKHSA/CDC enhancements
    mock_df = pd.DataFrame({
        'state': ['California', 'Alaska'],
        'flu_deaths': [10, 5],
        'ICU_Beds': [1000, 50],
        'Stress_Index': [15.0, 150.0], # (Deaths * 15 / Beds) * 100
        'Risk_Level': ['Moderate', 'Critical'],
        'date': pd.to_datetime(['2024-01-01', '2024-01-01'])
    })

    ui = FluDashboardUI()

    assert ui.get_risk_color('Critical') == 'red'
    assert ui.get_risk_color('Low') == 'green'