"""Builds edit_p2.py from the approved master engine (edit4.py): new content plan only."""
src = open("../edit4.py").read()
s = src

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:60], c)
    s = s.replace(a, b)

# ---------- content plan ----------
i0 = s.index("# ---------- content plan ----------")
i1 = s.index("T_IN, T_OUT = 0.32, 0.30")
s = s[:i0] + '''# ---------- content plan (video: Microsoft Clarity for e-commerce) ----------
FIX = {"pattern,": "button,"}
KW = {
    10: ("pop", WHITE, None),      # SALES
    22: ("pop", WHITE, None),      # Shopify
    23: ("pop", WHITE, None),      # WordPress
    25: ("pop", WHITE, None),      # WooCommerce
    30: ("pop", WHITE, None),      # losing
    32: ("pop", WHITE, None),      # customers
    72: ("pop", WHITE, None),      # insights
    75: ("pop", WHITE, None),      # friction
    76: ("pop", WHITE, None),      # fix
    80: ("pop", WHITE, None),      # measure
    85: ("pop", WHITE, None),      # conversion
    87: ("pop", WHITE, None),      # guessing
    95: ("pop", WHITE, None),      # understanding
    102: ("pop", WHITE, None),     # analytics
    106: ("pop", WHITE, None),     # optimization
}
COUNT = {}
ITAL = {17, 98}                    # "this."  "Follow"
ZOOM = {10: 0.10, 32: 0.09, 75: 0.08, 85: 0.10, 87: 0.09, 95: 0.10}
COUNTER = (-10.0, -9.0)            # no number scene in this video
CARDS = [
    dict(kind="replay", a=37, b=49),
    dict(kind="list", a=50, b=69, title="WHERE SHOPPERS STRUGGLE", icon="x",
         items=[(52, "Missing \\u201cAdd to Cart\\u201d"), (58, "Lost on product pages"), (64, "Abandoning checkout")]),
]
''' + s[i1:]

rep("def in_counter(i):\n    return 4 <= i <= 9", "def in_counter(i):\n    return False")

# stronger footage text shadow (light shirt in this footage)
rep('''        sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6)))''',
    '''        a1 = np.asarray(alpha.filter(ImageFilter.GaussianBlur(10)), np.float32) * 0.85
        a2 = np.asarray(alpha.filter(ImageFilter.GaussianBlur(30)), np.float32) * 0.5
        sh.putalpha(Image.fromarray(np.clip(np.maximum(a1, a2), 0, 255).astype(np.uint8)))''')

rep("FACE = (540.0, 700.0)", "FACE = (500.0, 700.0)")

