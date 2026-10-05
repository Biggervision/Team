# SK Mahbub: Brand & Video Style Guide

> **How to use this note:** attach this file to any new video, design, or content request.
> It is the source of truth for colors, type, layout, and motion. Don't invent a new palette.
> Pick **Dark Mode** (default, matches the website) or **Light Mode** (for bright and clean pieces).

---

## 1. Brand Basics

| Item | Value |
|---|---|
| Name | **SK MAHBUB** (all caps in titles, letter-spaced) |
| Short positioning | **Paid Ads \| Web Analytics \| Conversion Tracking** |
| Full title | **Paid Ads, Web Analytics & Conversion Tracking Consultant** |
| Feel | Premium · technical · clean · trustworthy · minimal · confident |
| Theme | Marketing technology + data infrastructure + advertising + analytics |
| Never | Cartoonish, gaming, glitch-heavy, stock-explainer, flashy, cluttered |

---

## 2. Dark Mode (primary, matches the website)

### Core colors

| Role | Hex / Value | Use |
|---|---|---|
| Background (base) | `#04090B` | Main canvas, near-black |
| Background glow | `#145C5E` at ~40% → transparent | Soft radial glow, top-left (like the website hero) |
| Secondary glow | `#19C3B1` at ~8% | Faint radial glow, bottom-right |
| Surface / card (top) | `#111F23` | Card gradient start |
| Surface / card (bottom) | `#091215` | Card gradient end |
| Card border | `#FFFFFF` at 7–8% | 1.5px hairline |
| Card top highlight | `#FFFFFF` at 10% | 1px gradient line on the top edge |
| **Accent: Brand Teal** | **`#19C3B1`** | Keywords, data signals, checkmarks, CTA, server nodes |
| Accent: Bright Teal | `#3BE3CF` | Data packets, glowing lines, chart strokes |
| Teal tint fill | `#19C3B1` at 10–16% | Icon boxes, pills, chips |
| Teal tint stroke | `#19C3B1` at 28–45% | Pill/icon borders, active card outline |
| Text: primary | `#F4F7F7` | Headlines, labels |
| Text: secondary | `#F4F7F7` at 60–72% | Subtitles, the full title line |
| Text: muted | `#F4F7F7` at 40–50% | Mono data labels, captions |
| Neutral / "lost" state | `#96A6A8` | Lost signals, errors, disabled. **No red.** |
| Dot grid | `#FFFFFF` at 5–6%, 2px dots every 60px | Subtle background texture |
| Vignette | `#000000` at 0 → 55% toward the edges | Focus toward the center |

### Contrast (checked)
- Teal `#19C3B1` on `#04090B` = **9.0 : 1** ✅
- White `#F4F7F7` on `#04090B` = **18.6 : 1** ✅
- Grey `#96A6A8` on `#04090B` = **7.9 : 1** ✅

### CSS tokens: Dark
```css
:root {
  --bg: #04090B;
  --bg-glow: rgba(20, 92, 94, 0.42);
  --surface-1: #111F23;
  --surface-2: #091215;
  --border: rgba(255, 255, 255, 0.075);
  --accent: #19C3B1;
  --accent-bright: #3BE3CF;
  --accent-fill: rgba(25, 195, 177, 0.12);
  --accent-stroke: rgba(25, 195, 177, 0.38);
  --text: #F4F7F7;
  --text-2: rgba(244, 247, 247, 0.65);
  --text-3: rgba(244, 247, 247, 0.45);
  --neutral: #96A6A8;
}
```

---

## 3. Light Mode (bright version, same brand)

Same teal identity, inverted for white backgrounds.
**Important:** bright teal `#19C3B1` is only 2.2 : 1 on white, so it's too light for text.
On light backgrounds use **Deep Teal `#0B7A70`** for text and thin lines. Keep `#19C3B1` for fills, glows, large shapes and buttons.

### Core colors

