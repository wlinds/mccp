from .augment import DataAugmenter
from .camera import CameraManager
from .utils import CameraConfigurator, Warehouse
from .utils import quickcap as qc

object_name = "test_object_without_input"
anomalies = ["cracked screen", "discolored front"]


def main():
    # Create a structured data warehouse
    warehouse = Warehouse()
    warehouse.build(object_name, anomalies)
    print(warehouse)
    # Configure all found cameras
    CameraConfigurator()

    camera_manager = CameraManager(warehouse, 2, 3, allow_user_input=True)
    camera_manager.run()
    print(warehouse)

    augmenter = DataAugmenter(object_name, temperature=0.05, logging_enabled=False)
    augmenter.augment_images()  # Pass selected_images if needed


if __name__ == "__main__":
    main()
