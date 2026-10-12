"""Revision 2: motion graphics, brand cards, zooms, full sound design."""
import json, subprocess, sys, wave, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, ".")
import sound as S

W_, H_, FPS = 1080, 1920, 30
F = "fonts/"
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
CLIP = len(sys.argv) > 1 and sys.argv[1] == "clip"   # clip t0 t1 -> short mp4

# ---------- palette ----------
INK = (23, 43, 38)          # deep forest green #172B26 (primary text)
SUB = (86, 108, 101)        # secondary text
TEAL = (13, 148, 136)       # #0D9488 checkmarks / positive / keywords
BLUE = (37, 99, 235)        # #2563EB numbers & data (sparingly)
ACC = TEAL
CORAL = TEAL
WHITE = (255, 255, 255)

cut = json.load(open("cut.json"))
words = cut["words"]
for w in words:
    w["t"] = w["w"].strip()
segs = cut["keep"]
seg_starts, acc_ = [], 0.0
for s, e in segs:
    seg_starts.append(acc_); acc_ += e - s
BASE_DUR = acc_
TOTAL = BASE_DUR

def wt(i): return words[i]["ns"]
def we(i): return words[i]["ne"]

def ease_out(p): p = min(1, max(0, p)); return 1 - (1 - p) ** 3
def ease_in(p): p = min(1, max(0, p)); return p ** 3
def ease_io(p): p = min(1, max(0, p)); return 3 * p * p - 2 * p * p * p
def back_out(p, s=1.7):
    p = min(1, max(0, p)) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2

# ---------- content plan ----------
FIX = {"Metapixel": "Meta Pixel", "-driven": "driven"}
# keyword -> (style, color, icon)
KW = {
    10: ("pop", WHITE, None),
    25: ("slide", WHITE, "users"),
    33: ("highlight", WHITE, "funnel"),
    52: ("highlight", WHITE, None),
    56: ("pop", WHITE, "target"),
    66: ("count", WHITE, None),
    93: ("slide", WHITE, None),
    112: ("highlight", WHITE, None),
    122: ("shake", WHITE, "warn"),
    150: ("pop", WHITE, None),
    154: ("pop", WHITE, None),
    163: ("pop", WHITE, "chart"),
    199: ("highlight", WHITE, None),
    208: ("pop", WHITE, "check"),
    218: ("pop", WHITE, "dollar"),
    223: ("slide", WHITE, None),
    233: ("pop", WHITE, None),
    239: ("count", WHITE, "arrow"),
    252: ("slide", WHITE, None),
    265: ("shake", WHITE, "warn"),
    272: ("pop", WHITE, "dollar"),
    282: ("highlight", WHITE, None),
    288: ("pop", WHITE, "chart"),
}
COUNT = {66: (0, 300, "{:.0f}"), 239: (1, 5, "{:.0f}x")}
ITAL = {0, 136, 285, 290}
# punch-in zooms: word index -> strength
ZOOM = {4: 0.07, 33: 0.09, 52: 0.11, 66: 0.09, 122: 0.1, 136: 0.1, 163: 0.09,
        208: 0.08, 239: 0.11, 265: 0.1, 282: 0.09, 288: 0.08, 290: 0.12}

COUNTER = (wt(4), wt(10) - 0.05)          # $3,000 - $4,000 scene
CARDS = [
    dict(kind="wave", a=36, b=40, big="question?"),
    dict(kind="list", a=72, b=86, title="300 BUSINESS OWNERS",
         items=[(73, "Healthcare clinics"), (75, "Physiotherapy"), (77, "Home services"),
                (80, "HVAC companies"), (82, "Plumbers"), (83, "Roofers"), (84, "Ecommerce")]),
    dict(kind="wave", a=123, b=127, big="the thing."),
    dict(kind="list", a=171, b=189, title="YOUR TRACKING STACK",
         items=[(171, "Ads conversion tracking"), (174, "Google Analytics"),
                (177, "Meta Pixel + CAPI"), (181, "TikTok Pixel"), (183, "Microsoft Clarity")]),
    dict(kind="no", a=241, b=241),
]
T_IN, T_OUT = 0.32, 0.30
for c in CARDS:
    c["s"] = wt(c["a"]) - 0.12
    c["e"] = we(c["b"]) + 0.22
    # zoom-out return after each card
    c["ret"] = c["e"]

def card_at(t):
    for c in CARDS:
        if c["s"] <= t < c["e"]:
            return c
    return None

def in_card_word(i):
    t = wt(i) + 0.02
    return any(c["s"] + 0.05 <= t < c["e"] for c in CARDS)

