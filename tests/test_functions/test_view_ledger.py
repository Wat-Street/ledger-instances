from flask import Flask
from unittest.mock import patch, MagicMock

@patch('app.get_db_connection')
def test_view_ledger_success(mock_get_db_connection, client):
    """
    Test successful retrieval of a ledger.
    Mocks the database connection and query result.
    """
    # mocking both the database connection and the sqlalchemy query result
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.trades = [{"trade_id": 1, "amount": 100}]
    mock_result.holding = {"AAPL": 10}
    mock_result.value = {"AAPL": 1500}
    mock_result.balance = 100000

    # establish mock value for the desired function
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = mock_result

    # http request
    response = client.get("/view_ledger?name=test_ledger")

    # make assertions on expected values
    assert response.status_code == 200
    assert response.json == {
        "trades": [{"trade_id": 1, "amount": 100}],
        "holding": {"AAPL": 10},
        "value": {"AAPL": 1500},
        "balance": 100000
    }

    # make assertions on expected function calls
    mock_conn.execute.assert_called_once()
    mock_get_db_connection.assert_called_once()


@patch('app.get_db_connection')
def test_view_ledger_not_found(mock_get_db_connection, client):
    """
    Test retrieval of a non-existent ledger.
    Mock the database connection to return None.
    """
    # mock database connection
    mock_conn = MagicMock()
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = None

    # http request
    response = client.get("/view_ledger?name=non_existent_ledger")

    # make assertions on expected values
    assert response.status_code == 404
    assert response.json == {"error": "Ledger not found"}

    # make assertions on expected function calls
    mock_conn.execute.assert_called_once()
    mock_get_db_connection.assert_called_once()
