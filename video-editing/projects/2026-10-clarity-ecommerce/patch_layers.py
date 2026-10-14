"""Layered version: footage (L1) + pop-up motion graphics (L2) + captions (L3). No full-screen canvases."""
s = open("edit_p2.py").read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:70], c)
    s = s.replace(a, b)

# ---- content plan: keywords / zooms / no full-screen cards ----
i0 = s.index("KW = {"); i1 = s.index("COUNT = {}")
s = s[:i0] + '''KW = {
    10: ("pop", WHITE, None),      # SALES
    30: ("pop", WHITE, None),      # losing
    32: ("pop", WHITE, None),      # customers
    72: ("pop", WHITE, None),      # insights
    87: ("pop", WHITE, None),      # guessing
    95: ("pop", WHITE, None),      # understanding
    102: ("pop", WHITE, None),     # analytics
    106: ("pop", WHITE, None),     # optimization
}
''' + s[i1:]
rep("ZOOM = {10: 0.10, 32: 0.09, 75: 0.08, 85: 0.10, 87: 0.09, 95: 0.10}",
    "ZOOM = {10: 0.10, 17: 0.07, 32: 0.09, 72: 0.07, 87: 0.09, 95: 0.10}")
i0 = s.index("CARDS = ["); i1 = s.index("T_IN, T_OUT")
s = s[:i0] + "CARDS = []\n" + s[i1:]
rep("FACE = (500.0, 700.0)", "FACE = (430.0, 760.0)")

