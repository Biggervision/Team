"""SK Mahbub Fiverr intro — v3 'kinetic neon' variant.

Reuses the v2 pipeline (render2.py) and swaps in:
- electric cyan -> blue -> violet palette with neon glow
- per-letter staggered hero reveal with overshoot + light sweep
- alternating hero styles: gradient fill / glowing outline
- bouncy captions with gradient highlight pills on keywords
- punch-zoom on every camera cut
- springy tool chips with shine sweep + glowing border
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render2 as r2
import chips as chipmod

W, H = r2.W, r2.H
mont, play = r2.mont, r2.play
ease_out, ease_io = r2.ease_out, r2.ease_io
def ease_back(t, s=1.9):
    t = min(1, max(0, t)); t -= 1; return t * t * ((s + 1) * t + s) + 1

# ---------------- palette ----------------
STOPS = [(0.0, (190, 248, 255)), (0.33, (40, 214, 240)), (0.66, (64, 120, 250)), (1.0, (150, 92, 250))]
rng = np.random.default_rng(11)
def texture(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((xx / w) * 0.8 + (yy / h) * 0.3, 0, 1)
    col = np.zeros((h, w, 3), np.float32)
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        m = (t >= t0) & (t <= t1); k = ((t - t0) / (t1 - t0))[..., None]
        col[m] = (np.array(c0) * (1 - k) + np.array(c1) * k)[m]
    n = Image.fromarray((rng.random((max(2, h // 50), max(2, w // 50))) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    n = np.asarray(n.filter(ImageFilter.GaussianBlur(8)), np.float32)[..., None] / 255 - 0.5
    col = np.clip(col + n * np.array([30, 20, 30]), 0, 255)
    return Image.fromarray(col.astype(np.uint8), "RGB")
r2.texture = texture

# ---------------- punch-zoom on cuts ----------------
_base_framing = r2.framing
def framing(t):
    box = _base_framing(t)
    last = max(t0 for t0, _ in r2.CUTS if t >= t0)
    k = 1 - ease_out((t - last) / 0.32) if last > 0 else 0
    z = 1 + 0.07 * k
    if z <= 1.0005: return box
    x, y, w, h = box; nw, nh = w / z, h / z
    return (int(x + (w - nw) / 2), int(y + (h - nh) * 0.35), int(nw), int(nh))
r2.framing = framing
# keep "is WIDE" checks working: hero height uses the un-zoomed framing
def is_wide(t): return _base_framing(t) is r2.WIDE

# ---------------- hero: per-letter kinetic reveal ----------------
HCACHE = {}
def hero_assets(idx, italic, word):
    key = (idx, word)
    if key in HCACHE: return HCACHE[key]
    name = word == "SK Mahbub"
    style = "fill" if (name or idx % 2 == 0) else "outline"
    size = 160 if name else 300
    f = mont(900, size)
    while f.getbbox(word)[2] - f.getbbox(word)[0] > 1640 and size > 120:
        size -= 8; f = mont(900, size)
    bb = f.getbbox(word); pad = 50
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    mask = Image.new("L", (w, h), 0)
    if style == "fill":
        ImageDraw.Draw(mask).text((pad - bb[0], pad - bb[1]), word, font=f, fill=255)
        body = Image.new("RGBA", (w, h), (0, 0, 0, 0)); body.paste(texture(w, h), (0, 0), mask)
        glow_src = mask
    else:
        sw = max(7, size // 26)
        ImageDraw.Draw(mask).text((pad - bb[0], pad - bb[1]), word, font=f, fill=0, stroke_width=sw, stroke_fill=255)
        inner = Image.new("L", (w, h), 0); ImageDraw.Draw(inner).text((pad - bb[0], pad - bb[1]), word, font=f, fill=255)
        mask = Image.fromarray(np.clip(np.asarray(mask, np.int16) - np.asarray(inner, np.int16) // 1 * 0 + 0, 0, 255).astype(np.uint8))
        # stroke only: stroke mask minus the glyph interior
        ring = np.clip(np.asarray(mask, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8)
        mask = Image.fromarray(ring)
        body = Image.new("RGBA", (w, h), (0, 0, 0, 0)); body.paste(texture(w, h), (0, 0), mask)
        # faint tinted fill so the outline still reads as a word
        tint = Image.new("RGBA", (w, h), (120, 200, 255, 0)); tint.putalpha(inner.point(lambda v: v * 70 // 255))
        body = Image.alpha_composite(tint, body)
        glow_src = mask
    glow = Image.new("RGBA", (w, h), (60, 170, 255, 0))
    glow.putalpha(glow_src.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, v * 2)))
    # letter x-ranges (in body coords)
    xs = []; x0 = pad - bb[0]
    for i, ch in enumerate(word):
        a = x0 + f.getlength(word[:i]); b = x0 + f.getlength(word[:i + 1])
        if ch != " ": xs.append((int(a) - 6, int(b) + 6))
    fi = play(int(max(70, size * 0.36)))
    ib = fi.getbbox(italic)
    it = Image.new("RGBA", (ib[2] - ib[0] + 40, ib[3] - ib[1] + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", it.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((20 - ib[0], 22 - ib[1]), italic, font=fi, fill=(0, 0, 0, 140))
    it.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(it).text((20 - ib[0], 20 - ib[1]), italic, font=fi, fill=(255, 255, 255, 255))
    HCACHE[key] = dict(body=body, glow=glow, xs=xs, it=it, size=size, w=w, h=h, mask=mask, style=style)
    return HCACHE[key]

def alpha_mul(im, a):
    if a >= 0.999: return im
    arr = np.array(im); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); return Image.fromarray(arr)

def draw_hero(layer, t, h, front):
    idx = r2.HEROES.index(h)
    t_in, _, t_out, italic, word = h
    if not (t_in <= t <= t_out + 0.3): return False
    A = hero_assets(idx, italic, word)
    name = word == "SK Mahbub"
    out_k = ease_io((t - t_out) / 0.28) if t > t_out else 0
    gA = 1 - out_k
    if gA <= 0.01: return False
    cy = 100 if name else (225 if is_wide(t) else 245)
    push = 1 + 0.035 * min(1, (t - t_in) / max(0.6, t_out - t_in)) + 0.06 * out_k   # slow push, quick blow-out on exit
    bw, bh = int(A["w"] * push), int(A["h"] * push)
    canvas = Image.new("RGBA", (A["w"], A["h"]), (0, 0, 0, 0))
    gl = Image.new("RGBA", (A["w"], A["h"]), (0, 0, 0, 0))
    n = len(A["xs"])
    stagger = min(0.045, 0.32 / max(1, n))
    for i, (a, b) in enumerate(A["xs"]):
        p = (t - t_in - i * stagger) / 0.42
        if p <= 0: continue
        e = ease_back(p); al = min(1, p * 2.2)
        dy = int((1 - e) * A["h"] * 0.55)
        sl = A["body"].crop((a, 0, b, A["h"])); g = A["glow"].crop((a, 0, b, A["h"]))
        if al < 1: sl = alpha_mul(sl, al); g = alpha_mul(g, al)
        canvas.alpha_composite(sl, (a, dy)); gl.alpha_composite(g, (a, dy))
    # light sweep across the word right after it lands
    sp = (t - t_in - 0.30) / 0.55
    if 0 < sp < 1:
        band = Image.new("L", (A["w"], A["h"]), 0); bd = ImageDraw.Draw(band)
        cx = -200 + sp * (A["w"] + 400)
        bd.polygon([(cx - 60, 0), (cx + 30, 0), (cx - 40, A["h"]), (cx - 130, A["h"])], fill=200)
        band = band.filter(ImageFilter.GaussianBlur(14))
        m = Image.fromarray((np.asarray(band, np.float32) * np.asarray(canvas.split()[3], np.float32) / 255).astype(np.uint8))
        white = Image.new("RGBA", canvas.size, (255, 255, 255, 0)); white.putalpha(m)
        canvas.alpha_composite(white)
    if push != 1:
        canvas = canvas.resize((bw, bh), Image.BICUBIC); gl = gl.resize((bw, bh), Image.BICUBIC)
    canvas = alpha_mul(canvas, gA); gl = alpha_mul(gl, gA * 0.75)
    target = front if name else layer
    pos = (int(W / 2 - bw / 2), int(cy - bh / 2))
    target.alpha_composite(gl, pos); target.alpha_composite(canvas, pos)
    # italic lead-in: slides + fades, underline swipe
    pi = ease_out((t - t_in - 0.06) / 0.45)
    ai = gA * min(1, max(0, (t - t_in - 0.04) / 0.2))
    if ai > 0.01:
        it = A["it"]
        if name:
            x = int(W / 2 - bw / 2 + 40 - it.width - 30 * (1 - pi)); y = int(cy - it.height / 2 + 6)
        else:
            left = W / 2 - bw / 2 + 50
            xr = min(left + 0.30 * bw, W / 2 - 200)
            x = int(xr - it.width - 40 * (1 - pi)); y = int(cy - bh / 2 - it.height * 0.30 + 24)
        x, y = max(50, x), max(8, y)
        front.alpha_composite(alpha_mul(it, ai), (x, y))
        u = ease_out((t - t_in - 0.25) / 0.4)
        if u > 0:
            d = ImageDraw.Draw(front)
            ux0, uy = x + 24, y + it.height - 22
            d.rounded_rectangle((ux0, uy, ux0 + int((it.width - 48) * u), uy + 5), 3, fill=(40, 214, 240, int(230 * ai)))
    return True
r2.draw_hero = draw_hero

# ---------------- captions: bouncy words + gradient keyword pills ----------------
PILL_TEX = texture(600, 120)
def caption_img(chunk, t):
    fb, fr = mont(800, 78), mont(600, 64)
    items = [(w, fb if w in r2.KEY else fr, a, w in r2.KEY) for a, b, w in chunk]
    sp = 22; padx = 22
    widths = [f.getlength(w) + (2 * padx if k else 0) for w, f, _, k in items]
    tot = sum(widths) + sp * (len(items) - 1)
    im = Image.new("RGBA", (int(tot) + 160, 210), (0, 0, 0, 0))
    x = 80
    for (w, f, a, k), ww in zip(items, widths):
        a0 = chunk[0][0] + (a - chunk[0][0]) * 0.0 + (items.index((w, f, a, k))) * 0.06
        p = (t - a0) / 0.32
        if p > 0:
            e = ease_back(p, 2.4); al = min(1, p * 3)
            wi = Image.new("RGBA", (int(ww) + 40, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(wi)
            by = 112 - f.getbbox("Hg")[3]
            if k:
                pm = Image.new("L", wi.size, 0)
                ImageDraw.Draw(pm).rounded_rectangle((20, 22, 20 + int(ww), 128), 26, fill=255)
                pill = Image.new("RGBA", wi.size, (0, 0, 0, 0)); pill.paste(PILL_TEX.resize(wi.size), (0, 0), pm)
                gshadow = Image.new("RGBA", wi.size, (40, 120, 255, 0)); gshadow.putalpha(pm.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v // 2))
                wi.alpha_composite(gshadow); wi.alpha_composite(pill)
                d.text((20 + padx, by), w, font=f, fill=(255, 255, 255, 255))
            else:
                sh = Image.new("RGBA", wi.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((20, by + 5), w, font=f, fill=(0, 0, 0, 210))
                wi.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); d.text((20, by), w, font=f, fill=(255, 255, 255, 255))
            s = max(0.3, e)
            if abs(s - 1) > 0.01:
                wi = wi.resize((max(1, int(wi.width * s)), max(1, int(wi.height * s))), Image.BICUBIC)
            wi = alpha_mul(wi, al)
            cxw = x + ww / 2
            im.alpha_composite(wi, (int(cxw - wi.width / 2), int(105 - wi.height / 2 + (1 - min(1, e)) * 20)))
        x += ww + sp
    return im
r2.caption_img = caption_img

def draw_caption(frame, t):
    for c, c_end in r2.CHUNKS:
        if c[0][0] - 0.02 <= t < c_end:
            a = 1 - ease_io((t - (c_end - 0.12)) / 0.12) if t > c_end - 0.12 else 1
            im = alpha_mul(caption_img(c, t), a)
            frame.alpha_composite(im, (int(W / 2 - im.width / 2), r2.CAP_Y - 120))
r2.draw_caption = draw_caption

# ---------------- chips: spring + shine + glowing border ----------------
class Chips3(chipmod.Chips):
    def draw(self, layer, t, wide):
        for end, side, xo, y0, items in self.groups:
            if not (items[0][0] - 0.05 <= t <= end + 0.3): continue
            gout = 1 - ease_out((t - end) / 0.3) if t > end else 1
            for i, (t0, kind, title, sub) in enumerate(items):
                if t < t0: continue
                p = t - t0
                k = ease_back(p / 0.45, 2.2); a = min(1, p / 0.18) * gout
                if a <= 0.01: continue
                im = self.base[(title, sub)].copy()
                im.alpha_composite(chipmod.glyph(kind, p), (10, 10))
                # glowing border pulse on entry
                bp = max(0, 1 - p / 0.9)
                if bp > 0:
                    d = ImageDraw.Draw(im)
                    d.rounded_rectangle((1, 1, self.CW - 2, self.CH - 2), 26, outline=(80, 220, 255, int(255 * bp)), width=3)
                # shine sweep
                sp = (p - 0.15) / 0.5
                if 0 < sp < 1:
                    band = Image.new("L", im.size, 0)
                    cx = -80 + sp * (self.CW + 160)
                    ImageDraw.Draw(band).polygon([(cx, 0), (cx + 40, 0), (cx - 10, self.CH), (cx - 50, self.CH)], fill=110)
                    band = band.filter(ImageFilter.GaussianBlur(8))
                    m = Image.fromarray((np.asarray(band, np.float32) * np.asarray(im.split()[3], np.float32) / 255).astype(np.uint8))
                    wht = Image.new("RGBA", im.size, (255, 255, 255, 0)); wht.putalpha(m); im.alpha_composite(wht)
                s = max(0.5, 0.82 + 0.18 * k)
                if abs(s - 1) > 0.005: im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
                im = alpha_mul(im, a)
                slide = int(70 * (1 - min(1, k)))
                x = (56 - slide) if side == "L" else (self.W - 56 - self.CW + slide)
                x += (self.CW - im.width) // 2
                y = y0 + i * (self.CH + self.GAP) + (self.CH - im.height) // 2
                layer.alpha_composite(im, (x, y))
            return True
        return False
r2.CHIPS = Chips3(mont, texture, W)
r2.ICON_IMG = {k: r2.make_icon(k) for _, _, k, _ in r2.ICONS}

if __name__ == "__main__":
    r2.main()
