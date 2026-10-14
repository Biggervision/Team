"""Project 3 engine: reference 3 style (dark tech-creator, pixel accents) in brand colours."""
import json, subprocess, sys, wave, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, ".")
import sound as S

W_, H_, FPS = 1080, 1920, 30
F = "fonts/"
MODE = sys.argv[1] if len(sys.argv) > 1 else "full"

WHITE = (255, 255, 255); TEAL = (13, 148, 136); TEAL_G = (45, 212, 191); RED = (255, 72, 72)
MINT = (0xF6, 0xFB, 0xF9); INK = (23, 43, 38); BLUE = (37, 99, 235); DARKUI = (18, 22, 24)

cut = json.load(open("cut.json"))
words = cut["words"]
FIX = {"Clarities": "Clarity", "from": None}
for w in words:
    w["t"] = w["w"].strip()
for _i, _t in ((16, "add"), (46, "add"), (34, "replay"), (36, "sessions"), (53, "product"), (54, "variants")): words[_i]["t"] = _t
TOTAL = sum(e - s for s, e in cut["keep"])
def wt(i): return words[i]["ns"]
def we(i): return words[i]["ne"]

def ease_out(p): p = min(1, max(0, p)); return 1 - (1 - p) ** 3
def ease_in(p): p = min(1, max(0, p)); return p ** 3
def ease_io(p): p = min(1, max(0, p)); return 3 * p * p - 2 * p * p * p
def back_out(p, s=1.7):
    p = min(1, max(0, p)) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2

# ---------------- text ----------------
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(F + {"anton": "Anton-Regular.ttf", "pix": "Silkscreen-Regular.ttf", "pixb": "Silkscreen-Bold.ttf",
                                         "semi": "Poppins-SemiBold.ttf", "bold": "Poppins-Bold.ttf", "med": "Poppins-Medium.ttf",
                                         "xbold": "Poppins-ExtraBold.ttf"}[name], size)
    return _fc[k]

_tc = {}
def text_img(txt, name, size, color=WHITE, track=0.0, shadow=True, maxw=None, stroke=0):
    k = (txt, name, size, color, track, shadow, maxw, stroke)
    if k in _tc: return _tc[k]
    while True:
        f = font(name, size); sp = track * size
        ws = [f.getlength(c) for c in txt]; tw = sum(ws) + sp * max(0, len(txt) - 1)
        if maxw is None or tw <= maxw or size < 30: break
        size = int(size * 0.94)
    asc, desc = f.getmetrics(); pad = 40
    im = Image.new("RGBA", (int(tw) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = pad
    for c, cw in zip(txt, ws):
        d.text((x, pad), c, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255)); x += cw + sp
    if shadow:
        a = im.split()[3]
        s1 = np.asarray(a.filter(ImageFilter.GaussianBlur(8)), np.float32) * 0.9
        s2 = np.asarray(a.filter(ImageFilter.GaussianBlur(26)), np.float32) * 0.55
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(Image.fromarray(np.clip(np.maximum(s1, s2), 0, 255).astype(np.uint8)))
        b = Image.new("RGBA", im.size, (0, 0, 0, 0)); b.paste(sh, (0, 6)); im = Image.alpha_composite(b, im)
    _tc[k] = im
    return im

def paste(cv, img, cx, cy, sc=1.0, a=1.0, dx=0, dy=0, rot=0):
    if a <= 0.01 or sc <= 0.01: return
    if abs(sc - 1) > 0.002: img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
    if rot: img = img.rotate(rot, Image.BILINEAR, expand=True)
    if a < 0.999: img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * a)))
    cv.alpha_composite(img, (int(cx - img.width / 2 + dx), int(cy - img.height / 2 + dy)))

