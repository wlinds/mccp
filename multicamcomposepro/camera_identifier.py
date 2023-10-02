import cv2
import json
from platform import system
import os


class CameraIdentifier:
    def __init__(self):
        self.camera_mapping = {}
        self.os_name = system()

    def identify_camera(self, index):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        while True:
            ret, frame = cap.read()
            cv2.imshow(f"Camera {index}", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

    def save_to_json(self, filename="camera_config.json"):
        with open(filename, "w") as f:
            json.dump(self.camera_mapping, f)

    def get_camera_count(self):
        max_tested = 6  # Change this if you have more than 6 cameras
        for i in range(max_tested):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                return i
        return max_tested

    def identify_all_cameras(self):
        number_cameras = self.get_camera_count()
        for i in range(number_cameras):
            if (self.os_name == "Windows" and i == 0) or (
                self.os_name != "Windows" and i == 1
            ):
                continue
            print(
                f"Identifying camera at index {i-1}. Press 'q' to move to the next camera."
            )
            self.identify_camera(i)
            identifier = input(f"Enter a unique identifier for camera at index {i-1}: ")
            self.camera_mapping[identifier] = i - 1


if __name__ == "__main__":
    camera_identifier = CameraIdentifier()

    # Manually identify each camera and assign an identifier
    camera_identifier.identify_all_cameras()

    # Save to JSON
    camera_identifier.save_to_json()

    # Load from JSON
    # camera_identifier.load_from_json()
    # print(f"Loaded cameras from JSON: {camera_identifier.camera_mapping}")