# ---------- fonts / text ----------
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        if name == "ital":
            f = ImageFont.truetype(F + "Playfair-Italic.ttf", size); f.set_variation_by_name("Bold Italic")
        else:
            f = ImageFont.truetype(F + {"semi": "Poppins-SemiBold.ttf", "bold": "Poppins-Bold.ttf", "regular": "Poppins-Regular.ttf", "medium": "Poppins-Medium.ttf",
                                        "xbold": "Poppins-ExtraBold.ttf"}[name], size)
        _fc[k] = f
    return _fc[k]

_tc = {}
def text_img(txt, name, size, color=WHITE, track=0.0, shadow=True, maxw=None, glow=None):
    k = (txt, name, size, color, track, shadow, maxw, glow)
    if k in _tc: return _tc[k]
    while True:
        f = font(name, size); sp = track * size
        ws = [f.getlength(ch) for ch in txt]
        tw = sum(ws) + sp * (len(txt) - 1)
        if maxw is None or tw <= maxw or size < 40: break
        size = int(size * 0.93)
    asc, desc = f.getmetrics(); pad = 44
    im = Image.new("RGBA", (int(tw) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = pad
    for ch, cw in zip(txt, ws):
        d.text((x, pad), ch, font=f, fill=color + (255,)); x += cw + sp
    alpha = im.split()[3]
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if glow:
        g = Image.new("RGBA", im.size, glow + (0,)); g.putalpha(alpha.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.8)))
        base = Image.alpha_composite(base, g)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6)))
        sh2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh2.paste(sh, (0, 5))
        base = Image.alpha_composite(base, sh2)
    im = Image.alpha_composite(base, im)
    _tc[k] = im
    return im

def paste(canvas, img, cx, cy, scale=1.0, alpha=1.0, dx=0, dy=0, rot=0):
    if alpha <= 0.01 or scale <= 0.01: return
    if abs(scale - 1) > 0.002:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if rot: img = img.rotate(rot, Image.BILINEAR, expand=True)
    if alpha < 0.999:
        img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(img, (int(cx - img.width / 2 + dx), int(cy - img.height / 2 + dy)))

def popin(canvas, img, cx, cy, age, dur=0.16, s0=0.7, overshoot=True, **kw):
    if age < 0: return
    p = age / dur
    s = s0 + (1 - s0) * (back_out(p, 1.4) if overshoot else ease_out(p))
    paste(canvas, img, cx, cy, s, min(1, p * 2.2), **kw)

# ---------- icons ----------
_ic = {}
def icon(name, size=124):
    if name in _ic: return _ic[name]
    S4 = size * 4
    im = Image.new("RGBA", (S4, S4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([8, 8, S4 - 8, S4 - 8], fill=(255, 255, 255, 235))
    d.ellipse([8, 8, S4 - 8, S4 - 8], outline=(255, 255, 255, 255), width=10)
    c = S4 / 2; u = S4 / 10; wd = int(u * 0.75)
    Wt = (BLUE if name in ("dollar", "chart", "arrow") else TEAL) + (255,)
    if name == "warn": Wt = INK + (255,)
    if name == "check":
        d.line([(c - 2.2 * u, c + 0.1 * u), (c - 0.6 * u, c + 1.7 * u), (c + 2.4 * u, c - 1.6 * u)], fill=Wt, width=wd, joint="curve")
    elif name == "dollar":
        f = font("xbold", int(S4 * 0.55)); d.text((c, c + u * 0.3), "$", font=f, fill=Wt, anchor="mm")
    elif name == "chart":
        for k, hgt in enumerate((1.2, 2.2, 3.4)):
            x0 = c - 2.4 * u + k * 1.7 * u
            d.rounded_rectangle([x0, c + 2.2 * u - hgt * u, x0 + 1.1 * u, c + 2.2 * u], radius=u * 0.3, fill=Wt)
        d.line([(c - 2.6 * u, c - 0.2 * u), (c - 0.6 * u, c - 1.6 * u), (c + 0.6 * u, c - 0.8 * u), (c + 2.5 * u, c - 2.6 * u)], fill=Wt, width=int(u * 0.45), joint="curve")
    elif name == "arrow":
        d.polygon([(c, c - 2.8 * u), (c + 2.2 * u, c - 0.4 * u), (c + 0.8 * u, c - 0.4 * u), (c + 0.8 * u, c + 2.6 * u),
                   (c - 0.8 * u, c + 2.6 * u), (c - 0.8 * u, c - 0.4 * u), (c - 2.2 * u, c - 0.4 * u)], fill=Wt)
    elif name == "target":
        for r_, w_ in ((2.8, 0.55), (1.7, 0.55)):
            d.ellipse([c - r_ * u, c - r_ * u, c + r_ * u, c + r_ * u], outline=Wt, width=int(w_ * u))
        d.ellipse([c - 0.6 * u, c - 0.6 * u, c + 0.6 * u, c + 0.6 * u], fill=Wt)
    elif name == "funnel":
        d.polygon([(c - 2.8 * u, c - 2.2 * u), (c + 2.8 * u, c - 2.2 * u), (c + 0.7 * u, c + 0.4 * u), (c + 0.7 * u, c + 2.6 * u),
                   (c - 0.7 * u, c + 1.9 * u), (c - 0.7 * u, c + 0.4 * u)], fill=Wt)
    elif name == "warn":
        d.polygon([(c, c - 2.6 * u), (c + 2.7 * u, c + 2.0 * u), (c - 2.7 * u, c + 2.0 * u)], fill=Wt)
        d.rectangle([c - 0.32 * u, c - 1.0 * u, c + 0.32 * u, c + 0.8 * u], fill=(255, 255, 255, 255))
        d.ellipse([c - 0.36 * u, c + 1.1 * u, c + 0.36 * u, c + 1.8 * u], fill=(255, 255, 255, 255))
    elif name == "users":
        d.ellipse([c - 1.0 * u, c - 2.6 * u, c + 1.0 * u, c - 0.6 * u], fill=Wt)
        d.pieslice([c - 2.2 * u, c - 0.2 * u, c + 2.2 * u, c + 4.0 * u], 180, 360, fill=Wt)
        d.ellipse([c - 3.0 * u, c - 1.8 * u, c - 1.5 * u, c - 0.3 * u], fill=TEAL + (140,))
        d.ellipse([c + 1.5 * u, c - 1.8 * u, c + 3.0 * u, c - 0.3 * u], fill=TEAL + (140,))
    im = im.resize((size, size), Image.LANCZOS)
    sh = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    a = Image.new("L", sh.size, 0); a.paste(im.split()[3], (20, 26))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.35)))
    sh.alpha_composite(im, (20, 20))
    _ic[name] = sh
    return sh

