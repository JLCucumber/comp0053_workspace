import cv2
import json
import os
import subprocess
import sys
import time
import csv  # 新增


class VideoAnnotator:
    def __init__(self, video_path, output_file="annotations.json", segment_duration=20):
        self.video_path = video_path
        self.converted_video_path = "converted_video.mp4"
        self.audio_path = "audio.mp3"
        self.output_file = output_file
        self.segment_duration = segment_duration
        self.annotations = []
        self.cap = None
        self.segment_index = 0  # **新变量：确保时间正确**

    def extract_audio(self):
        """从视频中提取音频 (MP3 格式)"""
        if not os.path.exists(self.audio_path):
            print("提取音频...")
            cmd = [
                "ffmpeg", "-y", "-i", self.converted_video_path, "-q:a", "0", "-map", "a", self.audio_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("音频提取完成！")

    def convert_video(self):
        """使用 FFmpeg 转换 AV1 视频为 H.264 (如果需要)"""
        if not os.path.exists(self.converted_video_path):
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
        self.extract_audio()
        self.cap = cv2.VideoCapture(self.converted_video_path)

        if not self.cap.isOpened():
            print("无法打开视频文件！")
            sys.exit(1)

        frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # 计算 FPS
        print(f"视频 FPS: {frame_rate}")

        while True:
            # **修正 start_time，确保是标准间隔**
            start_time = self.segment_index * self.segment_duration
            segment_end_time = start_time + self.segment_duration

            print(f"播放片段 {start_time:.2f}s - {segment_end_time:.2f}s")

            # **确保视频跳转到正确的时间**
            self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

            # **启动音频**
            audio_process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-ss", str(start_time), "-t", str(self.segment_duration), self.audio_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # **同步播放视频**
            video_start_time = time.time()
            while self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 < segment_end_time:
                ret, frame = self.cap.read()
                if not ret:
                    break

                cv2.imshow("Annotation Tool", frame)
                elapsed_time = time.time() - video_start_time

                # **等待同步**
                video_elapsed = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 - start_time
                if video_elapsed > elapsed_time:
                    time.sleep(video_elapsed - elapsed_time)

                key = cv2.waitKey(int(1000 / frame_rate)) & 0xFF
                if key == ord('q'):
                    self.exit_and_save()
                elif key == ord('r'):  # **重播**
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
                    audio_process.kill()  # **停止音频**
                    break  # **退出播放循环，重新播放**

            # **等待音频播放完毕**
            audio_process.wait()

            # **等待用户打分**
            print("请打分 (0-9)，按 'q' 退出，按 'r' 重新播放:")
            while True:
                key = cv2.waitKey(0) & 0xFF
                if ord('0') <= key <= ord('9'):
                    self.annotations.append({"timestamp": start_time, "arousal": key - ord('0')})
                    self.segment_index += 1  # **正确推进到下一个片段**
                    break
                elif key == ord('q'):
                    self.exit_and_save()
                elif key == ord('r'):  # **用户想重播**
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
                    break  # **跳出打分循环，重播当前片段**

    def exit_and_save(self):
        """退出程序并保存标注数据"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

        with open(self.output_file, "w") as f:
            json.dump(self.annotations, f, indent=4)
        
        self.save_annotations_to_csv()  # 新增

        print(f"标注完成！数据已保存到 {os.path.join("data/", self.output_file)}")
        sys.exit(0)

    def save_annotations_to_csv(self):
        """将标注数据保存为 CSV 文件"""
        csv_file = self.output_file.replace(".json", ".csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "arousal"])
            for annotation in self.annotations:
                writer.writerow([annotation["timestamp"], annotation["arousal"]])
        print(f"标注数据已保存到 {csv_file}")

    def post_data_interpolation(self):
        """数据插值"""
        if not os.path.exists(self.output_file):
            print("请先标注数据！")
            sys.exit(1)

        with open(self.output_file, "r") as f:
            data = json.load(f)

        if len(data) < 2:
            print("数据不足，无法插值！")
            sys.exit(1)

        new_data = []
        for i in range(len(data) - 1):
            start_time = data[i]["timestamp"]
            end_time = data[i + 1]["timestamp"]
            arousal = data[i]["arousal"]

            new_data.append({"timestamp": start_time, "arousal": arousal})
            time_diff = end_time - start_time
            if time_diff > self.segment_duration:
                num_segments = int(time_diff / self.segment_duration)
                for j in range(1, num_segments):
                    new_data.append({"timestamp": start_time + j * self.segment_duration, "arousal": arousal})

        new_data.append(data[-1])
        self.annotations = new_data

        with open(self.output_file, "w") as f:
            json.dump(self.annotations, f, indent=4)

        print("数据插值完成！")        

if __name__ == "__main__":
    video_path = "video.mp4"
    annotator = VideoAnnotator(video_path, segment_duration=3)
    annotator.start_annotation()
    annotator.post_data_interpolation()  # 新增
