from PIL import ImageFont

def check_font_installed(font_name):
    try:
        font = ImageFont.truetype(font_name, 28)
        print(f"✅ 字体 {font_name} 可用")
    except Exception as e:
        print(f"❌ 字体 {font_name} 不可用: {e}")

# 检查 NotoColorEmoji.ttf 是否安装
check_font_installed("NotoColorEmoji.ttf")
# 备用检查 Arial 是否可用
check_font_installed("Arial.ttf")
