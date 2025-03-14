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


def test_update_ledger_success(client, mock_db_connection):
    mock_result = Mock()
    mock_result.trades = []
    mock_result.balance = 10000
    mock_result.worth = {}

    mock_db_connection.execute.return_value.fetchone.return_value = mock_result

    with patch('app.calculate_total_value') as mock_calculate_value, \
            patch('app.calculate_new_balance') as mock_calculate_balance:

        mock_calculate_value.return_value = 100000
        mock_calculate_balance.return_value = 78549

        test_params = {
            'name': 'test_ledger',
            'trades': [{"type": "buy", "ticker": "AAPL", "price": 100, "quantity": 8}],
            'holding': {"AAPL": 8},
            'balance': 78549
        }

        response = client.patch("/update_ledger", json=test_params)

        mock_db_connection.execute.assert_called()
        mock_calculate_value.assert_called_once_with(
            test_params['holding'], test_params['balance'])
        mock_calculate_balance.assert_called_once_with(
            mock_result.balance, test_params['trades'])

        assert response.status_code == 200
        assert response.json["message"] == "Ledger 'test_ledger' updated successfully"


def test_update_ledger_nonexistent_ledger(client, mock_db_connection):
    mock_db_connection.execute.return_value.fetchone.return_value = None\

    test_params = {
        'name': 'test_ledger',
        'trades': [{"type": "buy", "ticker": "AAPL", "price": 100, "quantity": 8}],
        'holding': {"AAPL": 8},
        'balance': 10000
    }

    response = client.patch("/update_ledger", json=test_params)

    mock_db_connection.execute.assert_called()
    assert response.status_code == 404
    assert "does not exist" in response.json["error"]


def test_update_ledger_missing_fields(client, mock_db_connection):
    test_params = {
        'name': "test_ledger",
        'balance': 10000
    }

    response = client.patch("/update_ledger", json=test_params)

    mock_db_connection.execute.assert_not_called()
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]
