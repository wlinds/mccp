from camera import CameraManager
from utils import CameraConfigurator, CameraIdentifier, Warehouse

# TODO Summarized:
# Make modular grid of camera streams (i.e. not only a row, but columns as well)


def main():
    camera_identifier = CameraIdentifier()
    camera_identifier.camera_config()  # Check if camera_config.json exists

    camera_configurator = CameraConfigurator()
    camera_configurator.camera_configurator()

    warehouse = Warehouse()
    warehouse.build(
        object_name="object",
        anomalies=["anomaly"],
    )
    print(warehouse)
    camera_manager = CameraManager(warehouse)
    camera_manager.run()


if __name__ == "__main__":
    main()
