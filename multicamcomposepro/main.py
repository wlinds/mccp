import cv2
from datetime import datetime


# TODO refactor for better camera idx ignore to avoid undesired connected cameras
def initialize_cameras(ignore_camera_idx: int = None) -> list:
    camera_array = []

    for idx in range(100):
        cap = cv2.VideoCapture(idx)
        
        if not cap.isOpened():
            break
        
        if ignore_camera_idx is not None and idx == ignore_camera_idx:
            cap.release()
            continue
        
        camera_array.append(cap)

    return camera_array

def camera_text_overlay(frame, camera_name):
    font = cv2.FONT_HERSHEY_SIMPLEX
    position = (10, frame.shape[0] - 10)  # Bottom-left corner frame for each cam stream
    font_scale = 0.5
    font_color = (255, 255, 255)
    line_type = 2
    cv2.putText(frame, camera_name, position, font, font_scale, font_color, line_type)

def main():
    camera_array = initialize_cameras()
    if not camera_array:
        print("No cameras found.")
        return

    try:
        while True:
            frames, camera_names = [], []
            for cap in camera_array:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frames from one or more cameras.")
                    break
                # Resize all frames to a common width and height TODO: crop
                width, height = 640, 360
                frame = cv2.resize(frame, (width, height))
                frames.append(frame)

                camera_names.append(f"Camera {len(frames)}") # TODO this might cause issues with initialize_cameras() if ignore_camera_idx
                camera_text_overlay(frame, camera_name="Camera " + str(len(frames)))

            # Stacking frames side by side (composition) TODO: create modular compositions
            composite_frame = cv2.hconcat(frames)

            cv2.imshow("Camera Streams", composite_frame)

            # Hold 'c' to capture images from all cameras. TODO: custom selection, custom name mapping
            if cv2.waitKey(1) & 0xFF == ord('c'):
                current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
                for i, frame in enumerate(frames):
                    filename = f"cam{i+1}_{current_time.replace('/', '-')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Still image captured: {filename}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        for cap in camera_array:
            cap.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

    #TODO use vendorid and deviceid to ignore cameras

