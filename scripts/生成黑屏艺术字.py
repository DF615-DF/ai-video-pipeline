from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
img = Image.new("RGB", (W, H), (0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(r"C:\Windows\Fonts\STKAITI.TTF", 340)
chars = ["缘", "结", "守"]
start_y = 120
step_y = 330

for i, ch in enumerate(chars):
    bbox = draw.textbbox((0, 0), ch, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2 - bbox[0]
    y = start_y + i * step_y - bbox[1]
    draw.text((x + 4, y + 7), ch, font=font, fill=(52, 34, 26))
    draw.text((x, y), ch, font=font, fill=(238, 232, 218))

out = r"E:\AI\工作\my-knowledge\01-项目\缘结守\艺术字-缘结守-黑屏.png"
img.save(out)
print(out)
