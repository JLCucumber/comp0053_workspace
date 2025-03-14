# convert from mkv to mp4 using ffmpeg
def mkv_to_mp4(input_file, output_file):
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_file]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("视频转换完成！")