LAYER = r'''
# =================== LAYER 2: pop-up motion graphics ===================
POP = [
    dict(kind="sales",   t0=wt(1),  t1=we(10) + 0.5,  zone="top"),
    dict(kind="chips",   t0=wt(22) - 0.1, t1=we(25) + 0.7, zone="top"),
    dict(kind="leaving", t0=wt(30) - 0.1, t1=we(36) + 0.2, zone="top"),
    dict(kind="replay",  t0=wt(37) - 0.15, t1=we(49) + 0.25, zone="low"),
    dict(kind="friction", t0=wt(50) - 0.1, t1=we(69) + 0.3, zone="low"),
    dict(kind="steps",   t0=wt(74) - 0.2, t1=we(85) + 0.45, zone="low"),
    dict(kind="toggle",  t0=wt(87) - 0.1, t1=we(97) + 0.3, zone="top"),
    dict(kind="follow",  t0=wt(98) - 0.15, t1=TOTAL, zone="top"),
]

def pop_state(t, p):
    a_in = ease_out((t - p["t0"]) / 0.32)
    a_out = 1 - ease_in((t - (p["t1"] - 0.25)) / 0.25)
    a = max(0.0, min(a_in, a_out))
    return a, 0.92 + 0.08 * a_in, (1 - a_in) * 34 + (1 - a_out) * 18

def low_card_active(t):
    return any(p["zone"] == "low" and p["t0"] - 0.1 <= t < p["t1"] + 0.1 for p in POP)

_cb = {}
def card(cv, cx, cy, w, h, a, sc=1.0, r=34):
    k = (w, h, r)
    if k not in _cb:
        _cb[k] = round_rect_img(w, h, r, (255, 255, 255, 246), outline=(0xD5, 0xE8, 0xE0, 255), ow=2)
    paste(cv, _cb[k], cx, cy, sc, a)

def mini_chart(d, x0, y0, w, h, pts, col, a, prog=1.0, width=6):
    n = max(2, int(len(pts) * prog + 0.999))
    P = [(x0 + px * w, y0 + (1 - py) * h) for px, py in pts[:n]]
    if prog < 1 and n >= 2:
        f = len(pts) * prog - (n - 1)
        (xa, ya), (xb, yb) = P[-2], P[-1]
        P[-1] = (xa + (xb - xa) * max(0, f), ya + (yb - ya) * max(0, f))
    d.line(P, fill=col + (int(255 * a),), width=width, joint="curve")
    xe, ye = P[-1]
    d.ellipse([xe - 9, ye - 9, xe + 9, ye + 9], fill=(255, 255, 255, int(255 * a)), outline=col + (int(255 * a),), width=4)

def person_icon(d, cx, cy, s, col):
    d.ellipse([cx - 0.28 * s, cy - 0.62 * s, cx + 0.28 * s, cy - 0.06 * s], fill=col)
    d.pieslice([cx - 0.5 * s, cy + 0.02 * s, cx + 0.5 * s, cy + 1.02 * s], 180, 360, fill=col)

def pop_sales(cv, t, p, a, sc, dy):
    cx, cy = 870, 300 + dy
    card(cv, cx, cy, 340, 240, a, sc)
    lab = text_img("Store sales", "semi", 34, SUB, 0, shadow=False)
    paste(cv, lab, cx - 70 + (lab.width - 88) / 2 - 60, cy - 78, 1, a)
    d = ImageDraw.Draw(cv)
    pts = [(0, 0.85), (0.2, 0.7), (0.4, 0.78), (0.6, 0.45), (0.8, 0.38), (1, 0.1)]
    prog = min(1, max(0.02, (t - p["t0"] - 0.2) / 1.6))
    mini_chart(d, cx - 140, cy - 30, 280, 110, pts, BLUE, a, prog)
    if t > wt(10):          # "sales?" -> down arrow badge
        ba = ease_out((t - wt(10)) / 0.25) * a
        d.ellipse([cx + 112, cy - 112, cx + 168, cy - 56], fill=BLUE + (int(255 * ba),))
        d.polygon([(cx + 140, cy - 66), (cx + 124, cy - 88), (cx + 156, cy - 88)], fill=(255, 255, 255, int(255 * ba)))
        d.rectangle([cx + 135, cy - 102, cx + 145, cy - 86], fill=(255, 255, 255, int(255 * ba)))

PLAT = [(22, "Shopify"), (23, "WordPress"), (25, "WooCommerce")]
def pop_chips(cv, t, p, a, sc, dy):
    for k, (wi, name) in enumerate(PLAT):
        ia = t - wt(wi)
        if ia < 0: continue
        q = ease_out(ia / 0.3)
        cx, cy = 800 + (1 - q) * 60, 250 + k * 116 + dy
        card(cv, cx, cy, 400, 96, a * q, 1.0, 48)
        d = ImageDraw.Draw(cv)
        d.ellipse([cx - 170, cy - 16, cx - 138, cy + 16], fill=TEAL + (int(255 * a * q),))
        im = text_img(name, "bold", 36, INK, -0.01, shadow=False)
        paste(cv, im, cx - 116 + (im.width - 88) / 2, cy, 1, a * q)

def pop_leaving(cv, t, p, a, sc, dy):
    cx, cy = 870, 300 + dy
    card(cv, cx, cy, 340, 240, a, sc)
    lab = text_img("Visitors", "semi", 34, SUB, 0, shadow=False)
    paste(cv, lab, cx - 130 + (lab.width - 88) / 2, cy - 88, 1, a)
    d = ImageDraw.Draw(cv)
    gone = ease_io((t - wt(31)) / 0.8)          # "potential customers" -> two leave
    for k in range(3):
        x = cx - 96 + k * 96
        if k == 0:
            col = TEAL + (int(255 * a),); xo = 0
        else:
            fade = 1 - gone * (0.75 if k == 1 else 0.85)
            col = (INK if gone < 0.3 else SUB) + (int(255 * a * fade),); xo = gone * (30 + k * 18)
        person_icon(d, x + xo, cy + 10, 70, col)

def draw_replay(cv, cx, cy, WW, WH, t, a):
    A = int(255 * a)
    x0, y0 = cx - WW / 2, cy - WH / 2
    d = ImageDraw.Draw(cv)
    hd = text_img("Microsoft Clarity  ·  Session replay", "semi", 32, SUB, 0, shadow=False)
    paste(cv, hd, x0 + 36 + (hd.width - 88) / 2, y0 + 44, 1, a)
    d.rounded_rectangle([x0 + 30, y0 + 84, x0 + WW - 30, y0 + 120], 18, fill=(0xF6, 0xFB, 0xF9, A), outline=(0xD5, 0xE8, 0xE0, A), width=2)
    u = text_img("yourstore.com/products/best-seller", "medium", 22, SUB, 0, shadow=False)
    paste(cv, u, x0 + 60 + (u.width - 88) / 2, y0 + 102, 1, a)
    d.rounded_rectangle([x0 + 30, y0 + 140, x0 + 350, y0 + 420], 20, fill=(0xE6, 0xF3, 0xEE, A))
    d.rounded_rectangle([x0 + 120, y0 + 200, x0 + 260, y0 + 360], 30, fill=(0xCF, 0xE5, 0xDC, A))
    d.rounded_rectangle([x0 + 380, y0 + 160, x0 + WW - 40, y0 + 186], 9, fill=INK + (int(200 * a),))
    d.rounded_rectangle([x0 + 380, y0 + 204, x0 + WW - 140, y0 + 222], 9, fill=SUB + (int(120 * a),))
    pr = text_img("$49.00", "bold", 46, INK, 0, shadow=False)
    paste(cv, pr, x0 + 380 + (pr.width - 88) / 2, y0 + 280, 1, a)
    bx0, by0, bx1, by1 = x0 + 380, y0 + 340, x0 + WW - 40, y0 + 412
    d.rounded_rectangle([bx0, by0, bx1, by1], 18, fill=TEAL + (A,))
    bt = text_img("Add to cart", "bold", 34, WHITE, 0, shadow=False)
    paste(cv, bt, (bx0 + bx1) / 2, (by0 + by1) / 2, 1, a)
    r0, r1 = wt(42), we(49)
    rp = min(1, max(0, (t - r0) / (r1 - r0)))
    py = y0 + WH - 50
    d.polygon([(x0 + 40, py - 12), (x0 + 40, py + 12), (x0 + 60, py)], fill=INK + (A,))
    tx0, tx1 = x0 + 84, x0 + WW - 120
    d.rounded_rectangle([tx0, py - 4, tx1, py + 4], 4, fill=(0xCF, 0xE5, 0xDC, A))
    if rp > 0: d.rounded_rectangle([tx0, py - 4, tx0 + (tx1 - tx0) * rp, py + 4], 4, fill=TEAL + (A,))
    d.ellipse([tx0 + (tx1 - tx0) * rp - 8, py - 8, tx0 + (tx1 - tx0) * rp + 8, py + 8], fill=TEAL + (A,))
    tm = text_img("00:{:02d}".format(int(rp * 47)), "medium", 26, SUB, 0, shadow=False)
    paste(cv, tm, x0 + WW - 66, py, 1, a)
    # path in card coords (fractions of WW/WH)
    path = [(0.20, 0.30), (0.62, 0.30), (0.30, 0.55), (0.75, 0.48), (0.62, 0.74), (0.80, 0.745), (0.66, 0.75), (0.74, 0.745)]
    def at(q):
        q = min(1, max(0, q)) * (len(path) - 1); k = min(int(q), len(path) - 2); u_ = ease_io(q - k)
        return (path[k][0] + (path[k + 1][0] - path[k][0]) * u_, path[k][1] + (path[k + 1][1] - path[k][1]) * u_)
    if t > wt(48):
        hp = ease_out((t - wt(48)) / 0.5)
        heat = Image.new("RGBA", cv.size, (0, 0, 0, 0)); h2 = ImageDraw.Draw(heat)
        hx, hy = (bx0 + bx1) / 2 + 40, (by0 + by1) / 2
        for rr, al in ((120, 35), (80, 55), (46, 80)):
            h2.ellipse([hx - rr * hp, hy - rr * hp * 0.6, hx + rr * hp, hy + rr * hp * 0.6], fill=BLUE + (int(al * a),))
        cv.alpha_composite(heat.filter(ImageFilter.GaussianBlur(14)))
    if t > wt(49):
        lab = text_img("Rage clicks detected", "bold", 30, WHITE, 0.01, shadow=False)
        pill = round_rect_img(lab.width - 40, 58, 29, BLUE + (255,), blur_shadow=True)
        pl = pill.copy(); pl.alpha_composite(lab, ((pl.width - lab.width) // 2, (pl.height - lab.height) // 2))
        popin(cv, pl, (bx0 + bx1) / 2, by0 - 52, t - wt(49), 0.22, 0.7)
    for cf in REPLAY_CLICKS:
        ra = t - (r0 + cf * (r1 - r0))
        if 0 <= ra < 0.45:
            qx, qy = at(cf); qx, qy = x0 + qx * WW, y0 + qy * WH
            rr = 10 + 40 * ease_out(ra / 0.45)
            d.ellipse([qx - rr, qy - rr, qx + rr, qy + rr], outline=TEAL + (int(230 * (1 - ra / 0.45) * a),), width=5)
    qx, qy = at(rp); qx, qy = x0 + qx * WW, y0 + qy * WH
    pts = [(0, 0), (0, 36), (9, 28), (15, 42), (21, 39), (15, 26), (27, 26)]
    poly = [(qx + x * 1.5, qy + y * 1.5) for x, y in pts]
    d.polygon(poly, fill=INK + (A,)); d.line(poly + [poly[0]], fill=(255, 255, 255, A), width=3)

REPLAY_CLICKS = [0.40, 0.78, 0.85, 0.92]
def pop_replay(cv, t, p, a, sc, dy):
    cx, cy = 540, 1490 + dy
    card(cv, cx, cy, 900, 560, a, sc)
    if a > 0.05: draw_replay(cv, cx, cy, 900 * sc, 560 * sc, t, a)

FRIC = [(52, "Missing “Add to Cart”"), (58, "Lost on product pages"), (64, "Abandoning checkout")]
def pop_friction(cv, t, p, a, sc, dy):
    cx, cy = 540, 1500 + dy
    card(cv, cx, cy, 900, 470, a, sc)
    tt = text_img("WHERE SHOPPERS STRUGGLE", "bold", 32, SUB, 0.14, shadow=False)
    paste(cv, tt, cx, cy - 178, 1, a)
    d = ImageDraw.Draw(cv)
    for k, (wi, lab) in enumerate(FRIC):
        ia = t - wt(wi)
        if ia < 0: continue
        q = ease_out(ia / 0.3)
        y = cy - 86 + k * 112 + (1 - q) * 16
        d.rounded_rectangle([cx - 410, y - 46, cx + 410, y + 46], 24, fill=(0xF6, 0xFB, 0xF9, int(255 * a * q)), outline=(0xD5, 0xE8, 0xE0, int(255 * a * q)), width=2)
        cs = back_out((ia - 0.05) / 0.22, 1.6) if ia > 0.05 else 0.01
        paste(cv, x_icon(ease_out((ia - 0.1) / 0.28), 64, max(0.01, cs)), cx - 360, y, 1, a * q)
        im = text_img(lab, "bold", 46, INK, -0.01, shadow=False, maxw=640)
        paste(cv, im, cx - 310 + (im.width - 88) / 2, y, 1, a * q)

STEPS = [(74, "Identify friction"), (76, "Fix the problem"), (80, "Measure the change")]
def pop_steps(cv, t, p, a, sc, dy):
    cx, cy = 540, 1500 + dy
    card(cv, cx, cy, 900, 500, a, sc)
    d = ImageDraw.Draw(cv)
    for k, (wi, lab) in enumerate(STEPS):
        ia = t - wt(wi)
        y = cy - 150 + k * 104
        done = ia >= 0
        q = ease_out(ia / 0.3) if done else 0
        num = text_img(str(k + 1), "bold", 34, WHITE if done else SUB, 0, shadow=False)
        d.ellipse([cx - 392, y - 32, cx - 328, y + 32], fill=(TEAL if done else (0xE6, 0xF3, 0xEE)) + (int(255 * a),))
        if done and ia > 0.15:
            paste(cv, check_icon(ease_out((ia - 0.15) / 0.28), 64, 1.0), cx - 360, y, 1, a)
        else:
            paste(cv, num, cx - 360, y, 1, a)
        im = text_img(lab, "bold", 46, INK if done else SUB, -0.01, shadow=False)
        paste(cv, im, cx - 300 + (im.width - 88) / 2, y, 1, a * (0.45 + 0.55 * q if done else 0.45))
    if t > wt(84):          # "improve conversion" -> blue rising chart
        ca = t - wt(84)
        lab = text_img("Conversion rate", "semi", 32, SUB, 0, shadow=False)
        paste(cv, lab, cx - 392 + (lab.width - 88) / 2, cy + 168, 1, a * ease_out(ca / 0.3))
        pts = [(0, 0.15), (0.25, 0.3), (0.5, 0.28), (0.75, 0.62), (1, 0.92)]
        mini_chart(d, cx - 40, cy + 120, 400, 90, pts, BLUE, a, min(1, max(0.02, ca / 0.8)))

def pop_toggle(cv, t, p, a, sc, dy):
    cx, cy = 870, 290 + dy
    flip = t >= wt(95)
    card(cv, cx, cy, 330, 150, a, sc, 75)
    d = ImageDraw.Draw(cv)
    if not flip:
        d.ellipse([cx - 140, cy - 44, cx - 52, cy + 44], fill=INK + (int(255 * a),))
        qm = text_img("?", "xbold", 64, WHITE, 0, shadow=False); paste(cv, qm, cx - 96, cy, 1, a)
        im = text_img("Guessing", "bold", 42, INK, 0, shadow=False)
    else:
        fa = t - wt(95)
        paste(cv, check_icon(ease_out(fa / 0.3), 88, back_out(min(1, fa / 0.25), 1.6) if fa < 0.25 else 1.0), cx - 96, cy, 1, a)
        im = text_img("Insight", "bold", 42, INK, 0, shadow=False)
    paste(cv, im, cx + 50, cy, 1, a)

def pop_follow(cv, t, p, a, sc, dy):
    cx, cy = 820, 330 + dy
    lab = text_img("+  Follow", "bold", 46, WHITE, 0.01, shadow=False)
    pill = round_rect_img(lab.width - 20, 96, 48, TEAL + (255,), blur_shadow=True)
    pl = pill.copy(); pl.alpha_composite(lab, ((pl.width - lab.width) // 2, (pl.height - lab.height) // 2))
    tap = t - (wt(99) + 0.1)
    s2 = 1 - 0.06 * math.sin(min(1, max(0, tap / 0.25)) * math.pi) if tap > 0 else 1
    paste(cv, pl, cx, cy, sc * s2, a)
    if 0 < tap < 0.5:
        d = ImageDraw.Draw(cv); rr = 20 + 60 * ease_out(tap / 0.5)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 255, 255, int(220 * (1 - tap / 0.5) * a)), width=5)

POP_FN = {"sales": pop_sales, "chips": pop_chips, "leaving": pop_leaving, "replay": pop_replay,
          "friction": pop_friction, "steps": pop_steps, "toggle": pop_toggle, "follow": pop_follow}

def popups(cv, t):
    for p in POP:
        if p["t0"] <= t < p["t1"]:
            a, sc, dy = pop_state(t, p)
            if a > 0.01: POP_FN[p["kind"]](cv, t, p, a, sc, dy)
'''
rep("# ---------- camera (zoom) ----------", LAYER + "\n# ---------- camera (zoom) ----------")

