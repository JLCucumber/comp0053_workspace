import cv2
import json
import time

video_path = "video.mp4"
output_file = "annotations.json"
frame_rate = 30  # 假设 FPS = 30
segment_duration = 20  # 20s 标注片段

cap = cv2.VideoCapture(video_path)
annotations = []

while True:
    start_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Annotation Tool", frame)

    # 监听键盘输入 (0-10)
    key = cv2.waitKey(0)
    if key in range(48, 58):  # ASCII 0-9
        annotations.append({"timestamp": start_time, "arousal": key - 48})
    elif key == ord('q'):  # 按 'q' 退出
        break

    # 跳转到下一个 20s 片段
    cap.set(cv2.CAP_PROP_POS_MSEC, (start_time + segment_duration) * 1000)

cap.release()
cv2.destroyAllWindows()

# 存储标注结果
with open(output_file, "w") as f:
    json.dump(annotations, f, indent=4)
