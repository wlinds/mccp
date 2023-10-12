import json
import os
from platform import system
from threading import Event, Thread
import threading
from typing import List, Optional, Union
import cv2
import numpy as np


class CameraIdentifier:
    def __init__(self, n_cameras: int = 10):
        self.camera_mapping: dict = {}
        self.max_usb_connection: int = n_cameras
        self.init()

    def init(self):
        if os.path.exists("camera_config.json"):
            print(system())
            reconfigure = input(
                "Do you want to reconfigure existing camera config? [Y/N] "
            )
            if reconfigure.lower() != "y" and reconfigure.lower() != "yes":
                print("CameraIdentifier cancelled.")
                return
            else:
                pass
        print("Running CameraIdentifier...")
        self.identify_all_cameras()
        self.save_to_json()

    def identify_all_cameras(self) -> None:
        """
        Allows the user to enter a unique identifier for each camera connected to the computer.
        :raises cv2.error: If the video capture device cannot be opened.
        """

        # Check which cameras are able to open stream TODO: refactor, this is very clunky
        if system() != "Windows":
            for i in range(self.max_usb_connection):
                if not cv2.VideoCapture(i).isOpened():
                    self.max_usb_connection -= 1
        else:
            for i in range(self.max_usb_connection):
                if not cv2.VideoCapture(i, cv2.CAP_DSHOW).isOpened():
                    self.max_usb_connection -= 1

        # Iterate over all accessible cameras
        for i in range(self.max_usb_connection):
            camera_id = None
            cap = (
                cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if system() == "Windows"
                else cv2.VideoCapture(i)
            )

            # User input in thread
            def user_input_thread():
                nonlocal camera_id
                while camera_id is None:
                    camera_id = input(f"Enter camera_id for camera at index {i}: ")

            input_thread = threading.Thread(target=user_input_thread)
            input_thread.start()

            while camera_id is None:
                ret, frame = cap.read()
                cv2.imshow(
                    f"mccp.CameraIdentifier | {cv2.__version__=} camera_{i} ", frame
                )
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()
            input_thread.join()

            if camera_id.lower() == "skip":
                if "skip" in self.camera_mapping:
                    self.camera_mapping["skip"].append(i)
                else:
                    self.camera_mapping["skip"] = [i]
            else:
                self.camera_mapping[camera_id] = i

    def save_to_json(self, filename: str = "camera_config.json") -> None:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["Camera Order"] = self.camera_mapping
        with open(filename, "w") as f:
            json.dump(data, f)
        print("Camera Order saved.")


