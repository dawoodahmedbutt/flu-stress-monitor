import pytest
from unittest.mock import MagicMock, patch
import sys

# We import the main function from app
# This will fail initially because app.py doesn't exist yet
from app import main

@patch('app.render_dashboard')      # Mock the dashboard view
@patch('app.render_admin_panel')    # Mock the admin view
@patch('app.st')                    # Mock Streamlit
@patch('app.get_service')           # Mock the database connection
def test_app_routing_dashboard(mock_service, mock_st, mock_admin, mock_dash):
    """Test that selecting 'Dashboard' loads the dashboard view"""
    
    # Arrange: Simulate user selecting "Dashboard" in sidebar
    mock_st.sidebar.radio.return_value = "Dashboard"
    
    # Act
    main()
    
    # Assert
    mock_dash.assert_called_once()  # Should load dashboard
    mock_admin.assert_not_called()  # Should NOT load admin

@patch('app.render_dashboard')
@patch('app.render_admin_panel')
@patch('app.st')
@patch('app.get_service')
def test_app_routing_admin(mock_service, mock_st, mock_admin, mock_dash):
    """Test that selecting 'Admin Panel' loads the admin view"""
    
    # Arrange: Simulate user selecting "Admin Panel"
    mock_st.sidebar.radio.return_value = "Admin Panel"
    
    # Act
    main()
    
    # Assert
    mock_admin.assert_called_once() # Should load admin
    mock_dash.assert_not_called()   # Should NOT load dashboard