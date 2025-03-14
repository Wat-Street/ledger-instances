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


def test_create_ledger_success(client, mock_db_connection, mock_dependencies):
    test_params = {
        'name': 'test_ledger',
        'tickerstotrack': 'AAPL,GOOG',
        'algo_path': 'https://github.com/test/repo',
        'updatetime': '5',
        'end': '7'
    }

    response = client.get('/create_ledger', query_string=test_params)

    assert response.status_code == 200
    assert b"has been created" in response.data


def test_create_ledger_missing_parameters(client):
    # Test with no parameters
    response = client.get('/create_ledger')
    assert response.status_code == 400
    assert b"Missing required parameters" in response.data

    # Test with partial parameters
    response = client.get(
        '/create_ledger?name=test&algo_path=https://github.com/test/repo')
    assert response.status_code == 400
    assert b"Missing required parameters" in response.data


def test_create_ledger_error(client, mock_dependencies):
    mock_dependencies['clone'].side_effect = Exception(
        "Failed to clone repository")

    test_params = {
        'name': 'test_ledger',
        'tickerstotrack': 'AAPL,GOOG',
        'algo_path': 'https://github.com/test/repo',
        'updatetime': '5',
        'end': '7'
    }

    response = client.get('/create_ledger', query_string=test_params)

    assert response.status_code == 500
    assert b"Failed to clone repository" in response.data