# L3 captions move up under the chin while a low card is up
rep('''        draw_line(canvas, u["ws"], t, CY, "medium", 72, ua)''',
    '''        draw_line(canvas, u["ws"], t, CYt(t), "medium", 72, ua)''')
rep("UNITS = None\ndef caption(canvas, t):", "UNITS = None\ndef CYt(t):\n    return 1150 if low_card_active(t) else CY\n\ndef caption(canvas, t):")

# compose: L1 camera -> L2 popups -> L3 captions
rep('''    caption(cv, t)
    return cv''', '''    popups(cv, t)
    caption(cv, t)
    return cv''')

# SFX for pop-ups
rep('''    # cards
''', '''    # layer-2 pop-ups
    for p in POP:
        sfx(p["t0"] - 0.08, "swish", 0.09, 0.4); sfx(p["t0"] + 0.04, "bubble", 0.08, 0.4)
        sfx(p["t1"] - 0.25, "whoosh_up", 0.06, 0.4)
    for wi, _ in PLAT: sfx(wt(wi), "click", 0.12, 0.4)
    for cf in REPLAY_CLICKS: sfx(wt(42) + cf * (we(49) - wt(42)), "click", 0.17, 0.0)
    sfx(wt(49), "pop", 0.12)
    for wi, _ in FRIC: sfx(wt(wi), "click", 0.12); sfx(wt(wi) + 0.05, "impact", 0.06)
    for wi, _ in STEPS: sfx(wt(wi) + 0.15, "click", 0.12); sfx(wt(wi) + 0.2, "pop", 0.06)
    sfx(wt(84) + 0.6, "ding", 0.06)
    sfx(wt(95), "ding", 0.06)
    sfx(wt(99) + 0.1, "click", 0.16)
    # cards
''')
open("edit_p2.py", "w").write(s)
print("layered engine written")
