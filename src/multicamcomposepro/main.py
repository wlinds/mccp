from augment import DataAugmenter
from camera import CameraManager
from utils import CameraConfigurator, CameraIdentifier, Warehouse

object_name = "aug_test2"
anomalies = ["cracked screen", "discolored front"]

def main():
    # Create a structured data warehouse
    warehouse = Warehouse()
    warehouse.build(object_name, anomalies)
    
    # Find all connected cameras
    CameraIdentifier()
    
    # Configure all found cameras
    CameraConfigurator().run()

    camera_manager = CameraManager(warehouse, 2, 3)
    camera_manager.run()

    augmenter = DataAugmenter(object_name, temperature=10, logging_enabled=False)
    augmenter.augment_images()  # Pass selected_images if needed

if __name__ == "__main__":
    main()
