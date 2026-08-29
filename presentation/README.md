# ASCENSION OPERATING SYSTEM™ — Foundation Edition v2.0

`ascension-os-deck.html` is the live-session deck: 41 speaker-led slides covering
the seven parts of the arc — Why → Philosophy → Daily OS → Weekly Tracker →
Review → Implementation → Q&A.

Open the file in any browser. No build step, no dependencies beyond the Google
Fonts stylesheet it links.

## Presenting

| Key | Action |
|---|---|
| `→` `space` `PgDn` | Next slide |
| `←` `PgUp` | Previous slide |
| `Home` / `End` | First / last slide |
| `O` | Overview grid — click any slide to jump |
| `Esc` | Close the overview |

Clicking the right side of the stage advances, the left side goes back, and
swipe works on touch screens. The deck remembers your position in that browser,
so reopening it mid-session picks up where you left off.

**Export to PDF:** print the page (`Ctrl/Cmd-P`) with background graphics on and
margins set to none — each slide becomes one 16:9 page.

## How the deck is built

Slides are declared as data in the single `<script>` block at the bottom of the
file, then rendered into a fixed 1600×900 stage that scales to fit any screen.

- **`BLOCKS`** — the sixteen daily blocks with their real start/end minutes. The
  24-hour rail on every block slide, and the architecture timeline on slide 12,
  are both drawn from this array, so editing a time updates every slide at once.
- **`PARTS`** — the seven part names, used by the divider slides' progress index.
- **`WEEK`** — the example 168-hour allocation, derived hour-for-hour from the
  daily architecture. Its palette is validated for colour-vision separation and
  contrast against the slide surface; if you change a colour, re-check it before
  presenting.

Editing copy means editing the `S.push({...})` entries — one per slide, in
running order. Keep slides to a headline plus three to five short lines; the
depth belongs to the speaker.

## Brand

`#04A2B8` accent · `#070808` ground · `#E5F1F2` and `#F1F1F1` light surfaces.
Dark slides carry the working content; the light slides are the seven part
dividers, so the shift in ground marks a new section.
