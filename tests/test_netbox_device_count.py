import pytest
import requests
import requests_mock
from scripts.netbox_device_count import get_device_count

NETBOX_API_URL = "http://localhost:8000/api/dcim/devices/"

@pytest.fixture
def mock_netbox_response():
    """Mock NetBox API response with multiple device statuses."""
    return {
        "results": [
            {"id": 1, "name": "Device 1", "status": {"value": "active"}},
            {"id": 2, "name": "Device 2", "status": {"value": "planned"}},
            {"id": 3, "name": "Device 3", "status": {"value": "active"}},
            {"id": 4, "name": "Device 4", "status": {"value": "decommissioned"}},
        ]
    }

@pytest.fixture
def mock_netbox_response_active():
    """Mock NetBox API response for active devices only."""
    return {
        "results": [
            {"id": 1, "name": "Device 1", "status": {"value": "active"}},
            {"id": 3, "name": "Device 3", "status": {"value": "active"}},
        ]
    }

@pytest.fixture
def mock_empty_response():
    """Mock NetBox API response with no devices."""
    return {"results": []}

@pytest.fixture
def mock_invalid_response():
    """Mock NetBox API response with missing 'results' field."""
    return {}

def test_get_device_count_with_status(mock_netbox_response_active):
    """Test API response when filtering by a specific device status."""
    with requests_mock.Mocker() as m:
        m.get(NETBOX_API_URL, json=mock_netbox_response_active)
        count = get_device_count(status="active")

    assert count == 2  # Expecting 2 active devices

def test_get_device_count_without_status(mock_netbox_response):
    """Test API response when no status filter is given (counts all statuses)."""
    with requests_mock.Mocker() as m:
        m.get(NETBOX_API_URL, json=mock_netbox_response)
        counts = get_device_count()

    assert counts["active"] == 2
    assert counts["planned"] == 1
    assert counts["decommissioned"] == 1
    assert counts.get("unknown", 0) == 0  # Ensure no 'unknown' category

def test_get_device_count_empty_response(mock_empty_response):
    """Test API response when no devices are returned."""
    with requests_mock.Mocker() as m:
        m.get(NETBOX_API_URL, json=mock_empty_response)
        counts = get_device_count()

    assert counts == {}  # Expecting an empty dictionary

def test_get_device_count_invalid_response(mock_invalid_response):
    """Test API response when the results field is missing."""
    with requests_mock.Mocker() as m:
        m.get(NETBOX_API_URL, json=mock_invalid_response)
        counts = get_device_count()

    assert counts == {}  # Should return an empty dictionary

def test_get_device_count_network_error():
    """Test handling of network failure scenarios."""
    with requests_mock.Mocker() as m:
        m.get(NETBOX_API_URL, exc=requests.exceptions.ConnectionError)
        counts = get_device_count()

    assert counts is None  # Expecting None due to network error
