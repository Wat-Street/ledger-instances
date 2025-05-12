import pytest
from unittest.mock import patch
from app import app, API_KEY

def test_start_ledger_success():
    app.config.update(TESTING=True)
    with app.test_client() as client, patch("app.start_ledger") as mock_start:
        mock_start.return_value = ({"msg": "started"}, 200)

        resp = client.get(
            "/start_ledger",
            query_string={"name": "demo"},
            headers={"X-API-Key": API_KEY},
        )

        assert resp.status_code == 200
        assert resp.get_json() == {"msg": "started"}
        mock_start.assert_called_once_with("demo")


def test_start_ledger_missing_name():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        resp = client.get(
            "/start_ledger",
            headers={"X-API-Key": API_KEY},
        )

        assert resp.status_code == 400
        assert "Missing required parameter" in resp.get_json()["error"]

# Need to unit test the validation and the start_ledger failed verification case, I was struggling with it - KP