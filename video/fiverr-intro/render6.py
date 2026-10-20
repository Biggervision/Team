"""SK Mahbub Fiverr intro — v5 in 9:16 (1080x1920).

Same design as v5. Footage (cropped around the speaker) fills the lower 1440px;
the wall is extended upward to fill the top 480px. Hero words, italics, captions
and floating logo tiles are re-laid-out for portrait.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render5 as r5
r2 = r5.r2
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/out/v6_noaudio.mp4"
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None

SW, SH = 1920, 1080                      # source
W, H = 1080, 1920                        # output
r2.W, r2.H = W, H
TOP = 480                                # extended-wall band
FH = H - TOP                             # footage height (1440)
WIDE_V = (555, 0, 810, 1080)             # 0.75 aspect crops -> 1080x1440
MED_V = (640, 20, 640, 853)
def framing_v(t): return WIDE_V if r2.framing(t) is r2.WIDE else MED_V
def is_wide(t): return r2.framing(t) is r2.WIDE
ease_out, ease_io, alpha_mul = r2.ease_out, r2.ease_io, r5.alpha_mul

# ---------------- hero words (portrait) ----------------
HC = {}
def hero_layer(italic, word):
    if (italic, word) in HC: return HC[(italic, word)]
    name = word == "SK Mahbub"
    size = 170 if name else 230
    f = r2.mont(900, size)
    while f.getbbox(word)[2] - f.getbbox(word)[0] > 990 and size > 80:
        size -= 6; f = r2.mont(900, size)
    bb = f.getbbox(word); pad = 50
    mask = Image.new("L", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), 0)
    ImageDraw.Draw(mask).text((pad - bb[0], pad - bb[1]), word, font=f, fill=255)
    img = Image.new("RGBA", mask.size, (0, 0, 0, 0)); img.paste(r2.texture(*mask.size), (0, 0), mask)
    sh = Image.new("RGBA", mask.size, (10, 14, 40, 0)); sh.putalpha(mask.point(lambda v: v * 70 // 255))
    base = Image.new("RGBA", mask.size, (0, 0, 0, 0)); base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (0, 6)); base.alpha_composite(img)
    fi = r2.play(max(64, int(size * 0.42)))
    ib = fi.getbbox(italic)
    it = Image.new("RGBA", (ib[2] - ib[0] + 40, ib[3] - ib[1] + 40), (0, 0, 0, 0))
    s2 = Image.new("RGBA", it.size, (0, 0, 0, 0)); ImageDraw.Draw(s2).text((20 - ib[0], 22 - ib[1]), italic, font=fi, fill=(0, 0, 0, 130))
    it.alpha_composite(s2.filter(ImageFilter.GaussianBlur(6))); ImageDraw.Draw(it).text((20 - ib[0], 20 - ib[1]), italic, font=fi, fill=(255, 255, 255, 255))
    HC[(italic, word)] = (base, it)
    return HC[(italic, word)]

def draw_hero(layer, t, h, front):
    i = r2.HEROES.index(h)
    if i + 1 < len(r2.HEROES):
        nxt = r2.HEROES[i + 1][0]
        if nxt - h[2] < 0.35 and t >= nxt - 0.03: return False
    t_in, _, t_out, italic, word = h
    if not (t_in <= t <= t_out + 0.22): return False
    base, it = hero_layer(italic, word)
    name = word == "SK Mahbub"
    p = ease_out((t - t_in) / 0.38)
    a = min(1, (t - t_in) / 0.18) * (1 - ease_io((t - t_out) / 0.22) if t > t_out else 1)
    if a <= 0.01: return False
    s = 1.10 - 0.10 * p if t <= t_out else 1 - 0.03 * ease_io((t - t_out) / 0.22)
    b = r2.scaled(base, s, a)
    cy = 560 if name else (690 if is_wide(t) else 720)       # behind the top of the head
    (front if name else layer).alpha_composite(b, (int(W / 2 - b.width / 2), int(cy - b.height / 2)))
    pi = ease_out((t - t_in - 0.08) / 0.4); ai = a * min(1, max(0, (t - t_in - 0.05) / 0.2))
    if ai > 0.01:
        x = int(W / 2 - b.width / 2 + 40 - 40 * (1 - pi)); y = int(cy - b.height / 2 - it.height * 0.62)
        front.alpha_composite(r2.scaled(it, 1, ai), (max(30, x), max(8, y)))
    return True
r2.draw_hero = draw_hero

# ---------------- captions (portrait) ----------------
CAP_Y = 1395
def draw_caption(frame, t):
    for c, c_end in r2.CHUNKS:
        if c[0][0] - 0.02 <= t < c_end:
            a = 1 - ease_io((t - (c_end - 0.12)) / 0.12) if t > c_end - 0.12 else 1
            im = r2.caption_img(c, t)
            if im.width > W - 20:
                k = (W - 20) / im.width; im = im.resize((int(im.width * k), int(im.height * k)), Image.BICUBIC)
            im = r2.scaled(im, 1, a)
            frame.alpha_composite(im, (int(W / 2 - im.width / 2), CAP_Y - im.height // 2))
r2.draw_caption = draw_caption

# ---------------- floating tiles (portrait slots) ----------------
r5.SLOT.clear()
r5.SLOT.update({"A": (240, 300, 0.95), "B": (840, 300, 0.95), "C": (170, 800, 0.84), "D": (910, 800, 0.84), "E": (540, 150, 0.8)})
r5.FLOAT[:] = [
    (3.08, 4.18, "chart", "A"), (4.62, 5.22, "target", "B"),
    (14.48, 18.66, "issue", "A"), (15.62, 18.66, "mismatch", "B"), (17.32, 18.66, "dedup", "E"),
    (21.08, 25.18, "ga4", "A"), (22.06, 25.18, "meta", "B"), (22.42, 25.18, "capi", "D"), (23.30, 25.18, "gads", "C"),
    (25.24, 29.36, "tiktok", "A"), (25.70, 29.36, "snapchat", "B"), (26.30, 29.36, "x", "C"), (26.58, 29.36, "linkedin", "D"),
    (28.28, 29.36, "clarity", "E"),
    (30.30, 32.92, "gtm", "A"), (31.22, 32.92, "server", "B"),
    (32.94, 35.50, "gads", "A"), (34.10, 35.50, "meta_ads", "B"),
    (38.66, 41.98, "funnel", "A"), (39.80, 41.98, "trend", "B"),
    (48.52, r2.VID_END, "chat", "B"),
]

# ---------------- frame composition ----------------
FEATHER = np.linspace(0, 1, 70, dtype=np.float32)
def compose(raw, mraw, t):
    box = framing_v(t)
    src = Image.frombuffer("RGB", (SW, SH), raw)
    foot = src.crop((box[0], box[1], box[0] + box[2], box[1] + box[3])).resize((W, FH), Image.LANCZOS)
    # extend the wall upward: stretch the top rows of the crop (vertical slats continue naturally)
    strip = src.crop((box[0], box[1], box[0] + box[2], box[1] + 36)).resize((W, TOP + 70), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    canvas = Image.new("RGB", (W, H)); canvas.paste(strip, (0, 0))
    fm = np.ones((FH, W), np.float32); fm[:70] = FEATHER[:, None]
    canvas.paste(foot, (0, TOP), Image.fromarray((fm * 255).astype(np.uint8)))
    # gentle top darkening so white text/tiles pop
    g = np.linspace(0.78, 1.0, TOP + 200, dtype=np.float32)
    arr = np.asarray(canvas, np.float32); arr[:TOP + 200] *= g[:, None, None]
    canvas = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    mt = Image.new("L", (W, H), 0)
    mt.paste(Image.frombuffer("L", (SW, SH), mraw).crop((box[0], box[1], box[0] + box[2], box[1] + box[3])).resize((W, FH), Image.BILINEAR), (0, TOP))
    return canvas, mt

def grab(p, n):
    b = p.stdout.read(n); return b if len(b) == n else None

def main():
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", r2.SRC, "-vf", "eq=saturation=0.88:contrast=1.04:gamma=0.98", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    mat = subprocess.Popen(["ffmpeg", "-v", "error", "-i", r2.MATTE, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    if PREVIEW is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    targets = PREVIEW or [i / 30 for i in range(int(round(r2.DUR * 30)))]
    fi, last, photo, ec, lastout = 0, None, None, None, None
    for t in targets:
        while t <= r2.VID_END and fi / 30 <= t + 1e-6:
            raw = grab(dec, SW * SH * 3); mraw = grab(mat, SW * SH)
            if raw is None: break
            ft = fi / 30; fi += 1
            if abs(ft - 40.0) < 0.02: photo = Image.frombuffer("RGB", (SW, SH), raw).copy()
            last = (raw, mraw)
            if ft >= t - 0.5 / 30: break
        if t <= r2.VID_END and last is not None:
            canvas, mt = compose(*last, t)
            frame = canvas.convert("RGBA")
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            used = r2.CHIPS.draw(layer, t, is_wide(t))
            for h in r2.HEROES: used = r2.draw_hero(layer, t, h, front) or used
            if used:
                back = frame.copy(); back.alpha_composite(layer)
                frame = Image.composite(frame, back, mt); frame.alpha_composite(front)
            r2.draw_caption(frame, t)
            out = frame.convert("RGB"); lastout = out
        else:
            if ec is None: ec = r2.end_card(lastout, photo or Image.frombuffer("RGB", (SW, SH), last[0]))
            bg, card, shadow = ec
            k = (t - r2.VID_END) / 0.45; p = ease_out((t - r2.VID_END - 0.1) / 0.6)
            frame = Image.blend(lastout, bg.convert("RGB"), ease_io(k)).convert("RGBA")
            a = min(1, max(0, (t - r2.VID_END - 0.1) / 0.35))
            cs = r2.scaled(card, 0.94 + 0.06 * p, a); ss = r2.scaled(shadow, 0.94 + 0.06 * p, a)
            frame.alpha_composite(ss, (int(W / 2 - ss.width / 2), int(H / 2 - ss.height / 2 + 30 * (1 - p))))
            frame.alpha_composite(cs, (int(W / 2 - cs.width / 2), int(H / 2 - cs.height / 2 + 30 * (1 - p))))
            out = frame.convert("RGB")
        if PREVIEW is None: enc.stdin.write(out.tobytes())
        else: out.save(f"{HERE}/out/v6_{t:05.2f}.png")
    dec.kill(); mat.kill()
    if PREVIEW is None: enc.stdin.close(); enc.wait()

if __name__ == "__main__":
    main()
