"""SK Mahbub Fiverr intro — v5.

Text + shape treatment from v2 (white/blue gradient hero words behind the speaker,
Playfair italic lead-ins, white Montserrat captions). Layout from v4: glossy tiles
floating behind the speaker, now white/blue, with official full-colour platform
logos (GA4, GTM, Google Ads, Meta Pixel, Meta CAPI, server-side, + TikTok, Snapchat,
X, LinkedIn, Clarity) synced to speech.
"""
import io, math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render2 as r2
import chips as chipmod
import cairosvg

W, H = r2.W, r2.H
ease_out, ease_io = r2.ease_out, r2.ease_io
def ease_back(t, s=1.7):
    t = min(1, max(0, t)); t -= 1; return t * t * ((s + 1) * t + s) + 1
def alpha_mul(im, a):
    if a >= 0.999: return im
    arr = np.array(im); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); return Image.fromarray(arr)

r2.ICONS = []

# hero handover: when the next hero word starts, the previous one is gone (no cross-fade clutter)
_draw_hero = r2.draw_hero
def draw_hero(layer, t, h, front):
    i = r2.HEROES.index(h)
    if i + 1 < len(r2.HEROES):
        nxt = r2.HEROES[i + 1][0]
        if nxt - h[2] < 0.35 and t >= nxt - 0.03: return False
    return _draw_hero(layer, t, h, front)
r2.draw_hero = draw_hero   # replaced by the blue concept tiles below

# ---------------- logo rendering ----------------
def svg_png(path, size, fill=None):
    svg = open(path).read()
    if fill: svg = re.sub(r"<svg ", f'<svg fill="{fill}" ', svg, count=1)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")
def logo(name, size): return svg_png(f"{HERE}/icons/L_{name}.svg", size)

def recolor(glyph, rgb):
    out = Image.new("RGBA", glyph.size, rgb + (0,)); out.putalpha(glyph.split()[3]); return out

def snap_logo(S):
    y = svg_png(f"{HERE}/icons/snapchat.svg", S, "#FFFC00"); k = svg_png(f"{HERE}/icons/snapchat.svg", S, "#111111").filter(ImageFilter.MaxFilter(7))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0)); out.alpha_composite(k); out.alpha_composite(y); return out

# ---------------- glossy tile ----------------
S, PAD = 220, 70
def face_white(S):
    y = np.linspace(0, 1, S)[:, None, None]
    c = np.array((255, 255, 255)) * (1 - y) + np.array((226, 236, 250)) * y
    return Image.fromarray(np.repeat(c, S, axis=1).astype(np.uint8), "RGB")
def face_blue(S): return r2.texture(S, S)

