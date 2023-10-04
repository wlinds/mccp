import cv2
import os
from typing import List
import json
from platform import system
import threading


# Camera #


def camera_text_overlay(frame, camera_name):
    font = cv2.FONT_HERSHEY_SIMPLEX
    position = (10, frame.shape[0] - 10)  # Bottom-left corner frame for each cam stream
    font_scale = 0.5
    font_color = (255, 255, 255)
    line_type = 2
    cv2.putText(frame, camera_name, position, font, font_scale, font_color, line_type)


# File structures #


class Warehouse:
    """
    Class for building a structurized data warehouse for train|test images.
    """

    def __init__(self):
        self.created_dirs = []
        self.created_sub_dirs = []
        self.created_nested_sub_dirs = []
        self.object_name = str()
        self.anomalies = []  # Used in camera.py

    def clean_folder_name(self, folder_name: str):
        cleaned_name = folder_name.replace(" ", "_")
        return cleaned_name

    def create_directory(self, path: str):
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
        self, object_name, anomalies: List[str] = ["Default1", "Default2", "Default3"]
    ):
        """
        Build the data warehouse directory structure based on the given object name and anomalies.

        Parameters:
            object_name (str): The name of the object directory.
            anomalies (List[str]): A list of anomaly names for nested subdirectories.
        """
        self.object_name = self.clean_folder_name(object_name)
        base_dir_path = os.path.join(os.getcwd(), "data_warehouse")
        dataset_dir_path = os.path.join(base_dir_path, "dataset")
        object_dir_path = os.path.join(dataset_dir_path, self.object_name)

        for path in [base_dir_path, dataset_dir_path]:
            self.create_directory(path)

        self.create_directory(object_dir_path)

        self.anomalies = (
            anomalies  # populates the anomalies list so that camera.py can use it
        )
        sub_dirs = ["train", "test"]
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + anomalies}

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(object_dir_path, sub_dir)
            self.create_directory(sub_dir_path)

            for nested_sub_dir in nested_sub_dirs.get(sub_dir, []):
                nested_sub_dir = self.clean_folder_name(nested_sub_dir)
                nested_sub_dir_path = os.path.join(sub_dir_path, nested_sub_dir)
                self.create_directory(nested_sub_dir_path)

    def __str__(self):
        ret = ""
        if self.created_dirs:
            ret += f"Created the following directories: {', '.join(self.created_dirs)} in {self.object_name} \n"
        if self.created_sub_dirs:
            ret += f"Created the following subdirectories for object {self.object_name}: {', '.join(self.created_sub_dirs)}"
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


#   camera order #


class CameraIdentifier:
    def __init__(self):
        self.camera_mapping = {}
        self.os_name = system()
        self.max_tested = 10  # Max USB connections / cameras

    def identify_camera(self, index, event):
        cap = (
            cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if self.os_name == "Windows"
            else cv2.VideoCapture(index)
        )
        while not event.is_set():
            ret, frame = cap.read()
            cv2.imshow(f"Camera {index}", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

    def save_to_json(self, filename="camera_config.json"):
        with open(filename, "w") as f:
            json.dump({"Camera Order": self.camera_mapping}, f)

    def get_camera_count(self):
        for i in range(self.max_tested):
            cap = (
                cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if self.os_name == "Windows"
                else cv2.VideoCapture(i)
            )
            if not cap.isOpened():
                cap.release()
                return i
        return self.max_tested

    def identify_all_cameras(self):
        number_cameras = self.get_camera_count()
        for i in range(number_cameras):
            event = threading.Event()
            thread = threading.Thread(target=self.identify_camera, args=(i, event))
            thread.start()
            identifier = input(f"Enter a unique identifier for camera at index {i}: ")
            event.set()
            thread.join()
            if identifier.lower() == "skip":
                if "skip" in self.camera_mapping:
                    self.camera_mapping["skip"].append(i)
                else:
                    self.camera_mapping["skip"] = [i]
            else:
                self.camera_mapping[identifier] = i

    def camera_config(self):
        # Check if camera_config.json exists
        if not os.path.exists("camera_config.json"):
            print("camera_config.json not found. Running CameraIdentifier...")
            camera_identifier = CameraIdentifier()
            camera_identifier.identify_all_cameras()
            camera_identifier.save_to_json()