# ---------- glassmorphism ----------
def glass(canvas, cx, cy, w, h, r=40, a=1.0, scale=1.0, frost=0.72, blur=20, border=210):
    """frosted panel: backdrop blur + white tint + thin white border + soft shadow"""
    if a <= 0.01: return
    w2, h2 = int(w * scale), int(h * scale); r2 = int(r * scale)
    x0, y0 = int(cx - w2 / 2), int(cy - h2 / 2)
    x0c, y0c = max(0, x0), max(0, y0); x1c, y1c = min(W_, x0 + w2), min(H_, y0 + h2)
    if x1c <= x0c or y1c <= y0c: return
    # soft shadow
    sh = Image.new("L", (w2 + 100, h2 + 100), 0)
    ImageDraw.Draw(sh).rounded_rectangle([50, 62, 50 + w2, 62 + h2], r2, fill=int(80 * a))
    shl = Image.new("RGBA", sh.size, (8, 30, 25, 0)); shl.putalpha(sh.filter(ImageFilter.GaussianBlur(22)))
    canvas.alpha_composite(shl, (x0 - 50, y0 - 50)) if x0 - 50 >= 0 and y0 - 50 >= 0 else None
    # frosted backdrop
    reg = np.asarray(canvas.crop((x0c, y0c, x1c, y1c)).convert("RGB")).astype(np.float32)
    fr = cv2.GaussianBlur(reg, (0, 0), blur)
    hh = fr.shape[0]
    hl = np.linspace(1.0, 0.0, hh)[:, None, None] * 0.12   # top sheen
    fr = fr * (1 - frost) + 255 * frost
    fr = fr * (1 - hl) + 255 * hl
    m = Image.new("L", (w2, h2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w2 - 1, h2 - 1], r2, fill=int(255 * a))
    m = m.crop((x0c - x0, y0c - y0, x1c - x0, y1c - y0))
    fi = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).convert("RGBA"); fi.putalpha(m)
    canvas.alpha_composite(fi, (x0c, y0c))
    # thin white border
    bl = Image.new("RGBA", (w2 + 4, h2 + 4), (0, 0, 0, 0))
    ImageDraw.Draw(bl).rounded_rectangle([2, 2, w2 + 1, h2 + 1], r2, outline=(255, 255, 255, int(border * a)), width=2)
    canvas.alpha_composite(bl, (x0 - 2, y0 - 2)) if x0 - 2 >= 0 and y0 - 2 >= 0 else None

def panel_anim(age, dur=0.24):
    p = ease_out(age / dur)
    return p, 0.95 + 0.05 * p, (1 - p) * 28      # alpha, scale, dy

def round_rect_img(w, h, r, fill, outline=None, ow=0, blur_shadow=True):
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    if blur_shadow:
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle([30, 38, 30 + w, 38 + h], r, fill=120)
        s2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); s2.putalpha(sh.filter(ImageFilter.GaussianBlur(14))); im = s2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 30, 30 + w, 30 + h], r, fill=fill, outline=outline, width=ow)
    return im

