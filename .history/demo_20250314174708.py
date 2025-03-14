
from PIL import Image, ImageDraw, ImageFont

# **尝试加载 NotoColorEmoji**
try:
    font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
    font = ImageFont.truetype(font_path, 40)  # **字体大小**
    print(f"✅ 成功加载: {font_path}")
except Exception as e:
    print(f"❌ 加载失败: {e}")


