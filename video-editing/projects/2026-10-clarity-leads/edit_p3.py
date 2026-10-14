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
words[83]["t"] = "form"            # "contact from" -> "contact form"
words[52]["t"] = "Clarity"
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

# ---------------- caption system (Anton caps, 2-line, coloured keyword line) ----------------
POS = {4, 51, 52, 86, 90, 94, 99, 100, 112, 118, 120, 121}
NEG = {9, 10, 16, 43, 44, 45, 69, 75, 80, 104, 109, 111}
def group_chunks():
    ch, cur = [], []
    for w in words:
        i = w["i"]
        if cur and (len(cur) >= 3 or wt(i) - we(cur[-1]) > 0.28 or words[cur[-1]]["t"].endswith((".", "?", ","))
                    or ((i in POS or i in NEG) and not (cur[-1] in POS or cur[-1] in NEG) and len(cur) >= 2)
                    or ((cur[-1] in POS or cur[-1] in NEG) and not (i in POS or i in NEG))):
            ch.append(cur); cur = []
        cur.append(i)
    if cur: ch.append(cur)
    out = []
    for n, c in enumerate(ch):
        t0 = wt(c[0]); t1 = wt(ch[n + 1][0]) if n + 1 < len(ch) else TOTAL
        t1 = min(t1, we(c[-1]) + 0.6)
        out.append(dict(ws=c, t0=t0, t1=t1))
    return out
CHUNKS = None
CAP_Y = 1250

def tok(i): return words[i]["t"].upper().rstrip(",.?")

def caption(cv, t, y=None):
    global CHUNKS
    if CHUNKS is None: CHUNKS = group_chunks()
    y = CAP_Y if y is None else y
    for c in CHUNKS:
        if not (c["t0"] <= t < c["t1"]): continue
        if any(in_canvas(wt(i)) for i in c["ws"]): return
        key = [i for i in c["ws"] if i in POS or i in NEG]
        age = t - c["t0"]
        if key:
            k0 = c["ws"].index(key[0])
            l1 = [i for i in c["ws"][:k0]]; l2 = c["ws"][k0:]
            col = RED if key[0] in NEG else TEAL_G
            if l1:
                im1 = text_img(" ".join(tok(i) for i in l1), "anton", 96, WHITE, 0.01, maxw=960)
                paste(cv, im1, 540, y - 62, 1.08 - 0.08 * ease_out(age / 0.14), min(1, age / 0.06))
            shown = [i for i in l2 if wt(i) <= t + 0.02]
            if shown:
                im2 = text_img(" ".join(tok(i) for i in l2), "anton", 118, col, 0.01, maxw=980)
                a2 = t - wt(l2[0])
                if col == RED: glitch_in(cv, im2, 540, y + 50 if l1 else y, a2)
                else: paste(cv, im2, 540, y + 50 if l1 else y, 1.12 - 0.12 * ease_out(a2 / 0.16), min(1, a2 / 0.06))
        else:
            im = text_img(" ".join(tok(i) for i in c["ws"]), "anton", 104, WHITE, 0.01, maxw=960)
            paste(cv, im, 540, y, 1.08 - 0.08 * ease_out(age / 0.14), min(1, age / 0.06))
        return

# ---------------- canvas scenes (dark monitor mockup) ----------------
CANVAS = [dict(kind="clarity", s=wt(51) - 0.1, e=we(66) + 0.15), dict(kind="struggle", s=wt(67) - 0.08, e=we(85) + 0.2)]
def canvas_at(t):
    for c in CANVAS:
        if c["s"] <= t < c["e"]: return c
def in_canvas(t): return canvas_at(t) is not None

_yy, _xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
_rr = np.sqrt(((_xx - 540) / 900) ** 2 + ((_yy - 760) / 1200) ** 2)
ROOM = np.clip(np.array([8, 10, 11.])[None, None] + np.array([22, 30, 30.])[None, None] * np.clip(1 - _rr, 0, 1)[..., None] ** 1.5, 0, 255).astype(np.float32)
_g = np.random.default_rng(3); GR = [_g.normal(0, 3, (H_, W_, 1)).astype(np.float32) for _ in range(3)]
SX0, SY0, SX1, SY1 = 70, 360, 1010, 1080          # monitor screen rect

