# ASCENSION OPERATING SYSTEM™ — Foundation Edition v2.0

The live-session deck, built directly from the Foundation Edition v2.0 document.
49 slides across the seven parts: Why → Philosophy → Daily OS → Weekly Tracker →
Review → Implementation → Q&A.

| File | Use it for |
|---|---|
| **`Ascension-Operating-System-v2.pptx`** | Presenting from PowerPoint or Keynote, or handing the deck to someone else to edit. Fully native and editable — every slide is real text and shapes, and all 49 carry speaker notes. |
| **`ascension-os-deck.html`** | Presenting from a browser. Adds the live 24-hour rail, keyboard navigation, an overview grid and a hoverable 168-hour week grid. No build step. |

Both carry the same content and the same visual system; the HTML version is the
interactive one, the PowerPoint the portable one.

## Presenting from the browser deck

| Key | Action |
|---|---|
| `→` `space` `PgDn` | Next slide |
| `←` `PgUp` | Previous slide |
| `Home` / `End` | First / last slide |
| `O` | Overview grid — click any slide to jump |
| `Esc` | Close the overview |

`F` toggles full screen. Two buttons sit in the bottom-right corner — all slides,
and full screen — so the deck is fully operable with no keyboard.

Tapping the right side of the stage advances, the left side goes back, and
horizontal swipes work on touch screens; a vertical drag scrolls instead, so a long
slide stays readable. The deck remembers your position in that browser, so reopening
it mid-session picks up where you left off. Print (`Ctrl/Cmd-P`) with background
graphics on and margins set to none to export one 16:9 page per slide — the PDF is
always landscape regardless of the screen you print from.

## On phones and tablets

The deck has two design targets and picks one from the viewport's aspect ratio, then
scales it to fill the screen edge to edge:

| Viewport | Stage | Layout |
|---|---|---|
| Landscape (aspect ≥ 1.15) | 1600 wide, 900–1150 tall | The full two-column design. A 16:10 or 3:2 laptop fills completely; an ultra-wide screen gets side bars, like any 16:9 deck. |
| Portrait or near-square | 680 wide, 920–1560 tall | Single column: paired columns stack, tile grids drop to two or three across, and the type is re-scaled for a narrow screen. |

Small landscape screens (a phone held sideways) additionally get a `compact` tier
that enlarges the small monospace labels, which would otherwise scale down to a few
pixels. In portrait the 168-hour grid keeps all 24 columns, so one row is still one
day, and tapping a cell names its category — the hover behaviour, on touch.

Everything below was checked on every slide at 360×640, 390×844, 844×390, 820×1180,
1180×820, 1440×900 and 1920×1080: no slide overflows its frame at any of them.

## Fonts

The browser deck uses Archivo, Hanken Grotesk and IBM Plex Mono from Google Fonts.
The PowerPoint uses Arial and Courier New so it renders identically on any machine
without installing anything.

## The day the deck describes

Seventeen blocks, 1:00 PM wake to 5:00 AM sleep, with eight protected hours of
recovery. The block list, times and content all come from the source document:

| | Block | Time |
|---|---|---|
| 01 | Wake Up Consistently | 1:00 PM |
| 02 | Win Your First Hour | 1:00 – 1:40 PM |
| 03 | Refuel Your System | 1:40 – 2:00 PM |
| 04 | Protect Your Peak Hours | 2:00 – 4:00 PM |
| 05 | Reset Your Energy | 4:00 – 4:30 PM |
| 06 | Move Your Body | 4:30 – 6:30 PM |
| 07 | Communicate Without Constant Interruption | 6:45 – 7:45 PM |
| 08 | Make Time to Live | 7:45 – 10:30 PM |
| 09 | Execute & Level Up | 10:30 PM – 12:30 AM |
| 10 | Protect Your Deep Work | 12:30 – 2:30 AM |
| 11 | Deep Work Break | 2:30 – 2:45 AM |
| 12 | Read to Build Your Mind | 2:45 – 3:15 AM |
| 13 | Build Your Future Value | 3:15 – 4:00 AM |
| 14 | Close Your Workday | 4:00 – 4:15 AM |
| 15 | Design Tomorrow | 4:15 – 4:30 AM |
| 16 | Enter Your Recovery Window | 4:30 – 5:00 AM |
| 17 | Sleep Consistently | 5:00 AM – 1:00 PM |

## Editing

**PowerPoint** — edit it like any deck. To regenerate it from source instead, the
generator lives in this session's scratchpad (`build.js` + `lib.js`, pptxgenjs);
`lib.js` holds the design system and the `BLOCKS` array, `build.js` the slide content.

**Browser deck** — everything is in the single `<script>` block at the bottom of the
file. Slides are `S.push({...})` entries in running order; edit the copy there.

- **`BLOCKS`** — the seventeen daily blocks with their real start/end minutes. The
  24-hour rail on every block slide and the architecture timeline are both drawn
  from this array, so changing a time updates every slide at once.
- **`PARTS`** — the seven part names, used by the divider slides' progress index.
- **`WEEK`** — the example 168-hour allocation, built from the Weekly Scorecard
  targets. Its colours are validated for colour-vision separation and for contrast
  against the slide surface; re-check them if you change one.

Keep slides to a headline plus three to five short lines. The depth belongs to the
speaker — that is what the notes field is for.

## Brand

`#04A2B8` accent · `#070808` ground · `#E5F1F2` and `#F1F1F1` light surfaces.
Dark slides carry the working content; the light slides are the seven part
dividers, so the change of ground marks a new section.
