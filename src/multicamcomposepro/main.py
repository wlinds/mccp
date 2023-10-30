from augment import DataAugmenter
from camera import CameraManager
from utils import CameraConfigurator, Warehouse

object_name = "5324146"
anomalies = ["cracked screen", "discolored front"]


def main():
    # Create a structured data warehouse
    warehouse = Warehouse()
    warehouse.build(object_name, anomalies)
    print(warehouse)
    # Find all connected cameras
    # Configure all found cameras
    CameraConfigurator()

    camera_manager = CameraManager(warehouse, 2, 3)
    camera_manager.run()
    print(warehouse)

    augmenter = DataAugmenter(object_name, temperature=0.05, logging_enabled=False)
    augmenter.augment_images()  # Pass selected_images if needed


if __name__ == "__main__":
    main()