# ---------- SFX timeline ----------
EV = []   # (time, name, gain, pan)
def sfx(t, name, g, pan=0.0): EV.append((t, name, g, pan))

# ---------- caption system ----------
CY = 1340

def disp(i):
    return FIX.get(words[i]["t"], words[i]["t"])

def big_txt(i):
    return disp(i).rstrip(",?.")

def in_counter(i):
    return 4 <= i <= 9

def kw_block_start(c):
    """return keyword index governing word c (if within 1.7s & <=3 trailing words)"""
    for j in range(c, max(-1, c - 4), -1):
        if j in KW and wt(c) - wt(j) < 1.7 and not in_card_word(j):
            return j
        if j != c and (j in ITAL or in_card_word(j)):
            return None
    return None

# ===== footage typography: clean white, no panels =====
def units_build():
    """split words into display units: keyword blocks, italic accents, plain chunks"""
    owner = {}
    blocks = {}
    for k in sorted(KW):
        if in_card_word(k) or in_counter(k): continue
        pre, j = [], k - 1
        while j >= 0 and len(pre) < 3 and j not in KW and j not in ITAL and not in_card_word(j) and not in_counter(j) \
                and j not in owner and wt(j + 1) - we(j) < 0.35 and wt(k) - wt(j) < 1.3 \
                and not disp(j).endswith((".", "?", ",")):
            pre.insert(0, j); j -= 1
        post, j = [], k + 1
        while j < len(words) and len(post) < 3 and j not in KW and j not in ITAL and not in_card_word(j) and not in_counter(j) \
                and wt(j) - we(j - 1) < 0.35 and wt(j) - wt(k) < 1.5 and not disp(j - 1).endswith((".", "?")):
            post.append(j); j += 1
        u = dict(kind="kw", k=k, pre=pre, post=post, ws=pre + [k] + post)
        for x in u["ws"]: owner[x] = u
    units = []
    i = 0
    while i < len(words):
        if i in owner:
            u = owner[i]
            if not units or units[-1] is not u: units.append(u)
            i += 1; continue
        if in_card_word(i) or in_counter(i): i += 1; continue
        if i in ITAL:
            units.append(dict(kind="ital", ws=[i])); i += 1; continue
        ch = [i]; j = i + 1
        while j < len(words) and len(ch) < 3 and j not in owner and j not in ITAL and not in_card_word(j) and not in_counter(j) \
                and wt(j) - we(j - 1) < 0.3 and not disp(j - 1).endswith((".", "?", ",")):
            ch.append(j); j += 1
        units.append(dict(kind="plain", ws=ch)); i = j
    for u in units:
        u["t0"] = wt(u["ws"][0])
    for n, u in enumerate(units):
        nxt = units[n + 1]["t0"] if n + 1 < len(units) else 1e9
        u["t1"] = min(nxt, we(u["ws"][-1]) + 0.65)
    return units

SHADOW_TXT = {}
def wtxt(s, name, size, track=0.0):
    return text_img(s, name, size, WHITE, track, shadow=True)

def line_layout(ids, name, size, upper=False):
    f = font(name, size)
    toks = [disp(i).upper() if upper else disp(i) for i in ids]
    sp = f.getlength(" ")
    ws = [f.getlength(tk) for tk in toks]
    total = sum(ws) + sp * (len(toks) - 1)
    xs, x = [], W_ / 2 - total / 2
    for w_ in ws:
        xs.append(x + w_ / 2); x += w_ + sp
    return toks, xs

def reveal_word(canvas, img, x, y, age, ua, dur=0.22, rise=18):
    if age < 0: return
    p = ease_out(age / dur)
    paste(canvas, img, x, y + (1 - p) * rise, 1.0, p * ua)

def draw_line(canvas, ids, t, y, name, size, ua, upper=False):
    toks, xs = line_layout(ids, name, size, upper)
    for i, tk, x in zip(ids, toks, xs):
        reveal_word(canvas, wtxt(tk, name, size), x, y, t - wt(i), ua)

UNITS = None
def caption(canvas, t):
    global UNITS
    if UNITS is None: UNITS = units_build()
    u = None
    for x in UNITS:
        if x["t0"] <= t < x["t1"]: u = x
        if x["t0"] > t: break
    if u is None: return
    ua = min(1.0, (u["t1"] - t) / 0.16)          # fade-out at unit end
    if u["kind"] == "plain":
        draw_line(canvas, u["ws"], t, CY, "medium", 72, ua)
    elif u["kind"] == "ital":
        i = u["ws"][0]
        im = text_img(disp(i).rstrip(".,"), "ital", 140, WHITE, maxw=940)
        age = t - wt(i); p = ease_out(age / 0.35)
        paste(canvas, im, W_ / 2, CY + (1 - p) * 20, 0.96 + 0.04 * p, p * ua)
    else:
        k = u["k"]; age = t - wt(k)
        style = KW[k][0]
        if style == "count":
            a, b, fmt = COUNT[k]
            v = a + (b - a) * ease_out(age / 0.6)
            txt = "{:,.0f}".format(v) if k == 66 else fmt.format(v).upper()
        else:
            txt = big_txt(k).upper()
        big = text_img(txt, "xbold", 168, WHITE, -0.02, shadow=True, maxw=960)
        p = ease_out(age / 0.3)
        if age >= 0:
            paste(canvas, big, W_ / 2, CY + 10 + (1 - p) * 14, 0.92 + 0.08 * p, p * ua)
        if u["pre"]:
            draw_line(canvas, u["pre"], t, CY - 112, "regular", 64, ua)
        if u["post"]:
            draw_line(canvas, u["post"], t, CY + 128, "regular", 64, ua)

