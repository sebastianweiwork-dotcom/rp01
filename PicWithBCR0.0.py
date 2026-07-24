import csv
import os
import cv2
import time
from datetime import datetime

# ==========================
# 根目录（树莓派路径）
# ==========================
root_dir = "/home/rp01/rp01-rp/output01"

csv_dir = root_dir
photo_dir = os.path.join(root_dir, "photos")

# ==========================
# 可配置参数
# ==========================
photo_count = 3          # 每次拍照数量
photo_delay = 0.5        # 每张照片之间的延迟（秒）
use_default_resolution = True   # 使用摄像头默认分辨率（可调）

# ==========================
# 自动检测摄像头（树莓派使用 V4L2）
# ==========================
def find_camera_index(max_test=10):
    """自动检测树莓派可用摄像头编号（V4L2）"""
    for i in range(max_test):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cap.release()
                print(f"找到摄像头: index={i}")
                return i
        cap.release()
    return None

cam_index = find_camera_index()

if cam_index is None:
    raise RuntimeError("❌ 未找到可用摄像头，请检查 USB 摄像头连接")

print(f"✅ 使用摄像头编号: {cam_index}")

# 初始化摄像头
camera = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)

# 使用摄像头默认分辨率（可调）
if not use_default_resolution:
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 创建图片目录
os.makedirs(photo_dir, exist_ok=True)

# ==========================
# CSV 文件命名（每次运行生成一个新的）
# ==========================
session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_file = os.path.join(csv_dir, f"{session_start_time}_session.csv")

print(f"📄 本次日志文件: {csv_file}")

# ==========================
# 拍照函数（保存 PNG）
# ==========================
def take_photos(barcode):
    """拍摄多张照片并返回路径列表"""
    photo_paths = []
    for i in range(photo_count):
        ret, frame = camera.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{barcode}_{timestamp}_{i+1}.png"
            filepath = os.path.join(photo_dir, filename)

            # 保存 PNG（无损）
            ok = cv2.imwrite(filepath, frame)
            if ok:
                photo_paths.append(filepath)
                print(f"📸 保存图片: {filepath}")
            else:
                print(f"❌ 图片保存失败: {filepath}")
        else:
            print("⚠ 摄像头读取失败，跳过此张照片")

        time.sleep(photo_delay)

    return photo_paths

# ==========================
# 主程序
# ==========================
print("开始监听扫码器输入（输入 quit 退出）...")
print(f"📁 保存目录: {root_dir}")

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
                print("退出程序")
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # 记录第一次扫码
            if first_scan_time is None:
                first_scan_time = timestamp
                first_scan_content = barcode

            # 记录最后一次扫码
            last_scan_time = timestamp
            last_scan_content = barcode

            # 拍照
            photo_paths = take_photos(barcode)

            # 写入 CSV：时间戳、条码、图片路径列表
            writer.writerow([timestamp, barcode, ";".join(photo_paths)])

            print(f"{timestamp} | {barcode}")

        except KeyboardInterrupt:
            print("退出程序")
            break

# ==========================
# 程序结束后重命名 CSV 文件
# ==========================
if first_scan_time and last_scan_time:
    new_csv_name = f"{first_scan_time}_{first_scan_content}_{last_scan_time}_{last_scan_content}.csv"
    new_csv_path = os.path.join(csv_dir, new_csv_name)

    os.rename(csv_file, new_csv_path)
    print(f"📄 日志文件已重命名为: {new_csv_path}")
else:
    print("⚠ 本次运行没有扫码，不生成日志文件名")
