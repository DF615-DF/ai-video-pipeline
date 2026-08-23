from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1920, 1080
img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
font = ImageFont.truetype(r"C:\Windows\Fonts\STKAITI.TTF", 280)
chars = ["缘", "结", "守"]
start_y = 90
step_y = 320
positions = []

for i, ch in enumerate(chars):
    bbox = font.getbbox(ch)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2 - bbox[0]
    y = start_y + i * step_y - bbox[1]
    positions.append((x, y, bbox))

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for (x, y, _), ch in zip(positions, chars):
    gdraw.text((x, y), ch, font=font, fill=(218, 202, 170, 120))
glow = glow.filter(ImageFilter.GaussianBlur(18))
img.alpha_composite(glow)

draw = ImageDraw.Draw(img)
for (x, y, _), ch in zip(positions, chars):
    draw.text((x + 3, y + 6), ch, font=font, fill=(45, 28, 20, 255))
    draw.text((x, y), ch, font=font, fill=(242, 236, 224, 255))

seal_size = 72
seal_x = W // 2 + 210
seal_y = start_y + 2 * step_y + 20
draw.rounded_rectangle(
    [seal_x, seal_y, seal_x + seal_size, seal_y + seal_size],
    radius=10,
    fill=(177, 37, 44, 235),
    outline=(226, 196, 137, 255),
    width=2,
)

seal_font = ImageFont.truetype(r"C:\Windows\Fonts\STKAITI.TTF", 44)
seal_bbox = seal_font.getbbox("结")
seal_w = seal_bbox[2] - seal_bbox[0]
seal_h = seal_bbox[3] - seal_bbox[1]
draw.text(
    (
        seal_x + (seal_size - seal_w) // 2 - seal_bbox[0],
        seal_y + (seal_size - seal_h) // 2 - seal_bbox[1],
    ),
    "结",
    font=seal_font,
    fill=(245, 238, 222, 255),
)

out = r"E:\AI\工作\my-knowledge\01-项目\缘结守\艺术字-缘结守-黑屏-艺术版.png"
img.convert("RGB").save(out)
print(out)
