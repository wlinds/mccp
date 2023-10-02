import cv2
import json
from platform import system
import os
import threading

class CameraIdentifier:
    def __init__(self):
        self.camera_mapping = {}
        self.os_name = system()

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
        max_tested = 10  # Change this if you have more than 10 cameras
        for i in range(max_tested):
            cap = (
                cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if self.os_name == "Windows"
                else cv2.VideoCapture(i)
            )
            if not cap.isOpened():
                cap.release()
                return i
        return max_tested

    def identify_all_cameras(self):
        number_cameras = self.get_camera_count()
        for i in range(number_cameras):
            event = threading.Event()
            thread = threading.Thread(target=self.identify_camera, args=(i, event))
            thread.start()
            identifier = input(f"Enter a unique identifier for camera at index {i}: ")
            event.set()
            thread.join()
            if identifier.lower() == 'skip':
                if 'skip' in self.camera_mapping:
                    self.camera_mapping['skip'].append(i)
                else:
                    self.camera_mapping['skip'] = [i]
            else:
                self.camera_mapping[identifier] = i

if __name__ == "__main__":
    camera_identifier = CameraIdentifier()
    camera_identifier.identify_all_cameras()
    camera_identifier.save_to_json()
