import pytest

from tests.fixtures.fixture_artifact import sample_fixture
from unittest.mock import MagicMock

# Mock Docker execution 
@pytest.fixture(scope="function")
def mock_docker(mocker):
    """Mock the run_docker_container function from docker_utils.py"""
    return mocker.patch("utils.docker_utils.run_docker_container", return_value=b"Mocked container logs")


