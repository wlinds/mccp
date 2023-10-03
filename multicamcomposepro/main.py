from datetime import datetime
from camera import CameraManager
from utils import CameraIdentifier, camera_text_overlay, Warehouse
import os

# TODO Summarized:
# Make modular grid of camera streams (i.e. not only a row, but columns as well)


def main():
    camera_identifier = CameraIdentifier()
    camera_identifier.camera_config()  # Check if camera_config.json exists

    warehouse = Warehouse()
    warehouse.build(
        object_name="purple_duck",
        anomalies=["Albinism", "Melanism", "Polydactyly", "Missing Limbs"],
    )
    print(warehouse)
    camera_manager = CameraManager(warehouse)
    camera_manager.run()


if __name__ == "__main__":
    main()
