import csv
import os
import cv2
import time
from datetime import datetime

# ==========================
# 输出目录（你指定的路径）
# ==========================
output_dir = "/home/rp01/rp01-rp/output1"
csv_file = os.path.join(output_dir, "scan_log.csv")
photo_dir = output_dir  # 照片也放同一个目录

# ==========================
# 可配置参数
# ==========================
photo_count = 3          # 每次拍照数量
photo_delay = 0.4        # 每张照片之间的延迟（秒）
camera_index = 0         # USB 摄像头一般是 0

# ==========================
# 创建目录
# ==========================
os.makedirs(output_dir, exist_ok=True)

# ==========================
# 初始化摄像头（树莓派更稳健）
# ==========================
def init_camera():
    cam = cv2.VideoCapture(camera_index)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cam.set(cv2.CAP_PROP_FPS, 30)

    time.sleep(0.5)  # 给摄像头一点初始化时间

    if not cam.isOpened():
        raise RuntimeError("无法打开摄像头，请检查 USB 连接")

    return cam

camera = init_camera()

# ==========================
# 拍照函数（无 global，更专业）
# ==========================
def take_photos(cam, barcode):
    photo_paths = []

    for i in range(photo_count):
        # 丢弃缓存帧（树莓派 USB 摄像头常见问题）
        cam.read()

        ret, frame = cam.read()
        if not ret:
            print("⚠️ 摄像头读取失败，尝试重新初始化摄像头...")
            time.sleep(0.5)
            cam = init_camera()
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{barcode}_{timestamp}_{i+1}.jpg"
        filepath = os.path.join(photo_dir, filename)

        cv2.imwrite(filepath, frame)
        photo_paths.append(filepath)

        time.sleep(photo_delay)

    return photo_paths, cam

# ==========================
# 主程序
# ==========================
print("📡 开始监听扫码器输入（输入 quit 退出）...")

with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    while True:
        try:
            barcode = input().strip()

            if barcode.lower() in ["quit", "exit"]:
                print("👋 程序退出")
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # 拍照
            photo_paths, camera = take_photos(camera, barcode)

            # 写入 CSV
            writer.writerow([timestamp, barcode, ";".join(photo_paths)])
            f.flush()
            os.fsync(f.fileno())

            print(f"{timestamp} | {barcode}")
            for p in photo_paths:
                print(f"  📷 保存图片: {p}")

        except KeyboardInterrupt:
            print("👋 程序退出（Ctrl+C）")
            break

camera.release()
cv2.destroyAllWindows()