class CameraConfigurator:
    """
    Utility Class for configuring camera exposure and color temperature.
    Sets exposure and color temperature to 0 and 3000 respectively by default.
    If another value is chosen during the setup it will be saved to all connected cameras.
    """

    def __init__(self, device_id: int = 0) -> None:
        print("Initializing CameraConfigurator...")
        self.captureDevice = cv2.VideoCapture(
            device_id, cv2.CAP_DSHOW
        )  # REFACTOR FOR MAC
        self.device_id = device_id
        self.exposure: int = 0
        self.color_temp: int = 3000
        self.init_camera_settings()

    def init_camera_settings(self) -> None:
        print("Running CameraConfigurator...")
        if system() == "Windows":
            print(system())
            self.captureDevice = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        self.captureDevice.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        self.captureDevice.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.color_temp)
        self.captureDevice.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.captureDevice.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

    def camera_text_overlay(self, frame: np.ndarray) -> None:
        print("Running camera text overlay...")
        font, font_scale = cv2.FONT_HERSHEY_SIMPLEX, 1
        font_color, line_type = (255, 255, 255), 2
        position_exposure = (10, frame.shape[0] - 40)
        position_color_temp = (10, position_exposure[1] - 40)

        cv2.putText(
            frame,
            f"Exposure: {self.exposure}",
            position_exposure,
            font,
            font_scale,
            font_color,
            line_type,
        )

        cv2.putText(
            frame,
            f"Color Temp: {self.color_temp}",
            position_color_temp,
            font,
            font_scale,
            font_color,
            line_type,
        )

    def update_camera_settings(self, key: int) -> None:
        if key == ord("2"):
            self.exposure += 1
            self.captureDevice.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        elif key == ord("1"):
            self.exposure -= 1
            self.captureDevice.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        elif key == ord("5"):
            self.color_temp += 50
            self.captureDevice.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.color_temp)
        elif key == ord("4"):
            self.color_temp -= 50
            self.captureDevice.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.color_temp)

    def save_to_json(self, filename: str = "camera_config.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["CameraSettings"] = {
            "Camera Exposure": self.exposure,
            "Camera Color Temperature": self.color_temp,
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def run(self) -> None:
        print("running again. the actual run function. running run function. ")
        self.captureDevice.open(0, cv2.CAP_DSHOW)  # REFACTOR FOR MAC
        while self.captureDevice.isOpened():
            ret, frame = self.captureDevice.read()
            key = cv2.waitKey(1)

            self.update_camera_settings(key)
            self.camera_text_overlay(frame)

            cv2.imshow(f"mccp.CameraConfigurator | {cv2.__version__=})", frame)

            if key == ord("q"):
                break

        self.captureDevice.release()
        cv2.destroyAllWindows()

    def camera_configurator(self) -> None:
        print("Running CameraConfigurator... FUNCTION")

        with open("camera_config.json", "r") as f:
            data = json.load(f)
            camera_settings = data.get("CameraSettings", {})
        if (
            "Camera Exposure" not in camera_settings
            or "Camera Color Temperature" not in camera_settings
        ):
            print(
                '"Camera Exposure" or "Camera Color Temperature" not found in camera_config.json. Running CameraConfigurator...'
            )

        self.run()
        self.save_to_json()


class Warehouse:
    """
    Class for building a structurized data warehouse for train|test images.
    """

    def __init__(self) -> None:
        self.created_dirs: List[str] = []
        self.created_sub_dirs: List[str] = []
        self.created_nested_sub_dirs: List[str] = []
        self.object_name: str = str()
        self.anomalies: List[str] = []  # Used in camera.py

    def clean_folder_name(self, folder_name: str) -> str:
        folder_name = folder_name.replace(" ", "_")
        return folder_name

    def create_directory(self, path: str) -> None:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                self.created_dirs.append(os.path.basename(path))
        except PermissionError as e:
            print(f"Permission denied while creating {path}: {e}")

    def build(
        self,
        object_name: str = "default2_object",
        anomalies: Optional[List[str]] = ["Default1", "Default2", "Default3"],
    ):
        """
        Build the data warehouse directory structure based on the given object name and anomalies.

        Parameters:
            object_name (str): The name of the object directory.
            anomalies (List[str]): A list of anomaly names for nested subdirectories.
        """
        self.object_name = self.clean_folder_name(str(object_name))
        base_dir_path = os.path.join(os.getcwd(), "data_warehouse")
        dataset_dir_path = os.path.join(base_dir_path, "dataset")
        object_dir_path = os.path.join(dataset_dir_path, self.object_name)

        for path in [base_dir_path, dataset_dir_path]:
            self.create_directory(path)

        self.create_directory(object_dir_path)
        self.anomalies = anomalies  # populates anomalies list for camera.py
        sub_dirs = ["train", "test"]
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + anomalies}

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(object_dir_path, sub_dir)
            self.create_directory(sub_dir_path)

            for nested_sub_dir in nested_sub_dirs.get(sub_dir, []):
                nested_sub_dir = self.clean_folder_name(nested_sub_dir)
                nested_sub_dir_path = os.path.join(sub_dir_path, nested_sub_dir)
                self.create_directory(nested_sub_dir_path)
        print(self)

    def __str__(self) -> str:
        ret = ""
        if self.created_dirs:
            ret += f"Created directories: {', '.join(self.created_dirs)} in {self.object_name} \n"
        if self.created_sub_dirs:
            ret += f"Created subdirectories for object {self.object_name}: {', '.join(self.created_sub_dirs)}"
        if self.created_nested_sub_dirs:
            ret += (
                f"With nested subdirectories: {', '.join(self.created_nested_sub_dirs)}"
            )
        elif not any(
            [self.created_dirs, self.created_sub_dirs, self.created_nested_sub_dirs]
        ):
            ret += (
                f"Directory {self.object_name} already exist! Nothing has been created."
            )
        return ret


if __name__ == "__main__":
    w = Warehouse()
    w.build()
    c = CameraIdentifier()
    conf = CameraConfigurator()
    conf.camera_configurator()
