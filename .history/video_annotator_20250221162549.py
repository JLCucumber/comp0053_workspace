import cv2
import json
import os
import subprocess
import sys

class VideoAnnotator:
    def __init__(self, video_path, output_file="annotations.json", segment_duration=20):
        self.video_path = video_path
        self.converted_video_path = "converted_video.mp4"
        self.output_file = output_file
        self.segment_duration = segment_duration
        self.annotations = []
        self.cap = None

    def convert_video(self):
        """使用 FFmpeg 转换 AV1 视频为 H.264 (如果需要)"""
        if not os.path.exists(self.converted_video_path):  # 避免重复转换
            print(f"转换 {self.video_path} 为 {self.converted_video_path} (H.264)...")
            cmd = [
                "ffmpeg", "-y", "-i", self.video_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                self.converted_video_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("视频转换完成！")

    def start_annotation(self):
        """开始播放视频并进行标注"""
        self.convert_video()
        self.cap = cv2.VideoCapture(self.converted_video_path)

        if not self.cap.isOpened():
            print("无法打开视频文件！")
            sys.exit(1)

        frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # 计算 FPS
        print(f"视频 FPS: {frame_rate}")

        while True:
            start_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            segment_end_time = start_time + self.segment_duration

            print(f"播放片段 {start_time:.2f}s - {segment_end_time:.2f}s")

            # 播放 20s 片段
            while self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 < segment_end_time:
                ret, frame = self.cap.read()
                if not ret:
                    break
                cv2.imshow("Annotation Tool", frame)
                if cv2.waitKey(int(1000 / frame_rate)) & 0xFF == ord('q'):
                    self.exit_and_save()

            # 播放结束，等待用户打分
            print("请打分 (0-9)，按 'q' 退出:")
            while True:
                key = cv2.waitKey(0) & 0xFF
                if ord('0') <= key <= ord('9'):
                    self.annotations.append({"timestamp": start_time, "arousal": key - ord('0')})
                    break
                elif key == ord('q'):
                    self.exit_and_save()

            # 跳转到下一个 20s 片段
            self.cap.set(cv2.CAP_PROP_POS_MSEC, (start_time + self.segment_duration) * 1000)

    def exit_and_save(self):
        """退出程序并保存标注数据"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

        with open(self.output_file, "w") as f:
            json.dump(self.annotations, f, indent=4)

        print(f"标注完成！数据已保存到 {self.output_file}")
        sys.exit(0)


if __name__ == "__main__":
    video_path = "video_2.mp4"  # 需要标注的视频文件
    annotator = VideoAnnotator(video_path)
    annotator.start_annotation()
