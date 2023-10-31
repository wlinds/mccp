import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os

def capture_frame(cap, i, labels):
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f'camera_{i}_frame.jpg', frame)
        print(f"Frame captured for camera {i}")
        update_displayed_image(labels[i], i)

def update_displayed_image(label, i):
    if os.path.exists(f'camera_{i}_frame.jpg'):
        img = Image.open(f'camera_{i}_frame.jpg')
        img = img.resize((320, 240), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        label.configure(image=img)
        label.image = img
    else:
        print(f"Image for camera {i} not found.")

def camera_image_capturer(*camera_indices):
    root = tk.Tk()
    root.title("Camera Image Capturer")

    labels = []

    for i in camera_indices:
        cap = cv2.VideoCapture(i)

        # Button for capturing a single frame
        def capture_wrapper(cap, idx):
            return lambda: capture_frame(cap, idx, labels)

        capture_button = tk.Button(root, text=f"Capture Frame {i}", command=capture_wrapper(cap, i))
        capture_button.grid(row=1, column=i)

        # Create label for displaying images
        label = tk.Label(root)
        label.grid(row=0, column=i)
        labels.append(label)

    for i in camera_indices:
        update_displayed_image(labels[i], i)

    root.mainloop()

if __name__ == "__main__":
    camera_image_capturer(0, 1, 2, 3)
