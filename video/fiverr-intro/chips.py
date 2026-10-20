"""Animated tool chips synced to speech (frosted glass chip + animated glyph)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def _ease(t): t = min(1, max(0, t)); return 1 - (1 - t) ** 3

def glyph(kind, p, s=84):
    """p = seconds since the chip appeared. White line glyph on transparent."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255); lw = 5
    e = _ease(p / 0.6)
    loop = (p % 1.2) / 1.2
    if kind == "ga4":
        for i, hh in enumerate([0.32, 0.52, 0.74]):
            x = 16 + i * 20; h = hh * s * _ease((p - i * 0.12) / 0.5)
            d.rounded_rectangle((x, s - 14 - h, x + 13, s - 14), 6, fill=c)
    elif kind == "pixel":
        for i in range(3):
            for j in range(3):
                x, y = 22 + i * 20, 22 + j * 20
                r = 6 if (i, j) == (1, 1) else 3
                d.ellipse((x - r, y - r, x + r, y + r), fill=c if (i, j) == (1, 1) else (255, 255, 255, 140))
        r = 8 + 26 * loop
        d.ellipse((42 - r, 42 - r, 42 + r, 42 + r), outline=(255, 255, 255, int(255 * (1 - loop))), width=3)
    elif kind == "capi":
        for k in range(3): d.rounded_rectangle((8, 20 + k * 16, 30, 32 + k * 16), 3, outline=c, width=3)
        d.ellipse((54, 30, 78, 54), outline=c, width=3); d.ellipse((46, 38, 64, 56), outline=c, width=3)
        d.line([(32, 42), (50, 42)], fill=(255, 255, 255, 150), width=2)
        x = 32 + 18 * loop; d.ellipse((x - 4, 38, x + 4, 46), fill=c)
    elif kind == "adsconv":
        for r in (30, 19):
            d.ellipse((42 - r, 42 - r, 42 + r, 42 + r), outline=c, width=4)
        k = _ease((p - 0.15) / 0.45)
        pts = [(30, 43), (39, 52), (56, 33)]
        if k > 0:
            if k < 0.4: d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * k / 0.4, pts[0][1] + (pts[1][1] - pts[0][1]) * k / 0.4)], fill=c, width=6)
            else:
                q = (k - 0.4) / 0.6
                d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)], fill=c, width=6, joint="curve")
    elif kind in ("T", "S", "X", "in"):
        from render2 import mont
        f = mont(900, 40 if kind != "in" else 36)
        d.text((s / 2, s / 2 + 1), kind, font=f, fill=c, anchor="mm")
        r = 30 + 10 * loop
        d.rounded_rectangle((42 - r, 42 - r, 42 + r, 42 + r), 14, outline=(255, 255, 255, int(160 * (1 - loop))), width=2)
    elif kind == "clarity":
        for k in range(3):
            q = (loop + k / 3) % 1; r = 6 + 28 * q
            d.ellipse((34 - r, 34 - r, 34 + r, 34 + r), outline=(255, 255, 255, int(220 * (1 - q))), width=3)
        d.polygon([(44, 40), (44, 72), (52, 63), (60, 76), (66, 73), (58, 60), (70, 59)], fill=c)
    elif kind == "gtm":
        a = math.radians(-35 * (1 - e))
        pts = [(16, 16), (48, 16), (72, 42), (48, 68), (16, 68)]
        cx, cy = 42, 42
        rp = [(cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a), cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) for x, y in pts]
        d.polygon(rp, outline=c, width=5)
        hx, hy = cx + (28 - cx) * math.cos(a) - (42 - cy) * math.sin(a), cy + (28 - cx) * math.sin(a) + (42 - cy) * math.cos(a)
        d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=c)
    elif kind == "server":
        for k in range(3):
            y = 14 + k * 21
            d.rounded_rectangle((14, y, 70, y + 16), 5, outline=c, width=4)
            on = int((p * 3 + k) % 3 == 0)
            d.ellipse((56, y + 5, 62, y + 11), fill=c if on else (255, 255, 255, 110))
            d.line([(22, y + 8), (40, y + 8)], fill=(255, 255, 255, 170), width=3)
    elif kind in ("gads", "mads"):
        pts = [(12, 64), (32, 46), (46, 54), (72, 22)]
        k = _ease(p / 0.7) * 3
        seg = []
        for i in range(3):
            if k <= i: break
            q = min(1, k - i); a, b = pts[i], pts[i + 1]
            seg.append((a, (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)))
        for a, b in seg: d.line([a, b], fill=c, width=6)
        if k >= 3: d.polygon([(74, 18), (60, 20), (72, 32)], fill=c)
    elif kind == "issue":
        k = _ease((p - 0.55) / 0.3)
        if k < 1:
            a = int(255 * (1 - k))
            d.line([(42, 18), (42, 50)], fill=(255, 255, 255, a), width=7); d.ellipse((37, 58, 47, 68), fill=(255, 255, 255, a))
        if k > 0:
            a = int(255 * k); d.line([(24, 44), (37, 57), (61, 30)], fill=(255, 255, 255, a), width=7, joint="curve")
    elif kind == "mismatch":
        k = _ease((p - 0.2) / 0.6)
        h1, h2 = 52, 52 - 26 * (1 - k)
        d.rounded_rectangle((18, 72 - h1, 36, 72), 5, fill=c); d.rounded_rectangle((48, 72 - h2, 66, 72), 5, fill=(255, 255, 255, 170 + int(85 * k)))
        if k > 0.95: d.line([(14, 16), (70, 16)], fill=c, width=3)
    elif kind == "dedup":
        k = _ease((p - 0.2) / 0.6)
        off = 16 * (1 - k)
        d.rounded_rectangle((20 - off, 26 - off * .3, 52 - off, 58 - off * .3), 8, outline=(255, 255, 255, int(255 * (1 - k))), width=4)
        d.rounded_rectangle((32 + off * .3, 26 + off * .3, 64 + off * .3, 58 + off * .3), 8, outline=c, width=5)
        if k > 0.9: d.line([(39, 42), (45, 48), (57, 36)], fill=c, width=4)
    glow = im.filter(ImageFilter.GaussianBlur(4))
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(im)
    return out

