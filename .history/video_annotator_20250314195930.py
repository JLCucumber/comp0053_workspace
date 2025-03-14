import cv2
import json
import os
import subprocess
import sys
import time
import csv  # 新增
from utils import *  # 新增
from PIL import Image, ImageDraw, ImageFont  # 新增
import numpy as np  # 新增
import pandas as pd  # 新增



class VideoAnnotator:
    def __init__(self, video_name, output_path="output/", segment_duration=3):

        self.video_path = os.path.join("video/", video_name)
        self.converted_audio_path = os.path.join("converted_audio/", video_name.replace(".mkv", "_converted.mp3"))
        self.converted_video_path = os.path.join("converted_video/", video_name.replace(".mkv", "_converted.mp4"))
        self.output_file = get_unique_filename(os.path.join(output_path, video_name.replace(".mkv", ".json")))

        self.segment_duration = segment_duration
        self.annotations = []
        self.cap = None
        self.segment_index = 0  # **新变量：确保时间正确**
        self.video_duration = 0  # **新变量：存储视频总时长**

        # **情绪标签定义（带 Emoji）**
        self.emotion_labels = [
            "Serenity", "Calm", "Relaxed",
            "Neutrality", "Focused", "Active", "Excited",
            "Agitated", "Overstimulated", "Explosive"
        ]

    def draw_emotion_labels(self, frame):
        """在视频左侧绘制情绪标签，使用统一的背景"""
        x, y = 20, 40  # **左上角起始位置**
        box_width, box_height = 220, 40  # **加大标签大小**
        spacing = 8  # **标签间距**
        total_height = len(self.emotion_labels) * (box_height + spacing)  # **计算总背景高度**
        
        # **转换 OpenCV 图像为 PIL**
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)

        # **绘制整体背景框**
        background_top_left = (x, y)
        background_bottom_right = (x + box_width, y + total_height)
        draw.rectangle([background_top_left, background_bottom_right], fill=(80, 80, 80, 220))  # **更亮的半透明背景**

        # **尝试加载不同字体**
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "Arial.ttf"
        ]

        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 28)
                # print(f"✅ 使用字体: {font_path}")
                break
            except:
                continue

        if font is None:
            print("❌ 没有找到可用字体，使用默认字体")
            font = ImageFont.load_default()

        for i, label in enumerate(self.emotion_labels):
            text_position = (x + 10, y + i * (box_height + spacing) + 15)
            draw.text(text_position, f"{i} - {label}", font=font, fill=(255, 255, 255, 255))

        # **转换回 OpenCV 图像**
        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
        return frame

    def check_csv_length(self):
        """检查 CSV 文件长度是否符合要求"""
        if not os.path.exists(self.output_file):
            return 0
        with open(self.output_file, "r") as f:
            data = json.load(f)
            return len(data)
    
    def start_annotation(self):
        """开始播放视频并进行标注"""
        mkv_to_mp4(self.video_path, self.converted_video_path)
        extract_audio(self.video_path, self.converted_audio_path)
        self.cap = cv2.VideoCapture(self.converted_video_path)

        if not self.cap.isOpened():
            print("无法打开视频文件！")
            sys.exit(1)

        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # 计算 FPS
        self.video_duration = total_frames / frame_rate  # **计算视频时长（秒）**
        print(f"视频总时长: {self.video_duration:.2f} 秒, FPS: {frame_rate}")


        while True:
            # **修正 start_time，确保是标准间隔**
            start_time = self.segment_index * self.segment_duration
            segment_end_time = start_time + self.segment_duration
            
             # **检测是否超过视频时长，超出则退出**
            if start_time >= self.video_duration:
                print("🎬 视频播放完成，标注结束！")
                self.exit_and_save()

            print(f"播放片段 {start_time:.2f}s - {segment_end_time:.2f}s")

            # **确保视频跳转到正确的时间**
            self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

            # **启动音频**
            audio_process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-ss", str(start_time), "-t", str(self.segment_duration), self.converted_audio_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # **同步播放视频**
            video_start_time = time.time()
            while self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 < segment_end_time:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = self.draw_emotion_labels(frame)  # **绘制情绪标签**
                cv2.imshow("Annotation Tool", frame)

                elapsed_time = time.time() - video_start_time
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
        csv_file = get_unique_filename(self.output_file.replace(".json", ".csv"))
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "arousal"])
            for annotation in self.annotations:
                writer.writerow([annotation["timestamp"], annotation["arousal"]])
        print(f"标注数据已保存到 {csv_file}")


if __name__ == "__main__":
    # 使用 VideoAnnotator 类
    # video_name = "rgb_lhb_game_session.mkv"
    # annotator = VideoAnnotator(video_name, segment_duration=3)
    # annotator.start_annotation()

    # # data extension checker
    # check_and_extend_csv("output/rgb_byz_game_session.csv", segment_duration=3)
    # check_and_extend_csv("output/rgb_byz_baseline.csv", segment_duration=3)

    # data interpolation
    input_csv_file = "output/rgb_byz_game_session.csv"  # 你的原始 CSV 文件
    output_csv_file = input_csv_file.replace(".csv", "_interpolated.csv")
    interpolate_csv(input_csv_file, output_csv_file, target_interval=1, visualize=True, method="linear")  # spline
    visualize_interpolation(input_csv_file, output_csv_file)

