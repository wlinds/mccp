import cv2
import os
from create_warehouse_directories import WarehouseBuilder
import logging
import platform

logging.basicConfig(level=logging.INFO)
os_name = platform.system()

class CameraManager:
    def __init__(self, warehouse, num_pics=1, num_cameras=6):
        self.warehouse = warehouse
        self.num_pics = num_pics
        self.num_cameras = num_cameras
        self.camera_angles = [
            "skip",
            "left",
            "right",
            "front",
            "front_left",
            "front_right",
        ]

    def capture_images(self, folder_path):
        image_counter = 0
        for _ in range(self.num_pics):
            for cam_idx, angle in enumerate(self.camera_angles):
                if (os_name == "Windows" and cam_idx == 0) or (
                    os_name != "Windows" and cam_idx == 1
                ):  # Trash code. Delete after testing.
                    continue
                
                self.capture_single_image(folder_path, cam_idx, angle, image_counter)
            image_counter += 1

    def capture_good_object(self):
        base_dir = os.path.join(os.getcwd(), "data_warehouse", "dataset", "object_name")
        for folder_type in ["test", "train"]:
            input(
                f"Press Enter to capture images for good object in {folder_type} folder:"
            )
            good_folder = os.path.join(base_dir, folder_type, "good")
            self.capture_images(good_folder)
            logging.info(f"Captured images for good object in {folder_type} folder.")

    def capture_single_image(self, folder_path, cam_idx, angle, image_counter):
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
        self.capture_good_object()
        base_dir = os.path.join(os.getcwd(), "data_warehouse", "dataset", "object_name")
        for anomaly in self.warehouse.anomalies:
            input(f"Press Enter to capture images for anomaly: {anomaly}")
            anomaly_folder = os.path.join(base_dir, "test", anomaly)
            self.capture_images(anomaly_folder)
            logging.info(f"Captured images for anomaly: {anomaly}")


if __name__ == "__main__":
    warehouse = WarehouseBuilder()
    warehouse.build("object_name", ["anomaly1", "anomaly2"])
    camera_manager = CameraManager(warehouse)
    camera_manager.run()
