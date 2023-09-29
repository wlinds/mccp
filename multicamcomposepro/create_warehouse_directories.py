import os
from typing import List


class WarehouseBuilder:
    """
    Class for building the data warehouse directory structure.
    """

    def __init__(self):
        """
        Initialize the WarehouseBuilder with empty lists for directories, subdirectories, and nested subdirectories.
        """
        self.created_dirs = []
        self.created_sub_dirs = []
        self.created_nested_sub_dirs = []
        self.anomalies = [] # Used in camera.py

    def create_directory(self, path: str):
        """
        Create a directory at the given path and add its name to the created_dirs list.

        Parameters:
            path (str): The path where the directory should be created.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                self.created_dirs.append(os.path.basename(path))
            except Exception as e:
                print(f"An error occurred while creating {path}: {e}")

    def build(self, object_name: str = "object", anomalies: List[str] = []):
        """
        Build the data warehouse directory structure based on the given object name and anomalies.

        Parameters:
            object_name (str): The name of the object directory.
            anomalies (List[str]): A list of anomaly names for nested subdirectories.
        """
        base_dir_path = os.path.join(os.getcwd(), "data_warehouse")
        dataset_dir_path = os.path.join(base_dir_path, "dataset")
        object_dir_path = os.path.join(dataset_dir_path, object_name)

        for path in [base_dir_path, dataset_dir_path]:
            self.create_directory(path)

        self.create_directory(object_dir_path)

        sub_dirs = ["train", "test"]
        nested_sub_dirs = {"train": ["good"], "test": ["good"] + anomalies}

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(object_dir_path, sub_dir)
            self.create_directory(sub_dir_path)

            for nested_sub_dir in nested_sub_dirs.get(sub_dir, []):
                nested_sub_dir_path = os.path.join(sub_dir_path, nested_sub_dir)
                self.create_directory(nested_sub_dir_path)

        self.print_summary(object_name)

    def print_summary(self, object_name: str):
        """
        Print a summary of the created directories, subdirectories, and nested subdirectories.

        Parameters:
            object_name (str): The name of the object directory.
        """
        if self.created_dirs:
            print(f"Created the following directories: {', '.join(self.created_dirs)}")
        if self.created_sub_dirs:
            print(
                f"Created the following subdirectories for object {object_name}: {', '.join(self.created_sub_dirs)}"
            )
        if self.created_nested_sub_dirs:
            print(
                f"With nested subdirectories: {', '.join(self.created_nested_sub_dirs)}"
            )
        elif not any(
            [self.created_dirs, self.created_sub_dirs, self.created_nested_sub_dirs]
        ):
            print(
                f"No folders created for object: {object_name}, because they already exist!"
            )


if __name__ == "__main__":
    builder = WarehouseBuilder()
    builder.build()
