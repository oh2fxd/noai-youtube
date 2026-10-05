import os
import math
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = '/home/oh2fxd/toolbox/python/noai'
os.makedirs(os.path.join(BASE_DIR, 'icons'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'store_assets'), exist_ok=True)

def generate_icons():
    S = 1024 # Canvas resolution for supersampling
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))

    # 1. Soft Drop Glow under squircle background
    padding = 40
    r_box = [padding, padding, S - padding, S - padding]
    corner = 220

    glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle([padding+12, padding+20, S-padding-12, S-padding+12], radius=corner, fill=(225, 29, 72, 130))
    glow = glow.filter(ImageFilter.GaussianBlur(36))
    img = Image.alpha_composite(img, glow)

    # 2. Main Squircle Base (Rich Obsidian Gradient)
    base = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(base)
    b_draw.rounded_rectangle(r_box, radius=corner, fill=(15, 23, 42, 255)) # slate-900

    # Gradient highlight at top-left
    top_glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    tg_draw = ImageDraw.Draw(top_glow)
    tg_draw.ellipse([-S//4, -S//4, S, S//2], fill=(30, 41, 59, 255))
    tg_mask = Image.new('L', (S, S), 0)
    tm_draw = ImageDraw.Draw(tg_mask)
    tm_draw.rounded_rectangle(r_box, radius=corner, fill=255)
    top_glow = Image.composite(top_glow, Image.new('RGBA', (S, S), (0,0,0,0)), tg_mask)
    top_glow = top_glow.filter(ImageFilter.GaussianBlur(40))
    base = Image.alpha_composite(base, top_glow)

    img = Image.alpha_composite(img, base)
    draw = ImageDraw.Draw(img)

    # Outer border / stroke: Glowing Rose/Crimson
    draw.rounded_rectangle(r_box, radius=corner, outline=(244, 63, 94, 255), width=20)
    
    # Inner subtle rim highlight
    inner_box = [padding + 14, padding + 14, S - padding - 14, S - padding - 14]
    draw.rounded_rectangle(inner_box, radius=corner - 10, outline=(255, 255, 255, 45), width=6)

    # 3. Central Symbol: Prohibition Ring + AI Spark Star
    cx, cy = S // 2, S // 2
    outer_r = 310
    ring_w = 64

    # Red prohibition ring
    ring_box = [cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r]
    draw.ellipse(ring_box, outline=(225, 29, 72, 255), width=ring_w)

    # Inner sheen on red ring
    ring_sheen_box = [cx - outer_r + ring_w//2, cy - outer_r + ring_w//2, cx + outer_r - ring_w//2, cy + outer_r - ring_w//2]
    draw.ellipse(ring_sheen_box, outline=(255, 255, 255, 80), width=5)

    # 4. AI Spark Symbol in center
    spark_r = 165
    inner_c = 40
    star_poly = [
        (cx, cy - spark_r),
        (cx + inner_c, cy - inner_c),
        (cx + spark_r, cy),
        (cx + inner_c, cy + inner_c),
        (cx, cy + spark_r),
        (cx - inner_c, cy + inner_c),
        (cx - spark_r, cy),
        (cx - inner_c, cy - inner_c)
    ]
    
    # Draw Spark with soft glow
    spark_img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sp_draw = ImageDraw.Draw(spark_img)
    sp_draw.polygon(star_poly, fill=(255, 255, 255, 255))
    
    # AI side dots
    dot_r = 18
    sp_draw.ellipse([cx - 135 - dot_r, cy - 135 - dot_r, cx - 135 + dot_r, cy - 135 + dot_r], fill=(253, 164, 175, 255))
    sp_draw.ellipse([cx + 135 - dot_r, cy + 135 - dot_r, cx + 135 + dot_r, cy + 135 + dot_r], fill=(253, 164, 175, 255))
    
    img = Image.alpha_composite(img, spark_img)
    draw = ImageDraw.Draw(img)

    # 5. Bold 45-degree Prohibition Slash
    slash_w = 68
    d = int(outer_r * 0.707)
    x1, y1 = cx - d, cy - d
    x2, y2 = cx + d, cy + d

    # Dark contrast outline under slash
    draw.line([(x1 - 5, y1 + 5), (x2 - 5, y2 + 5)], fill=(15, 23, 42, 220), width=slash_w + 12)
    # Red slash
    draw.line([(x1, y1), (x2, y2)], fill=(225, 29, 72, 255), width=slash_w)
    # Central highlight on slash
    draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 95), width=6)

    # Save to all required icon destinations
    for sz in [128, 48, 16]:
        resized = img.resize((sz, sz), Image.Resampling.LANCZOS)
        dest_icon = os.path.join(BASE_DIR, 'icons', f'icon-{sz}.png')
        resized.save(dest_icon, 'PNG')
        print(f"Generated {dest_icon}")
        if sz == 128:
            dest_store = os.path.join(BASE_DIR, 'store_assets', 'store_icon_128x128.png')
            dest_root = os.path.join(BASE_DIR, 'store_icon_128.png')
            resized.save(dest_store, 'PNG')
            resized.save(dest_root, 'PNG')
            print(f"Generated {dest_store}")
            print(f"Generated {dest_root}")

if __name__ == '__main__':
    generate_icons()
