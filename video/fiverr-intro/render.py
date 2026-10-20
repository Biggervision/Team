"""SK Mahbub Fiverr intro edit renderer.

Layout: light white->mint canvas with dot grid (Layout A), original footage in a
rounded card on the right, floating cards (Layout B) and minimal diagrams
(Layout C) on the left, subtitles at bottom-left. Timings come from word-level
timestamps of the original recording.
"""
import math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src/raw.mp4")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out/video_noaudio.mp4")
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None

W, H, FPS, DUR = 1920, 1080, 30, 52.15
F = os.path.join(HERE, "fonts/inter/extras/ttf/")
def font(w, s): return ImageFont.truetype(F + {"r": "Inter-Regular", "m": "Inter-Medium", "s": "Inter-SemiBold", "b": "Inter-Bold", "db": "InterDisplay-Bold", "ds": "InterDisplay-SemiBold"}[w] + ".ttf", s)

# palette
WHITE = (255, 255, 255); OFF = (250, 252, 251); MINT = (214, 243, 236); AQUA = (190, 236, 228)
TEAL = (13, 148, 136); TEAL_D = (15, 94, 89); INK = (31, 41, 46); MUTED = (95, 110, 115)
LINE = (222, 234, 231); CORAL = (226, 120, 104)

# ---------- footage card geometry ----------
CROP = (440, 0, 1480, 1080)              # removes black bars + busy wall edges, keeps full body/gestures
CW, CH = 936, 972                         # 0.9 scale
CX, CY = 904, 54
RAD = 34
LX, LW = 104, 720                         # left content column

def ease(t):  # easeOutCubic
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

# ---------- background (Layout A) ----------
def make_bg():
    x = np.linspace(0, 1, W)[None, :, None]; y = np.linspace(0, 1, H)[:, None, None]
    t = np.clip((x - 0.30) / 0.55, 0, 1) ** 1.4 * (0.85 + 0.15 * y)
    base = np.array(OFF, float) * (1 - t) + np.array(MINT, float) * t
    # soft aqua glow behind footage
    g = np.exp(-(((x - 0.72) / 0.28) ** 2 + ((y - 0.45) / 0.55) ** 2))
    base = base * (1 - 0.35 * g) + np.array(AQUA, float) * 0.35 * g
    img = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(dots)
    for yy in range(18, H, 30):
        for xx in range(18, W, 30):
            fade = 0.35 + 0.65 * min(1, xx / W * 1.6)
            a = int(26 * fade)
            d.ellipse((xx - 1.6, yy - 1.6, xx + 1.6, yy + 1.6), fill=(13, 148, 136, a))
    img.alpha_composite(dots)
    # footage shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((CX + 6, CY + 22, CX + CW - 6, CY + CH + 18), RAD, fill=(15, 70, 65, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)))
    # white ring
    rd = ImageDraw.Draw(img)
    rd.rounded_rectangle((CX - 6, CY - 6, CX + CW + 6, CY + CH + 6), RAD + 6, fill=(255, 255, 255, 255))
    return img

MASK = Image.new("L", (CW, CH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), RAD, fill=255)

# ---------- element helpers ----------
def shadowed(img, blur=18, alpha=40, dy=10, pad=40):
    w, h = img.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    s = Image.new("RGBA", img.size, (20, 80, 75, 255)); s.putalpha(a)
    tmp = Image.new("RGBA", out.size, (0, 0, 0, 0)); tmp.paste(s, (pad, pad + dy))
    out.alpha_composite(tmp.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(img, (pad, pad))
    return out, pad

def card(w, h, r=22, fill=WHITE, border=LINE):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill + (255,), outline=border + (255,), width=2)
    return im, d

def tsize(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1]

