import pytest
from app import app
from unittest.mock import patch, Mock
from tests.conftest import client
from tests.conftest import mock_db_connection, mock_dependencies


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
