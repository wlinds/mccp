# To manually test, run from root with python3 -m tests.test_main
from multicamcomposepro.create_warehouse_directories import WarehouseBuilder

if __name__ == "__main__":
    builder = WarehouseBuilder()
    builder.build("regn2", ["a","b"])
    print(builder)
