import cv2

# Test this on windows

class VideoCropper:
    def __init__(self):
        self.start_x, self.start_y = -1, -1
        self.end_x, self.end_y = -1, -1
        self.drawing = False

    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_x, self.start_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_x, self.end_y = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_x, self.end_y = x, y

    def capture_video(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 854)  # width
        cap.set(4, 480)  # height

        cv2.namedWindow('Camera')
        cv2.setMouseCallback('Camera', self.draw_rectangle)

        while True:
            ret, frame = cap.read()
            if ret:
                if self.drawing:
                    cv2.rectangle(frame, (self.start_x, self.start_y), (self.end_x, self.end_y), (0, 255, 0), 2)

                cv2.imshow('Camera', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    cropper = VideoCropper()
    cropper.capture_video()
