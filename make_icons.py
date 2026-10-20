from PIL import Image, ImageDraw, ImageFilter
import os, numpy as np
os.makedirs('www/icons', exist_ok=True)
egg = Image.open('/home/claude/cos/egg_idle_full.png').convert('RGBA')
def grad(size):
    y, x = np.mgrid[0:size, 0:size]
    t = ((x + y) / (2 * size))[..., None]
    a = np.array([255, 214, 196]); b = np.array([180, 200, 246])
    rgb = (a * (1 - t) + b * t).astype('uint8')
    return Image.fromarray(np.dstack([rgb, np.full((size, size), 255, 'uint8')]), 'RGBA')
def icon(size, pad, path, round_=True):
    bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    mask = Image.new('L', (size, size), 0); d = ImageDraw.Draw(mask)
    if round_: d.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * .22), fill=255)
    else: d.rectangle((0, 0, size, size), fill=255)
    bg.paste(grad(size), (0, 0), mask)
    s = int(size * (1 - 2 * pad)); e = egg.resize((s, s), Image.LANCZOS)
    sh = Image.new('RGBA', (size, size), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((size*.3, size*(1-pad)-size*.05, size*.7, size*(1-pad)+size*.02), fill=(44, 42, 74, 70))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * .02))); bg.alpha_composite(e, ((size - s) // 2, int(size * pad * .7)))
    bg.save(path)
icon(512, .1, 'www/icons/icon-512.png'); icon(192, .1, 'www/icons/icon-192.png')
icon(512, .2, 'www/icons/maskable-512.png', False); icon(180, .1, 'www/icons/apple-touch-icon.png', False)
icon(64, .06, 'www/icons/favicon.png')
# android adaptive foreground (108dp grid, safe zone 66dp) and splash
fg = Image.new('RGBA', (432, 432), (0, 0, 0, 0)); e = egg.resize((260, 260), Image.LANCZOS); fg.alpha_composite(e, (86, 80)); fg.save('icon_fg.png')
sp = grad(1080).resize((1080, 1920)); e = egg.resize((420, 420), Image.LANCZOS); sp.alpha_composite(e, (330, 700)); sp.save('splash.png')
print('ok')