def monitor_bg(t):
    img = Image.fromarray(np.clip(ROOM + GR[int(t * 20) % 3], 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # stand + base (silver gradient)
    for k in range(60):
        c = int(150 + 70 * math.sin(k / 60 * math.pi))
        d.line([(430 + k * 0.2, SY1 + 30 + k * 6), (650 - k * 0.2, SY1 + 30 + k * 6)], fill=(c, c, c + 4, 255), width=7)
    d.rounded_rectangle([300, SY1 + 390, 780, SY1 + 412], 10, fill=(170, 172, 176, 255))
    # bezel + chin
    d.rounded_rectangle([SX0 - 22, SY0 - 22, SX1 + 22, SY1 + 60], 26, fill=(14, 15, 17, 255), outline=(60, 62, 66, 255), width=2)
    d.rectangle([SX0 - 22, SY1 + 10, SX1 + 22, SY1 + 60], fill=(190, 192, 196, 255))
    d.rectangle([SX0, SY0, SX1, SY1], fill=DARKUI + (255,))
    return img

def prompt_bar(cv, txt, t0, t, y=SY1 - 80):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([SX0 + 30, y - 34, SX1 - 30, y + 34], 14, fill=(30, 34, 38, 255), outline=(70, 76, 82, 255), width=2)
    n = max(0, min(len(txt), int((t - t0) / 0.035)))
    im = text_img(txt[:n] + ("|" if int(t * 3) % 2 else ""), "med", 30, (210, 220, 225), 0, shadow=False)
    cv.alpha_composite(im, (SX0 + 60 - 40, int(y - im.height / 2)))

def site_mock(cv, t, a=1.0):
    d = ImageDraw.Draw(cv); A = int(255 * a)
    d.rectangle([SX0 + 30, SY0 + 30, SX1 - 30, SY0 + 90], fill=(28, 32, 36, A))
    lg = text_img("BRIGHT SMILE DENTAL", "bold", 26, (220, 230, 232), 0.04, shadow=False); cv.alpha_composite(lg, (SX0 + 40, SY0 + 60 - lg.height // 2))
    d.rounded_rectangle([SX0 + 30, SY0 + 120, SX1 - 30, SY0 + 330], 18, fill=(30, 46, 44, A))
    h = text_img("Pain-free dental care", "xbold", 44, MINT, -0.01, shadow=False); cv.alpha_composite(h, (SX0 + 40, SY0 + 160))
    d.rounded_rectangle([SX0 + 70, SY0 + 240, SX0 + 330, SY0 + 300], 14, fill=TEAL + (A,))
    bt = text_img("Book now", "bold", 28, WHITE, 0, shadow=False); cv.alpha_composite(bt, (int(SX0 + 200 - bt.width / 2), int(SY0 + 270 - bt.height / 2)))
    for k in range(3):
        d.rounded_rectangle([SX0 + 30 + k * 300, SY0 + 360, SX0 + 290 + k * 300, SY0 + 470], 12, fill=(32, 36, 40, A))
    d.rounded_rectangle([SX0 + 30, SY0 + 500, SX1 - 30, SY0 + 640], 12, fill=(28, 32, 36, A))
    for k in range(3):
        d.rounded_rectangle([SX0 + 60, SY0 + 520 + k * 38, SX0 + 560, SY0 + 546 + k * 38], 6, fill=(48, 54, 60, A))
    ph = text_img("Call (555) 012-3456", "med", 22, (120, 128, 134), 0, shadow=False); cv.alpha_composite(ph, (SX1 - 40 - ph.width + 40, SY0 + 680))

PATH = [(0.80, 0.20), (0.35, 0.30), (0.25, 0.42), (0.60, 0.55), (0.30, 0.78), (0.70, 0.72), (0.86, 0.95)]
def cursor_at(q):
    q = min(1, max(0, q)) * (len(PATH) - 1); k = min(int(q), len(PATH) - 2); u = ease_io(q - k)
    x = PATH[k][0] + (PATH[k + 1][0] - PATH[k][0]) * u; y = PATH[k][1] + (PATH[k + 1][1] - PATH[k][1]) * u
    return SX0 + x * (SX1 - SX0), SY0 + y * (SY1 - SY0)
def draw_cursor(cv, x, y):
    d = ImageDraw.Draw(cv)
    pts = [(0, 0), (0, 36), (9, 28), (15, 42), (21, 39), (15, 26), (27, 26)]
    poly = [(x + a * 1.6, y + b * 1.6) for a, b in pts]
    d.polygon(poly, fill=WHITE + (255,)); d.line(poly + [poly[0]], fill=(0, 0, 0, 255), width=3)

CLICKS = [0.35, 0.62, 0.70]
def sc_clarity(t, c):
    cv = monitor_bg(t); age = t - c["s"]
    # Clarity-like replay app chrome
    d = ImageDraw.Draw(cv)
    hd = text_img("Microsoft Clarity  •  Recordings", "semi", 30, (200, 210, 215), 0, shadow=False); cv.alpha_composite(hd, (SX0 + 10, SY0 + 10))
    site_mock(cv, t)
    r0, r1 = wt(56), we(66)
    rp = min(1, max(0, (t - r0) / (r1 - r0)))
    for cf in CLICKS:
        ra = t - (r0 + cf * (r1 - r0))
        if 0 <= ra < 0.45:
            x, y = cursor_at(cf); rr = 12 + 44 * ease_out(ra / 0.45)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=TEAL_G + (int(230 * (1 - ra / 0.45)),), width=5)
    x, y = cursor_at(rp); draw_cursor(cv, x, y)
    # replay bar
    by = SY1 - 160
    d.rectangle([SX0 + 30, by - 4, SX1 - 30, by + 4], fill=(50, 56, 62, 255))
    d.rectangle([SX0 + 30, by - 4, SX0 + 30 + (SX1 - SX0 - 60) * rp, by + 4], fill=TEAL_G + (255,))
    prompt_bar(cv, "Replay visitor sessions…", c["s"] + 0.2, t)
    inv = pixel_sprite(INVADER, 9, (220, 225, 230))
    paste(cv, inv, SX1 - 110, SY0 + 120 + math.sin(t * 3) * 8)
    # title above monitor
    tt = text_img("MICROSOFT CLARITY", "anton", 110, WHITE, 0.01)
    paste(cv, tt, 540, 220, 1.06 - 0.06 * ease_out(age / 0.2), min(1, age / 0.1))
    return cv

STRUG = [(69, "CAN'T FIND PHONE"), (75, "MISSED BOOKING"), (80, "FORM ABANDONED")]
def sc_struggle(t, c):
    cv = monitor_bg(t); age = t - c["s"]
    site_mock(cv, t, 0.55)
    ov = Image.new("RGBA", cv.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rectangle([SX0, SY0, SX1, SY1], fill=(0, 0, 0, 110)); cv.alpha_composite(ov)
    for k, (wi, lab) in enumerate(STRUG):
        ia = t - wt(wi)
        if ia < 0: continue
        tag = red_tag(lab, 40)
        glitch_in(cv, tag, 540, SY0 + 200 + k * 140, ia, 0.25)
    inv = pixel_sprite(INVADER, 9, RED, key="inv_red")
    paste(cv, inv, SX1 - 110, SY0 + 90 + math.sin(t * 4) * 6)
    tt = text_img("WHERE THEY", "anton", 96, WHITE, 0.01)
    t2 = text_img("DROP OFF", "anton", 120, RED, 0.01)
    paste(cv, tt, 540, 150, 1, min(1, age / 0.1)); glitch_in(cv, t2, 540, 262, age - 0.15)
    return cv

SCENE = {"clarity": sc_clarity, "struggle": sc_struggle}

# ---------------- footage overlays ----------------
def widget(cv, x, y, w, h, a=1.0):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 22, fill=(16, 20, 22, int(215 * a)), outline=(70, 80, 84, int(200 * a)), width=2)

def overlays(cv, t):
    # A. hook: visitors counter climbing, then calls = 0
    if t < we(10) + 0.5:
        a = min(ease_out((t - 0.15) / 0.3), 1 - ease_in((t - (we(10) + 0.25)) / 0.25))
        if a > 0.01:
            y = 1500
            widget(cv, 600, y, 560, 96, a)
            inv = pixel_sprite(INVADER, 8, TEAL_G, key="inv_t")
            paste(cv, inv, 245, y + math.sin(t * 4) * 5, 1, a)
            lab = text_img("Website visitors", "med", 30, (215, 222, 225), 0, shadow=False); paste(cv, lab, 450, y - 18, 1, a)
            v = int(1284 * ease_out((t - 0.2) / 2.0))
            num = text_img(f"{v:,}", "semi", 30, TEAL_G, 0, shadow=False); paste(cv, num, 810, y - 18, 1, a)
            d = ImageDraw.Draw(cv)
            d.rounded_rectangle([350, y + 18, 860, y + 26], 4, fill=(50, 58, 62, int(255 * a)))
            d.rounded_rectangle([350, y + 18, 350 + 510 * ease_out((t - 0.2) / 2.0), y + 26], 4, fill=TEAL_G + (int(255 * a),))
            if t > wt(7):
                pa = t - wt(7)
                ph = pixel_sprite(PHONE, 10, RED if t > wt(9) else (220, 225, 230), key=("ph", t > wt(9)))
                paste(cv, ph, 880, 560 + (math.sin(t * 40) * 6 if t > wt(9) and t < wt(9) + 0.6 else 0), 1, ease_out(pa / 0.2) * a)
                cl = text_img("CALLS: 0", "pixb", 34, RED if t > wt(9) else WHITE, 0.02)
                paste(cv, cl, 880, 680, 1, ease_out(pa / 0.2) * a)
    # B. red neon streaks behind the question
    if wt(11) <= t < we(21) + 0.4:
        a = min(ease_out((t - wt(16)) / 0.25), 1 - ease_in((t - we(21) - 0.15) / 0.25))
        if a > 0.01:
            ov = Image.new("RGBA", cv.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for k in range(5):
                y = 230 + k * 46; x0 = 60 + (k % 2) * 40; x1 = 330 + (k * 37) % 120
                od.line([(x0, y), (x1, y - 18)], fill=RED + (int(220 * a),), width=6)
            glow = ov.filter(ImageFilter.GaussianBlur(10)); cv.alpha_composite(glow); cv.alpha_composite(ov)
    # C. business-type pixel badges
    BIZ = [(26, "PLUMBING"), (29, "CLEANING"), (33, "PHYSIO CLINIC"), (37, "DENTAL CLINIC")]
    cur = None
    for wi, lab in BIZ:
        if t >= wt(wi) - 0.05: cur = (wi, lab)
    if cur and t < we(38) + 0.45:
        ia = t - wt(cur[0]) + 0.05
        a = 1 - ease_in((t - (we(38) + 0.2)) / 0.25)
        b = pixel_badge(cur[1], TEAL_G, "?", 40)
        paste(cv, b, 540, 1460, 0.75 + 0.25 * back_out(min(1, ia / 0.22), 1.8), min(1, ia / 0.08) * a)
    # D. leads draining (hearts)
    if wt(39) <= t < we(50) + 0.4:
        a = min(ease_out((t - wt(39)) / 0.25), 1 - ease_in((t - (we(50) + 0.15)) / 0.25))
        if a > 0.01:
            y = 1500; widget(cv, 540, y, 520, 100, a)
            lab = text_img("Leads", "pixb", 34, WHITE, 0.02, shadow=False); paste(cv, lab, 380, y, 1, a)
            lost = 0 if t < wt(43) else (1 if t < wt(45) else (2 if t < wt(48) else 3))
            for k in range(3):
                hc = RED if k >= lost else (70, 74, 78)
                hs = pixel_sprite(HEART, 9, hc, key=("h", hc))
                paste(cv, hs, 560 + k * 90, y, 1, a)
    # G. friction badge + leads saved
    if wt(86) <= t < we(89) + 0.4:
        ia = t - wt(86); a = 1 - ease_in((t - (we(89) + 0.15)) / 0.25)
        paste(cv, pixel_badge("FRICTION POINT", RED, "!", 40), 540, 1470, 0.75 + 0.25 * back_out(min(1, ia / 0.22), 1.8), min(1, ia / 0.08) * a)
    if wt(98) <= t < we(100) + 0.7:
        ia = t - wt(99); a = 1 - ease_in((t - (we(100) + 0.45)) / 0.25)
        if ia > 0:
            widget(cv, 540, 1480, 470, 150, a * ease_out(ia / 0.15))
            d = ImageDraw.Draw(cv)
            for k in range(3):
                paste(cv, pixel_sprite(HEART, 8, RED, key=("h", RED)), 470 + k * 70, 1445, 1, a * ease_out((ia - k * 0.08) / 0.12))
            sv = text_img("LEADS SAVED!", "pixb", 40, TEAL_G, 0.04, shadow=False)
            paste(cv, sv, 540, 1515, 1, a * ease_out((ia - 0.2) / 0.15))
    # I. chat-style follow input
    if t >= wt(112) - 0.1:
        ia = t - (wt(112) - 0.1)
        a = ease_out(ia / 0.3)
        y = 1500
        d = ImageDraw.Draw(cv)
        d.rounded_rectangle([90, y - 48, 990, y + 48], 48, fill=(20, 24, 27, int(230 * a)), outline=(80, 88, 92, int(220 * a)), width=2)
        txt = "Follow for Google Ads analytics"
        n = max(0, min(len(txt), int(ia / 0.045)))
        im = text_img(txt[:n], "med", 34, WHITE, 0, shadow=False); cv.alpha_composite(im, (130 - 40, int(y - im.height / 2)))
        tap = t - (wt(120) + 0.1)
        sc = 1 - 0.12 * math.sin(min(1, max(0, tap / 0.25)) * math.pi) if tap > 0 else 1
        r = 34 * sc
        d.ellipse([930 - r, y - r, 930 + r, y + r], fill=TEAL + (int(255 * a),))
        d.polygon([(930, y - 16 * sc), (918, y + 2), (942, y + 2)], fill=WHITE + (int(255 * a),))
        d.rectangle([926, y - 2, 934, y + 16 * sc], fill=WHITE + (int(255 * a),))
        if 0 < tap < 0.5:
            rr = 30 + 60 * ease_out(tap / 0.5)
            d.ellipse([930 - rr, y - rr, 930 + rr, y + rr], outline=WHITE + (int(200 * (1 - tap / 0.5)),), width=4)

# ---------------- article card behind the head (needs person mask) ----------------
CARD_S, CARD_E = wt(101) - 0.1, we(111) + 0.3
_seg = None
_pm = None
def person_mask(fr):
    global _seg, _pm
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    if _seg is None:
        _seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path="seg.tflite"), output_confidence_masks=True))
    small = cv2.resize(fr, (288, 512), interpolation=cv2.INTER_AREA)
    r = _seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small)))
    m = cv2.resize(1 - np.squeeze(r.confidence_masks[0].numpy_view()).astype(np.float32), (288, 512))
    _pm = m if _pm is None else _pm * 0.5 + m * 0.5
    mf = cv2.ximgproc.guidedFilter(fr, cv2.resize(_pm, (W_, H_), interpolation=cv2.INTER_CUBIC), 8, 1e-3)
    return np.clip((mf - 0.3) / 0.45, 0, 1)

