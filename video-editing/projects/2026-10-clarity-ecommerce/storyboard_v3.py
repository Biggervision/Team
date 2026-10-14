from PIL import Image, ImageDraw, ImageFont

F = "fonts/"
INK = (246, 251, 249); SUB = (150, 185, 175); TEAL = (45, 212, 191); BG = (11, 22, 19); LINE = (40, 70, 62)
def f(n, s): return ImageFont.truetype(F + n, s)
B, SB, R = "Poppins-Bold.ttf", "Poppins-SemiBold.ttf", "Poppins-Regular.ttf"

SC = [
    ("0.0–3.6s", "Hook · footage", "\u201cRunning ads… but not getting enough sales?\u201d",
     "Top headline: italic \u2018not getting enough\u2019 + gradient SALES? (blur-in)", "Punch-in on SALES", "Swish, impact on SALES", 3.4),
    ("3.6–5.9s", "Watch this · footage", "\u201cBefore spending more on ads, watch this.\u201d",
     "Top headline: italic \u2018Before spending more,\u2019 + gradient \u2018watch this.\u2019", "Punch-in on \u2018this\u2019", "Swish, soft impact", 5.8),
    ("6.0–9.2s", "Platforms · footage", "\u201cShopify, WordPress, or WooCommerce\u201d",
     "3D glowing tile beside your head, swaps per platform (S / W / Woo)", "—", "Whoosh + bubble per tile", 9.0),
    ("9.2–13.3s", "Problem · footage", "\u201c…could be losing potential customers…\u201d",
     "Top headline: italic \u2018your website could be\u2019 + gradient LOSING", "Punch-in on LOSING", "Swish, impact on LOSING", 10.9),
    ("13.8–15.0s", "Tool intro · canvas", "\u201cMicrosoft Clarity…\u201d",
     "Ring chapter card \u2018Microsoft Clarity\u2019, lifts away", "Zoom-blur in", "Whoosh, low boom", 14.4),
    ("15.0–19.7s", "Session replay · canvas", "\u201c…replay visitor sessions, where shoppers struggle.\u201d",
     "Dark-mode store page: cursor, clicks, blue heat + \u2018Rage clicks detected\u2019", "—", "Clicks synced, riser, pop", 18.8),
    ("20.1–28.6s", "Friction · footage", "\u201cMissing add to cart, product pages, checkout?\u201d",
     "Floating dark panel with teal/blue glow; 3 X rows draw on", "Small punch-in", "Click + soft thud per row", 25.8),
    ("28.7–35.1s", "The fix · canvas", "\u201cIdentify friction, fix the problem, measure…\u201d",
     "insights, then 01 Identify, 02 Fix, 03 Measure chapter beats + progress dots", "Zoom-blur in", "Whoosh + boom per step", 29.9),
    ("35.1–36.1s", "Payoff · canvas", "\u201c…improve conversion.\u201d",
     "Italic \u2018conversion\u2019 + glowing blue rising line", "Zoom-blur out", "Riser, ding", 35.9),
    ("36.1–38.9s", "Stop guessing · footage", "\u201cStop guessing why visitors are not buying.\u201d",
     "Top headline \u2018Stop guessing.\u2019 gets struck through", "Punch-in", "Swish, glitch tick", 37.2),
    ("38.9–41.1s", "Understand · footage", "\u201cStart understanding their behavior.\u201d",
     "\u2018Start\u2019 + gradient \u2018understanding.\u2019", "Punch-in", "Whoosh, ding", 40.2),
    ("41.3–45.7s", "Ending clip", "\u201cFollow me for actionable analytics…\u201d",
     "Glowing bookmark + \u2018Save & follow\u2019; ANALYTICS / OPTIMIZATION captions", "—", "Bubble, ding, music fade", 44.5),
]
FW, FH = 360, 640
COLS, PAD, TXT = 4, 40, 330
CW = FW + PAD
W = COLS * CW + PAD
rows = (len(SC) + COLS - 1) // COLS
H = 280 + rows * (FH + TXT + PAD) + 120
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
d.text((PAD, 60), "Storyboard v3: Microsoft Clarity for e-commerce", font=f(B, 46), fill=INK)
d.text((PAD, 124), "Revised draft for approval  ·  45.7s  ·  9:16  ·  dark cinematic direction  ·  fairer skin + iPhone Vivid look",
       font=f(R, 24), fill=SUB)
d.text((PAD, 160), "Face on camera in 8 scenes, full-screen canvases in 4 (2 topics)  ·  light background blur on footage  ·  3 layers: footage / graphics / captions", font=f(R, 22), fill=SUB)
d.rounded_rectangle([PAD, 204, PAD + 120, 210], 3, fill=TEAL)

def wrap(text, fo, w):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if d.textlength(t, font=fo) <= w: line = t
        else: out.append(line); line = word
    if line: out.append(line)
    return out

for n, (tm, title, said, vis, zoom, sfx, ts) in enumerate(SC):
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
    ty += 34; d.text((x, ty), tm, font=f(SB, 20), fill=TEAL)
    ty += 46
    for ln in wrap(said, f(R, 19), FW)[:3]:
        d.text((x, ty), ln, font=f(R, 19), fill=SUB); ty += 26
    ty += 8
    for lab, val in (("Visual", vis), ("Motion", zoom), ("Sound", sfx)):
        d.text((x, ty), lab, font=f(B, 19), fill=INK)
        lines = wrap(val, f(R, 19), FW - 82)
        for ln in lines[:3]:
            d.text((x + 82, ty), ln, font=f(R, 19), fill=INK); ty += 26
        ty += 6
d.text((PAD, H - 110), "Throughout: subtle music bed ducked under voice  ·  jump cuts on pauses  ·  zoom-blur transitions between footage and canvases", font=f(R, 22), fill=SUB)
d.text((PAD, H - 74), "Palette: forest #172B26 canvases · mint #F6FBF9 type · teal #0D9488 glow · blue #2563EB data only", font=f(R, 22), fill=SUB)
img.save("Storyboard_Clarity_v3.png", optimize=True)
img.save("Storyboard_Clarity_v3.pdf", resolution=150)
print(img.size)
