import json
import logging
import os
from platform import system
from time import sleep
from typing import List

import cv2
from utils import CameraConfigurator, Warehouse, wcap

logging.basicConfig(level=logging.INFO)
os_name = system()


class CameraManager:
    """
    Simultaneous capture train and test images.

    :param warehouse: Warehouse object with directory structure.
    :param test_anomaly_images: Number of test anomaly images to capture.
    :param train_images: Number of training images to capture.

    :raises: TODO Add exceptions.

    Example:
        warehouse = Warehouse()
        camera_manager = CameraManager(warehouse, test_anomaly_images=50, train_images=200)
    """

    def __init__(
        self, warehouse: Warehouse, test_anomaly_images: int = 5, train_images: int = 10
    ) -> None:
        self.warehouse: Warehouse = warehouse
        self.test_anomaly_images: int = test_anomaly_images
        self.train_images: int = train_images
        self.captures: List = []
        self.load_camera_config()
        self.sort_camera_angles()

    def initialize_cameras(self) -> None:
        self.captures = []
        for camera in self.camera_config:
            cam_idx = camera["Camera"]
            print(f"Camera {cam_idx} initializing...")
            cap = wcap(cam_idx)
            if isinstance(
                camera["Resolution"], str
            ):  # if the resolution is a string with format "width x height"
                cap.set(
                    cv2.CAP_PROP_FRAME_WIDTH, int(camera["Resolution"].split(" x ")[0])
                )
                cap.set(
                    cv2.CAP_PROP_FRAME_HEIGHT, int(camera["Resolution"].split(" x ")[1])
                )
            else:  # if the resolution is a touple / list with format [width, height]
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera["Resolution"][0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera["Resolution"][1])
            cap.set(cv2.CAP_PROP_EXPOSURE, camera["Camera Exposure"])
            cap.set(
                cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, camera["Camera Color Temperature"]
            )
            self.captures.append(cap)

    def load_camera_config(self, filename: str = "camera_config.json") -> None:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.camera_config = json.load(f)
        else:
            logging.warning(f"{filename} not found! Using default camera settings.")

    def sort_camera_angles(self) -> None:
        self.camera_angles = [camera["Angle"] for camera in self.camera_config]
        print("Debug: Sorted Camera Angles:", self.camera_angles)

    def __del__(self) -> None:
        for cap in self.captures:
            cap.release()

    def capture_multiple_images(
        self, folder_path: str, num_pictures_to_take: int
    ) -> None:
        """
        Capture multiple images from different cameras and angles.

        This method captures a specified number of images from various camera angles and saves them in the given folder.

        :param folder_path: Directory where the captured images will be saved.
        :param num_pictures_to_take: Number of pictures to capture.

        :raises SomeException: If capturing fails.

        Example:
            capture_multiple_images("/path/to/save", 5)
        """
        if num_pictures_to_take == 0:
            logging.info("Skipping capture due to test_anomaly_images set to 0.")
            return

        image_counter = 0
        for _ in range(num_pictures_to_take):
            # Pause here to allow for object adjustment
            input("Press Enter to continue capturing after adjusting the object...")
            for cam_idx, angle in enumerate(self.camera_angles):
                self.capture_single_image(folder_path, cam_idx, angle, image_counter)
            image_counter += 1

    def capture_training_and_test_images(self) -> None:
        """
        Capture both training and test images for good objects.

        This method captures both training and test images for good objects. It prompts the user to adjust the object before capturing.

        :raises: TODO Add exceptions.

        Example:
            capture_good_object()
        """
        base_dir = os.path.join(
            os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name
        )

        if self.train_images != 0:
            folder_type = "train"
            input(
                f"Press Enter to capture TRAINING images for {self.warehouse.object_name} in {folder_type}:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_multiple_images(good_folder, self.train_images)
            logging.info(f"Captured images for good object in {folder_type} folder.")

        if self.test_anomaly_images != 0:
            folder_type = "test"
            input(
                f"Press Enter to capture images for good object in {folder_type} folder:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_multiple_images(good_folder, self.test_anomaly_images)
            logging.info(f"Captured images for good object in {folder_type} folder.")

    def capture_single_image(
        self, folder_path: str, cam_idx: int, angle: str, image_counter: int
    ) -> None:
        """
        Capture a single image from a specific camera angle.

        This method captures a single image from a specific camera angle and saves it in the given folder.
        Its main purpose is to be used within the capture_multiple_images() method but can be called directly if needed.

        :param folder_path: Directory where the captured image will be saved.
        :param cam_idx: Index of the camera to use for capturing.
        :param angle: Camera angle for capturing.
        :param image_counter: Counter for the image to be captured.

        :raises: TODO Add exceptions.

        Example:
            capture_single_image("/path/to/save", 0, "cam_0_left", 0)
        """
        if angle is None or angle == "skip":
            return

        angle_folder_path = os.path.join(folder_path, angle)
        os.makedirs(angle_folder_path, exist_ok=True)

        # Use the pre-initialized capture object
        cap = self.captures[cam_idx]

        # Flush the buffer
        for _ in range(2):
            ret, _ = cap.read()
            if not ret:
                logging.error(
                    f"Could not read frame from camera {cam_idx} at angle {angle}."
                )
                return

        # Capture the actual frame
        ret, frame = cap.read()
        if not ret:
            logging.error(
                f"Could not read frame from camera {cam_idx} at angle {angle}."
            )
            return

        filename = os.path.join(angle_folder_path, f"{image_counter:03d}.png")
        cv2.imwrite(filename, frame)
        logging.info(f"Saved image {filename}")

    def run(self) -> None:
        """
        This method is the main function to run the camera capturing process. It prompts the user to adjust the object before capturing.

        :raises: TODO Add exceptions.

        """
        print(self.warehouse.anomalies)

        self.initialize_cameras()
        self.capture_training_and_test_images()
        base_dir = os.path.join(
            os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name
        )
        for anomaly in self.warehouse.anomalies:
            input(f"Press Enter to capture images for anomaly: {anomaly}")
            cleaned_anomaly = self.warehouse.clean_folder_name(
                anomaly
            )  # Clean the anomaly name
            anomaly_folder = os.path.join(
                base_dir, "test", cleaned_anomaly
            )  # Use the cleaned name
            self.capture_multiple_images(anomaly_folder, self.test_anomaly_images)
            logging.info(f"Captured images for anomaly: {anomaly}")

        print("Done.")


if __name__ == "__main__":
    warehouse = Warehouse()
    warehouse.build("train_image_test", ["anomaly_1", "anomaly_2"])

    CameraConfigurator()
    camera_manager = CameraManager(warehouse, test_anomaly_images=5, train_images=10)
    camera_manager.run()