def article_card(t):
    age = t - CARD_S
    lay = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    p = ease_out(age / 0.35); a = min(p, 1 - ease_in((t - (CARD_E - 0.25)) / 0.25))
    x0, y0, x1, y1 = 150, 180 + (1 - p) * 80, 930, 1080 + (1 - p) * 80
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0 + 10, y0 + 16, x1 + 10, y1 + 16], 18, fill=(0, 0, 0, int(120 * a)))
    lay = lay.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(250, 250, 248, int(255 * a)))
    h1 = text_img("MORE TRAFFIC", "anton", 120, (12, 12, 12), 0, shadow=False)
    h2 = text_img("WON'T FIX IT", "anton", 120, TEAL, 0, shadow=False)
    paste(lay, h1, x0 + 40 + h1.width / 2 - 40, y0 + 110, 1, a); paste(lay, h2, x0 + 40 + h2.width / 2 - 40, y0 + 240, 1, a)
    body = ["If your website doesn't convert,", "more visitors only means more", "people leaving without calling."]
    for k, ln in enumerate(body):
        b = text_img(ln, "med", 34, (60, 60, 60), 0, shadow=False); paste(lay, b, x0 + 40 + b.width / 2 - 40, y0 + 390 + k * 52, 1, a)
    return lay, a

