import cv2
import os

# 摄像头编号，通常 USB 摄像头是 0
cam = cv2.VideoCapture(0)

# 指定保存目录
save_dir = "/home/rp01/rp01-rp"
os.makedirs(save_dir, exist_ok=True)

save_path = os.path.join(save_dir, "photo.jpg")

# 读取一帧
ret, frame = cam.read()

if ret:
    cv2.imwrite(save_path, frame)
    print("保存成功:", save_path)
else:
    print("拍照失败")

cam.release()