def icon(kind, size, col=TEAL, bg=(225, 246, 241)):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), size // 3, fill=bg + (255,))
    c = size / 2; s = size; lw = max(3, size // 14)
    if kind == "check":
        d.line([(s * .3, s * .52), (s * .45, s * .66), (s * .72, s * .36)], fill=col, width=lw, joint="curve")
    elif kind == "x":
        d.line([(s * .34, s * .34), (s * .66, s * .66)], fill=col, width=lw); d.line([(s * .66, s * .34), (s * .34, s * .66)], fill=col, width=lw)
    elif kind == "data":
        for i, hh in enumerate([.22, .36, .5]):
            x0 = s * (.28 + i * .16); d.rounded_rectangle((x0, s * .72 - s * hh, x0 + s * .1, s * .72), 2, fill=col)
    elif kind == "target":
        for rr in (.30, .19, .07):
            d.ellipse((c - s * rr, c - s * rr, c + s * rr, c + s * rr), outline=col, width=lw if rr > .1 else 0, fill=col if rr < .1 else None)
    elif kind == "eye":
        d.ellipse((s * .22, s * .36, s * .78, s * .64), outline=col, width=lw); d.ellipse((c - s * .08, c - s * .08, c + s * .08, c + s * .08), fill=col)
    elif kind == "up":
        d.line([(s * .26, s * .66), (s * .44, s * .48), (s * .56, s * .58), (s * .74, s * .36)], fill=col, width=lw, joint="curve")
        d.polygon([(s * .76, s * .32), (s * .62, s * .34), (s * .74, s * .46)], fill=col)
    return im

# Element = (image, x, y, t_in, t_out, slide)
class El:
    def __init__(s, im, x, y, t0, t1, slide=26, dur=0.45, fade_out=0.3, kind="up"):
        s.im, s.x, s.y, s.t0, s.t1, s.slide, s.dur, s.fo, s.kind = im, x, y, t0, t1, slide, dur, fade_out, kind
        s.arr = np.array(im)
    def draw(s, frame, t):
        if t < s.t0 or t > s.t1: return
        p = ease((t - s.t0) / s.dur)
        a = p * min(1.0, (s.t1 - t) / s.fo)
        if a <= 0.01: return
        dx = dy = 0
        if s.kind == "up": dy = int(s.slide * (1 - p))
        elif s.kind == "left": dx = int(-s.slide * (1 - p))
        im = s.im
        if a < 0.999:
            arr = s.arr.copy(); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); im = Image.fromarray(arr, "RGBA")
        frame.alpha_composite(im, (s.x + dx, s.y + dy))

ELS = []
def add(im, x, y, t0, t1, shadow=True, **kw):
    if shadow:
        im, pad = shadowed(im); x -= pad; y -= pad
    ELS.append(El(im, x, y, t0, t1, **kw))