def glitch_in(cv, img, cx, cy, age, dur=0.32):
    """pixel-break entrance: horizontal slices jitter + RGB split, settle"""
    if age < 0: return
    p = min(1, age / dur)
    if p >= 1: paste(cv, img, cx, cy); return
    rng = np.random.default_rng(int(age * 1000))
    arr = np.asarray(img).copy(); h = arr.shape[0]
    amp = int(40 * (1 - p))
    for _ in range(9):
        y0 = rng.integers(0, h - 8); hh = rng.integers(4, max(6, h // 6))
        arr[y0:y0 + hh] = np.roll(arr[y0:y0 + hh], rng.integers(-amp - 1, amp + 1), axis=1)
    g = Image.fromarray(arr)
    r = g.copy(); r.putalpha(g.split()[3].point(lambda v: int(v * 0.55)))
    red = Image.new("RGBA", g.size, (255, 40, 40, 0)); red.putalpha(r.split()[3])
    cyan = Image.new("RGBA", g.size, (40, 220, 255, 0)); cyan.putalpha(r.split()[3])
    off = int(10 * (1 - p))
    paste(cv, red, cx - off, cy); paste(cv, cyan, cx + off, cy)
    paste(cv, g, cx, cy, 1, min(1, 0.4 + p))

# ---------------- pixel art ----------------
INVADER = ["..x.....x..", "...x...x...", "..xxxxxxx..", ".xx.xxx.xx.", "xxxxxxxxxxx", "x.xxxxxxx.x", "x.x.....x.x", "...xx.xx..."]
HEART = [".xx.xx.", "xxxxxxx", "xxxxxxx", ".xxxxx.", "..xxx..", "...x..."]
PHONE = ["xxxxx", "x...x", "x...x", "x...x", "x...x", "xxxxx", "x.x.x", "xxxxx"]
def pixel_sprite(grid, cell, col, key=None):
    k = ("spr", key or tuple(grid), cell, col)
    if k in _tc: return _tc[k]
    h, w = len(grid), len(grid[0])
    im = Image.new("RGBA", (w * cell + 20, h * cell + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "x": d.rectangle([10 + x * cell, 10 + y * cell, 10 + (x + 1) * cell - 1, 10 + (y + 1) * cell - 1], fill=col + (255,))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.6)))
    out = Image.alpha_composite(sh, im); _tc[k] = out
    return out

def pixel_badge(label, col_border=TEAL_G, icon="?", size=40, bg=(16, 20, 22)):
    k = ("pbadge", label, col_border, icon, size)
    if k in _tc: return _tc[k]
    f = font("pixb", size); tw = f.getlength(label)
    ib = size + 18
    Wb, Hb = int(tw + ib + 70), size + 44
    im = Image.new("RGBA", (Wb + 20, Hb + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 10 + Wb, 10 + Hb], fill=bg + (240,), outline=col_border + (255,), width=5)
    d.rectangle([22, 18, 22 + ib, 18 + ib], fill=col_border + (255,))
    if icon == "x":
        d.line([(32, 28), (12 + ib, 8 + ib)], fill=WHITE + (255,), width=7); d.line([(12 + ib, 28), (32, 8 + ib)], fill=WHITE + (255,), width=7)
    else:
        d.text((22 + ib / 2, 18 + ib / 2), icon, font=font("pixb", size), fill=(10, 14, 16, 255), anchor="mm")
    d.text((40 + ib, 10 + Hb / 2), label, font=f, fill=WHITE + (255,), anchor="lm")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6)))
    out = Image.alpha_composite(sh, im); _tc[k] = out
    return out

