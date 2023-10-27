# To run manually
# Unix systems: run from root with python3 -m pytest tests/test_camera.py
# For Windows: $ python -m pytest tests/test_camera.py

from unittest.mock import Mock, mock_open, patch

import pytest

from src.multicamcomposepro.camera import CameraManager
from src.multicamcomposepro.utils import Warehouse


@pytest.fixture
def mock_warehouse():
    return Mock(spec=Warehouse)


@pytest.fixture
def camera_manager(mock_warehouse):
    return CameraManager(mock_warehouse)


# Test 1: Test Initialization
def test_initialization(camera_manager, mock_warehouse):
    assert camera_manager.warehouse == mock_warehouse
    assert camera_manager.test_anomaly_images == 5
    assert camera_manager.train_images == 10


# Test 2: Test Camera Configuration Loading
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="{}")
@patch("json.load")
def test_load_camera_config(
    mock_json_load, mock_file_open, mock_exists, camera_manager
):
    mock_json_load.return_value = [
        {
            "Camera": 2,
            "Resolution": "400 x 400",
            "Angle": "Right",
            "Camera Exposure": -5,
            "Camera Color Temperature": 3500,
            "Mask": 0,
        }
    ]
    camera_manager.load_camera_config()
    assert camera_manager.camera_config[0]["Camera Exposure"] == -5
    assert camera_manager.camera_config[0]["Camera Color Temperature"] == 3500