| Role | Hex / Value | Use |
|---|---|---|
| Background (base) | `#F4F9F8` | Main canvas, cool off-white with a hint of teal |
| Background glow | `#19C3B1` at 10–14% → transparent | Soft radial glow, top-left |
| Secondary glow | `#19C3B1` at 6% | Faint glow, bottom-right |
| Surface / card | `#FFFFFF` | Cards |
| Card border | `#0A1A1D` at 8% (≈ `#DCE6E5`) | 1.5px hairline |
| Card shadow | `#0A1A1D` at 6–8%, blur 40px, y +12px | Soft lift (replaces dark-mode glow) |
| **Accent: Brand Teal** | **`#19C3B1`** | Buttons, fills, icon backgrounds, charts, data packets |
| **Accent: Deep Teal (text-safe)** | **`#0B7A70`** | Highlighted keywords, links, thin lines, checkmarks |
| Teal tint fill | `#19C3B1` at 10–12% | Icon boxes, pills, chips |
| Teal tint stroke | `#0B7A70` at 25–35% | Pill/icon borders, active card outline |
| Text: primary | `#0A1A1D` | Headlines, labels |
| Text: secondary | `#4A5C5F` | Subtitles, the full title line |
| Text: muted | `#6B7C7F` | Mono data labels, captions (large or bold only) |
| Neutral / "lost" state | `#9AA8AA` (shapes) / `#6B7C7F` (text) | Lost signals, errors, disabled. **No red.** |
| Dot grid | `#0A1A1D` at 6%, 2px dots every 60px | Subtle background texture |
| Button | Fill `#19C3B1`, text `#04090B` | Same as the website's teal buttons |

### Contrast (checked)
- Deep Teal `#0B7A70` on `#F4F9F8` = **4.9 : 1** ✅
- Text `#0A1A1D` on `#F4F9F8` = **16.8 : 1** ✅
- Secondary `#4A5C5F` on `#F4F9F8` = **6.6 : 1** ✅
- Dark text `#04090B` on teal button `#19C3B1` = **9.0 : 1** ✅
- ⚠️ `#19C3B1` text on white = 2.2 : 1. Don't use it for text in light mode.

### CSS tokens: Light
```css
:root[data-theme="light"] {
  --bg: #F4F9F8;
  --bg-glow: rgba(25, 195, 177, 0.12);
  --surface-1: #FFFFFF;
  --surface-2: #FFFFFF;
  --border: rgba(10, 26, 29, 0.08);
  --shadow: 0 12px 40px rgba(10, 26, 29, 0.07);
  --accent: #19C3B1;          /* fills, buttons, graphics */
  --accent-text: #0B7A70;     /* text-safe teal */
  --accent-fill: rgba(25, 195, 177, 0.11);
  --accent-stroke: rgba(11, 122, 112, 0.30);
  --text: #0A1A1D;
  --text-2: #4A5C5F;
  --text-3: #6B7C7F;
  --neutral: #9AA8AA;
  --button-text: #04090B;
}
```

---

## 4. Typography

| Use | Font | Weight | Notes |
|---|---|---|---|
| Big statements / hooks | **Inter** | 900 (Black) | ALL CAPS, tight tracking (−2 to −4px), 120–200px on a 1080-wide canvas |
| Headlines | Inter | 800 | Sentence case, tracking −1px, 74–96px |
| Labels / card titles | Inter | 700–800 | 28–52px |
| Body / title line | Inter | 500–700 | 26–36px |
| Eyebrow labels | Inter | 700 | ALL CAPS, +4px letter-spacing, 22px, teal, inside a pill with a dot |
| Data / tech labels | **JetBrains Mono** | 500–700 | ALL CAPS, +2px tracking, 17–22px, muted (e.g. `SIGNAL QUALITY`, `EVENTS SENT`) |

- Both fonts are free (Google Fonts / Fontsource).
- **Keyword highlight rule:** only 1–3 words per line in teal (e.g. "Running **Facebook** or **Google Ads?**"). Everything else white (dark mode) or `#0A1A1D` (light mode).
- Never put the whole voice-over on screen. Show only key phrases, numbers and keywords.

---

## 5. Shapes & UI Components

| Element | Spec |
|---|---|
| Card radius | 28px (large), 22–26px (medium), 18–20px (rows/small) |
| Icon box | Rounded square, radius ≈ 28% of size; teal tint fill + teal stroke; line icons at 3px stroke |
| Pill / eyebrow | Fully rounded; teal tint fill + teal stroke; optional glowing teal dot |
| Node (diagram) | Card + icon box on the left + bold ALL-CAPS label + mono sub-label |
| Server node | Larger card, teal border at 55%, teal outer glow, pulsing rings. Always the visual center of the system |
| Data packet | 6–7px teal circle with soft glow and a short gradient trail |
| Checkmark | Teal circle that draws on, then a check stroke |
| Lost / error state | Grey (`#96A6A8` dark / `#9AA8AA` light), dashed outline, "?" or "×". **Never red.** |
| Lines/connectors | 2.5–3px teal at 35–40% opacity; dashed for "blocked/weak" |
| Icons | Simple line icons: globe (website), browser window, server rack, target (ad platform), megaphone (ads), chart, shield, signal bars |
| Platform names | Plain text labels ("Google", "Meta", "TikTok") with generic icons. **Never copy real platform UIs or logos.** |

