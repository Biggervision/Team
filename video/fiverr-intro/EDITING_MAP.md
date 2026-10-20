# SK Mahbub — Fiverr Intro Video: Editing Map (v1)

Source: `Fiverr intro Draft.mp4` (Google Drive) — 1920×1080, 30 fps, 52.15 s, H.264/AAC.
Output: `SK_Mahbub_Fiverr_Intro.mp4` — 1920×1080, 30 fps, H.264 + AAC, 52.1 s, ~28 MB, -17 LUFS.
Timestamps come from word-level speech recognition of the actual recording (two models, results agree).

## Layout system (3 layouts only)
- **A – Light canvas:** off-white (left) blending to mint/aqua (right), faint teal dot grid.
- **B – Floating cards:** white rounded cards, soft teal shadow, small icon chips.
- **C – Minimal data visuals:** tracking hub → platform grid, fix/verified rows, step bars (no numbers).

Footage: full recording, uncut, never covered. Black side bars and outer wall cropped (x 440–1480), scaled 0.9, rounded card on the right. Graphics + subtitles live only in the left column.

## Timeline
| Time | Spoken (as recorded) | Left-column visual |
|---|---|---|
| 0.00–8.20 | Growing your business takes more than just running ads… accurate data, the right strategy, clear understanding of what drives results | Headline "More than just running ads." + 3 cards at 3.08 / 4.22 / 5.66 s |
| 8.40–12.95 | This is SK Mahbub, a Web Analytics, Conversion Tracking and Paid Advertising Consultant | Name title + 3 role pills at 9.34 / 9.92 / 11.16 s |
| 13.38–18.62 | I help businesses fix tracking issues, resolve conversion mismatches, eliminate duplicate events | 3 rows flip ✕ → ✓ (Resolved / Matched / Deduplicated) at 14.48 / 15.62 / 17.32 s |
| 18.72–29.32 | …reliable tracking system using GA, Meta Pixel + CAPI, Google Ads conversion tracking, TikTok, Snapchat, Twitter, LinkedIn, Microsoft Clarity | "Your website" hub → 8 platform chips, each appears when named |
| 29.38–35.46 | …other essential tracking tools combined with Google Ads and Meta Ads optimization | Server-side tracking + Event validation chips, Google Ads / Meta Ads cards, "Campaign optimization" |
| 35.56–41.95 | This helps you make smarter decisions, generate more qualified leads, increase sales, grow your business | 4 outcome cards with step bars (illustrative, no figures) |
| 42.02–47.72 | Let's fix what's holding your marketing back and turn better data into better business results | Statement + "Better data → better business results" — **reserved testimonial slot** |
| 48.00–52.13 | Need better tracking and stronger ad performance? Let's talk. | CTA headline + "Let's talk →" button at 51.18 s |

## Testimonial recommendation
- Fiverr intro videos: **only the seller may appear** → no client video/face. Use a text excerpt card, no star ratings or Fiverr badges.
- Best slot: **42.02–47.72 s** (5.7 s), left column, replaces the statement card. Fade + 20 px slide up (0.45 s), fade out 0.3 s. Reason: right after the outcomes list — proof lands where the claim was made, without interrupting the platform list.
- Pick a ≤ 20-word excerpt about fixed tracking / accurate conversions / reliable communication. Attribute as first name + country or "Fiverr client".

## Audio
High-pass 70 Hz, light FFT denoise (6 dB), loudness normalized to ~-16/-17 LUFS, true peak -1.5 dB. No music added (none supplied; no unlicensed tracks).

## Open items
- Instagram references are behind a login wall — not reviewed. Need the files.
- Visual reference screenshot — not received; palette built from the written brief.
- Testimonials — none received.

---

# v2 — Reel-style redesign (current)

Reference: Instagram Reel `Dcs_d-LRaRK` (downloaded and studied frame by frame).
Output: `SK_Mahbub_Fiverr_Intro_v2.mp4` — 1920×1080, 30 fps, H.264 + AAC, 55.0 s (52.1 s speech + 2.9 s name card), ~35 MB.

Design system copied from the reference:
- Full-frame footage (black bars removed), multi-cam style hard cuts between wide and medium framing at sentence starts.
- Hero words: Montserrat Black, silver→sky→royal-blue painterly gradient, placed **behind** the speaker using an AI person matte (RobustVideoMatting).
- Italic lead-ins: Playfair Display Italic, white.
- Captions: Montserrat 800 (keywords) / 600 (other words), white with soft shadow, 1–2 words at a time, synced to word timestamps.
- Faint glowing white line icons behind the speaker (data, funnel, chat).
- Animated tool chips (frosted glass + gradient icon tile) that pop in when each tool is spoken: GA4 21.08, Meta Pixel 22.06, Conversion API 22.42, Google Ads 23.30, TikTok 25.24, Snapchat 25.70, X 26.30, LinkedIn 26.58, Microsoft Clarity 28.28, Google Tag Manager 30.30 + Server-side 31.22 (on "other essential tracking tools"), Google Ads 32.94, Meta Ads 34.10; plus tracking issues / conversion mismatches / duplicate events fixes at 14.48 / 15.62 / 17.32.
- End card: name, title, "Let's talk".

Pipeline: `tx.py` (word timestamps) → `matte.py` (person matte) → `render2.py` + `chips.py` (frames) → ffmpeg mux with cleaned audio.
