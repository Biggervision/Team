"""SK Mahbub Fiverr intro — v4 'floating apps + gold captions' (new reference screenshot).

- Two-tier captions in front: white line on top, bigger glowing GOLD keyword line below.
- Glossy app-icon tiles (brand + concept) float BEHIND the speaker, synced to speech,
  with pop-in overshoot, gentle bob and coloured glow.
- No hero words / chips; same footage pipeline, cuts and end card as v2.
"""
import io, math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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
IFONT = lambda w, s: ImageFont.truetype(f"{HERE}/fonts/inter/extras/ttf/InterDisplay-{w}.ttf", s)

# ======================= captions =======================
# (t_top, top_text, t_bottom, gold_text)
BEATS = [
    (0.00, "growing your", 0.44, "business"),
    (1.08, "takes more than just", 1.80, "running ads"),
    (2.86, "you need", 3.08, "accurate data"),
    (4.22, "the right", 4.62, "strategy"),
    (5.26, "and a clear", 5.90, "understanding"),
    (6.42, "of what drives", 7.72, "results"),
    (8.40, "this is", 8.68, "SK Mahbub"),
    (9.14, "a", 9.34, "web analytics"),
    (9.92, "conversion tracking &", 11.16, "paid advertising"),
    (12.26, "", 12.26, "consultant"),
    (13.38, "I help businesses", 14.08, "fix tracking issues"),
    (15.38, "resolve conversion", 16.02, "mismatches"),
    (17.02, "eliminate", 17.32, "duplicate events"),
    (18.72, "and build reliable", 19.54, "tracking systems"),
    (20.44, "using", 21.08, "Google Analytics"),
    (22.06, "Meta Pixel", 22.42, "Conversion API"),
    (23.30, "Google Ads", 23.66, "conversion tracking"),
    (25.24, "TikTok · Snapchat", 26.30, "X · LinkedIn"),
    (26.90, "tracking setup", 28.28, "Microsoft Clarity"),
    (29.38, "and other essential", 31.22, "tracking tools"),
    (32.00, "combined with", 32.94, "Google Ads"),
    (34.10, "Meta Ads", 34.68, "optimization"),
    (35.56, "this helps you make", 37.16, "smarter decisions"),
    (38.06, "generate more", 38.66, "qualified leads"),
    (39.56, "increase", 39.80, "sales"),
    (40.46, "and grow your", 41.30, "business"),
    (42.02, "let's fix what's holding", 43.54, "your marketing back"),
    (44.22, "and turn", 45.24, "better data"),
    (45.72, "into better", 46.62, "business results"),
    (48.00, "need better", 48.52, "tracking"),
    (48.92, "and stronger", 50.12, "ad performance?"),
    (51.18, "let's", 51.34, "talk."),
]
ENDS = [BEATS[i + 1][0] for i in range(len(BEATS) - 1)] + [r2.VID_END]
# shorten beats that would linger across long pauses
ENDS = [min(e, max(b[2] + 1.6, b[0] + 1.2)) if e - b[2] > 2.0 else e for e, b in zip(ENDS, BEATS)]

GOLD = [(255, 228, 160), (246, 178, 72), (214, 122, 26)]
def gold_fill(w, h):
    y = np.linspace(0, 1, h)[:, None, None]
    c = np.where(y < 0.5, np.array(GOLD[0]) * (1 - y * 2) + np.array(GOLD[1]) * (y * 2),
                 np.array(GOLD[1]) * (2 - y * 2) + np.array(GOLD[2]) * (y * 2 - 1))
    return Image.fromarray(np.repeat(c, w, axis=1).astype(np.uint8), "RGB")

