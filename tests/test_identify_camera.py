from unittest.mock import Mock, patch

import pytest

from src.multicamcomposepro.utils import CameraIdentifier


@pytest.fixture
def camera_identifier():
    return CameraIdentifier()


def test_init(camera_identifier):
    assert isinstance(camera_identifier.camera_mapping, dict)
    assert isinstance(camera_identifier.os_name, str)
    assert camera_identifier.max_tested == 10


@patch("src.multicamcomposepro.utils.cv2.VideoCapture")
def test_get_camera_count(MockVideoCapture, camera_identifier):
    mock_cap = Mock()
    mock_cap.isOpened.return_value = False
    MockVideoCapture.return_value = mock_cap

    result = camera_identifier.get_camera_count()
    assert result == 0


@patch("src.multicamcomposepro.utils.json.dump")
@patch("src.multicamcomposepro.utils.json.load")
@patch("src.multicamcomposepro.utils.open")
def test_save_to_json(mock_open, mock_json_load, mock_json_dump, camera_identifier):
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_json_load.return_value = {}

    camera_identifier.save_to_json()
    mock_json_dump.assert_called()
