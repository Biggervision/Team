import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
F = "fonts/"
WHITE = (0xF6, 0xFB, 0xF9); SOFT = (0xE6, 0xF3, 0xEE); TEAL = (13, 148, 136); TEAL_L = (45, 180, 166)

# cinematic dark background: forest-tinted black, top spotlight, vignette, grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.array([0x11, 0x22, 0x1E])
spot = np.exp(-(((xx - 540) / 620) ** 2 + ((yy - 520) / 820) ** 2))
beam = np.exp(-((xx - 540) / (260 + yy * 0.32)) ** 2) * np.clip(1 - yy / 1500, 0, 1)
g = base + np.array([0x17 - 0x11 + 22, 0x2B - 0x22 + 34, 0x26 - 0x1E + 30.]) * spot[..., None] + np.array([16, 26, 23.]) * (beam * 0.5)[..., None]
r = np.sqrt(((xx - 540) / 760) ** 2 + ((yy - 900) / 1150) ** 2)
g *= np.clip(1.12 - 0.45 * r ** 2, 0.55, 1)[..., None]
rng = np.random.default_rng(3)
g += rng.normal(0, 4.5, (H, W, 1))
img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")

def fnt(n, s, var=None):
    f = ImageFont.truetype(F + n, s)
    if var: f.set_variation_by_name(var)
    return f
XB, MD = "Poppins-ExtraBold.ttf", "Poppins-Medium.ttf"
SERIF = "Playfair-Italic.ttf"

text = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(text)
def w_(t, fo, tr): return sum(fo.getlength(c) for c in t) + tr * (len(t) - 1)
def line(y, t, fo, col, tr=0.0):
    x = W / 2 - w_(t, fo, tr) / 2
    for c in t:
        d.text((x, y), c, font=fo, fill=col, anchor="ls"); x += fo.getlength(c) + tr

y = 420
line(y, "SPENDING", fnt(MD, 54), SOFT, 14)
y += 262
line(y, "$50", fnt(XB, 250), WHITE, -9)
y += 112
line(y, "or", fnt(SERIF, 120, "Italic"), TEAL_L, 0)
y += 232
line(y, "$4,000", fnt(XB, 228), WHITE, -9)
y += 118
line(y, "a Month on Ads?", fnt(MD, 72), SOFT, -1)
# hairline rules framing the turn
y += 70
d.line([(W / 2 - 300, y), (W / 2 - 40, y)], fill=SOFT + (110,), width=2)
d.line([(W / 2 + 40, y), (W / 2 + 300, y)], fill=SOFT + (110,), width=2)
d.ellipse([W / 2 - 6, y - 6, W / 2 + 6, y + 6], fill=TEAL_L)
y += 128
line(y, "Check This", fnt(SERIF, 104, "Italic"), WHITE, 0)
y += 136
fo = fnt(XB, 84); tw = w_("BEFORE YOU SCALE.", fo, 1)
d.rounded_rectangle([W / 2 - tw / 2 - 36, y - 88, W / 2 + tw / 2 + 36, y + 32], 24, fill=TEAL)
line(y, "BEFORE YOU SCALE.", fo, WHITE, 1)
y += 32
print("content y 360 ->", y + 38, "| widest", int(tw))

# soft glow behind the type for a premium lift
glow = text.split()[3].filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.22))
gl = Image.new("RGBA", (W, H), (0xE6, 0xF3, 0xEE, 0)); gl.putalpha(glow)
img.alpha_composite(gl)
img.alpha_composite(text)

out = img.convert("RGB")
out.save("thumb/Reel_Cover_Iman_Style_Brand_1080x1920.png", optimize=True)