def red_tag(label, size=34):
    k = ("rtag", label, size)
    if k in _tc: return _tc[k]
    f = font("pixb", size); tw = f.getlength(label)
    Wb, Hb = int(tw + 90), size + 26
    im = Image.new("RGBA", (Wb + 16, Hb + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([8, 8, 8 + Wb, 8 + Hb], fill=(40, 10, 12, 235), outline=RED + (255,), width=4)
    d.rectangle([16, 16, 16 + Hb - 16, 8 + Hb - 8], fill=RED + (255,))
    c0, c1 = 24, Hb - 8
    d.line([(c0, c0), (c1, c1)], fill=WHITE + (255,), width=5); d.line([(c1, c0), (c0, c1)], fill=WHITE + (255,), width=5)
    d.text((Hb + 22, 8 + Hb / 2), label, font=f, fill=WHITE + (255,), anchor="lm")
    _tc[k] = im
    return im

_g = np.random.default_rng(3); GR = [_g.normal(0, 3, (H_, W_, 1)).astype(np.float32) for _ in range(3)]
# ======================= project 4: reference-4 style (B-roll + talking head) =======================
BLUE_L = (96, 165, 250)
FACE = (480.0, 700.0)

# ---------- B-roll plan (cut-timeline seconds) ----------
BROLL = [
    dict(id="42133", s=wt(3) - 0.04, e=wt(5) - 0.02, src=1.0, cx=0.5),            # store gets traffic
    dict(id="42123", s=wt(15) - 0.04, e=wt(21) - 0.04, src=2.0, cx=0.62),         # between add to cart & checkout
    dict(id="46977", s=wt(26) - 0.04, e=wt(30) - 0.04, src=3.0, cx=0.6),          # investigate journey
    dict(id="8843", s=wt(50) - 0.04, e=wt(55) - 0.02, src=3.0, cx=0.5),           # struggling with variants
    dict(id="25897", s=wt(55) - 0.02, e=wt(57) - 0.02, src=2.0, cx=0.33),         # dropping
    dict(id="35902", s=wt(57) - 0.02, e=wt(65) - 0.04, src=3.0, cx=0.45),         # mobile checkout
    dict(id="4401", s=wt(82) - 0.04, e=wt(89) - 0.04, src=2.0, cx=0.5, bw=True),  # more traffic (B&W)
]
PIP = dict(id="18264", s=wt(95) - 0.1, e=we(98) + 0.35, src=2.0, cx=0.62)
def broll_at(t):
    for b in BROLL:
        if b["s"] <= t < b["e"]: return b

def prep_broll():
    for b in BROLL + [PIP]:
        out = f"br_{b['id']}.mp4"
        if os.path.exists(out): continue
        dur = b["e"] - b["s"] + 0.5
        w, h = [int(x) for x in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", f"broll/{b['id']}.mp4"], capture_output=True, text=True).stdout.strip().split(",")]
        if h >= w:
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        else:
            sw = int(w * 1920 / h)
            x = int(max(0, min(sw - 1080, b["cx"] * sw - 540)))
            vf = f"scale={sw}:1920,crop=1080:1920:{x}:0"
        vf += f",scale='1080*(1+0.07*t/{dur:.2f})':-2:eval=frame,crop=1080:1920,fps=30"
        vf += ",hue=s=0,eq=contrast=1.15" if b.get("bw") else ",eq=contrast=1.06:saturation=1.08"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(b["src"]), "-i", f"broll/{b['id']}.mp4", "-t", f"{dur:.2f}", "-vf", vf,
                        "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True)

_cap = {}
def broll_frame(b, t):
    k = b["id"]
    if k not in _cap: _cap[k] = [cv2.VideoCapture(f"br_{k}.mp4"), -1, None]
    c = _cap[k]; fi = int((t - b["s"]) * FPS)
    if fi != c[1] + 1 or c[2] is None:
        c[0].set(cv2.CAP_PROP_POS_FRAMES, max(0, fi))
    ok, fr = c[0].read()
    if ok: c[2] = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    c[1] = fi
    return c[2]

# ---------- full-screen motion canvases ----------
CANVAS = [dict(kind="replay", s=wt(33) - 0.1, e=we(41) + 0.2), dict(kind="chart", s=wt(72) - 0.1, e=we(81) + 0.2)]
END_S = wt(106) - 0.1
def canvas_at(t):
    for c in CANVAS:
        if c["s"] <= t < c["e"]: return c
def in_canvas(t): return canvas_at(t) is not None or broll_at(t) is not None

_yy, _xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
_r = np.sqrt(((_xx - 540) / 820) ** 2 + ((_yy - 900) / 1200) ** 2)
BG = np.clip(np.array([6, 9, 14.])[None, None] + np.array([16, 30, 60.])[None, None] * np.clip(1 - _r, 0, 1)[..., None] ** 1.6, 0, 255).astype(np.float32)
def dark_bg(t):
    return Image.fromarray(np.clip(BG + GR[int(t * 20) % 3], 0, 255).astype(np.uint8)).convert("RGBA")

def phone_frame(cv, cx, cy, w, h, screen_fn=None, a=1.0):
    d = ImageDraw.Draw(cv)
    gl = Image.new("RGBA", cv.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle([cx - w / 2 - 10, cy - h / 2 - 10, cx + w / 2 + 10, cy + h / 2 + 10], 80, fill=BLUE + (int(90 * a),))
    cv.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 74, fill=(12, 12, 14, int(255 * a)), outline=(170, 175, 185, int(255 * a)), width=5)
    sx0, sy0, sx1, sy1 = cx - w / 2 + 18, cy - h / 2 + 18, cx + w / 2 - 18, cy + h / 2 - 18
    if screen_fn: screen_fn(cv, sx0, sy0, sx1, sy1)
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([cx - 70, sy0 + 14, cx + 70, sy0 + 46], 16, fill=(8, 8, 10, int(255 * a)))
    return sx0, sy0, sx1, sy1

def store_screen(cv, x0, y0, x1, y1, t, phase):
    d = ImageDraw.Draw(cv)
    m = Image.new("L", cv.size, 0); ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], 58, fill=255)
    lay = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rectangle([x0, y0, x1, y1], fill=(246, 247, 248, 255))
    W = x1 - x0
    ld.rectangle([x0, y0 + 60, x1, y0 + 130], fill=(255, 255, 255, 255))
    lg = text_img("STORE", "xbold", 30, (20, 20, 20), 0.2, shadow=False); lay.alpha_composite(lg, (int(x0 + 30 - 40), int(y0 + 95 - lg.height / 2)))
    ld.rounded_rectangle([x0 + 30, y0 + 160, x1 - 30, y0 + 560], 26, fill=(214, 228, 240, 255))
    ld.ellipse([x0 + W / 2 - 110, y0 + 250, x0 + W / 2 + 110, y0 + 470], fill=(170, 196, 220, 255))
    pt = text_img("Everyday Sneaker", "bold", 38, (20, 20, 20), 0, shadow=False); lay.alpha_composite(pt, (int(x0 + 30 - 40), int(y0 + 590)))
    pr = text_img("$89.00", "semi", 34, (60, 60, 60), 0, shadow=False); lay.alpha_composite(pr, (int(x0 + 30 - 40), int(y0 + 645)))
    sizes = ["7", "8", "9", "10", "11"]
    for k, sz in enumerate(sizes):
        bx = x0 + 30 + k * 86
        sel = phase.get("sel") == k
        ld.rounded_rectangle([bx, y0 + 720, bx + 72, y0 + 786], 14, fill=(255, 255, 255, 255), outline=((37, 99, 235) if sel else (200, 205, 210)) + (255,), width=4 if sel else 2)
        st = text_img(sz, "semi", 30, (20, 20, 20), 0, shadow=False); lay.alpha_composite(st, (int(bx + 36 - st.width / 2), int(y0 + 753 - st.height / 2)))
    ld.rounded_rectangle([x0 + 30, y0 + 820, x1 - 30, y0 + 910], 20, fill=(20, 20, 20, 255))
    bt = text_img("Add to cart", "bold", 34, WHITE, 0, shadow=False); lay.alpha_composite(bt, (int(x0 + W / 2 - bt.width / 2), int(y0 + 865 - bt.height / 2)))
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(m))))
    cv.alpha_composite(lay)

