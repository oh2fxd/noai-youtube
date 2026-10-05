import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = '/home/oh2fxd/toolbox/python/noai'
STORE_DIR = os.path.join(BASE_DIR, 'store_assets')
ICON_PATH = os.path.join(STORE_DIR, 'store_icon_128x128.png')

def draw_promo_small():
    W, H = 440, 280
    canvas = Image.new('RGBA', (W, H), (15, 23, 42, 255)) # slate-900
    draw = ImageDraw.Draw(canvas)

    # Ambient background glow
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([W//2 - 160, H//2 - 140, W//2 + 160, H//2 + 140], fill=(225, 29, 72, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    canvas = Image.alpha_composite(canvas, glow)
    draw = ImageDraw.Draw(canvas)

    # Outer border accent
    draw.rectangle([0, 0, W-1, H-1], outline=(244, 63, 94, 180), width=2)

    # Load & Paste Logo
    if os.path.exists(ICON_PATH):
        logo = Image.open(ICON_PATH).convert('RGBA')
        logo = logo.resize((96, 96), Image.Resampling.LANCZOS)
        canvas.paste(logo, (30, H//2 - 48), logo)

    # Text content
    # Title
    tx = 145
    draw.text((tx, 65), "NoAI for YouTube", fill=(255, 255, 255, 255), font_size=24)
    draw.text((tx, 100), "AI Video & Music Filter", fill=(244, 63, 94, 255), font_size=16)

    # Features
    draw.text((tx, 140), "• Visual AI Badges & Disclosures", fill=(226, 232, 240, 240), font_size=13)
    draw.text((tx, 162), "• 1-Click Channel Blocking", fill=(226, 232, 240, 240), font_size=13)
    draw.text((tx, 184), "• Tag, Hide, or Blur Modes", fill=(226, 232, 240, 240), font_size=13)

    # Footer badge
    draw.rounded_rectangle([tx, 215, tx + 245, 242], radius=6, fill=(30, 41, 59, 255), outline=(244, 63, 94, 150), width=1)
    draw.text((tx + 12, 221), "🔒 100% On-Device  • Zero Tracking", fill=(253, 164, 175, 255), font_size=11)

    out_path = os.path.join(STORE_DIR, 'promo_small_440x280.png')
    canvas.save(out_path, 'PNG')
    print(f"Generated {out_path}")

def draw_promo_marquee():
    W, H = 1400, 560
    canvas = Image.new('RGBA', (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(canvas)

    # Background gradient lighting
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([100, -100, 700, 500], fill=(225, 29, 72, 80))
    g_draw.ellipse([900, 100, 1500, 700], fill=(136, 19, 55, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    canvas = Image.alpha_composite(canvas, glow)
    draw = ImageDraw.Draw(canvas)

    # Subtle grid lines
    grid = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gr_draw = ImageDraw.Draw(grid)
    for x in range(0, W, 70):
        gr_draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 12), width=1)
    for y in range(0, H, 70):
        gr_draw.line([(0, y), (W, y)], fill=(255, 255, 255, 12), width=1)
    canvas = Image.alpha_composite(canvas, grid)
    draw = ImageDraw.Draw(canvas)

    # Border
    draw.rectangle([0, 0, W-1, H-1], outline=(244, 63, 94, 200), width=3)

    # Large Logo on left
    if os.path.exists(ICON_PATH):
        logo = Image.open(ICON_PATH).convert('RGBA')
        logo = logo.resize((220, 220), Image.Resampling.LANCZOS)
        canvas.paste(logo, (100, H//2 - 110), logo)

    # Text Block
    tx = 360
    draw.text((tx, 130), "NoAI for YouTube", fill=(255, 255, 255, 255), font_size=58)
    draw.text((tx, 205), "Reclaim Your Feed from AI Content Farms & Synthetic Slop", fill=(244, 63, 94, 255), font_size=26)

    # Bullet point cards
    bullets = [
        ("🏷️ Prominent AI Badges", "Detects Suno, Udio, ElevenLabs, Sora & official YouTube labels"),
        ("🚫 1-Click Channel Block", "Permanently filter synthetic media channels directly in your feed"),
        ("🛡️ 100% Privacy-First", "Zero remote requests, zero analytics, complete local control")
    ]

    by = 275
    for title, desc in bullets:
        # Card container
        draw.rounded_rectangle([tx, by, tx + 880, by + 65], radius=10, fill=(30, 41, 59, 230), outline=(255, 255, 255, 30), width=1)
        draw.text((tx + 20, by + 12), title, fill=(255, 255, 255, 255), font_size=18)
        draw.text((tx + 20, by + 37), desc, fill=(203, 213, 225, 240), font_size=14)
        by += 78

    out_path = os.path.join(STORE_DIR, 'promo_marquee_1400x560.png')
    canvas.save(out_path, 'PNG')
    print(f"Generated {out_path}")

if __name__ == '__main__':
    draw_promo_small()
    draw_promo_marquee()