# ---------------- zoom ----------------
ZOOM = {10: 0.08, 16: 0.06, 43: 0.09, 109: 0.08}
FACE = (540.0, 640.0)
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

# ---------------- compositor ----------------
FLASH = 0.16
def footage(fr, t):
    f = camera(fr, t)
    if CARD_S <= t < CARD_E:
        m = person_mask(f)[..., None]
        lay, a = article_card(t)
        base = Image.fromarray(f).convert("RGBA"); base.alpha_composite(lay)
        f = (np.asarray(base.convert("RGB")) * (1 - m) + f * m).astype(np.uint8)
    cv = Image.fromarray(f).convert("RGBA")
    overlays(cv, t)
    caption(cv, t, 1300 if CARD_S <= t < CARD_E else None)
    return np.asarray(cv.convert("RGB"))

def render(fr, t):
    c = canvas_at(t)
    out = np.asarray(SCENE[c["kind"]](t, c).convert("RGB")) if c else footage(fr, t)
    # white flash on every cut into / out of a canvas
    for cc in CANVAS:
        for edge in (cc["s"], cc["e"]):
            u = abs(t - edge)
            if u < FLASH:
                k = (1 - u / FLASH) ** 1.5 * 0.85
                out = (out * (1 - k) + 255 * k).astype(np.uint8)
    return out

