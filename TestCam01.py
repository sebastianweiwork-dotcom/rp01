import cv2
import time

# === 配置你的网络摄像头地址 ===
# 常见格式：
# - RTSP: rtsp://username:password@camera_ip:554/stream
# - HTTP/MJPEG: http://camera_ip:8080/video
CAMERA_URL = "rtsp://admin:123456@192.168.1.100:554/stream"

def check_camera_connection(url):
    print("=== 网络摄像头连接测试 ===")
    print(f"检查地址: {url}")

    cap = cv2.VideoCapture(url)

    # 检查是否成功打开
    if not cap.isOpened():
        print("❌ 摄像头连接失败：无法打开视频流")
        return None

    print("✔ 摄像头连接成功：视频流已打开")

    # 尝试读取一帧
    ret, frame = cap.read()
    if not ret:
        print("❌ 摄像头连接成功，但无法读取画面")
        cap.release()
        return None

    print("✔ 成功读取画面帧")

    # 保存测试照片
    test_photo_path = "test_photo.jpg"
    cv2.imwrite(test_photo_path, frame)
    print(f"📸 测试照片已保存: {test_photo_path}")

    cap.release()
    return frame

if __name__ == "__main__":
    check_camera_connection(CAMERA_URL)
