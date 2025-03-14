from PIL import ImageFont

def check_font(font_name, size=28):
    try:
        font = ImageFont.truetype(font_name, size)
        print(f"✅ 字体 {font_name} 可用")
    except Exception as e:
        print(f"❌ 字体 {font_name} 不可用: {e}")

# 测试字体
check_font("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
check_font("/usr/share/fonts/noto/NotoColorEmoji-Regular.ttf")

