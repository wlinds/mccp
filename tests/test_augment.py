# To test manually:
# Unix systems: run from root with python3 -m tests.test_augment
# For Windows: $ python -m pytest tests/test_augment.py

import logging
from unittest.mock import Mock, mock_open, patch

import cv2
import numpy as np
import pytest
import os

from src.multicamcomposepro.augment import DataAugmenter


@pytest.fixture
def mock_logging():
    return Mock(spec=logging)


@pytest.fixture
def data_augmenter(mock_logging):
    return DataAugmenter(logging_enabled=False)


# Test 1: Test Initialization
def test_initialization(data_augmenter):
    assert data_augmenter.num_augmented_images == 3
    assert data_augmenter.temperature == 1.0
    assert data_augmenter.logging_enabled == False


# Test 2: Test Process Image
@patch("cv2.imread")
@patch("cv2.imwrite")
def test_process_image(mock_imwrite, mock_imread, data_augmenter):
    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_imread.return_value = mock_img
    data_augmenter.process_image(mock_img, "test.png", "./")
    assert mock_imwrite.called


# Test 3: Test Augment Images
@patch("cv2.imread")
@patch("os.listdir")
@patch("os.path.isdir")
def test_augment_images(mock_isdir, mock_listdir, mock_imread, data_augmenter):
    mock_listdir.return_value = ["image1.png", "image2.png"]
    mock_isdir.return_value = True
    mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
    data_augmenter.augment_images()
    assert mock_listdir.called


# Test 4: Test Random White Balance
@patch("cv2.split")
@patch("cv2.merge")
def test_random_white_balance(mock_merge, mock_split, data_augmenter):
    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_split.return_value = [mock_img[:, :, 0], mock_img[:, :, 1], mock_img[:, :, 2]]
    img, factor_str = data_augmenter.random_white_balance(mock_img)
    assert mock_split.called
    assert mock_merge.called
    assert "R:" in factor_str


# Test 5: Test Different Image Sizes
def test_image_sizes(data_augmenter):
    # Mocking cv2.imread to return images of different sizes
    sizes = [(480, 480), (640, 640), (1080, 1920)]
    mock_images = [np.zeros(size + (3,), dtype=np.uint8) for size in sizes]

    with patch("cv2.imread") as mock_imread, patch("cv2.imwrite") as mock_imwrite:
        for i, mock_img in enumerate(mock_images):
            print("Mock image shape:", mock_img.shape)

            mock_imread.return_value = mock_img

            # Call the method you want to test
            data_augmenter.process_image(mock_img, f"test_{i}.png", "./")

            # Validate the behavior
            assert data_augmenter.resolution == mock_img.shape[:2]

            # Assert that cv2.imwrite was called (optional)
            mock_imwrite.assert_called()