# ---------- $3,000 - $4,000 counter ----------
def counter(canvas, t):
    a0, a1 = COUNTER
    age = t - a0
    p_in = ease_out(age / 0.35)
    out = ease_in(max(0, (t - (a1 - 0.2)) / 0.2))
    alpha = p_in * (1 - out)
    y = CY + 10 + (1 - p_in) * 18
    lab = text_img("MONTHLY AD SPEND", "medium", 36, WHITE, 0.18, shadow=True)
    paste(canvas, lab, W_ / 2, y - 120, 1.0, alpha * 0.9)
    t3 = wt(4); t4 = wt(6)
    v1 = 3000 * ease_out((t - t3) / 0.55)
    n1 = text_img("${:,.0f}".format(v1), "xbold", 150, WHITE, -0.02, shadow=True)
    if t >= t4 - 0.05:
        v2 = 3000 + 1000 * ease_out((t - t4) / 0.5)
        n2 = text_img("${:,.0f}".format(v2), "xbold", 150, WHITE, -0.02, shadow=True)
        dash = text_img("–", "regular", 120, WHITE, shadow=True)
        p2 = ease_out((t - t4 + 0.05) / 0.3)
        c1, cd, c2 = n1.width - 88, dash.width - 88, n2.width - 88
        gap = 22
        total = c1 + cd + c2 + gap * 2
        sc = min(1, 940 / total)
        xs = W_ / 2 - total * sc / 2
        paste(canvas, n1, xs + c1 * sc / 2, y, sc, alpha)
        paste(canvas, dash, xs + (c1 + gap + cd / 2) * sc, y - 4, sc, alpha * p2)
        paste(canvas, n2, xs + (c1 + gap * 2 + cd + c2 / 2) * sc, y + (1 - p2) * 14, sc, alpha * p2)
    else:
        paste(canvas, n1, W_ / 2, y, 1.0, alpha)
    tm = wt(7)
    if t >= tm:
        mt = text_img("every month", "regular", 54, WHITE, 0.0, shadow=True)
        pm = ease_out((t - tm) / 0.25)
        paste(canvas, mt, W_ / 2, y + 118 + (1 - pm) * 14, 1.0, pm * alpha)

# ---------- brand cards ----------
yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
def _grad():
    top = np.array([255, 255, 255], np.float32); mid = np.array([0xF6, 0xFB, 0xF9], np.float32); bot = np.array([0xE6, 0xF3, 0xEE], np.float32)
    v = (yy / H_)[..., None]
    g = np.where(v < 0.5, top + (mid - top) * (v / 0.5), mid + (bot - mid) * ((v - 0.5) / 0.5))
    # soft mint glow top-right and lower-left
    g -= (np.exp(-(((xx - 900) / 520) ** 2 + ((yy - 300) / 520) ** 2)) * 10)[..., None] * np.array([1, 0.3, 0.6])
    g -= (np.exp(-(((xx - 150) / 600) ** 2 + ((yy - 1650) / 600) ** 2)) * 14)[..., None] * np.array([1, 0.35, 0.6])
    return g
GRAD = _grad()
GRID_P = 72
LINE = np.array([0xC9, 0xE2, 0xD8], np.float32)

def card_bg(t, c):
    age = t - c["s"]
    off = (t * 14) % GRID_P
    gx = np.abs(((xx + 0) % GRID_P) - GRID_P / 2) > GRID_P / 2 - 1.2
    gy = np.abs(((yy + off) % GRID_P) - GRID_P / 2) > GRID_P / 2 - 1.2
    grid = (gx | gy).astype(np.float32)
    # reveal from centre outwards
    rad = np.sqrt((xx - W_ / 2) ** 2 + (yy - H_ / 2) ** 2)
    reveal = np.clip((age * 2600 - rad) / 300, 0, 1)
    # soft light sweep (diagonal band)
    sweep_pos = ((t * 0.45) % 1.6 - 0.3) * (W_ + H_)
    band = np.exp(-(((xx + yy) - sweep_pos) / 160) ** 2)
    a = grid * reveal * (0.55 + 0.45 * band)
    img = GRAD * (1 - a[..., None]) + LINE * a[..., None]
    img += band[..., None] * 6
    # fade grid toward edges (vignette)
    return np.clip(img, 0, 255).astype(np.uint8)