TAPS = [(0.30, 0.47, 0.72), (0.55, 0.30, 0.75), (0.70, 0.58, 0.75), (0.80, 0.50, 0.865), (0.86, 0.50, 0.865), (0.92, 0.50, 0.865)]
def sc_replay(t, c):
    cv = dark_bg(t); age = t - c["s"]
    tt = text_img("MICROSOFT CLARITY", "anton", 104, WHITE, 0.01)
    paste(cv, tt, 540, 170, 1.08 - 0.08 * ease_out(age / 0.2), min(1, age / 0.1))
    sb = text_img("Session replay", "semi", 40, BLUE_L, 0.02, shadow=False); paste(cv, sb, 540, 255, 1, min(1, (age - 0.15) / 0.2))
    r0, r1 = wt(34), we(41); rp = min(1, max(0, (t - r0) / (r1 - r0)))
    phase = {"sel": 2 if rp > 0.58 else None}
    pa = ease_out(age / 0.4)
    cy = 1080 + (1 - pa) * 160
    sx0, sy0, sx1, sy1 = phone_frame(cv, 540, cy, 600, 1240, lambda c_, a, b, c2, d2: store_screen(c_, a, b, c2, d2, t, phase))
    d = ImageDraw.Draw(cv)
    # touch point travels between taps
    pts = [(0.5, 0.2)] + [(x, y) for _, x, y in TAPS]
    q = rp * (len(pts) - 1); k = min(int(q), len(pts) - 2); u = ease_io(q - k)
    fx = pts[k][0] + (pts[k + 1][0] - pts[k][0]) * u; fy = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * u
    px, py = sx0 + fx * (sx1 - sx0), sy0 + fy * (sy1 - sy0)
    for f, x, y in TAPS:
        ra = t - (r0 + f * (r1 - r0))
        if 0 <= ra < 0.45:
            X, Y = sx0 + x * (sx1 - sx0), sy0 + y * (sy1 - sy0); rr = 14 + 50 * ease_out(ra / 0.45)
            d.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=BLUE + (int(240 * (1 - ra / 0.45)),), width=6)
    d.ellipse([px - 26, py - 26, px + 26, py + 26], fill=(37, 99, 235, 120), outline=WHITE + (230,), width=4)
    if rp > 0.84:
        ch = text_img("Rage taps on Add to cart", "bold", 34, WHITE, 0.01, shadow=False)
        pill = Image.new("RGBA", (ch.width + 10, 80), (0, 0, 0, 0)); ImageDraw.Draw(pill).rounded_rectangle([0, 6, ch.width + 6, 74], 34, fill=(220, 38, 38, 255))
        pill.alpha_composite(ch, (3, int(40 - ch.height / 2)))
        paste(cv, pill, 540, sy0 + 0.865 * (sy1 - sy0) - 120, 0.8 + 0.2 * back_out(min(1, (rp - 0.84) * 8), 1.6))
    return cv