LCACHE = {}
def line_img(text, kind):
    key = (text, kind)
    if key in LCACHE: return LCACHE[key]
    size = 92 if kind == "top" else 128
    f = IFONT("SemiBold" if kind == "top" else "Bold", size)
    while f.getlength(text) > 1350 and size > 50:
        size -= 4; f = IFONT("SemiBold" if kind == "top" else "Bold", size)
    bb = f.getbbox(text); pad = 50
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (20, 10, 0, 0)); sh.putalpha(m.point(lambda v: v * 200 // 255))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (0, 6))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), (0, 3))
    if kind == "gold":
        rim = Image.new("RGBA", (w, h), (70, 30, 0, 0)); rim.putalpha(m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, int(v * 1.1))))
        out.alpha_composite(rim, (0, 3))
        glow = Image.new("RGBA", (w, h), (255, 150, 40, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(20)).point(lambda v: min(255, int(v * 1.1))))
        out.alpha_composite(glow)
        body = Image.new("RGBA", (w, h), (0, 0, 0, 0)); body.paste(gold_fill(w, h), (0, 0), m)
        out.alpha_composite(body)
    else:
        body = Image.new("RGBA", (w, h), (255, 255, 255, 0)); body.putalpha(m); out.alpha_composite(body)
    LCACHE[key] = (out, pad, bb[3] - bb[1])
    return LCACHE[key]

CAP_TOP_Y = 640   # visual top of the white line
def draw_caption(frame, t):
    for (t1, top, t2, gold), end in zip(BEATS, ENDS):
        if not (t1 - 0.02 <= t < end): continue
        out_a = 1 - ease_io((t - (end - 0.1)) / 0.1) if t > end - 0.1 else 1
        y_cursor = CAP_TOP_Y
        th = 0
        if top:
            im, pad, th = line_img(top, "top")
            p = (t - t1) / 0.32
            if p > 0:
                e = ease_back(p, 1.6); a = min(1, p * 3) * out_a
                s = 0.9 + 0.1 * e
                im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC) if abs(s - 1) > .005 else im
                frame.alpha_composite(alpha_mul(im2, a), (int(W / 2 - im2.width / 2), int(y_cursor - pad * s + 24 * (1 - min(1, e)))))
        gim, gpad, gh = line_img(gold, "gold")
        gy = CAP_TOP_Y + (th * 0.80 if top else 0)
        p = (t - t2) / 0.38
        if p > 0:
            e = ease_back(p, 1.8); a = min(1, p * 3) * out_a
            s = 0.82 + 0.18 * e
            g2 = gim.resize((int(gim.width * s), int(gim.height * s)), Image.BICUBIC) if abs(s - 1) > .005 else gim
            frame.alpha_composite(alpha_mul(g2, a), (int(W / 2 - g2.width / 2), int(gy - gpad * s + 30 * (1 - min(1, e)))))
r2.draw_caption = draw_caption

def no_hero(layer, t, h, front): return False
r2.draw_hero = no_hero
r2.ICONS = []

# ======================= floating app tiles =======================
def svg_glyph(name, size, color="#FFFFFF"):
    svg = open(f"{HERE}/icons/{name}.svg").read()
    svg = re.sub(r"<svg ", f'<svg fill="{color}" ', svg, count=1)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")

def grad(size, c1, c2):
    y = np.linspace(0, 1, size)[:, None, None]; x = np.linspace(0, 1, size)[None, :, None]
    k = np.clip(0.65 * y + 0.35 * x, 0, 1)
    c = np.array(c1) * (1 - k) + np.array(c2) * k
    return Image.fromarray(c.astype(np.uint8), "RGB")

