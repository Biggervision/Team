"""SK Mahbub Fiverr intro — v2, reference-Reel style.

Full-frame footage, multi-cam style framing cuts, huge gradient "hero" words
placed BEHIND the speaker (person matte), italic serif lead-ins, word-by-word
Montserrat captions, faint glowing line icons, end name card.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, MATTE = f"{HERE}/src/raw.mp4", f"{HERE}/src/matte.mp4"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/out/v2_noaudio.mp4"
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
W, H, FPS = 1920, 1080, 30
VID_END = 52.13            # last frame of the recording
END_CARD = 2.9             # name card after "Let's talk."
DUR = VID_END + END_CARD

FD = f"{HERE}/fonts/"
def mont(w, s): return ImageFont.truetype(f"{FD}Montserrat-{w}.ttf", s)
def play(s): return ImageFont.truetype(f"{FD}Playfair-600.ttf", s)

def ease_out(t): t = min(1, max(0, t)); return 1 - (1 - t) ** 3
def ease_io(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)

# ---------------- framing (multi-cam feel; hard cuts on sentence starts) ----------------
WIDE = (70, 40, 1780, 1001)        # removes the black pillarbox bars
MED = (240, 22, 1440, 810)         # ~1.33x, face-centred
CUTS = [(0, WIDE), (8.40, WIDE), (10.30, MED), (13.38, WIDE), (18.72, MED), (25.24, WIDE), (32.00, MED),
        (35.56, WIDE), (42.02, MED), (48.00, WIDE)]
def framing(t):
    f = CUTS[0][1]
    for t0, c in CUTS:
        if t >= t0: f = c
    return f

# ---------------- words (clean-verbatim of the recording) ----------------
words = json.load(open(f"{HERE}/words.json"))
fix = {"Eskimo,": "SK Mahbub,", "drive": "drives", "Metapixel": "Meta Pixel,", "conversion": "conversion",
       "system": "systems", "run": "turn", "clarity": "Clarity", "decision,": "decisions,"}
WORDS = []
for a, b, w in words:
    w = w.strip(); w = fix.get(w, w)
    if (w == "a" and abs(a - 46.06) < .05) or (w == "a" and abs(a - 36.90) < .05): continue  # "into a better", "make a smarter"
    WORDS.append([a, b, w])
caps = {"Analytics,": "Analytics,", "API,": "API,"}
for wd in WORDS:   # title-case platform/product names
    if wd[2] in ("conversion", "tracking,") and 22.0 < wd[0] < 24.2: wd[2] = wd[2].capitalize()
    if 9.3 < wd[0] < 12.5: wd[2] = wd[2].capitalize() if wd[2] not in ("and", "a") else wd[2]
    if wd[2] in ("clarity",): wd[2] = "Clarity"
KEY = {"accurate", "data,", "strategy,", "results.", "SK", "Mahbub,", "Analytics,", "Analytics", "Conversion", "Tracking",
       "Paid", "Advertising", "Consultant.", "issues,", "mismatches,", "duplicate", "events,", "Google", "Meta", "Pixel,",
       "API,", "Ads", "TikTok,", "Snapchat,", "Twitter,", "LinkedIn", "Microsoft", "Clarity", "qualified", "leads,",
       "sales,", "business.", "marketing", "better", "performance?", "talk.", "tools", "optimization."}

# ---------------- hero words: (t_in, hide_until, t_out, italic, hero, side-icon) ----------------
HEROES = [
    (0.00, 1.07, 1.40, "Growing your", "business"),
    (2.86, 4.20, 4.18, "accurate", "data"),
    (4.22, 5.24, 5.22, "the right", "strategy"),
    (6.96, 8.30, 8.28, "what drives", "results"),
    (8.40, 9.12, 9.95, "This is", "SK Mahbub"),
    (14.08, 14.92, 15.34, "fix", "tracking"),
    (15.38, 16.70, 16.98, "resolve", "mismatches"),
    (17.02, 18.70, 18.66, "eliminate duplicate", "events"),
    (18.72, 20.42, 20.42, "build reliable", "systems"),
    (32.94, 35.50, 35.50, "Google & Meta Ads", "optimization"),
    (36.40, 38.00, 38.02, "make smarter", "decisions"),
    (38.06, 39.50, 39.54, "more qualified", "leads"),
    (39.56, 40.44, 40.44, "increase", "sales"),
    (40.46, 41.98, 41.98, "grow your", "business"),
    (42.40, 44.20, 44.20, "what's holding your", "marketing"),
    (44.72, 47.70, 47.80, "better data, better", "results"),
    (48.00, 49.66, 49.66, "need better", "tracking"),
    (49.68, 51.00, 51.10, "and stronger ad", "performance"),
    (51.18, 52.20, VID_END, "let's", "talk"),
]
# glowing line icons behind the speaker: (t_in, t_out, kind, side)
ICONS = [(2.86, 5.22, "chart", "L"), (38.06, 41.98, "funnel", "L"), (48.00, VID_END, "chat", "R")]

# ---------------- hero rendering ----------------
rng = np.random.default_rng(7)
def texture(w, h):
    """Cool silver->sky->royal-blue diagonal gradient with soft painterly blotches (reference look)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((xx / w) * 0.75 + (yy / h) * 0.35, 0, 1)
    stops = [(0.0, (236, 244, 250)), (0.38, (178, 214, 236)), (0.62, (96, 140, 222)), (1.0, (64, 92, 206))]
    col = np.zeros((h, w, 3), np.float32)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1); k = ((t - t0) / (t1 - t0))[..., None]
        col[m] = (np.array(c0) * (1 - k) + np.array(c1) * k)[m]
    n = Image.fromarray((rng.random((max(2, h // 40), max(2, w // 40))) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    n = np.asarray(n.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255 - 0.5
    col = np.clip(col + n * np.array([-40, -30, 50]), 0, 255)
    return Image.fromarray(col.astype(np.uint8), "RGB")

HERO_CACHE = {}
def hero_layer(italic, word):
    key = (italic, word)
    if key in HERO_CACHE: return HERO_CACHE[key]
    size = 160 if word == "SK Mahbub" else 300
    f = mont(900, size)
    while True:
        bb = f.getbbox(word)
        if bb[2] - bb[0] <= 1640 or size < 120: break
        size -= 8; f = mont(900, size)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 60
    mask = Image.new("L", (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(mask).text((pad - bb[0], pad - bb[1]), word, font=f, fill=255)
    tex = texture(*mask.size)
    img = Image.new("RGBA", mask.size, (0, 0, 0, 0)); img.paste(tex, (0, 0), mask)
    # soft shadow for separation from the warm wall
    sh = Image.new("RGBA", mask.size, (10, 14, 40, 0)); sh.putalpha(mask.point(lambda v: v * 70 // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    base = Image.new("RGBA", mask.size, (0, 0, 0, 0)); base.alpha_composite(sh, (0, 6)); base.alpha_composite(img)
    # italic lead-in overlapping the upper-left of the hero word
    fi = play(int(max(70, size * 0.36)))
    ib = fi.getbbox(italic)
    it = Image.new("RGBA", (ib[2] - ib[0] + 40, ib[3] - ib[1] + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(it)
    sh2 = Image.new("RGBA", it.size, (0, 0, 0, 0)); ImageDraw.Draw(sh2).text((20 - ib[0], 22 - ib[1]), italic, font=fi, fill=(0, 0, 0, 120))
    it.alpha_composite(sh2.filter(ImageFilter.GaussianBlur(6)))
    d.text((20 - ib[0], 20 - ib[1]), italic, font=fi, fill=(255, 255, 255, 255))
    HERO_CACHE[key] = (base, it, size)
    return HERO_CACHE[key]

def scaled(im, s, a):
    if abs(s - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if a < 0.999:
        arr = np.array(im); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); im = Image.fromarray(arr)
    return im

def draw_hero(layer, t, h, front):
    t_in, _, t_out, italic, word = h
    if not (t_in <= t <= t_out + 0.22): return False
    base, it, size = hero_layer(italic, word)
    p = ease_out((t - t_in) / 0.38)
    a = min(1, (t - t_in) / 0.18) * (1 - ease_io((t - t_out) / 0.22) if t > t_out else 1)
    if a <= 0.01: return False
    s = 1.10 - 0.10 * p if t <= t_out else 1 - 0.03 * ease_io((t - t_out) / 0.22)
    b = scaled(base, s, a)
    cy = 100 if word == "SK Mahbub" else (225 if framing(t) is WIDE else 245)
    (front if word == "SK Mahbub" else layer).alpha_composite(b, (int(W / 2 - b.width / 2), int(cy - b.height / 2)))
    # italic: slides in from left slightly after the hero word
    pi = ease_out((t - t_in - 0.08) / 0.4)
    ai = a * min(1, max(0, (t - t_in - 0.05) / 0.2))
    if ai > 0.01:
        i2 = scaled(it, 1, ai)
        left = W / 2 - base.width * s / 2 + 60
        xr = min(left + 0.30 * base.width, W / 2 - 200)
        x = int(xr - it.width - 40 * (1 - pi)); y = int(cy - base.height * s / 2 - it.height * 0.30 + 24)
        if word == "SK Mahbub":
            x = int(W / 2 - base.width * s / 2 + 50 - it.width - 30 * (1 - pi)); y = int(cy - it.height / 2 + 6)
        front.alpha_composite(i2, (max(50, x), max(8, y)))
    return True

# ---------------- glowing line icons ----------------
def make_icon(kind, s=360):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); lw = 14; c = (255, 255, 255, 255)
    if kind == "chart":
        d.rounded_rectangle((40, 40, s - 40, s - 40), 30, outline=c, width=lw)
        for i, hh in enumerate([90, 150, 210]): x = 95 + i * 65; d.rounded_rectangle((x, s - 80 - hh, x + 36, s - 80), 8, fill=c)
    elif kind == "alert":
        d.polygon([(s / 2, 50), (s - 40, s - 60), (40, s - 60)], outline=c, width=lw)
        d.line([(s / 2, 140), (s / 2, 220)], fill=c, width=lw + 2); d.ellipse((s / 2 - 11, 248, s / 2 + 11, 270), fill=c)
    elif kind == "nodes":
        pts = [(s / 2, 70), (80, s - 90), (s - 80, s - 90), (s / 2, s / 2 + 20)]
        for p in pts[:3]: d.line([pts[3], p], fill=c, width=lw - 4)
        for x, y in pts: d.ellipse((x - 34, y - 34, x + 34, y + 34), outline=c, width=lw, fill=(0, 0, 0, 0))
    elif kind == "gear":
        cx = cy = s / 2
        for k in range(8):
            a = k * math.pi / 4; d.line([(cx + 95 * math.cos(a), cy + 95 * math.sin(a)), (cx + 140 * math.cos(a), cy + 140 * math.sin(a))], fill=c, width=34)
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=c, width=lw); d.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), outline=c, width=lw)
    elif kind == "funnel":
        d.polygon([(50, 70), (s - 50, 70), (s / 2 + 40, 210), (s / 2 + 40, s - 50), (s / 2 - 40, s - 90), (s / 2 - 40, 210)], outline=c, width=lw)
        d.line([(90, 120), (s - 90, 120)], fill=c, width=lw - 4)
    elif kind == "chat":
        d.rounded_rectangle((40, 60, s - 40, s - 110), 50, outline=c, width=lw)
        d.polygon([(110, s - 112), (110, s - 40), (180, s - 112)], fill=c)
        for i in range(3): d.ellipse((115 + i * 55, 150, 145 + i * 55, 180), fill=c)
    glow = im.filter(ImageFilter.GaussianBlur(16))
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(glow); out.alpha_composite(im)
    arr = np.array(out); arr[..., 3] = (arr[..., 3] * 0.42).astype(np.uint8)
    return Image.fromarray(arr)
ICON_IMG = {k: make_icon(k) for _, _, k, _ in ICONS}

def draw_icons(layer, t):
    hit = False
    for t0, t1, k, side in ICONS:
        if t0 <= t <= t1 + 0.3:
            a = min(1, (t - t0) / 0.35) * (1 - ease_io((t - t1) / 0.3) if t > t1 else 1)
            p = ease_out((t - t0) / 0.5)
            im = scaled(ICON_IMG[k], 0.9 + 0.1 * p, a)
            x = 250 if side == "L" else W - 250 - im.width
            layer.alpha_composite(im, (x, int(560 - im.height / 2 + 30 * (1 - p)))); hit = True
    return hit

# ---------------- captions ----------------
def in_hero(t):
    return any(h[0] <= t < h[1] for h in HEROES)
vis = [w for w in WORDS if not in_hero(w[0]) and w[0] < VID_END]
CHUNKS = []
cur = []
for i, w in enumerate(vis):
    if cur and (len(cur) >= 2 or w[0] - cur[-1][1] > 0.35 or cur[-1][2][-1] in ",.?"):
        CHUNKS.append(cur); cur = []
    cur.append(w)
if cur: CHUNKS.append(cur)
for i, c in enumerate(CHUNKS):
    nxt = CHUNKS[i + 1][0][0] if i + 1 < len(CHUNKS) else VID_END
    c_end = min(nxt, c[-1][1] + 0.45)
    CHUNKS[i] = (c, c_end)

CAP_Y = 815
def caption_img(chunk, t):
    fb, fr = mont(800, 80), mont(600, 66)
    items = []
    for a, b, w in chunk:
        f = fb if w in KEY else fr
        items.append((w, f, a))
    sp = 18
    widths = [f.getlength(w) for w, f, _ in items]
    tot = sum(widths) + sp * (len(items) - 1)
    im = Image.new("RGBA", (int(tot) + 120, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    x = 60
    for (w, f, a), ww in zip(items, widths):
        a = chunk[0][0]
        if t >= a - 0.02:
            p = ease_out((t - a) / 0.16)
            col = (255, 255, 255, int(255 * min(1, (t - a + .02) / 0.1)))
            yoff = int(10 * (1 - p))
            base_y = 120 - f.getbbox("Hg")[3]
            sd.text((x, base_y + 6 + yoff), w, font=f, fill=(0, 0, 0, int(200 * min(1, (t - a + .02) / 0.1))))
            d.text((x, base_y + yoff), w, font=f, fill=col)
        x += ww + sp
    out = sh.filter(ImageFilter.GaussianBlur(10)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3))); out.alpha_composite(im)
    return out

def draw_caption(frame, t):
    for c, c_end in CHUNKS:
        if c[0][0] - 0.02 <= t < c_end:
            a = 1 - ease_io((t - (c_end - 0.12)) / 0.12) if t > c_end - 0.12 else 1
            im = scaled(caption_img(c, t), 1, a)
            frame.alpha_composite(im, (int(W / 2 - im.width / 2), CAP_Y - 120))

# ---------------- end card ----------------
def end_card(last_rgb, photo_rgb):
    bg = last_rgb.filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (12, 16, 30)), 0.45).convert("RGBA")
    cw, ch = 760, 760
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 44, fill=(250, 251, 253, 255))
    ph = photo_rgb.crop((620, 120, 1300, 800)).resize((360, 360), Image.LANCZOS)
    m = Image.new("L", (360, 360), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 359, 359), 36, fill=255)
    card.paste(ph, ((cw - 360) // 2, 70), m)
    f1, f2, f3 = mont(800, 64), mont(600, 26), mont(700, 22)
    d.text((cw / 2, 498), "SK Mahbub", font=f1, fill=(18, 24, 48), anchor="mm")
    d.text((cw / 2, 560), "Web Analytics · Conversion Tracking", font=f2, fill=(70, 80, 110), anchor="mm")
    d.text((cw / 2, 598), "Paid Advertising Consultant", font=f2, fill=(70, 80, 110), anchor="mm")
    tex = texture(300, 64); pm = Image.new("L", (300, 64), 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, 299, 63), 32, fill=255)
    pill = Image.new("RGBA", (300, 64), (0, 0, 0, 0)); pill.paste(Image.new('RGB', (300, 64), (52, 72, 190)), (0, 0), pm)
    ImageDraw.Draw(pill).text((150, 32), "LET'S TALK", font=f3, fill=(255, 255, 255), anchor="mm")
    card.alpha_composite(pill, ((cw - 300) // 2, 650))
    shadow = Image.new("RGBA", (cw + 120, ch + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((60, 75, cw + 60, ch + 75), 44, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    return bg, card, shadow

# ---------------- tool chips ----------------
sys.path.insert(0, HERE)
from chips import Chips
CHIPS = Chips(mont, texture, W)

# ---------------- main ----------------
def grab(proc, n):
    b = proc.stdout.read(n); return b if len(b) == n else None

def main():
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", "eq=saturation=0.88:contrast=1.04:gamma=0.98,vignette=angle=0.55",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    mat = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MATTE, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    if PREVIEW is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    targets = PREVIEW or [i / FPS for i in range(int(round(DUR * FPS)))]
    fi, last, photo, ec = 0, None, None, None
    for t in targets:
        while t <= VID_END and fi / FPS <= t + 1e-6 and (PREVIEW is None or fi / FPS < t - 0.5 / FPS or True):
            raw = grab(dec, W * H * 3); mraw = grab(mat, W * H)
            if raw is None: break
            ft = fi / FPS; fi += 1
            if abs(ft - 40.0) < 0.02: photo = Image.frombuffer("RGB", (W, H), raw).copy()
            last = (raw, mraw)
            if ft >= t - 0.5 / FPS: break
        if t <= VID_END and last is not None:
            raw, mraw = last
            box = framing(t)
            fr = Image.frombuffer("RGB", (W, H), raw).crop((box[0], box[1], box[0] + box[2], box[1] + box[3])).resize((W, H), Image.LANCZOS)
            mt = Image.frombuffer("L", (W, H), mraw).crop((box[0], box[1], box[0] + box[2], box[1] + box[3])).resize((W, H), Image.BILINEAR)
            frame = fr.convert("RGBA")
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            used = draw_icons(layer, t)
            used = CHIPS.draw(layer, t, framing(t) is WIDE) or used
            front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for h in HEROES: used = draw_hero(layer, t, h, front) or used
            if used:
                back = frame.copy(); back.alpha_composite(layer)
                frame = Image.composite(frame, back, mt)   # speaker stays in front of the words
                frame.alpha_composite(front)
            draw_caption(frame, t)
            out = frame.convert("RGB"); lastout = out
        else:
            if ec is None:
                ec = end_card(lastout, photo or lastout)
            bg, card, shadow = ec
            k = (t - VID_END) / 0.45
            p = ease_out((t - VID_END - 0.1) / 0.6)
            frame = Image.blend(lastout, bg.convert("RGB"), ease_io(k)).convert("RGBA")
            a = min(1, max(0, (t - VID_END - 0.1) / 0.35))
            cs = scaled(card, 0.94 + 0.06 * p, a); ss = scaled(shadow, 0.94 + 0.06 * p, a)
            frame.alpha_composite(ss, (int(W / 2 - ss.width / 2), int(H / 2 - ss.height / 2 + 30 * (1 - p))))
            frame.alpha_composite(cs, (int(W / 2 - cs.width / 2), int(H / 2 - cs.height / 2 + 30 * (1 - p))))
            out = frame.convert("RGB")
        if PREVIEW is None: enc.stdin.write(out.tobytes())
        else: out.save(f"{HERE}/out/v2_{t:05.2f}.png")
    dec.kill(); mat.kill()
    if PREVIEW is None: enc.stdin.close(); enc.wait()

if __name__ == "__main__":
    main()
