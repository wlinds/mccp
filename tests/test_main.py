# To manually test, run from root with python3 -m tests.test_main
from src.multicamcomposepro.main import initialize_cameras


def main():
    print(f"{__name__} test running...")
    camera_stream = initialize_cameras()
    if camera_stream:
        print(f"{len(camera_stream)} device(s) found: \n {camera_stream}")

    else:
        print("Test failed. No cameras found.")


if __name__ == "__main__":
    main()
