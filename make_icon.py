from PIL import Image, ImageDraw
import math

def make_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rect background — soft blue gradient feel
    margin = size // 8
    radius = size // 6

    # Base rounded rect (light blue)
    r1 = 100
    g1 = 180
    b1 = 255
    draw.rounded_rectangle(
        [margin, margin + size//16, size - margin, size - margin],
        radius=radius,
        fill=(r1, g1, b1, 230)
    )

    # Top clip board tab
    tab_w = size // 3
    tab_h = size // 12
    tab_x = (size - tab_w) // 2
    tab_y = margin - size // 24
    tab_r = tab_h // 2
    draw.rounded_rectangle(
        [tab_x, tab_y, tab_x + tab_w, tab_y + tab_h],
        radius=tab_r,
        fill=(70, 140, 210, 240)
    )

    # White text lines on the board
    line_color = (255, 255, 255, 230)
    line_h = max(2, size // 32)
    line_spacing = size // 9
    line_left = margin + size // 10
    line_right = size - margin - size // 10
    line_start_y = margin + size//16 + size // 8

    for i in range(3):
        y = line_start_y + i * line_spacing
        w = line_right - line_left if i < 2 else (line_right - line_left) * 2 // 3
        draw.rounded_rectangle(
            [line_left, y, line_left + w, y + line_h],
            radius=line_h // 2,
            fill=line_color
        )

    return img

# Generate multiple sizes for .ico
sizes = [16, 24, 32, 48, 64, 128, 256]
images = [make_icon(s) for s in sizes]

# Save as .ico
ico_path = r"D:\剪贴板\clipboard_icon.ico"
images[0].save(ico_path, format='ICO', sizes=[(s, s) for s in sizes], append_images=images[1:])

# Also save a large PNG for reference
make_icon(512).save(r"D:\剪贴板\clipboard_icon.png")

print(f"Icon saved to {ico_path}")
