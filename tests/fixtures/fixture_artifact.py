import pytest
from app import app


@pytest.fixture
def client():
    """Creating the test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
