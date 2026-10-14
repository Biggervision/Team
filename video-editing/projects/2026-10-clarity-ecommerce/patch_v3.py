"""v3: dark cinematic direction (reference 2) in brand colours. Applied on top of patch_p2 output."""
s = open("edit_p2.py").read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:70], c)
    s = s.replace(a, b)

# ---- content plan ----
i0 = s.index("KW = {"); i1 = s.index("COUNT = {}")
s = s[:i0] + '''KW = {
    102: ("pop", WHITE, None),     # analytics
    106: ("pop", WHITE, None),     # optimization
}
''' + s[i1:]
rep("ITAL = {17, 98}", "ITAL = {98}")
rep("ZOOM = {10: 0.10, 32: 0.09, 75: 0.08, 85: 0.10, 87: 0.09, 95: 0.10}",
    "ZOOM = {10: 0.08, 17: 0.07, 30: 0.09, 52: 0.05, 87: 0.07, 95: 0.08}")
i0 = s.index("CARDS = ["); i1 = s.index("T_IN, T_OUT")
s = s[:i0] + '''CARDS = [
    dict(kind="clarity", a=37, b=49),
    dict(kind="steps3", a=70, b=85),
]
''' + s[i1:]
rep("FACE = (500.0, 700.0)", "FACE = (430.0, 760.0)")

