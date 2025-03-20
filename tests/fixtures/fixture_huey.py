import pytest
from datetime import datetime, timedelta

@pytest.fixture
def sample_ledger():
    return {
        "name": "TestLedger", 
        "image_path": "test-image",
        "update_time": 5, # minutes
        "end_duration": 1, 
        "start_time": datetime.now()
    }

@pytest.fixture
def expired_ledger():
    return {
        "name": "ExpiredLedger",
        "image_path": "expired-image", 
        "update_time": 5, 
        "end_duration": 0, # ends immediately
        "start_time": datetime.now() - timedelta(days=1)
    }