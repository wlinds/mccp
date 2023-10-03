import cv2
from datetime import datetime
import platform
from camera import CameraManager
from utils import camera_text_overlay, Warehouse

# TODO Summarized:
# Make modular grid of camera streams (i.e. not only a row, but columns as well)

def main():
    warehouse = Warehouse()
    warehouse.build(object_name="purple_duck", anomalies=["Albinism", "Melanism", "Polydactyly", "Missing Limbs"])
    camera_manager = CameraManager(warehouse)
    camera_manager.run()

if __name__ == "__main__":
    main()

