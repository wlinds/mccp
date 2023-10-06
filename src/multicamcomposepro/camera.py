import json
import logging
import os
from platform import system

import cv2
from utils import Warehouse

logging.basicConfig(level=logging.INFO)
os_name = system()


class CameraManager:
    def __init__(self, warehouse, test_anomaly_images: int = 5, train_images: int = 10):
        self.warehouse = warehouse
        self.test_anomaly_images = test_anomaly_images
        self.train_images = train_images
        self.load_camera_config()
        self.load_camera_mapping()
        self.camera_angles = [
            "cam_0_left",
            "cam_1_right",
            "cam_2_front",
            "cam_3_front_left",
            "cam_4_front_right",
            "cam_5_back",
            "cam_6_back_left",
            "cam_7_back_right",
            "cam_8_top",
            "cam_9_top_left",
            "cam_10_top_right",
        ]
        self.sort_camera_angles()

        # Initialize cameras
    def initialize_cameras(self):
        self.captures = []
        for cam_idx in range(self.num_cameras):
            print("image capture", cam_idx)
            cap = (
                cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
                if os_name == "Windows"
                else cv2.VideoCapture(cam_idx)
            )
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
            cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
            cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.color_temp)
            cap.set(cv2.CAP_PROP_ZOOM, self.zoom)
            self.captures.append(cap)

    def __del__(self):
        for cap in self.captures:
            cap.release()

    def load_camera_config(self, filename="camera_config.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                camera_settings = data.get("CameraSettings", {})
                self.exposure = camera_settings.get("Camera Exposure", 0)
                self.color_temp = camera_settings.get("Camera Color Temperature", 0)
                self.zoom = camera_settings.get("Camera Zoom", 0)
                self.num_cameras = len(data.get("Camera Order", {}))
        else:
            logging.warning(f"{filename} not found! Using default camera settings.")

    def load_camera_mapping(self, filename="camera_config.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.camera_mapping = data.get("Camera Order", {})
        else:
            logging.warning(
                "camera_config.json not found! Please run camera_identifier.py first."
            )

    def sort_camera_angles(self):
        if hasattr(self, "camera_mapping"):
            sorted_angles = [None] * len(self.camera_angles)
            for identifier, index in self.camera_mapping.items():
                if identifier == "skip":
                    if isinstance(index, list):
                        for i in index:
                            sorted_angles[i] = "skip"
                    else:
                        sorted_angles[index] = "skip"
                else:
                    sorted_angles[index] = self.camera_angles[int(identifier)]
            self.camera_angles = sorted_angles
            print("Sorted Camera Angles:", self.camera_angles)  # Debugging line

    def capture_images(self, folder_path, num_pictures_to_take):
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


    def capture_good_object(self):
        base_dir = os.path.join(
            os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name
        )

        if self.train_images != 0:
            folder_type = "train"
            input(
                f"Press Enter to capture TRAINING images for {self.warehouse.object_name} in {folder_type}:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_images(good_folder, self.train_images)
            logging.info(f"Captured images for good object in {folder_type} folder.")

        if self.test_anomaly_images != 0:
            folder_type = "test"
            input(
                f"Press Enter to capture images for good object in {folder_type} folder:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_images(good_folder, self.test_anomaly_images)
            logging.info(f"Captured images for good object in {folder_type} folder.")

    def capture_single_image(self, folder_path, cam_idx, angle, image_counter):
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


    def run(self):
        print(self.warehouse.anomalies)

        self.initialize_cameras()
        self.capture_good_object()
        base_dir = os.path.join(
            os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name
        )
        if self.test_anomaly_images != 0:
            for anomaly in self.warehouse.anomalies:
                input(f"Press Enter to capture images for anomaly: {anomaly}")
                anomaly_folder = os.path.join(base_dir, "test", anomaly)
                self.capture_images(anomaly_folder, self.test_anomaly_images)
                logging.info(f"Captured images for anomaly: {anomaly}")


if __name__ == "__main__":
    warehouse = Warehouse()
    warehouse.build("train_image_test", ["anomaly_1", "anomaly_2"])
    camera_manager = CameraManager(warehouse, test_anomaly_images=5, train_images=10)
    camera_manager.run()
