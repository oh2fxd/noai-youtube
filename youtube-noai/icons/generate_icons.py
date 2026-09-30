import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('/home/oh2fxd/toolbox/python/noai/icons', exist_ok=True)

def create_icon(size):
    # RGBA image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle/rounded rect in crimson/coral red
    padding = max(1, size // 16)
    r_box = [padding, padding, size - padding, size - padding]
    corner = max(3, size // 4)
    draw.rounded_rectangle(r_box, radius=corner, fill=(225, 29, 72, 255)) # rose-600

    # Draw a stylized "AI" crossed out or robot / sparkle crossed
    line_w = max(1, size // 9)
    
    # White "AI" text or symbol
    # For small sizes (16), simple cross over a dot or text
    # Draw a clean white diagonal cancellation slash across
    offset = size // 4
    # Draw "AI" text if size >= 32
    if size >= 48:
        # Draw central letters A and I or abstract geometric shapes
        # Draw "AI" in white
        # Let's draw an A: left leg, right leg, crossbar
        mid_x = size // 2
        text_y_top = size // 4
        text_y_bot = size - size // 3
        # Left letter 'A'
        a_left = size // 4
        a_mid = size // 2 - size // 10
        a_right = size // 2
        draw.line([(a_left, text_y_bot), (a_mid, text_y_top)], fill=(255, 255, 255, 240), width=line_w)
        draw.line([(a_mid, text_y_top), (a_right, text_y_bot)], fill=(255, 255, 255, 240), width=line_w)
        draw.line([(a_left + size//12, size // 2), (a_right - size//12, size // 2)], fill=(255, 255, 255, 240), width=line_w)
        
        # Right letter 'I'
        i_x = size - size // 3
        draw.line([(i_x, text_y_top), (i_x, text_y_bot)], fill=(255, 255, 255, 240), width=line_w)
    elif size == 16:
        # Just simple stylized shape
        draw.ellipse([size//4, size//4, size - size//4, size - size//4], outline=(255, 255, 255, 255), width=1)

    # Diagonal red/white slash across
    slash_color = (255, 255, 255, 255) if size == 16 else (15, 23, 42, 240)
    draw.line([(padding + 1, size - padding - 1), (size - padding - 1, padding + 1)], fill=slash_color, width=line_w)

    img.save(f'/home/oh2fxd/toolbox/python/noai/icons/icon-{size}.png', 'PNG')
    print(f"Generated icon-{size}.png")

for s in [16, 48, 128]:
    create_icon(s)
