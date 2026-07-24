import csv
import os
import cv2
import time
from datetime import datetime

# ==========================
# Parameter Section (ALL configurable parameters)
# ==========================
root_dir = "/home/rp01/rp01-rp/output01"   # Root output directory
photo_count = 3                            # Number of photos per scan
photo_delay = 0.5                          # Delay between photos (seconds)

use_default_resolution = True              # Use camera default resolution
force_resolution_enabled = False           # Force custom resolution
force_resolution_width = 1920              # Forced width
force_resolution_height = 1080             # Forced height

# ==========================
# Derived directories
# ==========================
csv_dir = root_dir

# ==========================
# Auto-detect camera (V4L2)
# ==========================
def find_camera_index(max_test=10):
    """Auto-detect available camera index using V4L2."""
    for i in range(max_test):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cap.release()
                print(f"Camera detected at index: {i}")
                return i
        cap.release()
    return None

cam_index = find_camera_index()

if cam_index is None:
    raise RuntimeError("No camera detected. Please check USB camera connection.")

print(f"Using camera index: {cam_index}")

# Initialize camera
camera = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)

# ==========================
# Apply resolution settings
# ==========================
if force_resolution_enabled:
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, force_resolution_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, force_resolution_height)
    print(f"Forced resolution: {force_resolution_width} x {force_resolution_height}")
elif use_default_resolution:
    print("Using camera default resolution.")
else:
    print("Resolution settings unchanged.")

# ==========================
# Create new CSV file per session
# ==========================
session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_file = os.path.join(csv_dir, f"{session_start_time}_session.csv")

print(f"Log file for this session: {csv_file}")

# ==========================
# Photo capture function (PNG)
# ==========================
def take_photos(barcode, photo_folder):
    """Capture multiple photos and return file path list."""
    photo_paths = []
    for i in range(photo_count):
        ret, frame = camera.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{barcode}_{timestamp}_{i+1}.png"
            filepath = os.path.join(photo_folder, filename)

            ok = cv2.imwrite(filepath, frame)
            if ok:
                photo_paths.append(filepath)
                print(f"Saved photo: {filepath}")
            else:
                print(f"Failed to save photo: {filepath}")
        else:
            print("Camera read failed. Skipping this photo.")

        time.sleep(photo_delay)

    return photo_paths

# ==========================
# Main loop
# ==========================
print("Listening for barcode input (type 'quit' to exit)...")
print(f"Output directory: {root_dir}")

first_scan_time = None
first_scan_content = None
last_scan_time = None
last_scan_content = None

with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    while True:
        try:
            barcode = input()

            if barcode.lower() in ["quit", "exit"]:
                print("Exiting program.")
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Record first scan
            if first_scan_time is None:
                first_scan_time = timestamp
                first_scan_content = barcode

            # Record last scan
            last_scan_time = timestamp
            last_scan_content = barcode

            # Create photo folder for this scan
            folder_name = f"{first_scan_time}_{first_scan_content}_{last_scan_time}_{last_scan_content}_photo"
            photo_folder = os.path.join(root_dir, folder_name)
            os.makedirs(photo_folder, exist_ok=True)

            print(f"Photo folder created: {photo_folder}")

            # Capture photos
            photo_paths = take_photos(barcode, photo_folder)

            # Write to CSV
            writer.writerow([timestamp, barcode, ";".join(photo_paths)])

            print(f"{timestamp} | {barcode}")

        except KeyboardInterrupt:
            print("Program interrupted.")
            break

# ==========================
# Rename CSV file after session ends
# ==========================
if first_scan_time and last_scan_time:
    new_csv_name = f"{first_scan_time}_{first_scan_content}_{last_scan_time}_{last_scan_content}.csv"
    new_csv_path = os.path.join(csv_dir, new_csv_name)

    os.rename(csv_file, new_csv_path)
    print(f"Log file renamed to: {new_csv_path}")
else:
    print("No scans recorded. No log file generated.")
