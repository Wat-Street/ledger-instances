import pytest
import json
from app import app
from unittest.mock import patch, Mock
from tests.conftest import client
from tests.conftest import mock_db_connection, mock_dependencies


def test_update_ledger_nonexistent_ledger(client, mock_db_connection):
    mock_db_connection.execute.return_value.fetchone.return_value = None

    test_params = {
        'name': 'test_ledger',
        'trades': [{"type": "buy", "ticker": "AAPL", "price": 100, "quantity": 8}],
        'holding': {"AAPL": 8},
        'balance': 10000
    }

    response = client.patch(
        "/update_ledger",
        data=json.dumps(test_params),
        content_type='application/json',
        headers={'X-API-Key': 'test-key'}
    )

    mock_db_connection.execute.assert_called()
    assert response.status_code == 404
    response_data = json.loads(response.data.decode('utf-8'))
    assert "does not exist" in response_data.get("error", "")


def test_update_ledger_missing_fields(client, mock_db_connection):
    test_params = {
        'name': "test_ledger",
        'balance': 10000
    }

    response = client.patch(
        "/update_ledger",
        data=json.dumps(test_params),
        content_type='application/json',
        headers={'X-API-Key': 'test-key'}
    )

    mock_db_connection.execute.assert_not_called()
    assert response.status_code == 400
    response_data = json.loads(response.data.decode('utf-8'))
    assert "Missing required fields" in response_data.get("error", "")
