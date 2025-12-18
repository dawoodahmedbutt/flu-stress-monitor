import pytest
from unittest.mock import MagicMock, patch

def test_app_initialization():
    with patch('src.log_config.setup_logger') as mock_logger:
        with patch('streamlit.sidebar'): 
            from app import main
            assert callable(main)