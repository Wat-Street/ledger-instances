import pytest
from tests.fixtures.fixture_artifact import sample_fixture
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_db_connection():
    with patch('utils.db_config.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        yield mock_conn