class Chips:
    def __init__(self, mont, texture, W):
        self.mont, self.W = mont, W
        self.CW, self.CH, self.GAP = 410, 104, 14
        # (group_end, side, x_override, y_top, [(t_in, kind, title, sub)])
        self.groups = [
            (18.66, "R", None, 370, [(14.48, "issue", "Tracking issues", "Found & fixed"),
                                     (15.62, "mismatch", "Conversions", "Platforms matched"),
                                     (17.32, "dedup", "Duplicate events", "Deduplicated")]),
            (25.18, "L", None, 250, [(21.08, "ga4", "GA4", "Google Analytics"),
                                     (22.06, "pixel", "Meta Pixel", "Browser events"),
                                     (22.42, "capi", "Conversion API", "Server events"),
                                     (23.30, "adsconv", "Google Ads", "Conversion tracking")]),
            (29.36, "R", None, 196, [(25.24, "T", "TikTok", "Pixel + Events API"),
                                     (25.70, "S", "Snapchat", "Pixel + Conversions API"),
                                     (26.30, "X", "X (Twitter)", "Pixel tracking"),
                                     (26.58, "in", "LinkedIn", "Insight Tag"),
                                     (28.28, "clarity", "Microsoft Clarity", "Heatmaps & recordings")]),
            (32.92, "L", None, 330, [(30.30, "gtm", "Google Tag Manager", "Tag management"),
                                     (31.22, "server", "Server-side", "First-party tracking")]),
            (35.50, "R", None, 360, [(32.94, "gads", "Google Ads", "Campaign optimization"),
                                     (34.10, "mads", "Meta Ads", "Campaign optimization")]),
        ]
        self.tile = texture(84, 84)
        m = Image.new("L", (84, 84), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 83, 83), 22, fill=255)
        self.tmask = m
        self.base = {}
        for g in self.groups:
            for _, k, title, sub in g[4]: self.base[(title, sub)] = self._chip(title, sub)

    def _chip(self, title, sub):
        CW, CH = self.CW, self.CH
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, CW - 1, CH - 1), 26, fill=(14, 18, 36, 150), outline=(255, 255, 255, 80), width=2)
        tile = Image.new("RGBA", (84, 84), (0, 0, 0, 0)); tile.paste(self.tile, (0, 0), self.tmask)
        im.alpha_composite(tile, (10, 10))
        ft = self.mont(800, 30)
        while ft.getlength(title) > CW - 126: ft = self.mont(800, ft.size - 1)
        d.text((112, 20), title, font=ft, fill=(255, 255, 255, 255))
        d.text((113, 60), sub, font=self.mont(600, 19), fill=(225, 232, 255, 200))
        return im

    def draw(self, layer, t, framing_is_wide):
        for end, side, xo, y0, items in self.groups:
            if not (items[0][0] - 0.05 <= t <= end + 0.3): continue
            gout = 1 - _ease((t - end) / 0.3) if t > end else 1
            for i, (t0, kind, title, sub) in enumerate(items):
                if t < t0: continue
                p = t - t0
                k = _ease(p / 0.35); a = min(1, p / 0.2) * gout
                if a <= 0.01: continue
                im = self.base[(title, sub)].copy()
                im.alpha_composite(glyph(kind, p), (10, 10))
                if k < 1:
                    s = 0.9 + 0.1 * k
                    im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
                if a < 0.999:
                    arr = np.array(im); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); im = Image.fromarray(arr)
                slide = int(40 * (1 - k))
                if side == "L": x = 56 - slide
                else: x = self.W - 56 - self.CW + slide
                x += (self.CW - im.width) // 2
                y = y0 + i * (self.CH + self.GAP) + (self.CH - im.height) // 2
                layer.alpha_composite(im, (x, y))
            return True
        return False
