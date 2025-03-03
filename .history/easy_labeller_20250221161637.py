import cv2
import json
import subprocess
import os

video_path = "converted_video.mp4"  # 假设视频已转换为 H.264
output_file = "annotations.json"
segment_duration = 20  # 每段 20s
frame_rate = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FPS))  # 计算 FPS


# 2. 打开转换后的视频
cap = cv2.VideoCapture(converted_video_path)
annotations = []

while True:
    start_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Annotation Tool", frame)

    # 监听键盘输入 (0-10) 或 'q' 退出
    key = cv2.waitKey(0) & 0xFF
    if ord('0') <= key <= ord('9'):  # 0~9
        annotations.append({"timestamp": start_time, "arousal": key - ord('0')})
    elif key == ord('q'):
        break

    # 跳转到下一个 20s 片段
    cap.set(cv2.CAP_PROP_POS_MSEC, (start_time + segment_duration) * 1000)

cap.release()
cv2.destroyAllWindows()

# 3. 存储标注结果
with open(output_file, "w") as f:
    json.dump(annotations, f, indent=4)

print(f"标注完成！数据已保存到 {output_file}")