def sc_chart(t, c):
    cv = dark_bg(t); age = t - c["s"]
    tt = text_img("CONVERSION RATE", "anton", 104, WHITE, 0.01); paste(cv, tt, 540, 300, 1.08 - 0.08 * ease_out(age / 0.2), min(1, age / 0.1))
    d = ImageDraw.Draw(cv)
    base = 1460
    d.line([(160, base), (920, base)], fill=(80, 90, 110, 255), width=4)
    hb = 360 * ease_out((t - wt(77)) / 0.5); ha = 720 * ease_out((t - wt(79)) / 0.6)
    d.rounded_rectangle([230, base - max(4, hb), 450, base], 18, fill=(90, 100, 120, 255))
    gl = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle([630, base - max(4, ha), 850, base], 18, fill=BLUE + (200,))
    cv.alpha_composite(gl.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(cv); d.rounded_rectangle([630, base - max(4, ha), 850, base], 18, fill=BLUE + (255,))
    for x, lab, tt0 in ((340, "BEFORE", wt(77)), (740, "AFTER", wt(79))):
        im = text_img(lab, "anton", 64, WHITE if lab == "AFTER" else (170, 175, 185), 0.04); paste(cv, im, x, base + 70, 1, min(1, max(0, (t - tt0) / 0.2)))
    if t > wt(79) + 0.5:
        ar = ease_out((t - wt(79) - 0.5) / 0.3)
        d.polygon([(740, base - ha - 150 - 40 * (1 - ar)), (700, base - ha - 90), (780, base - ha - 90)], fill=BLUE_L + (int(255 * ar),))
    return cv

SCENE = {"replay": sc_replay, "chart": sc_chart}

# ---------- captions ----------
KEY = {1: "SHOPIFY", 8: None, 9: None, 32: None, 46: None, 47: None, 48: None, 49: None, 68: None, 95: None, 98: None, 103: None, 107: None}
CIRCLE = {9, 48, 98}
def group_chunks():
    ch, cur = [], []
    for w in words:
        i = w["i"]
        if cur and (len(cur) >= 3 or wt(i) - we(cur[-1]) > 0.28 or words[cur[-1]]["t"].endswith((".", "?", ","))
                    or (i in KEY and cur[-1] not in KEY) or (cur[-1] in KEY and i not in KEY)):
            ch.append(cur); cur = []
        cur.append(i)
    if cur: ch.append(cur)
    out = []
    for n, c in enumerate(ch):
        t1 = wt(ch[n + 1][0]) if n + 1 < len(ch) else TOTAL
        out.append(dict(ws=c, t0=wt(c[0]), t1=min(t1, we(c[-1]) + 0.6)))
    return out
CHUNKS = None

def grad_word(txt, size):
    k = ("gw", txt, size)
    if k in _tc: return _tc[k]
    base = text_img(txt, "xbold", size, WHITE, -0.02, shadow=False, maxw=980)
    a = np.asarray(base.split()[3], np.float32)
    h, w = a.shape; v = np.linspace(0, 1, h)[:, None, None]
    col = np.array((255, 255, 255), np.float32) * (1 - v) + np.array((236, 240, 245), np.float32) * v
    im = Image.fromarray(np.dstack([np.broadcast_to(col, (h, w, 3)), a[..., None]]).astype(np.uint8), "RGBA")
    outl = text_img(txt, "xbold", size, (8, 14, 34), -0.02, shadow=False, maxw=980, stroke=5)
    ol = Image.new("RGBA", outl.size, (8, 14, 34, 0)); ol.putalpha(outl.split()[3])
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(outl.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda q: int(q * 0.85)))
    out = Image.alpha_composite(Image.alpha_composite(sh, ol), im); _tc[k] = out
    return out

