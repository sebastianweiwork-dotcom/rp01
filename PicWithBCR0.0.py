import csv
import os
import cv2
import time
from datetime import datetime

# ==========================
# Parameter Section (ALL configurable parameters)
# ==========================
root_dir = "/home/rp01/rp01-rp/output01"

# New: delay array for each photo (拍照间隔数组)
photo_delays = [0.3, 0.8, 1.5]             # Delay between each photo (seconds)

# New: scan cooldown time (扫描冷却时间)
scan_cooldown = 1.0                       # Seconds to ignore repeated scans

use_default_resolution = True
force_resolution_enabled = False
force_resolution_width = 1920
force_resolution_height = 1080

csv_suffix = "_scan_log.csv"
photo_suffix = "_photo"

# ==========================
# Auto-detect camera (V4L2)
# ==========================
def find_camera_index(max_test=10):
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
# Helper: pure numeric timestamp
# ==========================
def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# ==========================
# Create temporary CSV + photo folder
# ==========================
session_start_ts = ts()

temp_csv_name = f"{session_start_ts}_session{csv_suffix}"
csv_file = os.path.join(root_dir, temp_csv_name)

temp_photo_folder = os.path.join(root_dir, f"{session_start_ts}_session{photo_suffix}")
os.makedirs(temp_photo_folder, exist_ok=True)

print(f"Temporary CSV file: {csv_file}")
print(f"Temporary photo folder: {temp_photo_folder}")

# ==========================
# Photo capture function (PNG)
# ==========================
def take_photos(barcode, photo_folder):
    photo_paths = []

    for i, delay in enumerate(photo_delays):
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

        print(f"Waiting {delay} seconds before next photo...")
        time.sleep(delay)

    return photo_paths

# ==========================
# Main loop
# ==========================
print("Listening for barcode input (type 'quit' to exit)...")
print(f"Output directory: {root_dir}")

first_scan_ts = None
first_scan_content = None
last_scan_time = 0   # New: last scan timestamp

with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    while True:
        try:
            barcode = input()

            if barcode.lower() in ["quit", "exit"]:
                print("Exiting program.")
                break

            now = time.time()

            # ==========================
            # Cooldown check (CD 时间)
            # ==========================
            if now - last_scan_time < scan_cooldown:
                print(f"Ignored duplicate scan (cooldown {scan_cooldown}s).")
                continue

            last_scan_time = now  # Update last scan time

            timestamp = ts()

            # Record first scan ONLY
            if first_scan_ts is None:
                first_scan_ts = timestamp
                first_scan_content = barcode

            # Capture photos
            photo_paths = take_photos(barcode, temp_photo_folder)

            # Write to CSV
            writer.writerow([timestamp, barcode, ";".join(photo_paths)])

            print(f"{timestamp} | {barcode}")

        except KeyboardInterrupt:
            print("Program interrupted.")
            break

# ==========================
# Rename CSV + photo folder using ONLY first scan info
# ==========================
if first_scan_ts and first_scan_content:
    final_name = f"{first_scan_ts}_{first_scan_content}"

    final_csv = os.path.join(root_dir, final_name + csv_suffix)
    final_photo_folder = os.path.join(root_dir, final_name + photo_suffix)

    os.rename(csv_file, final_csv)
    os.rename(temp_photo_folder, final_photo_folder)

    print(f"Final CSV file: {final_csv}")
    print(f"Final photo folder: {final_photo_folder}")

else:
    print("No scans recorded. No final naming applied.")
