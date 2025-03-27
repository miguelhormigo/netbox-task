import pytest
import yaml
from unittest.mock import MagicMock, patch
import sys

# Mock NetBox modules before importing DeviceReport
sys.modules["dcim.models"] = MagicMock()
sys.modules["extras.scripts"] = MagicMock()

# Define a mock Script class
class MockScript:
    def log_success(self, msg): pass
    def log_warning(self, msg, devices_type): pass
    def log_failure(self, msg): pass
    def log_info(self, msg): pass

# Assign mocks to extras.scripts
sys.modules["extras.scripts"].Script = MockScript
sys.modules["extras.scripts"].ChoiceVar = MagicMock()
sys.modules["extras.scripts"].ObjectVar = MagicMock()

# Import after mocking
from scripts.netbox_device_report import DeviceReport

@pytest.fixture
def mock_device():
    """Creates a mock device object"""
    device = MagicMock()
    device.id = 1
    device.name = "Device 1"
    device.site = MagicMock()
    device.site.name = "Site A"
    device.rack = MagicMock()
    device.rack.name = "Rack 1"
    return device

@pytest.fixture
def mock_no_device():
    """Creates a mock QuerySet that returns no devices"""
    queryset = MagicMock()
    queryset.exists.return_value = False
    queryset.filter.return_value = queryset
    return queryset

@pytest.fixture
def mock_devices(mock_device):
    """Creates a mock QuerySet that returns mock devices"""
    queryset = MagicMock()
    queryset.exists.return_value = True
    queryset.filter.return_value = queryset
    queryset.__iter__.return_value = [mock_device]
    return queryset

def test_device_report_missing_filters():
    """Test that the script fails if neither site nor rack is provided."""
    script = DeviceReport()
    script.log_failure = MagicMock()

    data = {"status": "active", "site": None, "rack": None}
    result = script.run(data, commit=True)

    script.log_failure.assert_called_once_with("❌ At least one additional filter (Site or Rack) must be selected.")
    assert result == "Error: At least one additional filter (Site or Rack) must be selected."

@patch("scripts.netbox_device_report.Device.objects")
def test_device_report_success(mock_device_model, mock_devices):
    """Test DeviceReport with valid data"""
    mock_device_model.filter.return_value = mock_devices

    script = DeviceReport()
    data = {"status": "active", "site": "Site 1", "rack": None}
    result = script.run(data, commit=True)

    expected_yaml = yaml.dump(
        ["Site Site A (Rack 1): #1 - Device 1"],
        default_flow_style=False, allow_unicode=True
    )
    assert result == expected_yaml

@patch("scripts.netbox_device_report.Device.objects")
def test_device_report_no_devices(mock_device_model, mock_no_device):
    """Test DeviceReport when no devices match the filter"""
    mock_device_model.filter.return_value = mock_no_device

    script = DeviceReport()
    data = {"status": "active", "site": None, "rack": "Rack 2"}
    result = script.run(data, commit=True)

    assert result == "No devices found."