# ---------- new card types ----------
NEW = '''
def x_icon(p, size=78, sc=1.0):
    S4 = size * 4
    im = Image.new("RGBA", (S4, S4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([4, 4, S4 - 4, S4 - 4], fill=INK + (255,))
    a, b = S4 * 0.32, S4 * 0.68
    w = int(S4 * 0.09)
    p1 = min(1, p * 2); p2 = max(0, p * 2 - 1)
    if p1 > 0.02: d.line([(a, a), (a + (b - a) * p1, a + (b - a) * p1)], fill=(255, 255, 255, 255), width=w)
    if p2 > 0.02: d.line([(b, a), (b - (b - a) * p2, a + (b - a) * p2)], fill=(255, 255, 255, 255), width=w)
    return im.resize((max(1, int(size * sc)), max(1, int(size * sc))), Image.LANCZOS)

# replay timeline (shared with SFX plan)
def replay_window():
    return wt(42), we(49)
CLICKS = [0.42, 0.80, 0.86, 0.92]          # fractions of the replay
PATH = [(0.78, 0.22), (0.40, 0.30), (0.55, 0.47), (0.30, 0.60), (0.66, 0.58), (0.50, 0.74), (0.62, 0.755), (0.46, 0.76), (0.55, 0.755)]

def path_at(p):
    p = min(1, max(0, p)) * (len(PATH) - 1)
    k = min(int(p), len(PATH) - 2); u = ease_io(p - k)
    (x0, y0), (x1, y1) = PATH[k], PATH[k + 1]
    return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u

def card_replay(cv, t, c):
    age = t - c["s"]
    tt = text_img("MICROSOFT CLARITY", "bold", 40, SUB, 0.14, shadow=False)
    popin(cv, tt, W_ / 2, 360, age - 0.1, 0.2, 0.9, overshoot=False)
    d = ImageDraw.Draw(cv)
    ul = 140 * ease_out((age - 0.2) / 0.35)
    if ul > 1: d.rounded_rectangle([W_ / 2 - ul / 2, 402, W_ / 2 + ul / 2, 409], 3, fill=TEAL + (255,))
    big = text_img("Session Replay", "xbold", 104, INK, -0.03, shadow=False)
    p0 = ease_out((age - 0.18) / 0.3)
    paste(cv, big, W_ / 2, 500 + (1 - p0) * 18, 0.96 + 0.04 * p0, p0)
    pa, ps, pdy = panel_anim(age - 0.2, 0.35)
    WX, WY, WW, WH = 540.0, 1170.0 + pdy, 860, 940
    glass(cv, WX, WY, WW, WH, 40, pa, ps, frost=0.82, blur=10)
    if pa < 0.05: return
    A = int(255 * pa)
    x0, y0 = WX - WW / 2, WY - WH / 2
    d = ImageDraw.Draw(cv)
    for k in range(3):
        d.ellipse([x0 + 34 + k * 30, y0 + 34, x0 + 52 + k * 30, y0 + 52], fill=INK + (int(70 * pa),))
    d.rounded_rectangle([x0 + 140, y0 + 24, x0 + WW - 36, y0 + 64], 20, fill=(255, 255, 255, int(220 * pa)), outline=(0xD5, 0xE8, 0xE0, A), width=2)
    url = text_img("yourstore.com/products/best-seller", "medium", 26, SUB, 0, shadow=False)
    paste(cv, url, x0 + 170 + (url.width - 88) / 2, y0 + 44, 1.0, pa)
    # product page skeleton
    d.rounded_rectangle([x0 + 40, y0 + 96, x0 + WW - 40, y0 + 470], 24, fill=(0xE6, 0xF3, 0xEE, A))
    d.rounded_rectangle([WX - 120, y0 + 170, WX + 120, y0 + 400], 40, fill=(0xCF, 0xE5, 0xDC, A))
    d.rounded_rectangle([x0 + 40, y0 + 510, x0 + 560, y0 + 540], 10, fill=INK + (int(200 * pa),))
    d.rounded_rectangle([x0 + 40, y0 + 560, x0 + 420, y0 + 582], 10, fill=SUB + (int(130 * pa),))
    price = text_img("$49.00", "bold", 54, INK, -0.01, shadow=False)
    paste(cv, price, x0 + 40 + (price.width - 88) / 2, y0 + 640, 1.0, pa)
    bx0, by0, bx1, by1 = x0 + 40, y0 + 700, x0 + WW - 40, y0 + 790
    d.rounded_rectangle([bx0, by0, bx1, by1], 22, fill=TEAL + (A,))
    bt = text_img("Add to cart", "bold", 44, WHITE, 0, shadow=False)
    paste(cv, bt, (bx0 + bx1) / 2, (by0 + by1) / 2, 1.0, pa)
    # playback bar
    r0, r1 = replay_window()
    rp = min(1, max(0, (t - r0) / (r1 - r0)))
    py = y0 + WH - 64
    d.polygon([(x0 + 44, py - 14), (x0 + 44, py + 14), (x0 + 68, py)], fill=INK + (A,))
    tx0, tx1 = x0 + 96, x0 + WW - 150
    d.rounded_rectangle([tx0, py - 4, tx1, py + 4], 4, fill=(0xCF, 0xE5, 0xDC, A))
    if rp > 0: d.rounded_rectangle([tx0, py - 4, tx0 + (tx1 - tx0) * rp, py + 4], 4, fill=TEAL + (A,))
    d.ellipse([tx0 + (tx1 - tx0) * rp - 9, py - 9, tx0 + (tx1 - tx0) * rp + 9, py + 9], fill=TEAL + (A,))
    tm = text_img("00:{:02d}".format(int(rp * 47)), "medium", 30, SUB, 0, shadow=False)
    paste(cv, tm, x0 + WW - 84, py, 1.0, pa)
    # struggle heat + chip (data accent: blue)
    st = t - wt(48)
    if st > 0:
        hp = ease_out(st / 0.5)
        heat = Image.new("RGBA", cv.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(heat)
        cx, cy = x0 + WW * 0.56, (by0 + by1) / 2
        for rr, al in ((150, 30), (100, 45), (60, 70)):
            hd.ellipse([cx - rr * hp, cy - rr * hp * 0.7, cx + rr * hp, cy + rr * hp * 0.7], fill=BLUE + (int(al * pa),))
        cv.alpha_composite(heat.filter(ImageFilter.GaussianBlur(18)))
    ch = t - wt(49)
    if ch > 0:
        lab = text_img("Rage clicks detected", "bold", 34, WHITE, 0.01, shadow=False)
        pill = round_rect_img(lab.width - 40, 66, 33, BLUE + (255,), blur_shadow=True)
        pl = pill.copy(); pl.alpha_composite(lab, ((pl.width - lab.width) // 2, (pl.height - lab.height) // 2))
        popin(cv, pl, x0 + WW * 0.56, by0 - 70, ch, 0.22, 0.7)
    # click ripples
    for cf in CLICKS:
        ct = r0 + cf * (r1 - r0)
        ra = t - ct
        if 0 <= ra < 0.45:
            cx, cy = path_at(cf)
            cx, cy = x0 + cx * WW, y0 + cy * WH
            rr = 12 + 46 * ease_out(ra / 0.45)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=TEAL + (int(230 * (1 - ra / 0.45) * pa),), width=5)
    # cursor
    cx, cy = path_at(rp)
    cx, cy = x0 + cx * WW, y0 + cy * WH
    sc = 1.7
    pts = [(0, 0), (0, 36), (9, 28), (15, 42), (21, 39), (15, 26), (27, 26)]
    poly = [(cx + x * sc, cy + y * sc) for x, y in pts]
    d.polygon([(px + 3, py_ + 4) for px, py_ in poly], fill=(0, 0, 0, int(60 * pa)))
    d.polygon(poly, fill=INK + (A,), outline=(255, 255, 255, A))
    d.line(poly + [poly[0]], fill=(255, 255, 255, A), width=3)

'''
rep("def card_no(cv, t, c):", NEW + "def card_no(cv, t, c):")
# list card: optional ✕ icons
rep('''        ci = check_icon(ease_out((ia - 0.12) / 0.28), 78, max(0.01, cs))''',
    '''        ci = (x_icon if c.get("icon") == "x" else check_icon)(ease_out((ia - 0.12) / 0.28), 78, max(0.01, cs))''')
