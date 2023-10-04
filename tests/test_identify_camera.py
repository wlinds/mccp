# To manually test, run from root with python3 -m tests.test_main
from multicamcomposepro.utils import CameraIdentifier

if __name__ == "__main__":
    camera_identifier = CameraIdentifier()
    camera_identifier.identify_all_cameras()
    camera_identifier.save_to_json()