def tile_base(face, glow=(80, 140, 255)):
    T = S + 2 * PAD
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), int(S * 0.24), fill=255)
    big = Image.new("L", (T, T), 0); big.paste(m, (PAD, PAD))
    out = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    g = Image.new("RGBA", (T, T), glow + (0,)); g.putalpha(big.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.75)))
    out.alpha_composite(g)
    sh = Image.new("RGBA", (T, T), (10, 20, 50, 0)); sh.putalpha(big.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v // 3))
    out.alpha_composite(sh, (0, 12))
    f = Image.new("RGBA", (S, S), (0, 0, 0, 0)); f.paste(face, (0, 0), m)
    hl = Image.new("L", (S, S), 0); ImageDraw.Draw(hl).ellipse((-S * 0.3, -S * 0.75, S * 1.3, S * 0.42), fill=60)
    hl = Image.fromarray((np.asarray(hl.filter(ImageFilter.GaussianBlur(10)), np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8))
    wh = Image.new("RGBA", (S, S), (255, 255, 255, 0)); wh.putalpha(hl); f.alpha_composite(wh)
    ImageDraw.Draw(f).rounded_rectangle((1, 1, S - 2, S - 2), int(S * 0.24), outline=(255, 255, 255, 110), width=3)
    out.alpha_composite(f, (PAD, PAD))
    return out

def place(base, img, scale=0.58, dx=0, dy=0):
    gs = int(S * scale)
    im = img.copy(); im.thumbnail((gs, gs), Image.LANCZOS)
    base.alpha_composite(im, (PAD + (S - im.width) // 2 + dx, PAD + (S - im.height) // 2 + dy))

def badge(base, img, size=74):
    b = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.ellipse((0, 0, size - 1, size - 1), fill=(255, 255, 255, 255), outline=(200, 215, 240, 255), width=2)
    im = img.copy(); im.thumbnail((int(size * 0.62), int(size * 0.62)), Image.LANCZOS)
    b.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    sh = Image.new("RGBA", (size + 30, size + 30), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((15, 20, size + 15, size + 25), fill=(0, 0, 0, 90))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (PAD + S - size + 4 - 15, PAD + S - size + 4 - 15))
    base.alpha_composite(b, (PAD + S - size + 4, PAD + S - size + 4))

def label(base, text):
    f = r2.mont(700, 30)
    tw = int(f.getlength(text))
    T = base.width
    out = Image.new("RGBA", (max(T, tw + 60), base.height + 56), (0, 0, 0, 0))
    out.alpha_composite(base, ((out.width - T) // 2, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((out.width / 2, PAD + S + 40), text, font=f, fill=(0, 0, 0, 220), anchor="mm")
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(out).text((out.width / 2, PAD + S + 36), text, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return out

STATIC = {}
def brand_tile(kind):
    if kind in STATIC: return STATIC[kind]
    b = tile_base(face_white(S))
    if kind == "ga4": place(b, logo("google-analytics", 300), 0.56); lab = "Google Analytics 4"
    elif kind == "gtm": place(b, logo("google-tag-manager", 300), 0.58); lab = "Google Tag Manager"
    elif kind == "gads": place(b, logo("google-ads", 300), 0.60); lab = "Google Ads"
    elif kind == "meta": place(b, logo("meta-icon", 300), 0.64); lab = "Meta Pixel"
    elif kind == "meta_ads": place(b, logo("meta-icon", 300), 0.64); lab = "Meta Ads"
    elif kind == "tiktok": place(b, logo("tiktok-icon", 300), 0.52); lab = "TikTok"
    elif kind == "snapchat": place(b, snap_logo(300), 0.56); lab = "Snapchat"
    elif kind == "x": place(b, logo("x", 300), 0.46); lab = "X (Twitter)"
    elif kind == "linkedin": place(b, logo("linkedin-icon", 300), 0.56); lab = "LinkedIn"
    STATIC[kind] = label(b, lab)
    return STATIC[kind]

# animated tiles (glyph re-drawn each frame)
ANIM = {
    "capi":   dict(face="white", glyph="capi", color=(8, 102, 255), badge="meta-icon", label="Conversion API"),
    "server": dict(face="white", glyph="server", color=(37, 99, 235), badge="google-cloud", label="Server-side Tracking"),
    "clarity": dict(face="white", glyph="clarity", color=(91, 95, 239), badge="microsoft-icon", label="Microsoft Clarity"),
    "chart":  dict(face="blue", glyph="ga4"), "target": dict(face="blue", glyph="adsconv"),
    "issue":  dict(face="blue", glyph="issue"), "mismatch": dict(face="blue", glyph="mismatch"), "dedup": dict(face="blue", glyph="dedup"),
    "trend":  dict(face="blue", glyph="gads"), "funnel": dict(face="blue", glyph="funnel"), "chat": dict(face="blue", glyph="chat"),
}
ABASE = {}
def funnel_glyph(p, s=84):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255)
    d.polygon([(14, 22), (70, 22), (48, 46), (48, 70), (36, 63), (36, 46)], fill=c)
    for k in range(3):
        q = ((p * 0.9 + k / 3) % 1); y = 2 + 14 * q
        d.ellipse((39 + (k - 1) * 11, y, 45 + (k - 1) * 11, y + 6), fill=(255, 255, 255, int(255 * (1 - q))))
    return im
def chat_glyph(p, s=84):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255)
    d.rounded_rectangle((10, 16, 74, 58), 16, outline=c, width=5); d.polygon([(24, 56), (22, 74), (40, 57)], fill=c)
    for i in range(3):
        b = 0.5 + 0.5 * math.sin(p * 6 - i * 0.9)
        d.ellipse((28 + i * 14 - 4, 37 - 4 - 3 * b, 28 + i * 14 + 4, 37 + 4 - 3 * b), fill=c)
    return im

def anim_tile(kind, p):
    a = ANIM[kind]
    if kind not in ABASE:
        b = tile_base(face_white(S) if a["face"] == "white" else face_blue(S))
        if a.get("badge"): badge(b, logo(a["badge"], 200))
        ABASE[kind] = b
    b = ABASE[kind].copy()
    g = funnel_glyph(p) if a["glyph"] == "funnel" else chat_glyph(p) if a["glyph"] == "chat" else chipmod.glyph(a["glyph"], p, 84)
    g = g.resize((168, 168), Image.LANCZOS)
    if a.get("color"): g = recolor(g, a["color"])
    b.alpha_composite(g, (PAD + (S - 168) // 2 - (8 if a.get("badge") else 0), PAD + (S - 168) // 2 - (8 if a.get("badge") else 0)))
    return label(b, a["label"]) if a.get("label") else b

def get_tile(kind, p):
    return anim_tile(kind, p) if kind in ANIM else brand_tile(kind)

# ---------------- timeline ----------------
SLOT = {"A": (560, 255, 0.95), "B": (1360, 255, 0.95), "C": (300, 600, 0.85), "D": (1620, 600, 0.85),
        "E": (960, 120, 0.72), "L2": (330, 860, 0.7), "R2": (1590, 860, 0.72)}
FLOAT = [
    (3.08, 4.18, "chart", "C"), (4.62, 5.22, "target", "D"),
    (14.48, 18.66, "issue", "C"), (15.62, 18.66, "mismatch", "D"), (17.32, 18.66, "dedup", "L2"),
    (21.08, 25.18, "ga4", "A"), (22.06, 25.18, "meta", "B"), (22.42, 25.18, "capi", "D"), (23.30, 25.18, "gads", "C"),
    (25.24, 29.36, "tiktok", "A"), (25.70, 29.36, "snapchat", "B"), (26.30, 29.36, "x", "C"), (26.58, 29.36, "linkedin", "D"),
    (28.28, 29.36, "clarity", "R2"),
    (30.30, 32.92, "gtm", "A"), (31.22, 32.92, "server", "B"),
    (32.94, 35.50, "gads", "C"), (34.10, 35.50, "meta_ads", "D"),
    (38.66, 41.98, "funnel", "C"), (39.80, 41.98, "trend", "D"),
    (48.52, r2.VID_END, "chat", "D"),
]

class Floaters:
    def draw(self, layer, t, wide):
        hit = False
        for i, (t0, t1, kind, slot) in enumerate(FLOAT):
            if not (t0 - 0.02 <= t <= t1 + 0.3): continue
            p = t - t0
            e = ease_back(p / 0.5, 1.8); a = min(1, p / 0.15)
            if t > t1:
                q = ease_io((t - t1) / 0.3); a *= 1 - q; e *= 1 - 0.2 * q
            if a <= 0.01: continue
            cx, cy, sc = SLOT[slot]
            im = get_tile(kind, p)
            s = max(0.05, sc * e)
            rot = -8 * (1 - min(1, e)) + 1.8 * math.sin(t * 1.6 + i)
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC).rotate(rot, Image.BICUBIC, expand=True)
            im = alpha_mul(im, a)
            bob = 8 * math.sin(t * 2.2 + i * 1.3)
            layer.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + bob + 36 * (1 - min(1, e)))))
            hit = True
        return hit
r2.CHIPS = Floaters()

if __name__ == "__main__":
    r2.main()
