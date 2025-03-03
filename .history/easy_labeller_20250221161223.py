import cv2
import json
import subprocess
import os

video_path = "video.mp4"
converted_video_path = "converted_video.mp4"
output_file = "annotations.json"
segment_duration = 20  # 20s 标注片段

# 1. 先检查是否需要转换视频
def convert_video(input_path, output_path):
    """使用 FFmpeg 转换视频为 H.264 编码"""
    if not os.path.exists(output_path):  # 如果已转换过就跳过
        print(f"转换 {input_path} 为 {output_path} (H.264)...")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,  # 输入文件
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # 视频压缩
            "-c:a", "aac", "-b:a", "128k",  # 音频保持
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("视频转换完成！")

convert_video(video_path, converted_video_path)

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
