# convert from mkv to mp4 using ffmpeg
import subprocess
import os

def mkv_to_mp4(video_path, converted_video_path):
    """将 MKV 视频转换为 MP4"""
    if not os.path.exists(converted_video_path):
        print(f"转换 {video_path} 为 {converted_video_path} (H.264)...")
        cmd = ["ffmpeg", "-y", "-i", video_path, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", converted_video_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("视频转换完成！")

def extract_audio(audio_path, converted_video_path):
    """从视频中提取音频 (MP3 格式)"""
    if not os.path.exists(audio_path):
        print("提取音频...")
        cmd = [
            "ffmpeg", "-y", "-i", converted_video_path, "-q:a", "0", "-map", "a", audio_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("音频提取完成！")

def convert_video(video_path, converted_video_path):
    """使用 FFmpeg 转换 AV1 视频为 H.264 (如果需要)"""
    if not os.path.exists(converted_video_path):
        print(f"转换 {video_path} 为 {converted_video_path} (H.264)...")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            converted_video_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("视频转换完成！")


# def