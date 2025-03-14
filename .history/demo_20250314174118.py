from PIL import ImageFont

def check_font(font_name, size=28):
    try:
        font = ImageFont.truetype(font_name, size)
        print(f"✅ 字体 {font_name} 可用")
    except Exception as e:
        print(f"❌ 字体 {font_name} 不可用: {e}")

# 测试字体
check_font("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")  # Linux 默认路径
check_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")    # 可能存在的字体
check_font("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")  # 可能存在
check_font("Arial.ttf")  # Windows 可能用这个
