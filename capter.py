import cv2
import numpy as np
import mss
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import win32gui
import win32con

weights_path = "D:/Scanner ALL/Scanner API/yolov4-tiny.weights"
cfg_path = "D:/Scanner ALL/Scanner API/yolov4-tiny.cfg"
names_path = "D:/Scanner ALL/Scanner API/coco.names"

net = cv2.dnn.readNet(weights_path, cfg_path)
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

last_frame = None
boxes_detected = []
smoothed_boxes = [] 
lock = threading.Lock()
running = True
alpha = 0.6  

def screen_capture_loop():
    global last_frame
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while running:
            img = np.array(sct.grab(monitor))
            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            with lock:
                last_frame = img.copy()
            time.sleep(0.005) 

def detection_loop():
    global boxes_detected
    while running:
        with lock:
            if last_frame is None:
                time.sleep(0.01)
                continue
            frame = last_frame.copy()

        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), swapRB=True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        boxes, confidences, class_ids = [], [], []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5 and classes[class_id] == "person":
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        new_boxes = []
        if len(indices) > 0:
            for i in indices:
                i = i[0] if isinstance(i, (list, tuple, np.ndarray)) else i
                if classes[class_ids[i]] == "person":
                    new_boxes.append((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

        with lock:
            boxes_detected = new_boxes

        time.sleep(0.02)

def smooth_boxes(new_boxes):
    global smoothed_boxes
    if not smoothed_boxes:
        smoothed_boxes = new_boxes
        return smoothed_boxes

    smoothed = []
    for i, new_box in enumerate(new_boxes):
        if i < len(smoothed_boxes):
            x = int(alpha * new_box[0] + (1 - alpha) * smoothed_boxes[i][0])
            y = int(alpha * new_box[1] + (1 - alpha) * smoothed_boxes[i][1])
            w = int(alpha * new_box[2] + (1 - alpha) * smoothed_boxes[i][2])
            h = int(alpha * new_box[3] + (1 - alpha) * smoothed_boxes[i][3])
            smoothed.append((x, y, w, h))
        else:
            smoothed.append(new_box)
    smoothed_boxes = smoothed
    return smoothed_boxes

def make_window_transparent_clickthrough(hwnd):
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_COLORKEY)

root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.overrideredirect(True)
root.config(bg='black')

canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

imgtk = None

def update_overlay():
    global imgtk
    if not running:
        return

    with lock:
        frame = last_frame.copy() if last_frame is not None else None
        boxes = boxes_detected.copy()

    if frame is None:
        root.after(10, update_overlay)
        return

    smoothed = smooth_boxes(boxes)

    img = Image.new('RGBA', (screen_width, screen_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for (x, y, w, h) in smoothed:
        draw.rectangle([(x, y), (x + w, y + h)], outline=(0, 255, 0, 255), width=3)
        draw.text((x, y - 15), "person", fill=(0, 255, 0, 255))

    imgtk = ImageTk.PhotoImage(image=img)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

    root.after(10, update_overlay)  

def on_key_press(event):
    global running
    if event.keysym == 'Escape':
        running = False
        root.destroy()

root.bind('<Key>', on_key_press)

capture_thread = threading.Thread(target=screen_capture_loop, daemon=True)
detection_thread = threading.Thread(target=detection_loop, daemon=True)
capture_thread.start()
detection_thread.start()

root.update_idletasks()
make_window_transparent_clickthrough(win32gui.FindWindow(None, root.title()))

update_overlay()
root.mainloop()

running = False
capture_thread.join(timeout=1)
detection_thread.join(timeout=1)