from datetime import datetime
from camera import CameraManager
from utils import CameraIdentifier, camera_text_overlay, Warehouse
import os

# TODO Summarized:
# Make modular grid of camera streams (i.e. not only a row, but columns as well)

def main():
    # Check if camera_config.json exists
    if not os.path.exists("camera_config.json"):
        print("camera_config.json not found. Running CameraIdentifier...")
        camera_identifier = CameraIdentifier()
        camera_identifier.identify_all_cameras()
        camera_identifier.save_to_json()
    warehouse = Warehouse()
    warehouse.build(object_name="purple_duck", anomalies=["Albinism", "Melanism", "Polydactyly", "Missing Limbs"])
    camera_manager = CameraManager(warehouse)
    camera_manager.run()

if __name__ == "__main__":
    main()

