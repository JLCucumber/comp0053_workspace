# convert from mkv to mp4 using ffmpeg
import subprocess
import os

def mkv_to_mp4(input_file, output_file):
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_file]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("视频转换完成！")

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