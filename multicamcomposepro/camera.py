import cv2
import os
from create_warehouse_directories import WarehouseBuilder
import logging
from platform import system
import json
from camera_identifier import CameraIdentifier


logging.basicConfig(level=logging.INFO)
os_name = system()



class CameraManager:
    def __init__(self, warehouse, num_pics=1):
        self.warehouse = warehouse
        self.num_pics = num_pics
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
        camera_identifier = CameraIdentifier()  # Create an instance
        self.num_cameras = camera_identifier.get_camera_count()

        self.load_camera_mapping()
        self.sort_camera_angles()

    def load_camera_mapping(self, filename="camera_config.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.camera_mapping = data.get("Camera Order", {})
        else:
            print("Camera mapping file not found.") # Change this to a logging statement and create the file if it doesn't exist

    def sort_camera_angles(self):
        if hasattr(self, 'camera_mapping'):
            sorted_angles = [None] * len(self.camera_angles)
            for identifier, index in self.camera_mapping.items():
                if identifier == 'skip':
                    if isinstance(index, list):
                        for i in index:
                            sorted_angles[i] = 'skip'
                    else:
                        sorted_angles[index] = 'skip'
                else:
                    sorted_angles[index] = self.camera_angles[int(identifier)]
            self.camera_angles = sorted_angles
            print("Sorted Camera Angles:", self.camera_angles)  # Debugging line






    def capture_images(self, folder_path):
        image_counter = 0
        for _ in range(self.num_pics):
            for cam_idx, angle in enumerate(self.camera_angles):
                
                self.capture_single_image(folder_path, cam_idx, angle, image_counter)
            image_counter += 1

    def capture_good_object(self):
        base_dir = os.path.join(os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name)
        for folder_type in ["test", "train"]:
            input(
                f"Press Enter to capture images for good object in {folder_type} folder:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_images(good_folder)
            logging.info(f"Captured images for good object in {folder_type} folder.")

    def capture_single_image(self, folder_path, cam_idx, angle, image_counter):
        if angle is None or angle == "skip":
            logging.warning(f"Skipping camera {cam_idx} as angle is {angle}.")
            return
        angle_folder_path = os.path.join(folder_path, angle)
        os.makedirs(angle_folder_path, exist_ok=True)

        cap = (
            cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
            if os_name == "Windows"
            else cv2.VideoCapture(cam_idx)
        )

        ret, frame = cap.read()
        cap.release()

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

        self.capture_good_object()
        base_dir = os.path.join(os.getcwd(), "data_warehouse", "dataset", self.warehouse.object_name)
        for anomaly in self.warehouse.anomalies:
            input(f"Press Enter to capture images for anomaly: {anomaly}")
            anomaly_folder = os.path.join(base_dir, "test", anomaly)
            self.capture_images(anomaly_folder)
            logging.info(f"Captured images for anomaly: {anomaly}")


if __name__ == "__main__":
    warehouse = WarehouseBuilder()
    warehouse.build("angle_index_test", ["angles_test"])
    camera_manager = CameraManager(warehouse)
    camera_manager.run()
