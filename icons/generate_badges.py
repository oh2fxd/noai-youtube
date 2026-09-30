import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('/home/oh2fxd/toolbox/python/noai/icons', exist_ok=True)

# 1. Generate Big AI Badge (PNG) - 120x44px for sharp rendering
w, h = 160, 48
ai_badge = Image.new('RGBA', (w, h), (0, 0, 0, 0))
draw = ImageDraw.Draw(ai_badge)

# Glowing gradient background
draw.rounded_rectangle([2, 2, w-2, h-2], radius=10, fill=(225, 29, 72, 245), outline=(255, 255, 255, 220), width=2)

# Inner accent border
draw.rounded_rectangle([5, 5, w-5, h-5], radius=8, outline=(253, 164, 175, 180), width=1)

# Draw Lightning bolt / sparkle symbol on left
# Sparkle polygon
draw.polygon([(20, 10), (25, 22), (37, 24), (27, 32), (30, 42), (20, 35), (10, 42), (13, 32), (3, 24), (15, 22)], fill=(255, 255, 255, 255))

# Draw bold text "AI GENERATED"
# Let's draw stylized block letters for maximum clarity
# "AI"
draw.rectangle([45, 12, 53, 36], fill=(255, 255, 255, 255))
draw.rectangle([53, 12, 65, 18], fill=(255, 255, 255, 255))
draw.rectangle([53, 21, 62, 26], fill=(255, 255, 255, 255))
draw.rectangle([65, 12, 73, 36], fill=(255, 255, 255, 255))

# Letter I
draw.rectangle([80, 12, 88, 36], fill=(255, 255, 255, 255))

# Word "MEDIA" or dot
draw.ellipse([98, 22, 104, 28], fill=(255, 255, 255, 255))

# Draw badge label
ai_badge.save('/home/oh2fxd/toolbox/python/noai/icons/ai-badge.png', 'PNG')
print("Generated ai-badge.png")

# 2. Generate NO AI Block Logo (PNG) - Circular prohibition sign with "NO AI"
size = 64
no_ai = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw2 = ImageDraw.Draw(no_ai)

# Dark backing disc for contrast over any thumbnail
draw2.ellipse([2, 2, size-2, size-2], fill=(15, 23, 42, 230))

# Red prohibition ring
draw2.ellipse([5, 5, size-5, size-5], outline=(225, 29, 72, 255), width=5)

# Diagonal red slash
draw2.line([(12, size-12), (size-12, 12)], fill=(225, 29, 72, 255), width=5)

# Text "AI" in center in bold white
# Draw 'A'
draw2.line([(22, 42), (28, 22)], fill=(255, 255, 255, 240), width=3)
draw2.line([(28, 22), (34, 42)], fill=(255, 255, 255, 240), width=3)
draw2.line([(24, 34), (32, 34)], fill=(255, 255, 255, 240), width=3)

# Draw 'I'
draw2.line([(42, 22), (42, 42)], fill=(255, 255, 255, 240), width=3)

no_ai.save('/home/oh2fxd/toolbox/python/noai/icons/no-ai-block.png', 'PNG')
print("Generated no-ai-block.png")

