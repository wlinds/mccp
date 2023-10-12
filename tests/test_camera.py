# To run manually
# Unix systems: run from root with python3 -m tests.test_camera
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
    mock_json_load.return_value = {
        "CameraSettings": {"Camera Exposure": 1, "Camera Color Temperature": 2},
        "Camera Order": {"0": 0, "1": 1},
    }
    camera_manager.load_camera_config()
    assert camera_manager.exposure == 1
    assert camera_manager.color_temp == 2
    assert camera_manager.num_cameras == 2


# Test 3: Test Camera Angle Sorting
def test_sort_camera_angles(camera_manager):
    camera_manager.camera_angles = [
        "cam_0_left",
        "cam_1_right",
    ]
    camera_manager.camera_mapping = {"0": 0, "1": 1}
    camera_manager.sort_camera_angles()
    assert camera_manager.camera_angles[0] == "cam_0_left"
