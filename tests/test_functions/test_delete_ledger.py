from flask import Flask, jsonify
from unittest.mock import patch, MagicMock

def test_delete_ledger_success(client, mock_db_connection):
    """Test successful deletion"""
    mock_select_result = MagicMock()
    mock_select_result.fetchone.return_value = ("test_ledger",)
    mock_db_connection.execute.return_value = mock_select_result

    response = client.get("/delete_ledger?name=test_ledger")

    # assertions
    assert response.status_code == 200
    assert response.json == {"Info": "Deleted ledger named 'test_ledger'"}

    # verify that db functions were called
    mock_db_connection.execute.assert_called()
    mock_db_connection.commit.assert_called_once()  # ensure commit happened


def test_delete_ledger_nonexistent(client, mock_db_connection):
    """Test unsuccessful deletion in the case where the ledger dne"""
    mock_select_result = MagicMock()
    mock_select_result.fetchone.return_value = None  # select statement null
    mock_db_connection.execute.return_value = mock_select_result

    response = client.get("/delete_ledger?name=non_existent_ledger")

    # assertions
    assert response.status_code == 404
    assert response.json == {
        "Error": "You are trying to delete a ledger called 'non_existent_ledger' that does not exist."
    }

    # assert that conn.commit was NOT called
    mock_db_connection.commit.assert_not_called()


def test_delete_ledger_missing_param(client):
    """Test unsuccessful deletion in the case the user does not provide a name param"""
    response = client.get("/delete_ledger")

    # assertions
    assert response.status_code == 400
    assert response.json == {
        "Error": "You did not specify a ledger name. Usage: `/delete_ledger?name=insert_name`"
    }