# waveform envelope
wf = wave.open("base2_audio.wav"); sr = wf.getframerate()
au = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
HOP = sr // 100
env = np.sqrt(np.convolve(au ** 2, np.ones(HOP) / HOP, "same")[::HOP]); env /= np.percentile(env, 99) + 1e-6

def card_wave(cv, t, c):
    age = t - c["s"]
    pa, ps, pdy = panel_anim(age - 0.1, 0.3)
    glass(cv, W_ / 2, 1110 + pdy, 900, 220, 44, pa, ps, frost=0.55, blur=14)
    d = ImageDraw.Draw(cv)
    n, x0, gap, y0 = 104, 182, 6.9, 1110 + pdy
    for k in range(n):
        tt = t - (n - k) * 0.011
        a = env[min(len(env) - 1, max(0, int(tt * 100)))]
        reveal = ease_out((age - 0.15 - abs(k - n / 2) / n * 0.4) / 0.25)
        h = (4 + 78 * a * (0.55 + 0.45 * math.sin(k * 1.7) ** 2)) * reveal
        x = x0 + k * gap
        if h > 0.5: d.rounded_rectangle([x, y0 - h / 2, x + 3, y0 + h / 2], 2, fill=TEAL + (int(255 * pa),))
    ws = [i for i in range(c["a"], c["b"] + 1) if wt(i) <= t]
    if not ws: return
    small = [i for i in ws if i != c["b"]]
    if small:
        im = text_img(" ".join(disp(i).rstrip(",") for i in small), "bold", 72, INK, shadow=False)
        paste(cv, im, W_ / 2, 760, 1.0, min(1, (t - wt(small[-1])) / 0.08))
    if c["b"] in ws:
        im = text_img(c["big"], "xbold", 180, TEAL, -0.04, shadow=False, maxw=960)
        popin(cv, im, W_ / 2, 900, t - wt(c["b"]), 0.2, 0.55)

def check_icon(p, size=78, sc=1.0):
    S4 = size * 4
    im = Image.new("RGBA", (S4, S4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([4, 4, S4 - 4, S4 - 4], fill=TEAL + (255,))
    pts = [(S4 * 0.27, S4 * 0.52), (S4 * 0.44, S4 * 0.68), (S4 * 0.74, S4 * 0.35)]
    L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); Lp = (L1 + L2) * p
    seg = [pts[0]]
    if Lp <= L1:
        q = Lp / L1; seg.append((pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q))
    else:
        q = (Lp - L1) / L2; seg += [pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)]
    if p > 0.02: d.line(seg, fill=(255, 255, 255, 255), width=int(S4 * 0.09), joint="curve")
    return im.resize((max(1, int(size * sc)), max(1, int(size * sc))), Image.LANCZOS)

def card_list(cv, t, c):
    age = t - c["s"]
    tt = text_img(c["title"], "bold", 40, SUB, 0.14, shadow=False)
    popin(cv, tt, W_ / 2, 470, age - 0.1, 0.2, 0.9, overshoot=False)
    d = ImageDraw.Draw(cv)
    ul = 140 * ease_out((age - 0.2) / 0.35)
    if ul > 1: d.rounded_rectangle([W_ / 2 - ul / 2, 515, W_ / 2 + ul / 2, 522], 3, fill=TEAL + (255,))
    items = c["items"]; step = 136 if len(items) > 6 else 160
    y0 = 650 if len(items) > 6 else 720
    shown = [it for it in items if wt(it[0]) <= t]
    for k, (wi, lab) in enumerate(items):
        ia = t - wt(wi)
        if ia < 0: break
        p = ease_out(ia / 0.3)
        y = y0 + k * step + (1 - p) * 24
        latest = k == len(shown) - 1
        glass(cv, W_ / 2, y, 840, 110, 30, p, 0.96 + 0.04 * p, frost=0.72 if latest else 0.5, blur=10,
              border=255 if latest else 190)
        cs = back_out((ia - 0.06) / 0.22, 1.6) if ia > 0.06 else 0
        ci = check_icon(ease_out((ia - 0.12) / 0.28), 78, max(0.01, cs))
        paste(cv, ci, 190, y, 1.0, p)
        im = text_img(lab, "bold", 58, INK if latest else SUB, -0.01, shadow=False, maxw=640)
        paste(cv, im, 250 + (im.width - 88) / 2, y, 1.0, p)

