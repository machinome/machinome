"""Spike helper: one comparison sheet, viewer snapshot beside the asset page and Blender.

usage: compose.py SITE_DIR
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

site = sys.argv[1]
rows = [
    ('Home', 'viewer-home.png', 'captures/asset-home.png', 'blender/blender-home.png'),
    ('Park', 'viewer-park.png', 'captures/asset-park.png', 'blender/blender-park-clip.png'),
    ('Place', 'viewer-place.png', 'captures/asset-place.png', None),
]
cols = ['machinome viewer (1.46 M triangles)', 'asset page, stock glTF loader (100 k)', 'Blender 4.2 import, Cycles (100 k)']
W, H, PAD, HEAD = 450, 350, 10, 28
font = ImageFont.load_default()
sheet = Image.new('RGB', (PAD + 3 * (W + PAD), HEAD + len(rows) * (H + HEAD + PAD)), 'white')
d = ImageDraw.Draw(sheet)
for c, label in enumerate(cols):
    d.text((PAD + c * (W + PAD), 8), label, fill='black', font=font)
for r, (name, *files) in enumerate(rows):
    y = HEAD + r * (H + HEAD + PAD)
    d.text((PAD, y + 6), name, fill='black', font=font)
    for c, f in enumerate(files):
        x = PAD + c * (W + PAD)
        if not f or not os.path.exists(os.path.join(site, f)):
            d.rectangle([x, y + HEAD, x + W, y + HEAD + H], outline='#ccc')
            d.text((x + 10, y + HEAD + 10), 'not rendered', fill='#888', font=font)
            continue
        im = Image.open(os.path.join(site, f)).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im).convert('RGB')
        im.thumbnail((W, H))
        sheet.paste(im, (x + (W - im.width) // 2, y + HEAD + (H - im.height) // 2))
out = os.path.join(site, 'comparison.png')
sheet.save(out)
print('wrote', out, sheet.size)