def scribble(cv, cx, cy, w, h, p):
    if p <= 0: return
    n = 90; pts = []
    for k in range(int(n * min(1, p)) + 1):
        a = -math.pi * 0.6 + 2.15 * math.pi * k / n
        wob = 1 + 0.06 * math.sin(k * 0.7)
        pts.append((cx + math.cos(a) * w / 2 * wob, cy + math.sin(a) * h / 2 * wob - 6 * k / n))
    if len(pts) > 1:
        d = ImageDraw.Draw(cv); d.line(pts, fill=WHITE + (255,), width=7, joint="curve")

def caption(cv, t):
    global CHUNKS
    if CHUNKS is None: CHUNKS = group_chunks()
    b = broll_at(t)
    for c in CHUNKS:
        if not (c["t0"] <= t < c["t1"]): continue
        if canvas_at(t): return
        age = t - c["t0"]
        if b is not None:      # big single-word caption over B-roll (reference: STARBUCKS)
            cur = [i for i in c["ws"] if wt(i) <= t + 0.02]
            i = cur[-1] if cur else c["ws"][0]
            im = text_img(words[i]["t"].upper().rstrip(",.?"), "anton", 132, WHITE, 0.01, maxw=980)
            a2 = t - wt(i)
            paste(cv, im, 540, 1420, 1.1 - 0.1 * ease_out(a2 / 0.12), min(1, a2 / 0.05 + 0.3))
            return
        keyed = [i for i in c["ws"] if i in KEY]
        if keyed:
            txt = " ".join(words[i]["t"].rstrip(",.?") for i in c["ws"])
            im = grad_word(txt, 150)
            p = ease_out(age / 0.22)
            paste(cv, im, 540, 1260, 0.85 + 0.15 * back_out(min(1, age / 0.22), 1.5), min(1, age / 0.06))
            if any(i in CIRCLE for i in c["ws"]):
                scribble(cv, 540, 1265, min(980, im.width - 20), im.height * 0.95, (age - 0.2) / 0.45)
        else:
            cur = [i for i in c["ws"] if wt(i) <= t + 0.02]
            txt = " ".join(words[i]["t"] for i in cur)
            im = text_img(txt, "semi", 62, WHITE, 0, maxw=940)
            paste(cv, im, 540, 1260, 1.04 - 0.04 * ease_out((t - wt(cur[-1])) / 0.12), 1)
        return

# ---------- footage overlays ----------
def bag_icon(size=210):
    k = ("bag", size)
    if k in _tc: return _tc[k]
    S2 = size + 120; im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); o = 60
    gl = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle([o, o, o + size, o + size], 52, fill=(149, 191, 71, 160))
    im = Image.alpha_composite(im, gl.filter(ImageFilter.GaussianBlur(26))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([o, o, o + size, o + size], 52, fill=(255, 255, 255, 255))
    c = o + size / 2; u = size / 10
    d.polygon([(c - 3 * u, c - 1.2 * u), (c + 3 * u, c - 1.2 * u), (c + 2.5 * u, c + 3.2 * u), (c - 2.5 * u, c + 3.2 * u)], fill=(149, 191, 71, 255))
    d.arc([c - 1.6 * u, c - 3.4 * u, c + 1.6 * u, c - 0.2 * u], 180, 360, fill=(149, 191, 71, 255), width=int(0.6 * u))
    sheen = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); ImageDraw.Draw(sheen).rounded_rectangle([o + 6, o + 6, o + size - 6, o + size * 0.42], 46, fill=(255, 255, 255, 60))
    im = Image.alpha_composite(im, sheen); _tc[k] = im
    return im

def overlays(cv, t):
    if t < wt(3):                       # 3D bag icon pops on "Shopify"
        ia = t - wt(1) + 0.05
        if ia > 0:
            a = 1 - ease_in((t - (wt(3) - 0.2)) / 0.2)
            paste(cv, bag_icon(), 800, 560 + math.sin(t * 3) * 8, 0.6 + 0.4 * back_out(min(1, ia / 0.3), 1.6), min(1, ia / 0.1) * a, rot=(1 - ease_out(ia / 0.3)) * -20)
    if PIP["s"] <= t < PIP["e"]:        # picture-in-picture B-roll (reference)
        p = ease_out((t - PIP["s"]) / 0.25); a = min(p, 1 - ease_in((t - (PIP["e"] - 0.2)) / 0.2))
        fr = broll_frame(PIP, t)
        if fr is not None:
            sm = Image.fromarray(fr).resize((300, 533))
            m = Image.new("L", sm.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 532], 28, fill=int(255 * a)); sm.putalpha(m)
            sh = Image.new("RGBA", (360, 600), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([30, 40, 330, 573], 28, fill=(0, 0, 0, int(140 * a)))
            cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (700 - 30, 140 - 30))
            cv.alpha_composite(sm, (700, int(140 + (1 - p) * 40)))