V3 = r'''
# ======================= v3 DARK CINEMATIC SYSTEM =======================
MINT = (0xF6, 0xFB, 0xF9); MINT2 = (0xE6, 0xF3, 0xEE); TEAL_G = (45, 212, 191)
for c in CARDS:
    c["s"] = wt(c["a"]) - 0.12
    c["e"] = we(c["b"]) + 0.22

# --- dark canvas: forest radial + grain, precomputed ---
_yy, _xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
_r = np.sqrt(((_xx - 540) / 900) ** 2 + ((_yy - 860) / 1300) ** 2)
DARK = np.clip(np.array([5, 11, 9.])[None, None] + np.array([0x17 - 5, 0x2B - 11, 0x26 - 9.])[None, None] * np.clip(1 - _r, 0, 1)[..., None] ** 1.6 * 1.25, 0, 255)
_rng = np.random.default_rng(11)
GRAIN = [_rng.normal(0, 3.2, (H_, W_, 1)).astype(np.float32) for _ in range(4)]

def ring_layer(R=520, width=150):
    S2 = 2 * R + 400
    im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S2 / 2
    d.ellipse([c - R, c - R, c + R, c + R], outline=MINT2 + (90,), width=width)
    glow = im.filter(ImageFilter.GaussianBlur(60))
    core = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); d2 = ImageDraw.Draw(core)
    d2.ellipse([c - R + width / 2 - 3, c - R + width / 2 - 3, c + R - width / 2 + 3, c + R - width / 2 + 3], outline=MINT + (150,), width=4)
    core = core.filter(ImageFilter.GaussianBlur(3))
    out = Image.alpha_composite(glow, glow); out = Image.alpha_composite(out, core)
    tint = Image.new("RGBA", (S2, S2), TEAL_G + (0,)); tint.putalpha(glow.split()[3].point(lambda v: int(v * 0.35)))
    return Image.alpha_composite(out, tint)
RING = ring_layer()
RING_S = ring_layer(300, 90)

def dark_canvas(t, ring=True, rx=540, ry=760, rs=1.0, ra=1.0, bright=1.0):
    g = DARK * bright + GRAIN[int(t * 24) % 4]
    cv = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    if ring and ra > 0.01:
        breathe = 1 + 0.02 * math.sin(t * 1.6)
        paste(cv, RING, rx, ry, rs * breathe, ra)
    return cv

def glow_text(txt, name, size, col=MINT, track=0.0, glow_col=TEAL_G, glow_a=0.55, maxw=960):
    k = ("gt", txt, name, size, col, track, glow_col, glow_a, maxw)
    if k in _tc: return _tc[k]
    base = text_img(txt, name, size, col, track, shadow=False, maxw=maxw)
    a = base.split()[3]
    gl = Image.new("RGBA", base.size, glow_col + (0,)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * glow_a)))
    out = Image.alpha_composite(gl, base); _tc[k] = out
    return out

def blur_in(cv, img, cx, cy, age, dur=0.45, s0=1.14):
    """cinematic entrance: scale down from s0 with a blurred ghost that fades"""
    if age < 0: return
    p = ease_out(age / dur)
    sc = s0 - (s0 - 1) * p
    if p < 1:
        ghost = img.filter(ImageFilter.GaussianBlur(14 * (1 - p)))
        paste(cv, ghost, cx, cy, sc * 1.03, (1 - p) * 0.6)
    paste(cv, img, cx, cy, sc, min(1, p * 1.4))

def grad_text(txt, size, c0=MINT, c1=TEAL_G, name="xbold", track=-0.03, maxw=980):
    k = ("grad", txt, size, c0, c1, name)
    if k in _tc: return _tc[k]
    base = text_img(txt, name, size, WHITE, track, shadow=False, maxw=maxw)
    a = np.asarray(base.split()[3], np.float32) / 255
    h, w = a.shape
    v = np.linspace(0, 1, h)[:, None, None]
    col = np.array(c0, np.float32) * (1 - v) + np.array(c1, np.float32) * v
    rgba = np.dstack([np.broadcast_to(col, (h, w, 3)), a[..., None] * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(base.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda q: int(q * 0.7)))
    gl = Image.new("RGBA", im.size, TEAL_G + (0,)); gl.putalpha(base.split()[3].filter(ImageFilter.GaussianBlur(26)).point(lambda q: int(q * 0.35)))
    out = Image.alpha_composite(Image.alpha_composite(sh, gl), im); _tc[k] = out
    return out

# ---------------- full-screen canvas scenes ----------------
def sc_chapter(t, c):
    cv = dark_canvas(t, rs=0.92 + 0.08 * ease_out((t - c["s"]) / 0.8), ra=ease_out((t - c["s"]) / 0.4))
    im = glow_text(c["text"], "ital", 170, MINT, 0, TEAL_G, 0.35)
    blur_in(cv, im, 540, 960, t - c["s"] - 0.05)
    return cv

DOTS = [(np.random.default_rng(k).random(), np.random.default_rng(k + 99).random()) for k in range(26)]
def sc_losing(t, c):
    cv = dark_canvas(t, ring=False)
    age = t - c["s"]
    small = text_img("Your website could be", "medium", 58, MINT2, 0, shadow=False)
    blur_in(cv, small, 540, 640, age - 0.05, 0.35, 1.06)
    # LOSING: outline first, then fills left->right on the spoken word
    big = text_img("LOSING", "xbold", 250, MINT, -0.03, shadow=False)
    outl = big.copy(); a = big.split()[3]
    edge = a.filter(ImageFilter.MaxFilter(7)); inner = a.filter(ImageFilter.MinFilter(5))
    ring_a = Image.fromarray(np.clip(np.asarray(edge, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))
    outl = Image.new("RGBA", big.size, MINT + (0,)); outl.putalpha(ring_a)
    blur_in(cv, outl, 540, 860, age - 0.2, 0.4, 1.08)
    fp = ease_io((t - wt(30)) / 0.5)
    if fp > 0:
        fill = glow_text("LOSING", "xbold", 250, MINT, -0.03, TEAL_G, 0.45)
        wcut = int(fill.width * fp)
        if wcut > 0:
            part = fill.crop((0, 0, wcut, fill.height))
            cv.alpha_composite(part, (int(540 - fill.width / 2), int(860 - fill.height / 2)))
    it = glow_text("potential customers", "ital", 104, MINT2, 0, TEAL_G, 0.25)
    blur_in(cv, it, 540, 1040, t - wt(31), 0.4, 1.08)
    # customers drifting away: particles move right & fade once "customers" is said
    d = ImageDraw.Draw(cv)
    dp = t - wt(32)
    for k, (u, v_) in enumerate(DOTS):
        x = 140 + u * 800; y = 1180 + v_ * 260
        if dp > 0:
            x += dp * (180 + 260 * u); y -= dp * 40 * (v_ - 0.5)
        al = 0.85 if dp <= 0 else max(0, 0.85 - dp * (0.35 + 0.5 * u))
        r = 7 + 5 * v_
        if al > 0.02 and age > 0.5:
            col = TEAL_G if k % 4 == 0 else MINT2
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(255 * al * min(1, (age - 0.5) / 0.3)),))
    ws = text_img("without you realizing it.", "medium", 50, MINT2, 0, shadow=False)
    blur_in(cv, ws, 540, 1560, t - wt(33), 0.35, 1.05)
    return cv

def dark_replay(cv, cx, cy, WW, WH, t, a):
    A = int(255 * a); x0, y0 = cx - WW / 2, cy - WH / 2
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x0, y0, x0 + WW, y0 + WH], 40, fill=(12, 26, 22, int(240 * a)), outline=(60, 110, 98, A), width=2)
    for k in range(3): d.ellipse([x0 + 36 + k * 30, y0 + 32, x0 + 54 + k * 30, y0 + 50], fill=(90, 130, 120, A))
    d.rounded_rectangle([x0 + 140, y0 + 22, x0 + WW - 36, y0 + 62], 20, fill=(22, 40, 35, A))
    u = text_img("yourstore.com/products/best-seller", "medium", 24, (150, 180, 170), 0, shadow=False)
    paste(cv, u, x0 + 170 + (u.width - 88) / 2, y0 + 42, 1, a)
    d.rounded_rectangle([x0 + 40, y0 + 96, x0 + WW - 40, y0 + 470], 24, fill=(20, 38, 33, A))
    d.rounded_rectangle([cx - 110, y0 + 170, cx + 110, y0 + 400], 40, fill=(34, 60, 53, A))
    d.rounded_rectangle([x0 + 40, y0 + 510, x0 + 560, y0 + 538], 10, fill=MINT2 + (int(210 * a),))
    d.rounded_rectangle([x0 + 40, y0 + 558, x0 + 420, y0 + 578], 10, fill=(120, 150, 140, A))
    pr = text_img("$49.00", "bold", 54, MINT, 0, shadow=False); paste(cv, pr, x0 + 40 + (pr.width - 88) / 2, y0 + 640, 1, a)
    bx0, by0, bx1, by1 = x0 + 40, y0 + 700, x0 + WW - 40, y0 + 790
    d.rounded_rectangle([bx0, by0, bx1, by1], 22, fill=TEAL + (A,))
    bt = text_img("Add to cart", "bold", 44, WHITE, 0, shadow=False); paste(cv, bt, (bx0 + bx1) / 2, (by0 + by1) / 2, 1, a)
    r0, r1 = wt(42), we(49)
    rp = min(1, max(0, (t - r0) / (r1 - r0)))
    py = y0 + WH - 60
    d.polygon([(x0 + 44, py - 14), (x0 + 44, py + 14), (x0 + 68, py)], fill=MINT + (A,))
    tx0, tx1 = x0 + 96, x0 + WW - 150
    d.rounded_rectangle([tx0, py - 4, tx1, py + 4], 4, fill=(40, 66, 59, A))
    if rp > 0: d.rounded_rectangle([tx0, py - 4, tx0 + (tx1 - tx0) * rp, py + 4], 4, fill=TEAL_G + (A,))
    d.ellipse([tx0 + (tx1 - tx0) * rp - 9, py - 9, tx0 + (tx1 - tx0) * rp + 9, py + 9], fill=TEAL_G + (A,))
    tm = text_img("00:{:02d}".format(int(rp * 47)), "medium", 30, (150, 180, 170), 0, shadow=False); paste(cv, tm, x0 + WW - 84, py, 1, a)
    if t > wt(48):
        hp = ease_out((t - wt(48)) / 0.5)
        heat = Image.new("RGBA", cv.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(heat)
        hx, hy = x0 + WW * 0.58, (by0 + by1) / 2
        for rr, al in ((170, 45), (110, 70), (60, 110)):
            hd.ellipse([hx - rr * hp, hy - rr * hp * 0.6, hx + rr * hp, hy + rr * hp * 0.6], fill=BLUE + (int(al * a),))
        cv.alpha_composite(heat.filter(ImageFilter.GaussianBlur(20)))
    if t > wt(49):
        lab = text_img("Rage clicks detected", "bold", 34, WHITE, 0.01, shadow=False)
        pill = round_rect_img(lab.width - 40, 66, 33, BLUE + (255,), blur_shadow=True)
        pl = pill.copy(); pl.alpha_composite(lab, ((pl.width - lab.width) // 2, (pl.height - lab.height) // 2))
        popin(cv, pl, x0 + WW * 0.58, by0 - 70, t - wt(49), 0.22, 0.7)
    path = [(0.78, 0.22), (0.40, 0.30), (0.55, 0.47), (0.30, 0.60), (0.66, 0.58), (0.50, 0.74), (0.62, 0.755), (0.46, 0.76), (0.58, 0.755)]
    def at(q):
        q = min(1, max(0, q)) * (len(path) - 1); k = min(int(q), len(path) - 2); u_ = ease_io(q - k)
        return path[k][0] + (path[k + 1][0] - path[k][0]) * u_, path[k][1] + (path[k + 1][1] - path[k][1]) * u_
    for cf in V3_CLICKS:
        ra = t - (r0 + cf * (r1 - r0))
        if 0 <= ra < 0.45:
            qx, qy = at(cf); qx, qy = x0 + qx * WW, y0 + qy * WH; rr = 12 + 46 * ease_out(ra / 0.45)
            d.ellipse([qx - rr, qy - rr, qx + rr, qy + rr], outline=TEAL_G + (int(230 * (1 - ra / 0.45) * a),), width=5)
    qx, qy = at(rp); qx, qy = x0 + qx * WW, y0 + qy * WH
    pts = [(0, 0), (0, 36), (9, 28), (15, 42), (21, 39), (15, 26), (27, 26)]
    poly = [(qx + x * 1.7, qy + y * 1.7) for x, y in pts]
    d.polygon(poly, fill=WHITE + (A,)); d.line(poly + [poly[0]], fill=(10, 20, 18, A), width=3)
V3_CLICKS = [0.42, 0.80, 0.86, 0.92]

def sc_clarity(t, c):
    age = t - c["s"]
    intro = 1.15
    if age < intro:   # chapter beat
        cv = dark_canvas(t, rs=0.92 + 0.08 * ease_out(age / 0.8), ra=min(1, 1.35 * ease_out(age / 0.35)) * (1 - ease_in((age - (intro - 0.25)) / 0.25)), bright=1.55)
        im = glow_text("Microsoft Clarity", "ital", 138, MINT, 0, TEAL_G, 0.35)
        out = ease_in((age - (intro - 0.25)) / 0.25)
        blur_in(cv, im, 540, 960 - out * 520, age - 0.05)
        return cv
    cv = dark_canvas(t, ring=True, ry=1200, rs=1.25, ra=0.6, bright=1.45)
    ttl = glow_text("Microsoft Clarity", "ital", 74, MINT, 0, TEAL_G, 0.3)
    paste(cv, ttl, 540, 440, 1, 1)
    sub = text_img("SESSION REPLAY", "medium", 30, (150, 190, 178), 0.2, shadow=False)
    paste(cv, sub, 540, 520, 1, min(1, (age - intro) / 0.3))
    pa = ease_out((age - intro) / 0.4)
    dark_replay(cv, 540, 1160 + (1 - pa) * 60, 880, 940, t, pa)
    return cv

STEPS3 = [(74, "01", "Identify", "the friction"), (76, "02", "Fix", "the problem"), (80, "03", "Measure", "the change")]
def sc_steps3(t, c):
    age = t - c["s"]
    # active beat
    k = -1
    for i, (wi, *_r) in enumerate(STEPS3):
        if t >= wt(wi) - 0.1: k = i
    if t < wt(STEPS3[0][0]) - 0.1:      # "Use these insights to..." opener
        cv = dark_canvas(t, ring=True, rs=0.9, ra=0.6 * ease_out(age / 0.4))
        im = glow_text("insights", "ital", 170, MINT, 0, TEAL_G, 0.35)
        sm = text_img("Use these", "medium", 58, MINT2, 0, shadow=False)
        blur_in(cv, sm, 540, 820, age - 0.05, 0.35, 1.05)
        blur_in(cv, im, 540, 960, t - wt(72), 0.45)
        return cv
    if t >= wt(84):                      # conversion payoff
        ca = t - wt(84)
        cv = dark_canvas(t, ring=False)
        lab = glow_text("conversion", "ital", 150, MINT, 0, TEAL_G, 0.35)
        sm = text_img("improve your", "medium", 56, MINT2, 0, shadow=False)
        blur_in(cv, sm, 540, 640, ca, 0.3, 1.05)
        blur_in(cv, lab, 540, 780, ca, 0.4)
        # glowing blue rising line
        pts = [(0, 0.12), (0.18, 0.2), (0.36, 0.18), (0.55, 0.42), (0.72, 0.5), (1, 0.92)]
        prog = min(1, max(0.02, ca / 0.9))
        gl = Image.new("RGBA", cv.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
        mini_chart_v3(gd, 160, 1000, 760, 440, pts, BLUE, 1.0, prog, 14)
        cv.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
        mini_chart_v3(ImageDraw.Draw(cv), 160, 1000, 760, 440, pts, (120, 160, 255), 1.0, prog, 7)
        return cv
    wi, num, word, rest = STEPS3[k]
    ba = t - wt(wi)
    cv = dark_canvas(t, rs=0.9 + 0.1 * ease_out(ba / 0.6), ra=1)
    n = glow_text(num, "medium", 60, TEAL_G, 0.2, TEAL_G, 0.4)
    blur_in(cv, n, 540, 760, ba + 0.05, 0.3, 1.1)
    im = glow_text(word, "ital", 190, MINT, 0, TEAL_G, 0.35)
    blur_in(cv, im, 540, 940, ba + 0.05)
    r_ = text_img(rest, "medium", 58, MINT2, 0, shadow=False)
    blur_in(cv, r_, 540, 1100, ba - 0.15, 0.3, 1.05)
    # progress dots
    d = ImageDraw.Draw(cv)
    for i in range(3):
        x = 540 + (i - 1) * 46
        on = i <= k
        d.ellipse([x - 9, 1260 - 9, x + 9, 1260 + 9], fill=(TEAL_G if on else (50, 80, 72)) + (255,))
    return cv

def mini_chart_v3(d, x0, y0, w, h, pts, col, a, prog=1.0, width=6):
    n = max(2, int(len(pts) * prog + 0.999))
    P = [(x0 + px * w, y0 + (1 - py) * h) for px, py in pts[:n]]
    if prog < 1 and n >= 2:
        f = len(pts) * prog - (n - 1)
        (xa, ya), (xb, yb) = P[-2], P[-1]
        P[-1] = (xa + (xb - xa) * max(0, f), ya + (yb - ya) * max(0, f))
    d.line(P, fill=col + (int(255 * a),), width=width, joint="curve")
    xe, ye = P[-1]; r = width * 1.6
    d.ellipse([xe - r, ye - r, xe + r, ye + r], fill=(255, 255, 255, int(255 * a)))

SCENE_FN = {"chapter": sc_chapter, "losing": sc_losing, "clarity": sc_clarity, "steps3": sc_steps3}

# ---------------- footage overlays (layer 2) ----------------
def headline(cv, t, lines, t_in, t_out):
    """big top headline over footage (reference: bold title at top)"""
    a_out = 1 - ease_in((t - (t_out - 0.2)) / 0.2)
    for txt, kind, size, tt, y in lines:
        if t < tt: continue
        im = grad_text(txt, size) if kind == "grad" else glow_text(txt, "ital", size, MINT, 0, (0, 0, 0), 0.6)
        age = t - tt
        if a_out < 1:
            paste(cv, im, 540, y, 1, a_out)
        else:
            blur_in(cv, im, 540, y, age, 0.4, 1.12)

def tile(name, glyph, size=230):
    k = ("tile", name)
    if k in _tc: return _tc[k]
    S2 = size + 120
    im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = 60
    gl = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle([o, o, o + size, o + size], 56, fill=TEAL_G + (150,))
    gl = gl.filter(ImageFilter.GaussianBlur(28))
    im = Image.alpha_composite(im, gl); d = ImageDraw.Draw(im)
    d.rounded_rectangle([o, o, o + size, o + size], 56, fill=(14, 30, 26, 255), outline=(120, 200, 180, 200), width=3)
    sheen = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sheen)
    sd.rounded_rectangle([o + 6, o + 6, o + size - 6, o + size * 0.45], 50, fill=(255, 255, 255, 22))
    im = Image.alpha_composite(im, sheen)
    g = glow_text(glyph, "xbold", 120 if len(glyph) == 1 else 80, MINT, -0.02, TEAL_G, 0.5)
    im.alpha_composite(g, (int(S2 / 2 - g.width / 2), int(S2 / 2 - g.height / 2)))
    _tc[k] = im
    return im

TILES = [(22, "Shopify", "S"), (23, "WordPress", "W"), (25, "WooCommerce", "Woo")]
def tiles(cv, t):
    cur = None
    for wi, name, gl in TILES:
        if t >= wt(wi) - 0.05: cur = (wi, name, gl)
    if cur is None or t > we(25) + 0.6: return
    wi, name, gl = cur
    age = t - wt(wi) + 0.05
    a_out = 1 - ease_in((t - (we(25) + 0.35)) / 0.25)
    p = ease_out(age / 0.35)
    rot = (1 - p) * -18 + math.sin(t * 2.2) * 3
    bob = math.sin(t * 2.6) * 8
    im = tile(name, gl)
    paste(cv, im, 790, 470 + bob + (1 - p) * 40, 0.7 + 0.3 * back_out(min(1, age / 0.35), 1.5), min(1, p * 1.6) * a_out, rot=rot)
    lab = text_img(name, "semi", 46, MINT, 0, shadow=True)
    paste(cv, lab, 790, 660 + bob, 1, p * a_out)

def dark_panel(cv, t, t0, t1):
    a = min(ease_out((t - t0) / 0.35), 1 - ease_in((t - (t1 - 0.25)) / 0.25))
    if a <= 0.01: return
    cx, cy = 540, 1500 + (1 - ease_out((t - t0) / 0.35)) * 50
    WW, HH = 900, 470
    glow = Image.new("RGBA", cv.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - 560, cy - 240, cx - 40, cy + 280], fill=TEAL_G + (int(150 * a),))
    gd.ellipse([cx + 20, cy - 220, cx + 560, cy + 300], fill=BLUE + (int(140 * a),))
    cv.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([cx - WW / 2, cy - HH / 2, cx + WW / 2, cy + HH / 2], 40, fill=(10, 22, 19, int(236 * a)), outline=(90, 150, 135, int(200 * a)), width=2)
    tt = text_img("WHERE SHOPPERS STRUGGLE", "semi", 32, (150, 190, 178), 0.16, shadow=False)
    paste(cv, tt, cx, cy - 178, 1, a)
    for k, (wi, lab) in enumerate(V3_FRIC):
        ia = t - wt(wi)
        if ia < 0: continue
        q = ease_out(ia / 0.3)
        y = cy - 86 + k * 112 + (1 - q) * 16
        d.rounded_rectangle([cx - 410, y - 46, cx + 410, y + 46], 24, fill=(22, 40, 35, int(255 * a * q)), outline=(50, 80, 72, int(255 * a * q)), width=2)
        cs = back_out((ia - 0.05) / 0.22, 1.6) if ia > 0.05 else 0.01
        xi = x_icon_dark(ease_out((ia - 0.1) / 0.28), 64, max(0.01, cs))
        paste(cv, xi, cx - 360, y, 1, a * q)
        im = text_img(lab, "bold", 46, MINT, -0.01, shadow=False, maxw=640)
        paste(cv, im, cx - 310 + (im.width - 88) / 2, y, 1, a * q)
V3_FRIC = [(52, "Missing “Add to Cart”"), (58, "Lost on product pages"), (64, "Abandoning checkout")]

def x_icon_dark(p, size=64, sc=1.0):
    S4 = size * 4
    im = Image.new("RGBA", (S4, S4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([4, 4, S4 - 4, S4 - 4], fill=(255, 112, 102, 255))
    a, b = S4 * 0.32, S4 * 0.68; w = int(S4 * 0.09)
    p1 = min(1, p * 2); p2 = max(0, p * 2 - 1)
    if p1 > 0.02: d.line([(a, a), (a + (b - a) * p1, a + (b - a) * p1)], fill=(255, 255, 255, 255), width=w)
    if p2 > 0.02: d.line([(b, a), (b - (b - a) * p2, a + (b - a) * p2)], fill=(255, 255, 255, 255), width=w)
    return im.resize((max(1, int(size * sc)), max(1, int(size * sc))), Image.LANCZOS)

def bookmark(cv, t):
    t0 = wt(98) + 0.4
    if t < t0: return
    age = t - t0
    p = ease_out(age / 0.4)
    k = ("bm",)
    if k not in _tc:
        S2 = 360; im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        poly = [(110, 60), (250, 60), (250, 300), (180, 245), (110, 300)]
        gl = Image.new("RGBA", (S2, S2), (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon(poly, fill=TEAL_G + (220,))
        im = Image.alpha_composite(im, gl.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(im); d.polygon(poly, fill=TEAL + (255,)); d.line(poly + [poly[0]], fill=(160, 240, 225, 255), width=4)
        _tc[k] = im
    bob = math.sin(t * 2.4) * 8
    paste(cv, _tc[k], 820, 470 + bob + (1 - p) * 60, 0.75 + 0.25 * back_out(min(1, age / 0.4), 1.5), min(1, p * 1.5))
    lab = text_img("Save & follow", "semi", 44, MINT, 0, shadow=True)
    paste(cv, lab, 820, 690 + bob, 1, ease_out((age - 0.2) / 0.3))

def overlays(cv, t):
    if t < we(10) + 0.4:
        headline(cv, t, [("not getting enough", "ital", 88, wt(7), 175), ("SALES?", "grad", 190, wt(10), 315)], 0, we(10) + 0.4)
    if wt(16) - 0.1 <= t < we(17) + 0.45:
        headline(cv, t, [("Before spending more,", "ital", 76, wt(11), 165), ("watch this.", "grad", 170, wt(16), 300)], 0, we(17) + 0.45)
    if wt(28) - 0.1 <= t < we(36) + 0.35:
        headline(cv, t, [("your website could be", "ital", 76, wt(28), 165), ("LOSING", "grad", 190, wt(30), 300)], 0, we(36) + 0.35)
    tiles(cv, t)
    dark_panel(cv, t, wt(50) - 0.1, we(69) + 0.3)
    if wt(86) - 0.1 <= t < we(97) + 0.4:
        a_strike = ease_io((t - wt(88)) / 0.35)
        if t < wt(94):
            im = grad_text("Stop guessing.", 150, MINT, MINT2)
            age = t - wt(86) + 0.05
            blur_in(cv, im, 540, 300, age, 0.4, 1.12)
            if a_strike > 0:
                d = ImageDraw.Draw(cv); w_ = (im.width - 88) * a_strike
                d.rounded_rectangle([540 - (im.width - 88) / 2, 300 - 6, 540 - (im.width - 88) / 2 + w_, 300 + 8], 6, fill=(255, 112, 102, 255))
        else:
            a_out = 1 - ease_in((t - (we(97) + 0.2)) / 0.2)
            im1 = glow_text("Start", "ital", 110, MINT, 0, (0, 0, 0), 0.6)
            im2 = grad_text("understanding.", 150)
            blur_in(cv, im1, 540, 230, t - wt(94), 0.35, 1.1) if a_out >= 1 else paste(cv, im1, 540, 230, 1, a_out)
            blur_in(cv, im2, 540, 360, t - wt(95), 0.4, 1.12) if a_out >= 1 else paste(cv, im2, 540, 360, 1, a_out)
    bookmark(cv, t)

def CYt(t):
    return 1150 if wt(50) - 0.2 <= t < we(69) + 0.4 else CY

# ---------------- compositor with zoom-blur transitions ----------------
TR = 0.22
LIFT_LUT = np.clip(255 * (np.arange(256) / 255) ** (1 / 1.16) * 1.04, 0, 255).astype(np.uint8)
def lift_w(t):
    a, b = wt(18) - 0.35, we(36) + 0.2          # scenes 3-4
    return min(ease_io((t - a) / 0.35), 1 - ease_io((t - b) / 0.35)) if a - 0.01 <= t <= b + 0.36 else 0.0
def footage_layer(fr, t):
    w = lift_w(t)
    if w > 0.01:
        fr = (fr * (1 - w) + cv2.LUT(fr, LIFT_LUT) * w).astype(np.uint8)
    cv = Image.fromarray(camera(fr, t)).convert("RGBA")
    overlays(cv, t)
    caption(cv, t)
    return cv

def zoom_img(arr, z, blur=0):
    if z != 1:
        M = np.float32([[z, 0, 540 * (1 - z)], [0, z, 960 * (1 - z)]])
        arr = cv2.warpAffine(arr, M, (W_, H_), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if blur > 0.5:
        arr = cv2.GaussianBlur(arr, (0, 0), blur)
    return arr

def render(fr, t):
    c = card_at(t)
    if not c:
        out = np.asarray(footage_layer(fr, t).convert("RGB"))
        for cc in CARDS:          # zoom-blur out of a card back to footage
            u = t - cc["e"]
            if 0 <= u < TR:
                p = u / TR
                out = zoom_img(out, 1.12 - 0.12 * ease_out(p), 10 * (1 - p))
        return out
    scene = np.asarray(SCENE_FN[c["kind"]](t, c).convert("RGB"))
    u = t - c["s"]
    if u < TR:                    # footage punches in + blurs, canvas lands
        p = u / TR
        if p < 0.5:
            f = np.asarray(footage_layer(fr, t).convert("RGB"))
            return zoom_img(f, 1 + 0.18 * ease_in(p * 2), 12 * p * 2)
        return zoom_img(scene, 1.12 - 0.12 * ease_out((p - 0.5) * 2), 10 * (1 - (p - 0.5) * 2))
    v = c["e"] - t
    if v < TR / 2:
        return zoom_img(scene, 1 + 0.15 * ease_in(1 - v / (TR / 2)), 10 * (1 - v / (TR / 2)))
    return scene

def plan_sfx():
    EV.clear()
    for k in KW:
        if in_card_word(k): continue
        sfx(wt(k) - 0.10, "swish", 0.09); sfx(wt(k), "pop", 0.08)
    for i in ITAL: sfx(wt(i) - 0.12, "swish", 0.09)
    for i, s_ in ZOOM.items(): sfx(wt(i) - 0.02, "impact", 0.10 + s_)
    # headline beats
    sfx(wt(7) - 0.1, "swish", 0.09); sfx(wt(10), "impact", 0.20); sfx(wt(10), "pop", 0.10)
    for wi, _, _ in TILES: sfx(wt(wi) - 0.05, "whoosh", 0.10, 0.5); sfx(wt(wi), "bubble", 0.10, 0.5)
    sfx(wt(50) - 0.15, "whoosh", 0.12)
    for wi, _ in V3_FRIC: sfx(wt(wi), "click", 0.12); sfx(wt(wi) + 0.05, "impact", 0.07)
    sfx(wt(86) - 0.1, "swish", 0.10); sfx(wt(88), "glitch", 0.06); sfx(wt(94), "whoosh", 0.10); sfx(wt(95), "ding", 0.06)
    sfx(wt(98) + 0.4, "bubble", 0.12); sfx(wt(98) + 0.45, "ding", 0.05)
    # canvas scenes: whoosh + low boom on every landing
    for c in CARDS:
        sfx(c["s"] - 0.6, "riser", 0.06)
        sfx(c["s"] - 0.05, "whoosh", 0.18); sfx(c["s"] + 0.1, "impact", 0.22)
        sfx(c["e"] - 0.1, "whoosh_up", 0.12)
    sfx(wt(16) - 0.1, "swish", 0.10); sfx(wt(16), "impact", 0.12)
    sfx(wt(28) - 0.1, "swish", 0.09); sfx(wt(30), "impact", 0.18)
    sfx(CARDS[0]["s"] + 1.1, "whoosh", 0.12)
    r0, r1 = wt(42), we(49)
    for cf in V3_CLICKS: sfx(r0 + cf * (r1 - r0), "click", 0.17)
    sfx(wt(48), "riser", 0.05); sfx(wt(49), "pop", 0.13)
    sfx(wt(72), "impact", 0.12)
    for wi, *_r in STEPS3: sfx(wt(wi) - 0.05, "whoosh", 0.10); sfx(wt(wi) + 0.05, "impact", 0.16)
    sfx(wt(84), "riser", 0.05); sfx(wt(84) + 0.9, "ding", 0.08)
    return EV
'''
rep("def frames(t0=0.0, t1=None):", V3 + "\ndef frames(t0=0.0, t1=None):")
# caption y uses CYt
rep('''        draw_line(canvas, u["ws"], t, CY, "medium", 72, ua)''', '''        draw_line(canvas, u["ws"], t, CYt(t), "medium", 64, ua)''')
open("edit_p2.py", "w").write(s)
print("v3 engine written")
