import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
F = "fonts/"
INK = (23, 43, 38); TEAL = (13, 148, 136); WHITE = (255, 255, 255)

# background: #FFFFFF -> #F6FBF9 -> #E6F3EE, soft mint glow, very faint grid
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
top = np.array([255, 255, 255.]); mid = np.array([0xF6, 0xFB, 0xF9]); bot = np.array([0xE6, 0xF3, 0xEE])
v = (yy / H)[..., None]
g = np.where(v < 0.45, top + (mid - top) * (v / 0.45), mid + (bot - mid) * ((v - 0.45) / 0.55))
glow = np.exp(-(((xx - 540) / 620) ** 2 + ((yy - 900) / 700) ** 2))
g = g * (1 - 0.08 * glow[..., None]) + np.array([222, 242, 235]) * 0.08 * glow[..., None]
P = 72
grid = ((np.abs((xx % P) - P / 2) > P / 2 - 1) | (np.abs((yy % P) - P / 2) > P / 2 - 1)).astype(np.float32)
fade = 0.22 * (1 - 0.6 * glow)          # grid quieter behind the headline
g = g * (1 - (grid * fade)[..., None]) + np.array([0xCF, 0xE5, 0xDC]) * (grid * fade)[..., None]
img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img)

def fnt(n, s): return ImageFont.truetype(F + n, s)
XB, BD, MD = "Poppins-ExtraBold.ttf", "Poppins-Bold.ttf", "Poppins-SemiBold.ttf"

def w_(t, fo, tr): return sum(fo.getlength(c) for c in t) + tr * (len(t) - 1)
def line(y, t, fo, col, tr=0.0):
    x = W / 2 - w_(t, fo, tr) / 2
    for c in t:
        d.text((x, y), c, font=fo, fill=col, anchor="ls"); x += fo.getlength(c) + tr

# --- headline (exact wording), stacked for mobile ---
y = 400
line(y, "Spending", fnt(BD, 92), INK, -2)
y += 258
line(y, "$50", fnt(XB, 250), TEAL, -8)
y += 104
line(y, "or", fnt(MD, 84), INK, -1)
y += 228
line(y, "$4,000", fnt(XB, 224), TEAL, -8)
y += 134
line(y, "a Month on Ads?", fnt(BD, 88), INK, -2)
y += 60
d.rounded_rectangle([W / 2 - 50, y, W / 2 + 50, y + 7], 4, fill=TEAL)
y += 112
line(y, "Check This", fnt(BD, 82), INK, -2)
fo = fnt(XB, 82); t = "BEFORE YOU SCALE."; tr = -2
tw = w_(t, fo, tr)
by0 = y + 30
d.rounded_rectangle([W / 2 - tw / 2 - 36, by0, W / 2 + tw / 2 + 36, by0 + 118], 26, fill=INK)
line(by0 + 89, t, fo, WHITE, tr)
print("content spans y", 400 - 100, "to", by0 + 138, "| block width", int(tw + 72))

out = img.convert("RGB")
out.save("thumb/Reel_Cover_1080x1920.png", optimize=True)
out.save("thumb/Reel_Cover_1080x1920.jpg", quality=95)
