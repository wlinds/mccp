import json
import os
from platform import system
from threading import Event, Thread
import threading
from typing import List, Optional, Union
import cv2
import numpy as np

class CameraIdentifier2:
    def __init__(self, n_cameras: int = 10):
        self.camera_mapping: dict = {}
        self.os_name = system()
        self.max_usb_connection: int = n_cameras
        self.init()

    def init(self):
        if os.path.exists("camera_config.json"):
            reconfigure = input("Do you want to reconfigure existing camera config? [Y/N] ")
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
        if self.os_name != "Windows":
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
            cap = (cv2.VideoCapture(i, cv2.CAP_DSHOW) if self.os_name == "Windows" else cv2.VideoCapture(i))

            # Uset input in thread
            def user_input_thread():
                nonlocal camera_id
                while camera_id is None:
                    camera_id = input(f"Enter camera_id for camera at index {i}: ")

            input_thread = threading.Thread(target=user_input_thread)
            input_thread.start()

            while camera_id is None:
                ret, frame = cap.read()
                cv2.imshow(f"camera {i}", frame)
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

class CameraIdentifier:
    """
    Opens Cameras one by one and asks the user to identify them.
    Saves camera order with unique identifiers to camera_config.json.
    Order is used in CameraManager to display the camera streams in the correct order.
    """

    def __init__(self):
        self.camera_mapping: dict = {}
        self.os_name: str = system()
        self.max_tested: int = 10  # Max USB connected cameras

    def identify_camera(self, index: Union[int, str], event: Event) -> None:
        """
        Opens a video capture device with the given index and displays its frames in a window.
        The window is closed when the 'q' key is pressed or the given event is set.

        :param index: The index of the video capture device to open.
        :param event: An event object that can be used to signal the method to stop displaying frames. using

        :raises cv2.error: If the video capture device cannot be opened.

        Example:
        Open the video capture device with index 0 and display its frames in a window.
        identify_camera(0, stop_event)
        Wait for the user to press the 'q' key or signal the stop event.
        stop_event.wait()

        """

        # Debug
        # cap = (
        #     cv2.VideoCapture(index, cv2.CAP_DSHOW)
        #     if self.os_name == "Windows"
        #     else cv2.VideoCapture(index)
        # )

        cap = cv2.VideoCapture(index)

        while not event.is_set():
            ret, frame = cap.read()
            cv2.imshow(f"Camera {index}", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_camera_count(self) -> int:
        """
        Iterates over range(max_tested). Returns n found cameras.
        """
        for i in range(self.max_tested):
            # Debug
            # cap = (
            #     cv2.VideoCapture(i, cv2.CAP_DSHOW)
            #     if self.os_name == "Windows"
            #     else cv2.VideoCapture(i)
            # )
            cap = cv2.VideoCapture(i)
            if not cap.isOpened():
                cap.release()
                return i
        return self.max_tested

    def identify_all_cameras(self) -> None:
        """
        Allows the user to enter a unique identifier for each camera connected to the computer.

        :raises cv2.error: If the video capture device cannot be opened.

        """
        number_cameras = self.get_camera_count()
        for i in range(number_cameras):
            event = Event()
            thread = Thread(target=self.identify_camera, args=(i, event))
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

    def run_camera_identifier(self) -> None:
        """
        Checks to see if the camera_config.json file exists and if it contains the 'Camera Order' key.

        If'Camera Order' key is not present in camera_config.json or file not found, the user is prompted to identify all connected cameras.
        """
        # Check if camera_config.json exists
        if not os.path.exists("camera_config.json"):
            print("camera_config.json not found. Running CameraIdentifier...")
            camera_identifier = CameraIdentifier() # TODO: Recursion
            camera_identifier.identify_all_cameras()
            camera_identifier.save_to_json()
        else:
            # Check if 'Camera Order' exists in the JSON file
            with open("camera_config.json", "r") as f:
                data = json.load(f)
                if "Camera Order" not in data:
                    print(
                        '"Camera Order" not found in camera_config.json. Running CameraIdentifier...'
                    )
                    camera_identifier = CameraIdentifier()
                    camera_identifier.identify_all_cameras()
                    camera_identifier.save_to_json()

    def save_to_json(self, filename: str = "camera_config.json") -> None:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["Camera Order"] = self.camera_mapping
        with open(filename, "w") as f:
            json.dump(data, f)

def camera_text_overlay(frame, camera_name):
    font, pos = cv2.FONT_HERSHEY_SIMPLEX, (10, frame.shape[0] - 10)
    font_scale, font_color = 0.5, (255, 255, 255)
    cv2.putText(frame, camera_name, position, font, font_scale, font_color, 2)

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
        self.anomalies = (anomalies) # populates anomalies list for camera.py
        sub_dirs = ["train", "test"]
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + anomalies}

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(object_dir_path, sub_dir)
            self.create_directory(sub_dir_path)

            for nested_sub_dir in nested_sub_dirs.get(sub_dir, []):
                nested_sub_dir = self.clean_folder_name(nested_sub_dir)
                nested_sub_dir_path = os.path.join(sub_dir_path, nested_sub_dir)
                self.create_directory(nested_sub_dir_path)

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
    #c = CameraIdentifier2()
    conf = CameraConfigurator()
    conf.run()