# ---------------- sound ----------------
def square(f, d, decay=18):
    tt = np.arange(int(d * S.SR)) / S.SR
    x = np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-tt * decay)
    return np.stack([x, x], 1) * 0.6
def arp(notes, step=0.07):
    out = np.zeros((int((len(notes) * step + 0.2) * S.SR), 2))
    for k, f in enumerate(notes):
        s_ = square(f, 0.16, 14); i = int(k * step * S.SR); out[i:i + len(s_)] += s_
    return out

EV = []
def sfx(t, n, g, pan=0.0): EV.append((t, n, g, pan))
def plan():
    EV.clear()
    for c in group_chunks():
        if any(in_canvas(wt(i)) for i in c["ws"]): continue
        key = [i for i in c["ws"] if i in POS or i in NEG]
        if key:
            k = key[0]
            if k in NEG: sfx(wt(k), "glitch", 0.10); sfx(wt(k), "impact", 0.12)
            else: sfx(wt(k) - 0.08, "swish", 0.09); sfx(wt(k), "pop", 0.09)
    for i, s_ in ZOOM.items(): sfx(wt(i) - 0.02, "impact", 0.10 + s_)
    for k in range(18): sfx(0.25 + k * 0.1, "tick", 0.035)
    sfx(wt(7), "blip_hi", 0.06); sfx(wt(9), "arp_down", 0.07)
    for wi in (26, 29, 33, 37): sfx(wt(wi), "blip", 0.07)
    sfx(wt(43), "arp_down", 0.06)
    sfx(wt(86), "blip", 0.07); sfx(wt(99), "arp_up", 0.08)
    for c in CANVAS:
        sfx(c["s"] - 0.5, "riser", 0.06); sfx(c["s"] - 0.06, "whoosh", 0.17); sfx(c["s"], "impact", 0.2)
        sfx(c["e"] - 0.06, "whoosh_up", 0.12)
    r0, r1 = wt(56), we(66)
    for cf in CLICKS: sfx(r0 + cf * (r1 - r0), "click", 0.16)
    for k in range(22): sfx(CANVAS[0]["s"] + 0.2 + k * 0.035, "tick", 0.025)
    for wi, _ in STRUG: sfx(wt(wi), "glitch", 0.08); sfx(wt(wi), "blip_lo", 0.06)
    sfx(CARD_S, "whoosh", 0.12); sfx(wt(109), "impact", 0.14)
    for k in range(30): sfx(wt(112) - 0.1 + k * 0.045, "tick", 0.03)
    sfx(wt(120) + 0.1, "click", 0.16); sfx(wt(120) + 0.12, "pop", 0.08)
    return EV

