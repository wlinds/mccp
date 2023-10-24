# To manually test, run from root with python3 -m pytest tests/test_warehouse.py
# For Windows: $ python -m pytest tests/test_warehouse.py
from unittest.mock import patch

import pytest

from src.multicamcomposepro.utils import Warehouse


@pytest.fixture
def warehouse():
    return Warehouse()


def test_clean_folder_name(warehouse):
    assert warehouse.clean_folder_name("my folder") == "my_folder"


@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
def test_create_directory(mock_exists, mock_makedirs, warehouse):
    warehouse.create_directory("test_path")
    mock_exists.assert_called_once_with("test_path")
    mock_makedirs.assert_called_once_with("test_path")


@patch("os.makedirs")
@patch("os.path.exists", return_value=True)
def test_create_directory_already_exists(mock_exists, mock_makedirs, warehouse):
    warehouse.create_directory("test_path")
    mock_exists.assert_called_once_with("test_path")
    mock_makedirs.assert_not_called()


def test_build(warehouse):
    with patch("os.getcwd", return_value="/test_path"), patch(
        "os.makedirs"
    ) as mock_makedirs:
        warehouse.build("test_object", ["test_anomaly_1", "test_anomaly_2"])
        assert len(mock_makedirs.call_args_list) == 9