def card_no(cv, t, c):
    age = t - wt(241)
    if age < 0: return
    p = ease_out(age / 0.14)
    s = 1.6 - 0.6 * p
    dx = math.sin(age * 80) * 14 * max(0, 1 - age / 0.3) if age > 0.1 else 0
    pa, ps, pdy = panel_anim(age, 0.25)
    glass(cv, W_ / 2, H_ / 2 - 20 + pdy, 760, 470, 56, pa, ps, frost=0.6, blur=12)
    im = text_img("No.", "xbold", 330, INK, -0.05, shadow=False)
    paste(cv, im, W_ / 2, H_ / 2 - 60, s, min(1, p * 1.5), dx=dx)
    d = ImageDraw.Draw(cv)
    ul = 420 * ease_out((age - 0.12) / 0.25)
    if ul > 1: d.rounded_rectangle([W_ / 2 - ul / 2, H_ / 2 + 100, W_ / 2 + ul / 2, H_ / 2 + 114], 7, fill=TEAL + (255,))

CARD_FN = {"wave": card_wave, "list": card_list, "no": card_no}

# ---------- camera (zoom) ----------
FACE = (540.0, 700.0)
def seg_index(t):
    i = 0
    for k, s in enumerate(seg_starts):
        if s <= t: i = k
    return i

def zoom_at(t):
    z = 1.0 + (0.045 if seg_index(t) % 2 else 0.0)        # jump-cut reframes
    for i, s in ZOOM.items():
        a = wt(i)
        if a - 0.05 <= t < a + 1.9:
            u = t - a
            up = ease_io((u + 0.05) / 0.28)
            down = 1 - ease_io((u - 1.25) / 0.6)
            z *= 1 + s * min(up, down)
    for c in CARDS:   # smooth zoom-out when footage returns from a card
        u = t - c["e"]
        if 0 <= u < 0.6:
            z *= 1 + 0.08 * (1 - ease_out(u / 0.6))
        u2 = t - c["s"]
        if 0 <= u2 < T_IN:
            z *= 1 + 0.06 * ease_in(u2 / T_IN)
    return z

