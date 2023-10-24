from augment import DataAugmenter
from camera import CameraManager
from utils import CameraConfigurator, CameraIdentifier, Warehouse

object_name = "aug_test2"


def main():
    # Existing code
    camera_identifier = CameraIdentifier()
    camera_identifier.camera_identifier()  # Check if camera_config.json exists

    camera_configurator = CameraConfigurator()
    camera_configurator.camera_configurator()

    warehouse = Warehouse()
    warehouse.build(
        object_name=object_name,
        anomalies=["a n o m a ly"],
    )
    print(warehouse)

    camera_manager = CameraManager(warehouse, 2, 3)
    camera_manager.run()

    # Data Augmentation
    augmenter = DataAugmenter(object_name, temperature=10, logging_enabled=False)
    augmenter.augment_images()  # You can pass selected_images if needed


if __name__ == "__main__":
    main()
