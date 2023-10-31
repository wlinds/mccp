import tkinter as tk
import cv2
from PIL import Image, ImageTk
import json
import threading

from utils import wcap, VALID_ANGLES, VALID_RESOLUTIONS

# This is running very slow (??) tbh not sure why
# Might run better with CAP_DSHOW on windows


def save_settings(caps, settings):
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

def display_video_feed(label, cap):
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.config(image=imgtk)
        label.after(10, display_video_feed, label, cap)

# Trying to improve performance
def threaded_display(label, cap):
    thread = threading.Thread(target=display_video_feed, args=(label, cap))
    thread.daemon = 1
    thread.start()

def camera_wizard(*camera_indices):
    root = tk.Tk()
    root.title("MCCP 0.1.4 - Camera Wizard")

    labels = []
    caps = []
    settings = []

    def save_settings_wrapper():
        settings_data = []
        for idx, cap in enumerate(caps):
            setting = {
                "Camera": camera_indices[idx],
                "Resolution": VALID_RESOLUTIONS[0],
                "Angle": VALID_ANGLES[0],
                "Camera Exposure": 0,
                "Camera Color Temperature": 0,
                "Mask": 0
            }
            settings_data.append(setting)
        save_settings(caps, settings_data)

    for idx, camera_index in enumerate(camera_indices):
        
        # Get CAP_DSHOW for windows
        cap = wcap(camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 12)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 7)
        caps.append(cap)

        # Camera name (index)
        label = tk.Label(root, text=f"Camera {camera_index}")
        label.grid(row=0, column=idx)
        labels.append(label)

        # Video feed TODO optimize performance 
        video_label = tk.Label(root)
        video_label.grid(row=1, column=idx)
        threaded_display(video_label, cap)

        # Dropdown: Angles
        label_angle = tk.Label(root, text="Angle:")
        label_angle.grid(row=2, column=idx)

        var_angle = tk.StringVar(root)
        var_angle.set(VALID_ANGLES[0])
        dropdown_angle = tk.OptionMenu(root, var_angle, *VALID_ANGLES)
        dropdown_angle.grid(row=3, column=idx)

        # Dropdown: Resolutions
        label_reso = tk.Label(root, text="Resolution:")
        label_reso.grid(row=4, column=idx)

        var_reso = tk.StringVar(root)
        var_reso.set(VALID_RESOLUTIONS[0])
        dropdown_reso = tk.OptionMenu(root, var_reso, *VALID_RESOLUTIONS)
        dropdown_reso.grid(row=5, column=idx)

        # Slider: Exposure
        label_exposure = tk.Label(root, text="Exposure:")
        label_exposure.grid(row=6, column=idx)

        slider_exposure = tk.Scale(root, from_=-10, to=10, orient=tk.HORIZONTAL)
        slider_exposure.set(0)
        slider_exposure.grid(row=6, column=idx)

        # Slider: Temperature
        label_temp = tk.Label(root, text="Temperature:")
        label_temp.grid(row=7, column=idx)

        slider_temp = tk.Scale(root, from_=-3000, to=4000, orient=tk.HORIZONTAL)
        slider_temp.set(3000)
        slider_temp.grid(row=8, column=idx)

        # Entry Field
        label_mask = tk.Label(root, text="Mask:")
        label_mask.grid(row=9, column=idx)

        entry = tk.Entry(root)
        entry.grid(row=10, column=idx)

        settings.append({
            "Camera": camera_index,
            "Resolution": var_reso,
            "Angle": var_angle,
            "Camera Exposure": slider_exposure,
            "Camera Color Temperature": slider_temp,
            "Mask": entry
        })

    save_button = tk.Button(root, text="Save Settings", command=save_settings_wrapper)
    save_button.grid(row=12, columnspan=len(camera_indices))

    root.mainloop()

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_wizard(0, 1) 

