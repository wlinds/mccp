# To manually test, run from root with python3 -m tests.test_main
from multicamcomposepro.utils import Warehouse

if __name__ == "__main__":
    warehouse = Warehouse()
    warehouse.build(object_name="purple_duck", anomalies=["Albinism", "Melanism", "Polydactyly", "Missing Limbs"])
    print(warehouse)