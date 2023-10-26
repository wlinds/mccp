import json
import os
from platform import system
import threading
from typing import List, Optional, Union

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

def test_camera(i=0):
    cap = wcap(i)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 12)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 7)
    while True:
        ret, frame = cap.read()
        cv2.imshow(f"mccp.test_camera | {cv2.__version__=} camera_{i} ", frame)
        key = cv2.waitKey(1) & 0xFF
        print(frame)
        if key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
VALID_ANGLES = ["Left", "Right", "Front", "Back", "Top", "Bottom", "Front-Left", "Front-Right", "Back-Left", "Back-Right"]
# Use CAP_DSHOW on Windows
def wcap(i=None):
    if system() != "Windows":
        return cv2.VideoCapture(i)
    else:
        return cv2.VideoCapture(i, cv2.CAP_DSHOW)

class CameraIdentifier:
    """
    Opens Cameras one by one and asks the user to identify them.
    Saves camera order with unique identifiers to camera_config.json.
    Order is used in CameraManager to display the camera streams in the correct order.
    """

    def __init__(self, n_cameras: int = 10):
        """
        Initialize CameraIdentifier object.

        :ivar camera_mapping: A dictionary containing the camera order with unique identifiers.

        You can change max_tested value to increase/decrease the number of cameras that can be connected to the computer.
        """
        self.camera_mapping: dict = {}
        self.max_usb_connection: int = n_cameras
        self.init()

    def init(self):
        if os.path.exists("camera_config.json"):
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
        angle_idx = 0
        """
        Allows the user to enter a unique identifier for each camera connected to the computer.
        :raises cv2.error: If the video capture device cannot be opened.
        """

        # Check all connectiond to find all camera streams
        for i in range(self.max_usb_connection):
            camera_id = None
            if not wcap(i).isOpened():
                self.max_usb_connection -= 1
            if angle_idx < len(VALID_ANGLES):
                angle = VALID_ANGLES[angle_idx]
                self.camera_mapping[angle] = i
                angle_idx += 1
            else:
                print("Warning: More cameras than valid angles provided. Some angles might be duplicated.")
                angle = VALID_ANGLES[angle_idx % len(VALID_ANGLES)]
                self.camera_mapping[angle] = i
                angle_idx += 1

        # Iterate over all accessible cameras, create threads for inputs
        for i in range(self.max_usb_connection):
            camera_id = None
            cap = wcap(i)

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
        data = []
        for camera_id, cam_idx in self.camera_mapping.items():
            if camera_id != "skip":
                data.append({
                    "Camera": cam_idx,
                    "Resolution": "1920 x 1440",  # default value; modify as necessary
                    "Angle": camera_id,
                    "Camera Exposure": 0,  # default value; modify as necessary
                    "Camera Color Temperature": 3000,  # default value
                    "Mask": 0  # default value; modify as necessary
                })
        with open(filename, "w") as f:
            json.dump(data, f)
        print("Camera Order saved.")
    


# Camera Configurator #


class CameraConfigurator:
    """
    Utility Class for configuring camera exposure and color temperature.
    Sets exposure and color temperature to 0 and 3000 respectively by default.
    If another value is chosen during the setup it will be saved to all connected cameras.
    """

    def __init__(self, device_id: int = 0) -> None:
        self.captureDevice = wcap(device_id)
        self.device_id = device_id
        self.exposure: int = 0
        self.color_temp: int = 3000
        self.init_camera_settings()

    def init_camera_settings(self) -> None:
        self.captureDevice.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        self.captureDevice.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.color_temp)
        self.captureDevice.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.captureDevice.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

    def camera_text_overlay(self, frame: np.ndarray) -> None:
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
        data = []
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        for entry in data:
            if entry["Camera"] == self.device_id:
                entry["Camera Exposure"] = self.exposure
                entry["Camera Color Temperature"] = self.color_temp
                break
        else:
            # Append new camera entry if not found
            data.append({
                "Camera": self.device_id,
                "Resolution": "1920 x 1440",  # default value; modify as necessary
                "Angle": "Unknown",  # default value; modify as necessary
                "Camera Exposure": self.exposure,
                "Camera Color Temperature": self.color_temp,
                "Mask": 0  # default value; modify as necessary
            })

        with open(filename, "w") as f:
            json.dump(data, f)

    def run(self, path="camera_config.json") -> None:
        if not os.path.exists(path):
            print(f"{path} not found. Try running CameraIdentifier first or ", end="")
            new_path = input("enter path for camera_config.json: ")
            self.run(path=new_path)
            return

        with open(path, "r") as f:
            data = json.load(f)

        # Find the current camera's settings in the list
        current_camera_settings = next((cam for cam in data if cam["Camera"] == self.device_id), None)

        if current_camera_settings:
            self.exposure = current_camera_settings["Camera Exposure"]
            self.color_temp = current_camera_settings["Camera Color Temperature"]
        else:
            print("Settings for the current camera not found. Using defaults.")

        print(f"Keybind Adjusts:\n\nExposure keys: [1/2]\nColor temp keys: [4/5]\nContinue: Q")
        while self.captureDevice.isOpened():
            ret, frame = self.captureDevice.read()
            key = cv2.waitKey(1)

            self.update_camera_settings(key)
            self.camera_text_overlay(frame)

            cv2.imshow(f"mccp.CameraConfigurator | {cv2.__version__=}) ", frame)

            if key == ord("q"):
                break

        self.captureDevice.release()
        cv2.destroyAllWindows()
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
        cleaned_name = folder_name.replace(" ", "_")
        return cleaned_name

    def create_directory(self, path: str) -> None:
        """
        Create a directory at the given path and add its name to the created_dirs list.

        Parameters:
            path (str): The path where the directory should be created.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                self.created_dirs.append(os.path.basename(path))
            except Exception as e:
                print(f"An error occurred while creating {path}: {e}")

    def build(self, object_name: str = "default2_object", anomalies: Optional[List[str]] = ["Anomaly1", "Anomaly2", "Anomaly3"]):
        self.object_name = self.clean_folder_name(object_name)
        base_dir_path = os.path.join(os.getcwd(), "data_warehouse")
        dataset_dir_path = os.path.join(base_dir_path, "dataset")
        object_dir_path = os.path.join(dataset_dir_path, self.object_name)

        for path in [base_dir_path, dataset_dir_path, object_dir_path]:
            self.create_directory(path)

        self.anomalies = anomalies
        sub_dirs = ["test", "train"]  # Changed the order to have 'test' first
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + anomalies}

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(object_dir_path, sub_dir)
            self.create_directory(sub_dir_path)
            if sub_dir not in self.created_sub_dirs:
                self.created_sub_dirs.append(sub_dir)

            for nested_sub_dir in nested_sub_dirs[sub_dir]:
                nested_sub_dir = self.clean_folder_name(nested_sub_dir)
                nested_sub_dir_path = os.path.join(sub_dir_path, nested_sub_dir)
                self.create_directory(nested_sub_dir_path)
                if nested_sub_dir not in self.created_nested_sub_dirs:
                    self.created_nested_sub_dirs.append(nested_sub_dir)

    def __str__(self) -> str:
        ret = self.object_name + "\n"
        
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + self.anomalies}  # Define this within the method
        
        for i, sub_dir in enumerate(self.created_sub_dirs):
            prefix = " ┗" if i == len(self.created_sub_dirs) - 1 else " ┣"
            ret += f"{prefix} {sub_dir}\n"
            
            nested_dirs = nested_sub_dirs[sub_dir]
            for j, nested_sub_directory in enumerate(nested_dirs):
                nested_prefix = " ┃ ┗" if j == len(nested_dirs) - 1 else " ┃ ┣"
                ret += f"{nested_prefix} {nested_sub_directory}\n"

        return ret


def allowed_file(filename, allowed_extensions=("png", "jpg", "jpeg")):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def batch_resize(
    root_input_dir, root_output_dir, target_size=(224, 224), overwrite_original=False
):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root_input_dir):
        relative_dir = os.path.relpath(dirpath, root_input_dir)

        if not any(allowed_file(filename) for filename in filenames):
            continue

        output_subdir = os.path.join(root_output_dir, relative_dir)
        os.makedirs(output_subdir, exist_ok=True)

        for filename in tqdm(filenames, desc=f"Processing image"):
            if not allowed_file(filename):
                tqdm.write(f"File type not allowed for {filename}")
                continue

            input_path = os.path.join(dirpath, filename)
            output_path = os.path.join(output_subdir, filename)

            if os.path.exists(output_path) and not overwrite_original:
                tqdm.write(
                    f"Skipping {filename} as it already exists in the output directory."
                )
                continue

            # Crop horizontally if crop size ratio mismatch #TODO crop vertical maybe
            with Image.open(input_path) as img:
                width, height = img.size
                if width > height:
                    left = (width - height) // 2
                    right = width - left
                    img = img.crop((left, 0, right, height))
                elif height > width:
                    upper = (height - width) // 2
                    lower = height - upper
                    img = img.crop((0, upper, width, lower))
                img_resized = img.resize(target_size)
                img_resized.save(output_path)

            if overwrite_original:
                os.remove(input_path)

            n += 1

    print(f"Finished resize of {n} images with new resolution: {target_size}")

if __name__ == "__main__":
    w = Warehouse()
    w.build("Object", ["Anomaly1", "Anomaly2", "Anomaly3"])
    print(w)