import pytest
import pytest_mock
from flask import Flask
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
from app import app


@pytest.fixture
def client():
    """Creating the test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.get_db_connection')
def test_view_ledger_success(mock_get_db_connection, client):
    """
    Test successful retrieval of a ledger.
    Mocks the database connection and query result.
    """
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.trades = [{"trade_id": 1, "amount": 100}]
    mock_result.holding = {"AAPL": 10}
    mock_result.value = {"AAPL": 1500}
    mock_result.balance = 100000

    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = mock_result

    response = client.get("/view_ledger?name=test_ledger")

    assert response.status_code == 200
    assert response.json == {
        "trades": [{"trade_id": 1, "amount": 100}],
        "holding": {"AAPL": 10},
        "value": {"AAPL": 1500},
        "balance": 100000
    }

    mock_conn.execute.assert_called_once()
    mock_get_db_connection.assert_called_once()


@patch('app.get_db_connection')
def test_view_ledger_not_found(mock_get_db_connection, client):
    """
    Test retrieval of a non-existent ledger.
    Mock the database connection to return None.
    """
    mock_conn = MagicMock()
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = None

    response = client.get("/view_ledger?name=non_existent_ledger")

    assert response.status_code == 404
    assert response.json == {"error": "Ledger not found"}

    mock_conn.execute.assert_called_once()
    mock_get_db_connection.assert_called_once()