# ---------- zoom ----------
ZOOM = {9: 0.08, 48: 0.07, 68: 0.07, 98: 0.08}
def zoom_at(t):
    z = 1.0
    for i, s in ZOOM.items():
        u = t - wt(i)
        if -0.05 <= u < 1.9: z *= 1 + s * min(ease_io((u + 0.05) / 0.25), 1 - ease_io((u - 1.2) / 0.6))
    return z
def camera(fr, t):
    z = zoom_at(t)
    if abs(z - 1) < 1e-3: return fr
    M = np.float32([[z, 0, FACE[0] * (1 - z)], [0, z, FACE[1] * (1 - z)]])
    return cv2.warpAffine(fr, M, (W_, H_), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------- light-streak transition ----------
def streak(out, t, t_c, dur=0.36):
    u = (t - (t_c - dur / 2)) / dur
    if not (0 <= u <= 1): return out
    lay = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(5):
        off = -900 + 2200 * u + k * 40
        pts = [(off + 300 * math.sin(y / 300 + k), y) for y in range(-100, 2020, 60)]
        d.line(pts, fill=(80, 255, 220, 200 - k * 30), width=60 - k * 8, joint="curve")
    glow = lay.filter(ImageFilter.GaussianBlur(30))
    base = Image.fromarray(out).convert("RGBA"); base.alpha_composite(glow); base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
    return np.asarray(base.convert("RGB"))

# ---------- ending: footage shrinks into a phone ----------
_pg = np.random.default_rng(5)
SPARKS = [(_pg.random(), _pg.random(), _pg.random()) for _ in range(70)]
def ending(foot_rgb, t):
    u = ease_io((t - END_S) / 0.7)
    cv = dark_bg(t)
    d = ImageDraw.Draw(cv)
    for x, y, s in SPARKS:
        xx = x * W_; yy = y * H_
        L = 40 + 120 * s
        ang = math.atan2(yy - 960, xx - 540)
        d.line([(xx, yy), (xx + math.cos(ang) * L, yy + math.sin(ang) * L)], fill=(200, 220, 255, int(140 * u)), width=2)
    sc = 1 - 0.42 * u
    w, h = int(W_ * sc), int(H_ * sc)
    fr = Image.fromarray(foot_rgb).resize((w, h))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], int(70 * u), fill=255); fr.putalpha(m)
    if u > 0.02:
        ImageDraw.Draw(cv).rounded_rectangle([540 - w / 2 - 14, 960 - h / 2 - 14, 540 + w / 2 + 14, 960 + h / 2 + 14], int(84 * u), fill=(14, 14, 16, 255), outline=(170, 175, 185, int(255 * u)), width=5)
    cv.alpha_composite(fr, (int(540 - w / 2), int(960 - h / 2)))
    return np.asarray(cv.convert("RGB"))

# ---------- compositor ----------
def footage(fr, t):
    cv = Image.fromarray(camera(fr, t)).convert("RGBA")
    overlays(cv, t); caption(cv, t)
    return np.asarray(cv.convert("RGB"))

def render(fr, t):
    c = canvas_at(t); b = broll_at(t)
    if c:
        out = np.asarray(SCENE[c["kind"]](t, c).convert("RGB"))
    elif b:
        bf = broll_frame(b, t)
        cv = Image.fromarray(bf).convert("RGBA"); caption(cv, t)
        out = np.asarray(cv.convert("RGB"))
        u = t - b["s"]
        if u < 0.12:     # punchy zoom-in entry
            z = 1.12 - 0.12 * ease_out(u / 0.12); M = np.float32([[z, 0, 540 * (1 - z)], [0, z, 960 * (1 - z)]])
            out = cv2.warpAffine(out, M, (W_, H_), borderMode=cv2.BORDER_REFLECT)
    else:
        out = footage(fr, t)
        if t >= END_S: out = ending(out, t)
    for cc in CANVAS: out = streak(out, t, cc["s"])
    out = streak(out, t, BROLL[0]["s"]); out = streak(out, t, BROLL[6]["s"])
    return out

