import pytest
from app import app
from unittest.mock import patch, Mock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db_connection():
    with patch('app.get_db_connection') as mock_conn:
        mock_context = Mock()
        mock_conn.return_value.__enter__.return_value = mock_context
        yield mock_context
