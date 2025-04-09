import pytest
from unittest.mock import patch, MagicMock, Mock
from app import app


@pytest.fixture
def client():
    """Creating the test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db_connection():
    with patch('app.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_dependencies():
    with patch('app.recursive_repo_clone') as mock_clone, \
            patch('app.build_docker_image') as mock_docker_build, \
            patch('app.start_ledger') as mock_start_ledger, \
            patch('app.open', create=True) as mock_open:

        mock_docker = Mock()
        mock_docker.save.return_value = [b'mock_image_data']
        mock_docker_build.return_value = mock_docker
        mock_start_ledger.return_value = ({"status": "success"}, 200)

        yield {
            'clone': mock_clone,
            'docker_build': mock_docker_build,
            'start_ledger': mock_start_ledger,
            'open': mock_open
        }


@pytest.fixture(autouse=True)
def mock_api_key_validation():
    with patch('app.validate_api_key') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate
