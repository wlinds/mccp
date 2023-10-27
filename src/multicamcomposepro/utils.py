import json
import os
import threading
from platform import system
from typing import List, Optional, Union

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm


def view_camera(camera_index=0):
    cap = wcap(camera_index)
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


# Use CAP_DSHOW on Windows
def wcap(i=None):
    if system() != "Windows":
        return cv2.VideoCapture(i)
    else:
        return cv2.VideoCapture(i, cv2.CAP_DSHOW)


VALID_ANGLES = [
    "Left",
    "Right",
    "Front",
    "Back",
    "Top",
    "Bottom",
    "Front-Left",
    "Front-Right",
    "Back-Left",
    "Back-Right",
]
VALID_RESOLUTIONS = ["400 x 400", "640 x 480", "800 x 640", "800 x 800"]


class CameraConfigurator:
    def __init__(self, n_cameras: int = 10):
        self.max_usb_connection: int = n_cameras
        self.camera_mapping: dict = {}
        self.camera_settings: dict = {}
        self.init()

    def init(self):
        if os.path.exists("camera_config.json"):
            reconfigure = input(
                "Do you want to reconfigure existing camera config? [Y/N] "
            )
            if reconfigure.lower() not in ["y", "yes"]:
                print("CameraManager cancelled.")
                return
        print("Running CameraManager...")
        self.identify_and_configure_all_cameras()
        self.save_to_json()

    def identify_and_configure_all_cameras(self) -> None:
        # Iterate over all accessible cameras
        for i in range(self.max_usb_connection):
            cap = wcap(i)  # Create a new capture object for each camera
            if not cap.isOpened():
                continue

            # Display the camera stream
            while True:
                ret, frame = cap.read()
                cv2.imshow(f"mccp.CameraManager | camera_{i}", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

            # Close the camera stream display
            cap.release()
            cv2.destroyAllWindows()

            # Ask the user for the angle or to skip
            print("Available angles:", ", ".join(VALID_ANGLES))
            camera_angle = input(
                f"Enter camera angle (or 'skip') for camera at index {i}: "
            )

            if camera_angle.lower() == "skip":
                continue
            elif camera_angle not in VALID_ANGLES:
                print(f"Invalid angle '{camera_angle}'! Skipping this camera.")
                continue

            # Ask for exposure and color temperature
            exposure = int(
                input(f"Enter exposure (default 0) for camera at index {i}: ") or 0
            )
            color_temp = int(
                input(
                    f"Enter color temperature (default 3000) for camera at index {i}: "
                )
                or 3000
            )

            # Ask for resolution
            print("Available resolutions:", ", ".join(VALID_RESOLUTIONS))
            resolution = input(
                f"Enter resolution (or 'default') for camera at index {i}: "
            )
            if resolution.lower() == "default" or resolution not in VALID_RESOLUTIONS:
                resolution = "400 x 400"  # default value

            # Store the settings
            self.camera_settings[i] = {
                "Angle": camera_angle,
                "Resolution": resolution,
                "Camera Exposure": exposure,
                "Camera Color Temperature": color_temp,
            }

    def save_to_json(self, filename: str = "camera_config.json") -> None:
        data = []
        for cam_idx, settings in self.camera_settings.items():
            data.append(
                {
                    "Camera": cam_idx,
                    "Resolution": settings["Resolution"],
                    "Angle": settings["Angle"],
                    "Camera Exposure": settings["Camera Exposure"],
                    "Camera Color Temperature": settings["Camera Color Temperature"],
                    "Mask": 0,  # default value; modify as necessary
                }
            )
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print("Camera settings saved.")


if __name__ == "__main__":
    cc = CameraConfigurator()


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

    def build(
        self,
        object_name: str = "default2_object",
        anomalies: Optional[List[str]] = ["Anomaly1", "Anomaly2", "Anomaly3"],
    ):
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

        nested_sub_dirs = {
            "train": ["good"],
            "test": ["good"] + self.anomalies,
        }  # Define this within the method

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
