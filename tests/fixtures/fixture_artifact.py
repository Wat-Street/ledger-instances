import pytest 

@pytest.fixture(scope="module")
def sample_fixture():
    city = ["NYC", "Chicago", "London", "Mumbai"]
    yield city


