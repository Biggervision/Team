# SK Mahbub — Master Edit Style (locked spec)

Exact values from the approved final edit (v4). The master brief is in
`MASTER_PROMPT.md`; this file is the technical translation of it. Change the
**content plan** per video, never these values, unless a change is requested.

## Output
- 9:16, 1080×1920, 30 fps, H.264 CRF 18 master + 2-pass ~1.65 Mbps share copy
- Loudness: voice chain → `loudnorm I=-14 TP=-1.5 LRA=9` (final mix measures ≈ −15 LUFS)
- Ends on the last spoken word. No outro, credits, logos or watermarks.

## Footage scenes (face to camera)
**Crop / camera**
- Landscape source → 608×1080 crop centred on the face, Lanczos up to 1080×1920
- Jump cuts: pauses > 0.30 s trimmed to ~0.12 s (`cuts.py`), 15 ms audio fades at every cut
- Alternate cuts reframe at 1.045× (hides the jump)
- Punch-ins on key lines: +7–12 %, ease-in 0.28 s, hold to ~1.25 s, ease-out 0.6 s, centred on the face
- 0.6 s zoom-out (1.08 → 1.0) when footage returns from a canvas scene

**Grade** (ffmpeg, `render_base.py`)
```
colortemperature=temperature=5300:mix=1,
colorbalance=rs=0.02:bs=-0.06:rm=0.03:bm=-0.06:rh=0.02:bh=-0.04,
eq=contrast=1.12:saturation=1.10:gamma=0.95,
curves=all='0/0 0.12/0.07 0.5/0.5 0.9/0.86 1/0.94',
vignette=PI/4.2
```
Final pass texture: `noise=alls=5:allf=t,unsharp=5:5:0.4`

**Captions**: clean white, no panels, no glass, no icons
| Element | Font | Size | Notes |
|---|---|---|---|
| Plain caption chunk (≤3 words) | Poppins Medium | 72 | centred, baseline y≈1340 |
| Supporting words around a keyword | Poppins Regular | 64 | line above (y−112) / below (y+128) |
| Keyword | Poppins ExtraBold, UPPERCASE | 168 (auto-shrinks to 960 px wide) | tracking −0.02 |
| Accent words | Playfair Display Bold Italic | 140 | e.g. *Imagine*, *foundation*, *confidence* |
| Number scene label | Poppins Medium, tracked 0.18em | 36 | e.g. MONTHLY AD SPEND |
| Number figures | Poppins ExtraBold | 150 | count up 0.5–0.6 s, ease-out |

- Soft drop shadow on all footage text (blur 9, 60 %, +5 px)
- Animation: word-by-word reveal = fade + 18 px rise over 0.22 s; keywords scale 0.92→1.0 + 14 px rise over 0.30 s;
  italic accents fade + 20 px rise over 0.35 s; every unit fades out over 0.16 s
- No bounce, shake, glitch, highlight bars or coloured text on footage

## Branded canvas scenes (only place for grid + glass)
- Gradient: `#FFFFFF` (top) → `#F6FBF9` (45 %) → `#E6F3EE` (bottom), soft mint glows
- Grid: 72 px, line `#C9E2D8`, drifts 14 px/s, radial reveal from centre, diagonal light sweep
- Text: deep forest `#172B26`; secondary `#566C65`; keyword/positive accent teal `#0D9488`; numbers/data blue `#2563EB` (sparingly)
- Glass: backdrop blur σ10–20, white frost 50–76 %, top sheen, 2 px white border, soft forest-tinted shadow
- Checkmarks: teal disc, white tick drawn on (0.28 s) after a 0.22 s back-out scale-in
- Card types used so far: waveform-phrase card, list card (glass rows + checks), single-word statement card
- Transition in: slide up 0.32 s ease-out (footage dims 35 %). Out: slide up 0.30 s ease-in + footage zoom-out

## Sound design (`sound.py` + `plan_sfx()` in `edit_master.py`)
All SFX are synthesised (no licensing). Gains are linear multipliers on the SFX bus.
| Moment | SFX | Gain |
|---|---|---|
| Keyword reveal | swish (−0.10 s) + pop | 0.10 / 0.09 |
| Number count | tick every 50 ms + ding at land | 0.05–0.07 / 0.07–0.13 |
| Punch-in zoom | soft impact | 0.14 + zoom strength |
| Italic accent | swish | 0.10 |
| Canvas in / out | whoosh / reverse whoosh | 0.20 / 0.15 |
| Before list / statement cards | riser (0.85 s lead) | 0.06 |
| List item | click + pop | 0.14 / 0.07 |
| Statement card ("No.") | heavy impact | 0.42 |

- Music bed: synthesised Am9–Fmaj7–Cmaj7–G6 pad, 88 bpm, soft kick/hat/pluck, low-passed at 7 kHz,
  level 0.16 with 55 % voice-keyed ducking, 1.5 s fade-in, 2 s fade-out
- SFX bus ducks 25 % under speech. Voice chain: HPF 80 Hz, −2 dB @250 Hz, +2.5 dB @3.5 kHz, 3:1 compression

## Covers (9:16, 1080×1920, text-only)
- `covers/cover_light.py`: light brand gradient + faint grid, forest text, teal figures, forest block CTA
- `covers/cover_dark_brand.py`: Iman-style dark forest spotlight + grain, mint text, serif-italic accents, teal block CTA
- Keep all text inside y≈300–1550 (Reels UI safe area)