def build_audio():
    lib = {"pop": S.pop(), "swish": S.swish(), "click": S.click(), "glitch": S.glitch(), "impact": S.impact(), "tick": S.tick(),
           "whoosh": S.whoosh(), "whoosh_up": S.whoosh(0.4, 600, 6000, 0.6, -0.6), "riser": S.riser(0.6),
           "blip": square(880, 0.09), "blip_hi": square(1320, 0.07), "blip_lo": square(330, 0.12),
           "arp_up": arp([523, 659, 784, 1047]), "arp_down": arp([784, 622, 494, 392], 0.08)}
    wf = wave.open("base2_audio.wav"); sr = wf.getframerate()
    au = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    n = len(au); fx = np.zeros((n + S.SR, 2))
    for t, nm, g, pan in plan():
        x = lib[nm] * g; i = max(0, int(t * S.SR)); fx[i:i + len(x)] += x[: len(fx) - i]
    fx = fx[:n]
    m = S.music(n / S.SR + 1)[:n]
    venv = np.convolve(np.sqrt(np.convolve(au ** 2, np.ones(2400) / 2400, "same")), np.ones(9600) / 9600, "same")
    rel = np.clip(venv / (np.percentile(venv, 90) + 1e-6), 0, 1)
    tt = np.arange(n) / S.SR
    fade = np.minimum(1, tt / 1.0) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    mix = np.repeat(au[:, None], 2, 1) * 0.92 + fx * (1 - 0.25 * rel)[:, None] + m * (0.15 * (1 - 0.55 * rel) * fade)[:, None]
    pk = np.abs(mix).max()
    if pk > 0.98: mix = mix / pk * 0.98
    with wave.open("mix_p3.wav", "wb") as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(S.SR); o.writeframes((mix * 32767).astype(np.int16).tobytes())