# ---------- sound ----------
EV = []
def sfx(t, n, g, pan=0.0): EV.append((t, n, g, pan))
def plan():
    EV.clear()
    for c in group_chunks():
        if canvas_at(c["t0"] + 0.01): continue
        if any(i in KEY for i in c["ws"]): sfx(c["t0"] - 0.06, "swish", 0.10); sfx(c["t0"], "pop", 0.10)
        if any(i in CIRCLE for i in c["ws"]): sfx(c["t0"] + 0.2, "scribble", 0.10)
    for i, s_ in ZOOM.items(): sfx(wt(i) - 0.02, "impact", 0.10 + s_)
    sfx(wt(1), "bubble", 0.14); sfx(wt(1) + 0.02, "pop", 0.08)
    for b in BROLL: sfx(b["s"] - 0.1, "whoosh", 0.12); sfx(b["s"], "impact", 0.07)
    sfx(PIP["s"], "swish", 0.1); sfx(PIP["s"] + 0.05, "pop", 0.07)
    for c in CANVAS: sfx(c["s"] - 0.5, "riser", 0.06); sfx(c["s"] - 0.15, "whoosh", 0.18); sfx(c["s"], "impact", 0.18)
    r0, r1 = wt(34), we(41)
    for f, _, _ in TAPS: sfx(r0 + f * (r1 - r0), "click", 0.15)
    sfx(r0 + 0.84 * (r1 - r0), "glitch", 0.07)
    sfx(wt(77), "tick", 0.06); sfx(wt(79), "riser", 0.05); sfx(wt(79) + 0.6, "ding", 0.09)
    sfx(END_S, "whoosh", 0.14); sfx(END_S + 0.5, "ding", 0.05)
    return EV

def build_audio():
    lib = {"pop": S.pop(), "swish": S.swish(), "click": S.click(), "glitch": S.glitch(), "impact": S.impact(), "tick": S.tick(),
           "whoosh": S.whoosh(), "riser": S.riser(0.6), "ding": S.ding(), "bubble": S.bubble(), "scribble": S.whoosh(0.4, 2500, 6000, -0.2, 0.2)}
    wf = wave.open("base2_audio.wav")
    au = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    n = len(au); fx = np.zeros((n + S.SR, 2))
    for t, nm, g, pan in plan():
        x = lib[nm] * g; i = max(0, int(t * S.SR)); fx[i:i + len(x)] += x[: len(fx) - i]
    fx = fx[:n]; m = S.music(n / S.SR + 1)[:n]
    venv = np.convolve(np.sqrt(np.convolve(au ** 2, np.ones(2400) / 2400, "same")), np.ones(9600) / 9600, "same")
    rel = np.clip(venv / (np.percentile(venv, 90) + 1e-6), 0, 1); tt = np.arange(n) / S.SR
    fade = np.minimum(1, tt / 1.0) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    mix = np.repeat(au[:, None], 2, 1) * 0.92 + fx * (1 - 0.25 * rel)[:, None] + m * (0.15 * (1 - 0.55 * rel) * fade)[:, None]
    pk = np.abs(mix).max()
    if pk > 0.98: mix = mix / pk * 0.98
    with wave.open("mix_p4.wav", "wb") as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(S.SR); o.writeframes((mix * 32767).astype(np.int16).tobytes())

def frames(t0, t1):
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", "base2.mov", "-t", f"{t1 - t0:.4f}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k0 = int(round(t0 * FPS)); nf = int(round((t1 - t0) * FPS)); last = None
    for k in range(nf):
        raw = dec.stdout.read(W_ * H_ * 3)
        if len(raw) == W_ * H_ * 3: last = np.frombuffer(raw, np.uint8).reshape(H_, W_, 3)
        yield (k0 + k) / FPS, last

if __name__ == "__main__":
    if MODE == "broll": prep_broll(); sys.exit()
    if MODE == "preview":
        for ts in sys.argv[2:]:
            t = float(ts)
            for tt, fr in frames(max(0, t - 0.1), t + 1 / FPS): img = render(fr, tt)
            Image.fromarray(img).resize((360, 640)).save(f"pv_{ts}.png")
        sys.exit()
    if MODE == "audio": build_audio(); sys.exit()
    t0, t1 = (float(sys.argv[2]), float(sys.argv[3])) if MODE == "clip" else (0.0, TOTAL)
    out = f"clip_p4_{t0:.3f}.mp4" if MODE == "clip" else "final_p4.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}", "-r", str(FPS), "-i", "-",
                            "-vf", "noise=alls=3:allf=t,unsharp=5:5:0.35,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-an", out], stdin=subprocess.PIPE)
    for t, fr in frames(t0, t1): enc.stdin.write(render(fr, t).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out)