rep('''    items = c["items"]; step = 136 if len(items) > 6 else 160
    y0 = 650 if len(items) > 6 else 720''', '''    items = c["items"]; step = 136 if len(items) > 6 else (180 if len(items) <= 3 else 160)
    y0 = 650 if len(items) > 6 else (820 if len(items) <= 3 else 720)''')
rep('CARD_FN = {"wave": card_wave, "list": card_list, "no": card_no}',
    'CARD_FN = {"wave": card_wave, "list": card_list, "no": card_no, "replay": card_replay}')

# ---------- SFX plan: drop counter block, add replay clicks ----------
i0 = s.index("    # counter scene\n")
i1 = s.index("    # cards\n")
s = s[:i0] + s[i1:]
rep('''        if c["kind"] == "no":
            sfx(wt(241), "impact_heavy", 0.42)''', '''        if c["kind"] == "replay":
            r0, r1 = replay_window()
            sfx(r0 - 0.05, "swish", 0.10)
            for cf in CLICKS: sfx(r0 + cf * (r1 - r0), "click", 0.18, 0.2)
            sfx(wt(48), "riser", 0.05)
            sfx(wt(49), "pop", 0.14); sfx(wt(49), "impact", 0.10)
        if c["kind"] == "list" and c.get("icon") == "x":
            for wi, _ in c["items"]: sfx(wt(wi), "impact", 0.07)''')

rep('"mix4.wav"', '"mix_p2.wav"', 2)
rep('"clip4.mp4" if CLIP else "final4.mp4"', '"clip_p2.mp4" if CLIP else "final_p2.mp4"')
rep('f"p4_{ts}.png"', 'f"pv_{ts}.png"')
open("edit_p2.py", "w").write(s)
print("edit_p2.py written")
