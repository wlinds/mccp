
# MultiCamComposePro - Manage multiple cameras using Python
## MCCP

## Overview

- This project aims to capture images of objects from multiple camera angles and detect anomalies. It uses OpenCV for image capturing and provides a modular approach to manage camera configurations and image storage.
Requirements

    - Python 3.10
    - OpenCV
    - JSON for configuration

## Installation

1. Clone the repository:

```bash

git clone https://github.com/your_username/your_project_name.git
```
2. Navigate to the project directory:
```bash

cd your_project_name
```
3. Install the required packages:

```bash

    pip install -r requirements.txt
```
## Usage

    Run the main.py script to start the application:

```bash

    python main.py
```
## Modules
### camera.py

    Class: CameraManager
        Manages multiple cameras and captures images.
        Loads camera configurations from a JSON file.
        Sorts camera angles based on the configuration.

### main.py

    Function: main()
        Orchestrates the camera identification, configuration, and image capturing process.

utils.py

    Class: Warehouse
        Manages object names and their anomalies.
    Class: CameraIdentifier
        Identifies and configures cameras.
    Class: CameraConfigurator
        Additional camera setup.

Configuration

    camera_config.json: Holds the camera settings and order.

TODO

    Make a modular grid of camera streams, i.e., not only a row but columns as well.

License

This project is licensed under the MIT License - see the LICENSE.md file for details.