def tile(bg1, bg2, glyph_img, glow, circle=False, S=240, glyph_scale=0.56):
    pad = 70; T = S + 2 * pad
    out = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    if circle: d.ellipse((0, 0, S - 1, S - 1), fill=255)
    else: d.rounded_rectangle((0, 0, S - 1, S - 1), int(S * 0.24), fill=255)
    big = Image.new("L", (T, T), 0); big.paste(m, (pad, pad))
    g = Image.new("RGBA", (T, T), glow + (0,)); g.putalpha(big.filter(ImageFilter.GaussianBlur(30)).point(lambda v: min(255, int(v * 0.85))))
    out.alpha_composite(g)
    sh = Image.new("RGBA", (T, T), (0, 0, 0, 0)); sh.putalpha(big.filter(ImageFilter.GaussianBlur(16)).point(lambda v: v // 3))
    out.alpha_composite(sh, (0, 12))
    face = Image.new("RGBA", (S, S), (0, 0, 0, 0)); face.paste(grad(S, bg1, bg2), (0, 0), m)
    if glyph_img is not None:
        gs = int(S * glyph_scale); gi = glyph_img.resize((gs, gs), Image.LANCZOS)
        face.alpha_composite(gi, ((S - gs) // 2, (S - gs) // 2))
    # glossy highlight on the upper half + thin inner rim
    hl = Image.new("L", (S, S), 0); ImageDraw.Draw(hl).ellipse((-S * 0.3, -S * 0.75, S * 1.3, S * 0.45), fill=70)
    hl = Image.fromarray((np.asarray(hl.filter(ImageFilter.GaussianBlur(10)), np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8))
    white = Image.new("RGBA", (S, S), (255, 255, 255, 0)); white.putalpha(hl); face.alpha_composite(white)
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0)); rd = ImageDraw.Draw(rim)
    if circle: rd.ellipse((1, 1, S - 2, S - 2), outline=(255, 255, 255, 70), width=3)
    else: rd.rounded_rectangle((1, 1, S - 2, S - 2), int(S * 0.24), outline=(255, 255, 255, 70), width=3)
    face.alpha_composite(rim)
    out.alpha_composite(face, (pad, pad))
    return out

def tiktok_glyph(S=240):
    base = svg_glyph("tiktok", S)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(svg_glyph("tiktok", S, "#25F4EE"), (-6, -4)); out.alpha_composite(svg_glyph("tiktok", S, "#FE2C55"), (6, 4))
    out.alpha_composite(base); return out

def snap_glyph(S=240):
    w = svg_glyph("snapchat", S, "#FFFFFF"); k = svg_glyph("snapchat", S, "#111111").filter(ImageFilter.MaxFilter(9))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0)); out.alpha_composite(k); out.alpha_composite(w); return out

def concept_glyph(kind):
    def f(p):
        g = chipmod.glyph(kind, p, 84)
        return g.resize((240, 240), Image.LANCZOS)
    return f

BRAND = {
    "ga4":      dict(bg=((255, 196, 60), (232, 113, 10)), glow=(255, 150, 40), glyph=lambda: svg_glyph("googleanalytics", 240)),
    "gtm":      dict(bg=((110, 168, 255), (36, 104, 220)), glow=(70, 140, 255), glyph=lambda: svg_glyph("googletagmanager", 240)),
    "meta":     dict(bg=((60, 160, 255), (0, 90, 225)), glow=(40, 130, 255), glyph=lambda: svg_glyph("meta", 240)),
    "gads":     dict(bg=((255, 255, 255), (226, 234, 245)), glow=(90, 150, 255), glyph=lambda: svg_glyph("googleads", 240, "#1A73E8")),
    "tiktok":   dict(bg=((40, 40, 46), (8, 8, 12)), glow=(60, 220, 230), glyph=tiktok_glyph, circle=True),
    "snapchat": dict(bg=((255, 252, 80), (250, 220, 0)), glow=(255, 230, 40), glyph=snap_glyph),
    "x":        dict(bg=((50, 50, 56), (6, 6, 8)), glow=(180, 180, 200), glyph=lambda: svg_glyph("x", 240), gs=0.46),
    "linkedin": dict(bg=((30, 130, 225), (8, 90, 180)), glow=(30, 120, 220), glyph=lambda: svg_glyph("linkedin", 240), gs=0.52),
}
CONCEPT = {  # warm gold tiles with animated white glyphs (match the gold captions)
    "chart": "ga4", "target": "adsconv", "issue": "issue", "mismatch": "mismatch", "dedup": "dedup",
    "server": "server", "funnel": None, "trend": "gads", "chat": None, "clarity": "clarity", "capi": "capi",
}
CONCEPT_BG = {"clarity": ((150, 120, 255), (90, 50, 220)), "capi": ((70, 150, 255), (20, 80, 210))}
CONCEPT_GLOW = {"clarity": (130, 90, 255), "capi": (60, 130, 255)}

def funnel_glyph(p):
    im = Image.new("RGBA", (240, 240), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255)
    d.polygon([(40, 60), (200, 60), (138, 130), (138, 196), (102, 176), (102, 130)], fill=c)
    for k in range(3):
        q = ((p * 0.9 + k / 3) % 1); y = 20 + 40 * q
        d.ellipse((112 + (k - 1) * 30, y, 128 + (k - 1) * 30, y + 16), fill=(255, 255, 255, int(255 * (1 - q))))
    return im
def chat_glyph(p):
    im = Image.new("RGBA", (240, 240), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255)
    d.rounded_rectangle((30, 46, 210, 166), 44, fill=c); d.polygon([(70, 160), (64, 210), (116, 162)], fill=c)
    for i in range(3):
        b = 0.5 + 0.5 * math.sin(p * 6 - i * 0.9)
        d.ellipse((78 + i * 34 - 11, 106 - 11 - 6 * b, 78 + i * 34 + 11, 106 + 11 - 6 * b), fill=(220, 140, 40, 255))
    return im

TILE_CACHE = {}
def tile_for(kind, p):
    if kind in BRAND:
        if kind not in TILE_CACHE:
            b = BRAND[kind]
            TILE_CACHE[kind] = tile(b["bg"][0], b["bg"][1], b["glyph"](), b["glow"], b.get("circle", False), glyph_scale=b.get("gs", 0.56))
        return TILE_CACHE[kind]
    # animated concept tile (re-rendered per frame, base cached without glyph)
    bkey = ("base", kind)
    bg = CONCEPT_BG.get(kind, ((255, 214, 130), (232, 140, 40))); gl = CONCEPT_GLOW.get(kind, (255, 160, 50))
    if bkey not in TILE_CACHE: TILE_CACHE[bkey] = tile(bg[0], bg[1], None, gl)
    base = TILE_CACHE[bkey].copy()
    if kind == "funnel": g = funnel_glyph(p)
    elif kind == "chat": g = chat_glyph(p)
    else: g = chipmod.glyph(CONCEPT[kind], p, 84).resize((240, 240), Image.LANCZOS)
    gs = int(240 * (0.95 if kind in ('dedup', 'issue', 'mismatch', 'server', 'capi', 'clarity', 'target', 'chart', 'trend') else 0.62)); g = g.resize((gs, gs), Image.LANCZOS)
    base.alpha_composite(g, (70 + (240 - gs) // 2, 70 + (240 - gs) // 2))
    return base

# slots in output coords (centre), scale
SLOT = {"A": (560, 250, 1.0), "B": (1360, 250, 1.0), "C": (300, 560, 0.86), "D": (1620, 560, 0.86), "E": (960, 120, 0.8),
        "F": (250, 220, 0.75), "G": (1670, 220, 0.75)}
# (t_in, t_out, kind, slot)
FLOAT = [
    (3.08, 4.18, "chart", "A"), (4.62, 5.22, "target", "B"),
    (14.08, 18.66, "issue", "A"), (15.62, 18.66, "mismatch", "B"), (17.32, 18.66, "dedup", "D"),
    (21.08, 25.18, "ga4", "A"), (22.06, 25.18, "meta", "B"), (22.42, 25.18, "capi", "D"), (23.30, 25.18, "gads", "C"),
    (25.24, 29.36, "tiktok", "A"), (25.70, 29.36, "snapchat", "B"), (26.30, 29.36, "x", "C"), (26.58, 29.36, "linkedin", "D"),
    (28.28, 29.36, "clarity", "E"),
    (30.30, 31.98, "gtm", "A"), (31.22, 31.98, "server", "B"),
    (32.94, 35.50, "gads", "A"), (34.10, 35.50, "meta", "B"), (34.68, 35.50, "trend", "D"),
    (38.66, 41.98, "funnel", "A"), (39.80, 41.98, "trend", "B"),
    (48.52, r2.VID_END, "chat", "B"),
]

class Floaters:
    def draw(self, layer, t, wide):
        hit = False
        for i, (t0, t1, kind, slot) in enumerate(FLOAT):
            if not (t0 - 0.02 <= t <= t1 + 0.3): continue
            p = t - t0
            e = ease_back(p / 0.5, 2.0); a = min(1, p / 0.15)
            if t > t1:
                q = ease_io((t - t1) / 0.3); a *= 1 - q; e *= 1 - 0.25 * q
            if a <= 0.01: continue
            cx, cy, sc = SLOT[slot]
            if not wide: cy += 10
            im = tile_for(kind, p)
            s = max(0.05, sc * e * 0.92)
            rot = -10 * (1 - min(1, e)) + 2.2 * math.sin(t * 1.7 + i)
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC).rotate(rot, Image.BICUBIC, expand=True)
            im = alpha_mul(im, a)
            bob = 9 * math.sin(t * 2.3 + i * 1.3)
            layer.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + bob + 40 * (1 - min(1, e)))))
            hit = True
        return hit
r2.CHIPS = Floaters()

if __name__ == "__main__":
    r2.main()