def camera(frame, t):
    z = zoom_at(t)
    if abs(z - 1) < 1e-3: return frame
    fx, fy = FACE
    M = np.float32([[z, 0, fx * (1 - z)], [0, z, fy * (1 - z)]])
    return cv2.warpAffine(frame, M, (W_, H_), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------- frame composition ----------
def footage_layer(fr, t):
    cv = Image.fromarray(camera(fr, t)).convert("RGBA")
    if COUNTER[0] - 0.05 <= t < COUNTER[1] + 0.05:
        counter(cv, t)
    caption(cv, t)
    return cv

def render(fr, t):
    c = card_at(t)
    if not c:
        return np.asarray(footage_layer(fr, t).convert("RGB"))
    card = Image.fromarray(card_bg(t, c)).convert("RGBA")
    CARD_FN[c["kind"]](card, t, c)
    card = np.asarray(card.convert("RGB"))
    a_in = ease_out((t - c["s"]) / T_IN)
    a_out = ease_in((t - (c["e"] - T_OUT)) / T_OUT)
    if a_in >= 1 and a_out <= 0:
        return card
    foot = np.asarray(footage_layer(fr, t).convert("RGB")).copy()
    if a_in < 1:      # card slides up from bottom, footage dims
        y = int(H_ * (1 - a_in))
        foot = (foot * (1 - 0.35 * a_in)).astype(np.uint8)
        foot[y:] = card[: H_ - y]
        if y > 0:
            sh = slice(max(0, y - 40), y)
            foot[sh] = (foot[sh] * np.linspace(1, 0.6, sh.stop - sh.start)[:, None, None]).astype(np.uint8)
        return foot
    # exit: card slides up and away revealing footage
    y = int(H_ * a_out)
    out = foot.copy()
    out[: H_ - y] = card[y:]
    return out

# ---------- SFX plan ----------
def plan_sfx():
    EV.clear()
    for k, (style, col, ic) in KW.items():
        if in_card_word(k): continue
        t = wt(k)
        if style == "count":
            for q in range(12): sfx(t + q * 0.05, "tick", 0.05, (q % 2) * 0.4 - 0.2)
            sfx(t + 0.6, "ding", 0.07)
        else:
            sfx(t - 0.10, "swish", 0.10, 0.15 if k % 2 else -0.15)
            sfx(t, "pop", 0.09)
    for i in ITAL:
        sfx(wt(i) - 0.15, "swish", 0.10)
    for i, s in ZOOM.items():
        if KW.get(i, ("",))[0] != "shake":
            sfx(wt(i) - 0.02, "impact", 0.14 + s)
    # counter scene
    a0 = COUNTER[0]
    sfx(a0 - 0.25, "whoosh", 0.14)
    for q in range(10): sfx(wt(4) + q * 0.05, "tick", 0.07, -0.3)
    sfx(wt(4) + 0.5, "impact", 0.12)
    for q in range(9): sfx(wt(6) + q * 0.05, "tick", 0.07, 0.3)
    sfx(wt(6) + 0.45, "ding", 0.13)
    sfx(COUNTER[1] - 0.2, "swish", 0.10)
    # cards
    for n, c in enumerate(CARDS):
        if c["kind"] in ("list", "no"):
            sfx(c["s"] - 0.85, "riser", 0.06)
        sfx(c["s"] - 0.12, "whoosh", 0.20)
        sfx(c["e"] - T_OUT - 0.05, "whoosh_up", 0.15)
        if c["kind"] == "list":
            for wi, _ in c["items"]:
                sfx(wt(wi), "click", 0.14, 0.3); sfx(wt(wi) + 0.1, "pop", 0.07)
        if c["kind"] == "wave":
            sfx(wt(c["b"]), "pop", 0.18); sfx(wt(c["b"]), "impact", 0.12)
        if c["kind"] == "no":
            sfx(wt(241), "impact_heavy", 0.42)
    return EV

def build_audio():
    lib = {"pop": S.pop(), "swish": S.swish(), "click": S.click(), "glitch": S.glitch(), "impact": S.impact(),
           "impact_heavy": S.impact(1.6, 120, 38, True), "tick": S.tick(), "ding": S.ding(), "bubble": S.bubble(),
           "whoosh": S.whoosh(), "whoosh_up": S.whoosh(0.4, 600, 6000, 0.6, -0.6), "riser": S.riser(0.9)}
    n = int(TOTAL * S.SR) + S.SR * 2
    fx = np.zeros((n, 2))
    for t, name, g, pan in plan_sfx():
        x = lib[name] * g
        if pan:
            l = math.cos((pan + 1) * math.pi / 4) * 1.414; r = math.sin((pan + 1) * math.pi / 4) * 1.414
            x = x * np.array([l, r])
        i = max(0, int(t * S.SR)); fx[i:i + len(x)] += x[: n - i]
    voice = np.repeat(au[:, None], 2, 1)
    if sr != S.SR: raise SystemExit("sr mismatch")
    n = len(voice)
    fx = fx[:n]
    # music bed with voice ducking, fade in/out, gentle duck under cards' impacts
    m = S.music(n / S.SR + 1)[:n]
    venv = np.sqrt(np.convolve(au ** 2, np.ones(2400) / 2400, "same"))
    venv = np.convolve(venv, np.ones(9600) / 9600, "same")
    duck = 1 - 0.55 * np.clip(venv / (np.percentile(venv, 90) + 1e-6), 0, 1)
    tt = np.arange(n) / S.SR
    fade = np.minimum(1, tt / 1.5) * np.clip((TOTAL - tt) / 2.0, 0, 1)
    m = m * (duck * fade * 0.16)[:, None]
    # sfx bus ducks slightly under voice too, so words stay on top
    fx = fx * (1 - 0.25 * np.clip(venv / (np.percentile(venv, 90) + 1e-6), 0, 1))[:, None]
    mix = voice * 0.92 + fx + m
    peak = np.abs(mix).max()
    if peak > 0.98: mix = mix / peak * 0.98
    with wave.open("mix4.wav", "wb") as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(S.SR)
        o.writeframes((mix * 32767).astype(np.int16).tobytes())

def frames(t0=0.0, t1=None):
    t1 = TOTAL if t1 is None else t1
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", "base2.mov", "-t", str(t1 - t0),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k0 = int(round(t0 * FPS)); nf = int(round((t1 - t0) * FPS)); last = None
    for k in range(nf):
        raw = dec.stdout.read(W_ * H_ * 3)
        if len(raw) == W_ * H_ * 3: last = np.frombuffer(raw, np.uint8).reshape(H_, W_, 3)
        yield (k0 + k) / FPS, last

TEX = "noise=alls=5:allf=t,unsharp=5:5:0.4,format=yuv420p"

if __name__ == "__main__":
    if PREVIEW:
        for ts in sys.argv[2:]:
            t = float(ts)
            for tt, fr in frames(t, t + 1 / FPS):
                Image.fromarray(render(fr, tt)).resize((360, 640)).save(f"p4_{ts}.png")
        sys.exit()
    build_audio()
    t0, t1 = (float(sys.argv[2]), float(sys.argv[3])) if CLIP else (0.0, TOTAL)
    out = "clip4.mp4" if CLIP else "final4.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}",
                            "-r", str(FPS), "-i", "-", "-ss", str(t0), "-t", str(t1 - t0), "-i", "mix4.wav",
                            "-vf", TEX, "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for k, (t, fr) in enumerate(frames(t0, t1)):
        enc.stdin.write(render(fr, t).tobytes())
        if k % 300 == 0: print(k, flush=True)
    enc.stdin.close(); enc.wait(); print("done", out)
