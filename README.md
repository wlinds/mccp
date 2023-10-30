
# MultiCamComposePro - Manage multiple cameras in Python
## MCCP

## Overview

- This project aims to capture images of objects from multiple camera angles and detect anomalies. It uses OpenCV for image capturing and provides a modular approach to manage camera configurations and image storage.



### Requirements

    - Python 3.10
    - OpenCV
    - JSON for configuration

### Installation

1. Install package:

```bash

pip install mccp
```


## Usage

Run the main.py script to start the application:


    python main.py

## Modules
### camera.py

    Class: CameraManager
        Manage and capture images.
        Load camera configurations from JSON file.
        Sort and display camera angles based on configuration.

### main.py

    Function: main()
        Run camera identification, configuration, and image capturing process.

### augment.py
    Class: DataAugmenter
        Create synthetic data from captured images.

### utils.py

    Class: Warehouse
        Manage object names and setup directories.

    Class: CameraConfigurator
        Find and configure all connected cameras.
        Configure exposure and white balance.

    Function: batch_resize()
        Post-capture resize.

    Function: wcap():
        Allow optimized image capture on Windows OS.

    Function: view_camera()
        View camera feed for any connected camera.


### Configuration

    camera_config.json: Holds the camera settings and order.

### Contributing

Information on how to contribute available [here.](https://github.com/wlinds/mccp/blob/main/CONTRIBUTING.md)



### License

This project is licensed under the MIT License - see the LICENSE file for details.