def frames(t0, t1):
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", "base2.mov", "-t", f"{t1 - t0:.4f}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k0 = int(round(t0 * FPS)); nf = int(round((t1 - t0) * FPS)); last = None
    for k in range(nf):
        raw = dec.stdout.read(W_ * H_ * 3)
        if len(raw) == W_ * H_ * 3: last = np.frombuffer(raw, np.uint8).reshape(H_, W_, 3)
        yield (k0 + k) / FPS, last

if __name__ == "__main__":
    if MODE == "preview":
        for ts in sys.argv[2:]:
            t = float(ts)
            for tt, fr in frames(max(0, t - 0.2), t + 1 / FPS):
                img = render(fr, tt)
            Image.fromarray(img).resize((360, 640)).save(f"pv_{ts}.png")
        sys.exit()
    if MODE == "audio": build_audio(); sys.exit()
    t0, t1 = (float(sys.argv[2]), float(sys.argv[3])) if MODE == "clip" else (0.0, TOTAL)
    if not os.path.exists("mix_p3.wav"): build_audio()
    out = f"clip_p3_{t0:.3f}.mp4" if MODE == "clip" else "final_p3.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}", "-r", str(FPS), "-i", "-",
                            "-vf", "noise=alls=4:allf=t,unsharp=5:5:0.35,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-an", out], stdin=subprocess.PIPE)
    for t, fr in frames(t0, t1): enc.stdin.write(render(fr, t).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out)