Dark mode uses **glow** for depth. Light mode uses **soft shadow** for depth (glow max 10–15%).

---

## 6. Layout

**9:16 vertical (1080×1920)**: Reels / TikTok / Shorts
- Safe area: keep critical content between **y = 220 and y = 1600**, with 90px side margins.
- Stack: eyebrow pill (y ≈ 300) → headline → main visual card → supporting text.

**16:9 landscape (1920×1080)**: YouTube / LinkedIn / web
- Text on the **left column** (center x ≈ 520), visuals on the **right** (center x ≈ 1400).
- Big statements and the end card are **centered**.
- Margins: ~100px sides, ~80px top/bottom.

---

## 7. Motion Language

- **Mask reveals:** words rise from below, staggered ~0.07s, ease-out (quint), ~0.5s each.
- **Exits:** move up + fade + slight blur, ~0.4s.
- **Scene transitions:** soft crossfade with a small scale (1.03 → 1) and blur out. No preset wipes or spins.
- **Camera:** slow push-ins (≈ +5% over 3s) on key moments ("solution has arrived").
- **Impacts:** a short scale-down (1.2 → 1, ease-out expo) plus a soft teal radial flash and a tiny shake. Only on the 1–2 strongest lines.
- **Data:** packets flow continuously; lost packets turn grey, drift sideways and fade.
- **Glitch:** max ~0.15s, one-off, only on "WRONG" / "DATA LOSS"-type words.
- **Pace:** a visual change every 2–4s; faster in problem sections, slower for solution, intro and CTA.
- **Voice-first:** the voice-over sets the timing. Key words trigger visual events at that exact moment.

---

## 8. Audio

- **Voice:** always the original recording. Clean-up only: high-pass, light noise reduction, gentle EQ, de-ess, light compression, loudness match. **No AI voice, no cloning, no pitch/tone change.**
- **Music:** minimal, premium tech/cinematic bed (e.g. D minor, ~100 BPM, airy pads + soft pluck arpeggio + subtle pulse). About 18 dB under the voice and ducked while speaking. Builds into the solution, dips to near-silence before the hardest line, resolves on the CTA.
- **SFX (subtle):** UI ticks, soft blips, confirm chimes, soft whooshes, low impacts, short signal dropouts. No sci-fi alarms.
- **Master:** −14 LUFS integrated, true peak ≤ −1 dBTP.

---

## 9. Messaging Rules

- ✅ "More reliable tracking", "Less data loss", "Better signals", "Stronger tracking infrastructure", "Better data quality"
- ❌ "100% tracking", "Zero data loss", "Perfect attribution", "Every conversion captured"
- CTA style: the final statement **is** the CTA (e.g. "FIX YOUR TRACKING BEFORE IT COSTS YOU MORE."). Avoid generic "Book a call / DM me" unless asked.
- End card: portrait (unedited) → **SK MAHBUB** → teal underline → *Paid Ads | Web Analytics | Conversion Tracking* → full title.

---

## 10. Portrait Rules

- Use the real portrait only. **No face edits, no AI restyling, no reshaping.**
- Allowed: framing (rounded card or circle), slow zoom/parallax, mask reveal, edge fade into the background, teal border/glow.

---

## 11. Quick Copy-Paste Brief (for future requests)

> Use my brand: **SK Mahbub, Paid Ads | Web Analytics | Conversion Tracking**.
> **Dark mode:** background `#04090B` with a soft teal glow (`#145C5E`), cards `#111F23→#091215` with 8% white borders, accent teal `#19C3B1` (bright `#3BE3CF` for data), text `#F4F7F7`, neutral grey `#96A6A8` for lost/error states (no red).
> **Light mode:** background `#F4F9F8`, white cards with soft shadow, accent teal `#19C3B1` for fills/buttons and deep teal `#0B7A70` for text, text `#0A1A1D` / `#4A5C5F`.
> **Fonts:** Inter (800–900 headlines, ALL-CAPS statements) + JetBrains Mono for data labels.
> **Style:** premium dark-tech data infrastructure, rounded cards (28px), line icons in teal icon boxes, teal eyebrow pills, mask-reveal kinetic type, data-packet flows, server as the visual hero.
> Use my original voice (clean-up only), my real portrait (no edits), and no absolute tracking claims.
