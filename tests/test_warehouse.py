# To manually test, run from root with python3 -m tests.test_main
from multicamcomposepro.create_warehouse_directories import WarehouseBuilder

if __name__ == "__main__":
    warehouse = WarehouseBuilder()
    warehouse.build(object_name="purple_duck", anomalies=["Albinism", "Melanism", "Polydactyly", "Missing Limbs"])
    print(warehouse)