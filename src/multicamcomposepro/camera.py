import json
import logging
import os
from platform import system
from time import sleep
from typing import List, Optional

import cv2

from .utils import CameraConfigurator, Warehouse, wcap

logging.basicConfig(level=logging.INFO)
os_name = system()


class CameraManager:
    """
    Simultaneous capture train and test images.

    Attributes:
        warehouse (Warehouse): Warehouse object with directory structure.
        test_anomaly_images (int): Number of test anomaly images to capture.
        train_images (int): Number of training images to capture.
        allow_user_input (bool): Whether to allow user input during capture.
        overwrite_original (bool): Whether to overwrite original images.
        captures (List[cv2.VideoCapture]): List of camera capture objects.
        camera_config (List[dict]): Configuration for each camera.
        camera_angles (List[str]): Sorted list of camera angles.

    Raises:
        TODO: Add exceptions.

    Example:
        warehouse = Warehouse()
        camera_manager = CameraManager(warehouse, test_anomaly_images=50, train_images=200)
    """

    def __init__(
        self,
        warehouse: Warehouse,
        test_anomaly_images: int = 5,
        train_images: int = 10,
        allow_user_input: bool = True,
        overwrite_original: bool = True,
    ) -> None:
        self.warehouse: Warehouse = warehouse
        self.test_anomaly_images: int = test_anomaly_images
        self.train_images: int = train_images
        self.allow_user_input: bool = allow_user_input
        self.overwrite_original: bool = overwrite_original
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
        """
        Load camera configuration from a JSON file.

        Args:
            filename (str): The name of the configuration file. Defaults to "camera_config.json".

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
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
            if self.allow_user_input == True:
                input("Press Enter to continue capturing after adjusting the object...")
            else:
                print("Continuing without user input...\nCapturing the object...")
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
            if self.allow_user_input == True:
                input(
                    f"Press Enter to capture TRAINING images for {self.warehouse.object_name} in {folder_type}:"
                )
            else:
                print(
                    f"Continuing without user input...\nCapturing TRAINING images for {self.warehouse.object_name} in {folder_type}:"
                )

            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_multiple_images(good_folder, self.train_images)
            logging.info(f"Captured images for good object in {folder_type} folder.")

        if self.test_anomaly_images != 0:
            folder_type = "test"
            if self.allow_user_input == True:
                input(
                    f"Press Enter to capture images for good object in {folder_type} folder:"
                )
            else:
                print(
                    f"Continuing without user input...\nCapturing images for good object in {folder_type} folder:"
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

        # Use the pre-initialized capture object, else use argument index
        cap = self.captures[cam_idx] if self.captures else wcap(cam_idx)

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

        if self.overwrite_original:
            filename = os.path.join(angle_folder_path, f"{image_counter:03d}.png")
            cv2.imwrite(filename, frame)
            logging.info(f"Saved image {filename}")

        else:
            # Find a filename that does not exist yet
            i = 0
            while True:
                potential_filename = os.path.join(
                    angle_folder_path, f"{image_counter + i:03d}.png"
                )
                if not os.path.exists(potential_filename):
                    cv2.imwrite(potential_filename, frame)
                    logging.info(f"Saved image {potential_filename}")
                    break
                i += 1

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
            if self.allow_user_input == True:
                input(f"Press Enter to capture images for anomaly: {anomaly}")
            else:
                print(
                    f"Continuing without user input...\nCapturing images for anomaly: {anomaly}"
                )
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


class QuickCapture(CameraManager):
    """Instantly capture images from all connected cameras
    Args:
        folder_path (str, optional): Defaults to current working directory.
        folder_name (str, optional): Defaults to "MCCP_QC".
        n_cameras (int, optional): Defaults to 5.
    """

    def __init__(
        self,
        folder_path: Optional[str] = None,
        folder_name: str = "MCCP_QC",
        n_cameras: int = 5,
    ) -> None:
        super().__init__(allow_user_input=False, warehouse=None)

        self.n_cameras = n_cameras
        if folder_path is None:
            self.folder_path = os.getcwd()
        else:
            self.folder_path = folder_path

        self.capture()

    def capture(self) -> None:
        for i in range(self.n_cameras):
            self.capture_single_image(
                folder_path=self.folder_path,
                cam_idx=i,
                angle="MCCP_QC",
                image_counter=1,
                overwrite_original=False,
            )
