# Welcome to Multi Cam Compose Pro


## Overview
- Multi Cam Compose Pro (MCCP) is a powerful tool designed to streamline and enhance multi-camera video composition workflows. It offers a range of features and functionalities to make multi-camera video editing more efficient and user-friendly.

## Features

- This project aims to capture images of objects from multiple camera angles and detect anomalies. It uses OpenCV for image capturing and provides a modular approach to manage camera configurations and image storage.

## Getting Started

# MultiCamComposePro - Manage multiple cameras in Python
## MCCP


### Requirements

    - Python 3.10
    - OpenCV
    - JSON for configuration
    - mkdocs, mkdocstrings, mkdocs-material
    - pytest

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

## Documentation

For full documentation run:

```bash
cd path/to/mccp
mkdocs serve
```

## Contact

PyPi page: [MCCP](https://pypi.org/project/mccp/)  
Github: [our GitHub](https://github.com/wlinds/mccp)


## Contributing

We welcome contributions to the MCCP project! If you're interested in contributing, please checkout the information [here.](https://github.com/wlinds/mccp/blob/main/CONTRIBUTING.md)


## Support

If you encounter any issues or have questions, please file them on our [GitHub issues page](https://github.com/wlinds/mccp/issues).


### License

This project is licensed under the MIT License - see the LICENSE file for details.