import cv2
import json
import subprocess
import os

video_path = "converted_video.mp4"  # 假设视频已转换为 H.264
output_file = "annotations.json"
segment_duration = 20  # 每段 20s
frame_rate = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FPS))  # 计算 FPS
cap = cv2.VideoCapture(video_path)
annotations = []

while True:
    start_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    segment_end_time = start_time + segment_duration  # 计算 20 秒后的时间戳

    print(f"播放片段 {start_time:.2f}s - {segment_end_time:.2f}s")

    # **播放 20 秒视频**
    while cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 < segment_end_time:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Annotation Tool", frame)
        
        # 以实际 FPS 控制播放速度
        if cv2.waitKey(int(1000 / frame_rate)) & 0xFF == ord('q'):
            break

    # **播放完 20s 片段后，等待用户输入 0-9 评分**
    print("请打分 (0-9)，按 'q' 退出:")
    while True:
        key = cv2.waitKey(0) & 0xFF
        if ord('0') <= key <= ord('9'):  # 0~9 评分
            annotations.append({"timestamp": start_time, "arousal": key - ord('0')})
            break
        elif key == ord('q'):  # 退出
            cap.release()
            cv2.destroyAllWindows()
            with open(output_file, "w") as f:
                json.dump(annotations, f, indent=4)
            print(f"标注完成！数据已保存到 {output_file}")
            exit()

    # **跳转到下一个 20s 片段**
    cap.set(cv2.CAP_PROP_POS_MSEC, (start_time + segment_duration) * 1000)

cap.release()
cv2.destroyAllWindows()

# **存储标注数据**
with open(output_file, "w") as f:
    json.dump(annotations, f, indent=4)

print(f"标注完成！数据已保存到 {output_file}")