def text_img(parts, size, weight="db", line_gap=1.12, maxw=LW):
    """parts: list of lines; each line a list of (text, color)."""
    f = font(weight, size); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lh = int(size * line_gap); h = lh * len(parts) + int(size * .3)
    im = Image.new("RGBA", (maxw, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, line in enumerate(parts):
        x = 0
        for s, col in line:
            d.text((x, i * lh), s, font=f, fill=col); x += d.textlength(s, font=f)
    return im

def eyebrow(s):
    f = font("s", 19); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(d0.textlength(s, font=f)) + 4 * len(s)
    im = Image.new("RGBA", (tw + 56, 42), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw + 55, 41), 21, fill=(225, 246, 241, 255), outline=(190, 230, 222, 255), width=2)
    d.ellipse((18, 16, 28, 26), fill=TEAL)
    x = 38
    for ch in s:
        d.text((x, 10), ch, font=f, fill=TEAL_D); x += d.textlength(ch, font=f) + 4
    return im

def row_card(label, kind, w=LW, h=92, sub=None, ic_col=TEAL, ic_bg=(225, 246, 241)):
    im, d = card(w, h)
    im.alpha_composite(icon(kind, 56, ic_col, ic_bg), (20, (h - 56) // 2))
    f = font("s", 30)
    if sub:
        d.text((96, h // 2 - 30), label, font=f, fill=INK); d.text((96, h // 2 + 6), sub, font=font("r", 21), fill=MUTED)
    else:
        d.text((96, h // 2 - 19), label, font=f, fill=INK)
    return im

def pill(s, size=26, fill=WHITE, col=INK, border=LINE, dot=None, padx=26, h=None):
    f = font("s", size); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(d0.textlength(s, font=f)); h = h or int(size * 2.2)
    extra = 26 if dot else 0
    im = Image.new("RGBA", (tw + 2 * padx + extra, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, h - 1), h // 2, fill=fill + (255,), outline=border + (255,), width=2)
    if dot: d.ellipse((padx, h // 2 - 7, padx + 14, h // 2 + 7), fill=dot)
    d.text((padx + extra, (h - size * 1.2) / 2), s, font=f, fill=col)
    return im

# ================= SCENES =================
# S1 hook 0.00-8.20
T = 8.20
add(eyebrow("GROWTH STARTS WITH DATA"), LX, 150, 0.10, T, shadow=False)
add(text_img([[("More than just", INK)], [("running ads.", TEAL)]], 76), LX, 222, 0.30, T, shadow=False)
for i, (lab, k, t0) in enumerate([("Accurate data", "data", 3.08), ("The right strategy", "target", 4.22),
                                  ("A clear view of what drives results", "eye", 5.66)]):
    add(row_card(lab, k), LX, 432 + i * 116, t0, T)

# S2 name 8.40-12.95
T = 12.95
add(eyebrow("MEET YOUR CONSULTANT"), LX, 190, 8.40, T, shadow=False)
add(text_img([[("SK Mahbub", INK)]], 104), LX, 258, 8.55, T, shadow=False)
bar = Image.new("RGBA", (120, 8), (0, 0, 0, 0)); ImageDraw.Draw(bar).rounded_rectangle((0, 0, 119, 7), 4, fill=TEAL)
add(bar, LX + 4, 392, 8.75, T, shadow=False, kind="left", slide=40)
y = 450
for lab, t0, x in [("Web Analytics", 9.34, LX), ("Conversion Tracking", 9.92, LX), ("Paid Advertising", 11.16, LX)]:
    add(pill(lab, 30, dot=TEAL, h=70), x, y, t0, T); y += 92
add(text_img([[("Consultant", MUTED)]], 34, "m"), LX + 6, y + 6, 12.26, T, shadow=False)

# S3 what I fix 13.38-18.60
T = 18.62
add(eyebrow("WHAT I FIX"), LX, 190, 13.38, T, shadow=False)
add(text_img([[("Tracking you can", INK)], [("trust again.", TEAL)]], 66), LX, 256, 13.50, T, shadow=False)
rows = [("Tracking issues", 14.48, "Resolved"), ("Conversion mismatches", 15.62, "Matched"), ("Duplicate events", 17.32, "Deduplicated")]
for i, (lab, t0, tag) in enumerate(rows):
    yy = 456 + i * 116
    # "problem" state then "fixed" state cross-fade
    bad = row_card(lab, "x", ic_col=CORAL, ic_bg=(252, 234, 230))
    good = row_card(lab, "check")
    gd = ImageDraw.Draw(good); tg = pill(tag, 20, fill=(225, 246, 241), col=TEAL_D, border=(190, 230, 222), padx=16, h=40)
    good.alpha_composite(tg, (LW - tg.width - 22, (92 - 40) // 2))
    tfix = t0 + 0.75
    add(bad, LX, yy, t0, tfix + 0.25, fade_out=0.25)
    add(good, LX, yy, tfix, T, slide=0, dur=0.3)

# S4 reliable tracking system 18.72-29.30
T = 29.32
add(eyebrow("RELIABLE TRACKING SYSTEM"), LX, 120, 18.72, T, shadow=False)
hub, hd = card(LW, 96, fill=(240, 251, 248), border=(190, 230, 222))
hub.alpha_composite(icon("data", 58), (20, 19))
hd.text((96, 18), "Your website & funnel", font=font("s", 29), fill=INK)
hd.text((96, 56), "Every key event, captured once and validated", font=font("r", 20), fill=MUTED)
add(hub, LX, 186, 19.06, T)
tools = [("Google Analytics 4", 21.08, (232, 113, 10)), ("Meta Pixel + CAPI", 22.06, (24, 119, 242)),
         ("Google Ads Tracking", 23.30, (52, 168, 83)), ("TikTok", 25.24, (37, 244, 238)),
         ("Snapchat", 25.70, (250, 204, 21)), ("X (Twitter)", 26.30, (40, 40, 40)),
         ("LinkedIn", 26.58, (10, 102, 194)), ("Microsoft Clarity", 28.28, (124, 58, 237))]
cw2, chh = (LW - 20) // 2, 78
for i, (lab, t0, dot) in enumerate(tools):
    col, rowi = i % 2, i // 2
    x = LX + col * (cw2 + 20); yy = 362 + rowi * (chh + 18)
    im, d = card(cw2, chh, r=18)
    d.ellipse((22, chh // 2 - 9, 40, chh // 2 + 9), fill=dot)
    fs = 25
    while d.textlength(lab, font=font("s", fs)) > cw2 - 112: fs -= 1
    d.text((56, chh // 2 - fs * 0.6), lab, font=font("s", fs), fill=INK)
    # tiny "event received" tick
    d.ellipse((cw2 - 40, chh // 2 - 11, cw2 - 18, chh // 2 + 11), fill=(225, 246, 241))
    d.line([(cw2 - 35, chh // 2), (cw2 - 30, chh // 2 + 5), (cw2 - 23, chh // 2 - 5)], fill=TEAL, width=3)
    add(im, x, yy, t0, T, slide=18)
# connector from hub to grid
con = Image.new("RGBA", (LW, 70), (0, 0, 0, 0)); cd = ImageDraw.Draw(con)
cd.line([(LW // 2, 0), (LW // 2, 26)], fill=(150, 210, 200), width=3)
cd.line([(cw2 // 2, 26), (LW - cw2 // 2, 26)], fill=(150, 210, 200), width=3)
cd.line([(cw2 // 2, 26), (cw2 // 2, 70)], fill=(150, 210, 200), width=3); cd.line([(LW - cw2 // 2, 26), (LW - cw2 // 2, 70)], fill=(150, 210, 200), width=3)
add(con, LX, 288, 20.60, T, shadow=False, slide=0)

# S5 tools + ads 29.38-35.45
T = 35.46
add(eyebrow("DATA + ADVERTISING"), LX, 170, 29.38, T, shadow=False)
add(text_img([[("Plus other essential", INK)], [("tracking tools", INK)]], 54, "ds"), LX, 236, 29.90, T, shadow=False)
xx = LX
for lab, t0 in [("Server-side tracking", 30.74), ("Event validation", 31.22)]:
    p = pill(lab, 24, fill=(240, 251, 248), col=TEAL_D, border=(190, 230, 222), dot=TEAL)
    add(p, xx, 382, t0, T, slide=16); xx += p.width + 16
add(text_img([[("combined with", MUTED)]], 30, "m"), LX, 488, 32.00, T, shadow=False)
for i, (lab, t0) in enumerate([("Google Ads", 32.94), ("Meta Ads", 34.10)]):
    im, d = card(340, 150)
    im.alpha_composite(icon("up", 56), (24, 24))
    d.text((24, 92), lab, font=font("db", 34), fill=INK)
    add(im, LX + i * 380, 546, t0, T)
add(pill("Campaign optimization", 26, fill=TEAL, col=WHITE, border=TEAL), LX, 732, 34.68, T, slide=16)

# S6 outcomes 35.56-41.95
T = 41.95
add(eyebrow("WHAT IT MEANS FOR YOU"), LX, 160, 35.56, T, shadow=False)
outs = [("Smarter decisions", 36.90), ("More qualified leads", 38.06), ("Increased sales", 39.56), ("Business growth", 40.46)]
for i, (lab, t0) in enumerate(outs):
    im, d = card(LW, 104)
    im.alpha_composite(icon("up", 60), (22, 22))
    d.text((104, 32), lab, font=font("s", 32), fill=INK)
    # illustrative step bars (no figures)
    for b in range(4):
        hh = 14 + b * 12; x0 = LW - 150 + b * 30
        d.rounded_rectangle((x0, 78 - hh, x0 + 18, 78), 4, fill=(TEAL if b <= i else (215, 236, 231)))
    add(im, LX, 236 + i * 126, t0, T)

# S7 statement 42.02-47.70
T = 47.72
add(eyebrow("LET'S FIX IT"), LX, 210, 42.02, T, shadow=False)
add(text_img([[("Let's fix what's", INK)], [("holding your", INK)], [("marketing back.", INK)]], 70), LX, 276, 42.10, T, shadow=False)
im, d = card(LW, 120, fill=(240, 251, 248), border=(190, 230, 222))
d.text((32, 22), "Better data", font=font("db", 34), fill=TEAL_D)
d.text((32, 66), "→  better business results", font=font("s", 30), fill=INK)
add(im, LX, 560, 45.24, T)

# S8 CTA 48.00-end
T = DUR + 1
add(eyebrow("LET'S WORK TOGETHER"), LX, 220, 48.00, T, shadow=False)
add(text_img([[("Need better tracking", INK)], [("& stronger", INK)], [("ad performance?", TEAL)]], 62), LX, 286, 48.10, T, shadow=False)
cta = pill("Let's talk  →", 38, fill=TEAL, col=WHITE, border=TEAL, padx=44, h=96)
add(cta, LX, 548, 51.18, T)

# ---------- subtitles ----------
SUBS = [
    (0.00, 2.55, "Growing your business takes more than just running ads.", []),
    (2.86, 5.18, "You need accurate data, the right strategy,", ["accurate data,"]),
    (5.26, 8.25, "and a clear understanding of what drives results.", []),
    (8.40, 9.90, "This is SK Mahbub,", ["SK Mahbub,"]),
    (9.90, 12.90, "a Web Analytics, Conversion Tracking and Paid Advertising Consultant.", []),
    (13.38, 15.33, "I help businesses fix tracking issues,", ["tracking issues,"]),
    (15.38, 18.62, "resolve conversion mismatches, eliminate duplicate events,", []),
    (18.72, 20.42, "and build reliable tracking systems", ["reliable"]),
    (20.44, 23.27, "using Google Analytics, Meta Pixel, Conversion API,", []),
    (23.30, 25.18, "Google Ads Conversion Tracking,", []),
    (25.24, 28.24, "TikTok, Snapchat, Twitter, LinkedIn tracking setup,", []),
    (28.28, 29.36, "Microsoft Clarity setup,", []),
    (29.38, 31.97, "and using other essential tracking tools,", []),
    (32.00, 35.48, "combined with Google Ads and Meta Ads optimization.", ["optimization."]),
    (35.56, 38.00, "This helps you make smarter decisions,", []),
    (38.06, 41.90, "generate more qualified leads, increase sales, and grow your business.", ["qualified", "leads,"]),
    (42.02, 44.20, "Let's fix what's holding your marketing back", []),
    (44.22, 47.70, "and turn better data into better business results.", ["better", "data"]),
    (48.00, 51.00, "Need better tracking and stronger ad performance?", []),
    (51.18, DUR + 1, "Let's talk.", ["Let's", "talk."]),
]
SUB_Y = 896

def sub_img(text, hl):
    f = font("m", 30); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    words = text.split(" "); lines = [[]]; maxw = LW - 48
    for w in words:
        trial = " ".join(lines[-1] + [w])
        if d0.textlength(trial, font=f) > maxw and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    lh = 42; h = lh * len(lines) + 30
    wmax = max(d0.textlength(" ".join(l), font=f) for l in lines)
    im = Image.new("RGBA", (int(wmax) + 48, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, h - 1), 18, fill=(255, 255, 255, 235), outline=LINE + (255,), width=2)
    for i, l in enumerate(lines):
        x = 24
        for w in l:
            d.text((x, 14 + i * lh), w, font=f, fill=TEAL if w in hl else INK); x += d.textlength(w + " ", font=f)
    return im

SUB_ELS = []
for t0, t1, s, hl in SUBS:
    im = sub_img(s, hl)
    SUB_ELS.append(El(im, LX, SUB_Y + (120 - im.height) // 2 + 20 if im.height < 100 else SUB_Y, t0, t1, slide=8, dur=0.18, fade_out=0.12))

# ---------- main loop ----------
def main():
    bg = make_bg()
    nfr = int(round(DUR * FPS))
    times = [i / FPS for i in range(nfr)] if PREVIEW is None else PREVIEW
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    if PREVIEW is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    fi = 0; want = 0
    while want < len(times):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = fi / FPS; fi += 1
        if PREVIEW is not None and abs(t - times[want]) > 0.5 / FPS: continue
        src = Image.frombuffer("RGB", (W, H), raw).crop(CROP).resize((CW, CH), Image.LANCZOS)
        frame = bg.copy()
        frame.paste(src, (CX, CY), MASK)
        for e in ELS: e.draw(frame, t)
        for e in SUB_ELS: e.draw(frame, t)
        rgb = frame.convert("RGB")
        if PREVIEW is None:
            enc.stdin.write(rgb.tobytes())
        else:
            rgb.save(os.path.join(HERE, f"out/prev_{times[want]:05.2f}.png"))
        want += 1
        if fi % 150 == 0: print("frame", fi, flush=True)
    dec.kill()
    if PREVIEW is None:
        enc.stdin.close(); enc.wait()

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
