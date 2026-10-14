from PIL import Image, ImageDraw, ImageFont

F = "fonts/"
INK = (23, 43, 38); SUB = (86, 108, 101); TEAL = (13, 148, 136); BG = (246, 251, 249); LINE = (213, 232, 224)
def f(n, s): return ImageFont.truetype(F + n, s)
B, SB, R = "Poppins-Bold.ttf", "Poppins-SemiBold.ttf", "Poppins-Regular.ttf"

SC = [
    ("0.0–3.6s", "Hook", "“Running ads for your e-commerce store but not getting enough SALES?”",
     "SALES (bold, scale-in)", "Store-sales card, blue line drops + down-arrow badge (top right)", "Punch-in on SALES", "Swish + pop, soft impact", 3.3),
    ("3.7–6.0s", "Watch this", "“Before spending more on ads, watch this.”",
     "this. (serif italic)", "—", "Small punch-in", "Swish", 5.9),
    ("6.2–9.3s", "Platforms", "“Shopify, WordPress, or WooCommerce”",
     "Word-by-word white captions", "3 platform chips pop in, one per name (top right)", "—", "Click per chip", 9.0),
    ("9.3–13.3s", "The problem", "“…could be LOSING potential CUSTOMERS…”",
     "LOSING · CUSTOMERS", "Visitors card: 2 of 3 people fade and drift away", "Punch-in on CUSTOMERS", "Pop, soft impact", 11.3),
    ("13.8–19.7s", "The tool", "“Microsoft Clarity helps you replay visitor sessions…”",
     "Captions move up under chin", "Session-replay window: cursor moves, clicks, ‘Rage clicks detected’ + heat glow", "—", "Clicks synced to cursor, riser", 19.6),
    ("20.1–28.6s", "Friction points", "“Missing your add to cart button, product pages, checkout?”",
     "Captions above card", "‘Where shoppers struggle’ card: 3 X rows draw on as spoken", "—", "Click + soft thud per row", 26.0),
    ("28.8–36.1s", "The fix", "“Identify friction, fix the problem, measure… conversion.”",
     "INSIGHTS (bold)", "3-step card: each step ticks teal as spoken + blue conversion chart rises", "Punch-in on INSIGHTS", "Click + pop per step, ding", 35.9),
    ("36.3–41.0s", "Mindset shift", "“Stop GUESSING… Start UNDERSTANDING their behavior.”",
     "GUESSING · UNDERSTANDING", "Badge flips from \u2018? Guessing\u2019 to \u2018Insight\u2019 with a teal tick (top right)", "Punch-ins on both words", "Pop, ding on flip", 40.0),
    ("41.3–45.7s", "Ending clip", "Side-angle clip: “Follow me for actionable analytics…”",
     "Follow (italic) · ANALYTICS · OPTIMIZATION", "‘+ Follow’ button pops in and gets tapped", "—", "Tap click, music fades out", 44.6),
]

FW, FH = 360, 640
COLS, PAD, TXT = 3, 44, 430
CW = FW + PAD
W = COLS * CW + PAD
rows = (len(SC) + COLS - 1) // COLS
H = 280 + rows * (FH + TXT + PAD) + 120
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
d.text((PAD, 60), "Storyboard: Microsoft Clarity for e-commerce", font=f(B, 46), fill=INK)
d.text((PAD, 124), "Draft for approval  ·  45.7s  ·  9:16",
       font=f(R, 24), fill=SUB)
d.text((PAD, 160), "Layer 1: footage + light background blur   ·   Layer 2: pop-ups   ·   Layer 3: captions", font=f(R, 22), fill=SUB)
d.rounded_rectangle([PAD, 204, PAD + 120, 210], 3, fill=TEAL)

def wrap(text, fo, w):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if d.textlength(t, font=fo) <= w: line = t
        else: out.append(line); line = word
    if line: out.append(line)
    return out

for n, (tm, title, said, cap, pop, zoom, sfx, ts) in enumerate(SC):
    r, c = divmod(n, COLS)
    x = PAD + c * CW; y = 250 + r * (FH + TXT + PAD)
    fr = Image.open(f"pv_{ts}.png").convert("RGB").resize((FW, FH))
    d.rounded_rectangle([x - 2, y - 2, x + FW + 2, y + FH + 2], 18, fill=LINE)
    m = Image.new("L", (FW, FH), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, FW - 1, FH - 1], 16, fill=255)
    img.paste(fr, (x, y), m)
    d.ellipse([x + 14, y + 14, x + 62, y + 62], fill=TEAL)
    d.text((x + 38, y + 38), str(n + 1), font=f(B, 26), fill=(255, 255, 255), anchor="mm")
    ty = y + FH + 18
    d.text((x, ty), title, font=f(B, 28), fill=INK)
    d.text((x + FW, ty + 6), tm, font=f(SB, 20), fill=TEAL, anchor="ra")
    ty += 46
    for ln in wrap(said, f(R, 19), FW)[:3]:
        d.text((x, ty), ln, font=f(R, 19), fill=SUB); ty += 26
    ty += 8
    for lab, val in (("Text", cap), ("Pop-up", pop), ("Zoom", zoom), ("Sound", sfx)):
        d.text((x, ty), lab, font=f(B, 19), fill=INK)
        lines = wrap(val, f(R, 19), FW - 78)
        for ln in lines[:3]:
            d.text((x + 78, ty), ln, font=f(R, 19), fill=INK); ty += 26
        ty += 6
d.text((PAD, H - 110), "Throughout: subtle music bed ducked under voice  ·  jump cuts on pauses", font=f(R, 22), fill=SUB)
d.text((PAD, H - 74), "Brand palette: #F6FBF9 · #172B26 · #0D9488 (teal) · #2563EB (blue, data only)", font=f(R, 22), fill=SUB)
img.save("Storyboard_Clarity.png", optimize=True)
img.save("Storyboard_Clarity.pdf", resolution=150)
print(img.size)
