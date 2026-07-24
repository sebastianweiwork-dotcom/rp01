import cv2
import os
from datetime import datetime

# ==========================
# 输出目录
# ==========================
output_dir = "/home/rp01/CamTest"
os.makedirs(output_dir, exist_ok=True)

result_path = os.path.join(output_dir, "result.txt")

# ==========================
# 自动生成序号
# ==========================
def get_next_index():
    files = os.listdir(output_dir)
    jpg_files = [f for f in files if f.endswith(".jpg")]

    if not jpg_files:
        return 1

    # 从文件名中提取序号
    indices = []
    for f in jpg_files:
        try:
            idx = int(f.split("_")[0])
            indices.append(idx)
        except:
            pass

    return max(indices) + 1 if indices else 1

# ==========================
# 初始化摄像头
# ==========================
def init_camera():
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cam.set(cv2.CAP_PROP_FPS, 30)
    return cam

camera = init_camera()

# ==========================
# 拍照测试
# ==========================
index = get_next_index()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
photo_name = f"{index}_{timestamp}.jpg"
photo_path = os.path.join(output_dir, photo_name)

with open(result_path, "a") as f:

    if not camera.isOpened():
        msg = "❌ 摄像头无法打开\n"
        f.write(msg)
        print(msg)
    else:
        camera.read()  # 丢弃缓存帧
        ret, frame = camera.read()

        if not ret:
            msg = "❌ 摄像头已打开，但无法读取画面\n"
            f.write(msg)
            print(msg)
        else:
            cv2.imwrite(photo_path, frame)
            msg = f"✅ 成功拍照: {photo_name}\n"
            f.write(msg)
            print(msg)

camera.release()
cv2.destroyAllWindows()
