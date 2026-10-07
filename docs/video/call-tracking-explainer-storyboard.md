# The Phone Call Black Hole — Production Storyboard

**Premium 3D explainer · Light version · 16:9 + 9:16**
Client: Google Ads, Web Analytics, Paid Ads, Web Analytics and Conversion Tracking Consultant
Audience: Local service business owners who run Google Ads and live on inbound phone calls
Single lesson: *"Your Google Ads may not be failing. Your conversion tracking may be hiding the leads that are actually working."*

---

## 0. Voiceover analysis (the timing source of truth)

The attached voiceover (`Home_4.m4a`) was transcribed with word-level timestamps and pause detection. Every cue in this document is locked to that recording.

| Measure | Value |
|---|---|
| Raw file length | 66.7 s |
| First word | 0.00 s (no lead-in) |
| Last word ends | 65.26 s |
| Trailing silence | 1.1 s (trim) |
| Longest internal pause | 1.3 s before "Here's the fix" (keep — it is the tonal pivot) |

**Runtime decision.** The brief targets ~50 s, but the recorded read runs 65 s of speech at a natural, unhurried pace. Per the instruction not to force the voice into a fixed timeline, the edit follows the recording. Final master runtime: **71.5 s** (0.5 s pre-roll + 65.3 s VO + ~5.7 s end card hold for the final statement, which is on screen but not spoken).

**Master timeline rule.** VO is placed at **00:00.50** in the master. All timecodes below are master timecodes (VO file time + 0.50 s). Pauses inside the read are kept; none exceed 1.3 s, so no internal cuts are needed.

**Two things to verify by ear before captioning:**
1. At ~6.4–8.6 s (file time) the transcriber heard "can be over $1000 of dollars" instead of the script's "can be worth thousands of dollars." Captions and on-screen text use the script wording. If the read genuinely differs, either re-record that line or match captions to what was said.
2. "Pause" was transcribed as "post" both times (24.04 s and 59.94 s file time). Captions use "pause/pausing." If it sounds like "post" to a native listener, consider a pickup of those two words.

Synced captions: [`call-tracking-explainer.srt`](call-tracking-explainer.srt) (master time, script wording).

### Word-cue map (master time)

| Cue | Time | Visual event it drives |
|---|---|---|
| "personal injury law firm" | 1.88–2.60 | Law firm chip lands |
| "HVAC" | 3.12 | HVAC chip lands |
| "roofing" | 3.86 | Roofing chip lands |
| "plumbing" | 4.32 | Plumbing chip lands |
| "phone calls" | 5.90 | Call cards burst from phone |
| "thousands of dollars" | 7.92–9.16 | Value tags count up |
| "not tracking" | 11.92–12.40 | First calls fall into the black hole |
| "30" | 14.90 | Actual Calls counter lands at 30 |
| "only sees 10" | 17.38–18.02 | Tracked Conversions locks at 10 |
| "underperforming" | 21.46 | Status pill flips to Underperforming |
| "budget" | 23.94 | Budget slider drags down |
| "pause" | 24.54 | Toggle → Campaign Paused |
| "best customers" | 29.58–30.62 | Last high-value lead dissolves |
| "not your ads" | 32.26–32.88 | Ads node gets a calm check |
| "tracking" | 33.98 | Tracking layer highlights, broken links visible |
| "hiding" | 34.90 | Black hole revealed inside the tracking layer |
| "Here's the fix" | 37.96 | Consultant card enters, energy turns |
| "Track" | 39.76 | Step 1 |
| "identify" | 41.50 | Step 2 |
| "send" | 45.04 | Step 3 — signals flow back |
| "sees" | 49.08 | Tracked counter climbs 10 → 30 |
| "optimize" | 53.50 | Performance curve lifts |
| "revenue" | 57.90 | Revenue metric resolves |
| "pausing" | 60.44 | Ghosted paused campaign |
| "competitors" | 63.76 | Calls drift to competitor pin |
| VO ends | 65.76 | Final card locks |

---

## 1. Creative concept summary

**Concept: "The Phone Call Black Hole."**

Phone calls are the most valuable thing a local service business gets from Google Ads, and they are the easiest conversions to lose. We visualize every call as a small, glowing call card. Most travel cleanly into Google Ads, Analytics and the CRM. Some quietly fall into a soft, elegant void sitting inside the tracking layer: the *black hole* of missing conversion data.

Google can only optimize on what it sees. When it sees 10 conversions instead of 30, it judges a working campaign as failing. The owner believes it and pauses. The calls, and the customers, go to a competitor.

The story turns when the camera pulls back and shows that the ads were never the broken part. The tracking layer was. The consultant enters as the guide, the broken connections close, and the system becomes whole: track calls → identify qualified leads → send signals back. Google now sees what matters and optimizes toward it.

**StoryBrand mapping**

| Beat | Scenes | Viewer feels |
|---|---|---|
| Character — the local service owner | 1 | "That's me." |
| Problem — calls aren't tracked | 2 | "Where did those calls go?" |
| Consequence — Google sees bad data | 3–5 | "That's why my campaign looks weak." |
| Guide — tracking reveals real performance | 6–7 | "It might not be my ads." |
| Plan — track, qualify, send | 8 | "That's simple enough." |
| Success — Google optimizes on real leads | 9 | "That's what I want." |
| Stakes — competitors capture them | 10 | "I should check before I pause." |
| CTA | 11 | Brand + statement |

**Emotional arc:** curiosity → unease → realization → relief → confidence.
**Visual arc:** scattered → leaking → broken → connected → rising → calm.

---

## 2. Visual style specification

### World
- **Canvas:** bright, near-white environment with a faint perspective grid floor that fades to the horizon. Grid reads as "analytics workspace," never as "Tron."
- **Depth:** 3–4 layers per shot — grid floor, primary object, floating UI cards, soft foreground bokeh of tiny data dots (sparse).
- **Lighting:** large soft key from top-left, gentle fill, subtle rim on glass edges. Soft contact shadows on the grid. No harsh specular blowouts.
- **Materials:**
  - UI panels: frosted glass (10–20% blur), white at 70–85% opacity, 1 px light edge, 16–24 px corner radius.
  - Phone: satin white/graphite body, clean glass screen, no real brand marks.
  - Nodes (Ads, Analytics, CRM, Tracking): soft-rounded matte tiles with a brand-color glyph.
  - Data: small luminous capsules (call cards) and thin, smooth light streams in brand color.
- **The black hole:** a soft, concave, pearl-grey vortex with a fine spiral of grid lines bending into it and a faint warm-orange rim only where calls cross the event horizon. Think "elegant data visualization of absence," not space horror. No stars, no lensing flares.

### Palette (provisional — swap for brand reference)
Brand colors were not attached yet. These are placeholder tokens; the provisional values are derived from the aqua backdrop of the supplied portrait so the portrait card sits naturally. Replace the hex values once the brand reference arrives; keep the token roles.

| Token | Role | Provisional |
|---|---|---|
| `canvas` | Background | `#F7F9FB` |
| `grid` | Grid lines | `#DDE4EC` at 50% |
| `ink` | Headlines, numbers | `#0E1A2B` |
| `ink-2` | Labels, secondary | `#5B6878` |
| `brand-primary` | Data streams, tracked calls, buttons, success | `#20B4CE` |
| `brand-deep` | Emphasis, charts, title accents | `#0B5F78` |
| `brand-tint` | Card fills, glows | `#E3F6FA` |
| `warn` | Untracked call rims, "Underperforming" pill | `#F08A24` |
| `loss` | "Campaign Paused," lost revenue only | `#E5484D` |

Rules: brand colors carry ~90% of accent use. `warn`/`loss` appear only in Scenes 2–6 and 10, on small elements, never as a full-frame wash. Scenes 8–9 and 11 contain zero warning color.

### Typography
- One geometric/neo-grotesk sans (e.g., Inter, Manrope, or the brand typeface).
- Hierarchy: Headline 600 weight · Supporting 400 · Data numbers 700, tabular figures · Small label 500, uppercase, +6% tracking.
- Max 3–7 words of on-screen text per scene. Text enters with the motion of its parent object (slides with the card, rises with the counter), never as a standalone fly-in.

### UI kit
Call card · Lead card (qualified / not qualified) · Industry chip · Conversion counter · Ad-campaign card (generic, "Ads" wordmark, no Google logo) · Budget slider · On/Off toggle · Pipeline nodes · Tracking status dot (green/amber) · Simple line/bar charts · CRM contact card · Consultant identity card.

**Platform note:** the campaign interface is "inspired by" ad platforms — generic layout, no Google logo, colors, or exact UI. Spoken references to Google Ads are fine; the visuals must not look like an official Google product.

### Motion language
- Easing: ease-in-out cubic for camera, soft spring (low bounce) for UI cards.
- Camera: slow push-ins, lateral dollies, gentle 10–15° orbits, parallax. No whip pans, no fast spins, no extreme zooms, no glitch.
- Particles: sparse and meaningful — every particle is a call or a signal.
- Transitions: match-moves and object continuity (one object becomes the next scene's anchor). No hard cuts except the single deliberate beat at "Here's the fix."

---

## 3–12. Scene-by-scene storyboard

Each scene: timing · VO · visual · 3D elements · camera · animation · on-screen text · transition · sound · purpose. 16:9 and 9:16 compositions are specified per scene.

---

### Scene 1 — The Hook: Calls Worth Thousands
**Master 00:00.00 – 00:09.30 (9.3 s)**

**VO:** "If you run a personal injury law firm, HVAC, roofing, or plumbing business, your phone calls can be worth thousands of dollars."

**Visual concept:** A premium 3D smartphone floats above the grid, screen glowing with an incoming call. Around it, four industry chips orbit into place in sync with the VO. Calls stream out of the phone, each tagged with value.

**3D elements:** Smartphone (satin white, tilted 12° toward camera) · 4 industry chips with simple line icons: scales (Law Firm), snowflake/flame (HVAC), roof outline (Roofing), pipe/droplet (Plumbing) · Call cards ("Incoming call · 2:41") · value tags (`$2,400`, `$8,500`, `$15,000+`, `$650`).

**Camera:** Starts tight on the phone screen (pre-roll ring), slow pull-back and 8° orbit right to reveal the chips; ends on a medium-wide.

**Animation:**
- 0.00–0.50 Pre-roll: phone screen lights, single soft ring, gentle haptic vibration.
- 1.88 Law Firm chip slides in on a soft spring; 3.12 HVAC; 3.86 Roofing; 4.32 Plumbing. Each chip emits one thin brand-color line back to the phone.
- 5.90 "phone calls": 6–8 call cards pop off the screen and drift outward in a fan.
- 7.92–9.16 "thousands of dollars": value tags tick up on each card (counter roll, 0.6 s).
- 8.6 Tension seed: one call card at the edge flickers amber and dims slightly. Nothing else yet.

**On-screen text:** Industry chip labels only, then "Calls worth thousands" (small, beside phone, at 7.9).

**Transition:** The fan of call cards begins flowing right (16:9) / down (9:16) — the camera follows the flow into Scene 2. Continuous move, no cut.

**Sound:** Soft modern phone ring (one cycle, filtered) at 0.0 · gentle notification ticks per chip (pitched up a step each) · light paper-like "pop" for each call card · faint coin-like shimmer on value tags (very subtle, not slot-machine).

**Purpose:** Instant self-identification ("that's my business") and establish that calls = money.

**16:9:** Phone left-of-center third; chips arc on the right side in a loose semicircle; call cards fan toward the right edge, setting up left→right flow.
**9:16:** Phone centered, upper-middle (y ≈ 38%). Chips stack in a 2×2 grid below the phone. Call cards fan downward. Value tags large (≥ 56 px).

---

### Scene 2 — The Phone Call Black Hole (Hero Visual)
**Master 00:09.30 – 00:13.60 (4.3 s)**

**VO:** "But what if Google Ads isn't tracking all of them?"

**Visual concept:** The call stream travels toward three clean destination nodes — Ads, Analytics, CRM. Midway, the grid floor bends into a soft pearl-grey vortex. Some calls arrive at the nodes with a brand-color confirmation; others curve, stretch slightly, and slip silently into the vortex.

**3D elements:** Call cards as luminous capsules · 3 destination nodes (Ads glyph, chart glyph, contact-card glyph) · the black hole: concave grid depression with spiral grid lines, warm hairline rim · tiny "✓" confirmations on tracked calls.

**Camera:** Smooth lateral dolly following the stream, then slight crane up to reveal the vortex beneath the flow at 11.9.

**Animation:**
- 9.36 Stream flows toward nodes; 3–4 calls land with a soft check pulse.
- 10.70 "Google Ads": the Ads node glows briefly.
- 11.92 "not tracking": the grid starts to sink; two calls curve down into the vortex. Each one leaves a faint amber trail that fades.
- 12.40–13.16 More calls split: roughly two of every three fall in. The Ads node counter stalls.
- Keep it slow and quiet: the vortex rotates at ~6°/s.

**On-screen text:** "Your best leads may be disappearing." (enters at 12.0, sits above the vortex)

**Transition:** Camera tilts down into the vortex's soft center; the grey center becomes the grey background of the dashboard card in Scene 3 (match-dissolve on shape and tone).

**Sound:** Light data-transfer ticks for arrivals · a soft descending "whoom" (low-pass, quiet) for each lost call · music introduces a sustained minor pad: first tension.

**Purpose:** The core metaphor. Viewer asks: "Where did those calls go?"

**16:9:** Horizontal flow: calls enter left → vortex center-frame on the floor → nodes stacked on the right edge. Text top-center.
**9:16:** Vertical flow: calls fall from top → vortex mid-frame → nodes in a row at the lower-middle (y ≈ 70%). Text at y ≈ 20%, two lines.

---

### Scene 3 — The Gap: 30 Calls, 10 Conversions (Aha Moment)
**Master 00:13.60 – 00:19.40 (5.8 s)**

**VO:** "You might receive 30 serious calls, while Google only sees 10 conversions."

**Visual concept:** A clean glass analytics panel with two big counters and one comparison bar. The difference is unmissable.

**3D elements:** Glass dashboard panel · counter A "Actual calls" · counter B "Tracked conversions" · horizontal 30-slot bar (one slot per call) · small phone icons filling slots.

**Camera:** Slow push-in on the panel, ending framed on both numbers. Minimal parallax between panel and background grid.

**Animation:**
- 13.84 Panel settles in from the vortex dissolve.
- 14.90 "30": Actual calls counter rolls 0 → 30 (0.5 s); the 30-slot bar fills left to right in brand color.
- 17.04 "Google": Tracked conversions counter appears beneath.
- 18.02 "10": counter lands on 10. Only the first 10 slots stay solid; the other 20 drain to hollow outlines with an amber hairline.
- 18.40 A soft bracket labels the hollow section: "20 missing."
- Hold still 0.6 s after "conversions" — let it land.

**On-screen text:** "Actual calls 30" · "Tracked conversions 10" · bracket "20 missing"

**Transition:** The panel slides left / up while the "10" number lifts out and flies into the campaign card of Scene 4, becoming its conversion figure (object continuity).

**Sound:** Fast soft tick-roll on the 30 count · single clean "lock" click on the 10 · a quiet hollow "tock" as the 20 slots drain. Music: pad sustains, small rhythmic pulse begins.

**VO direction:** emphasize "Google only sees 10 conversions." Leave the 0.9 s natural pause after it.

**Purpose:** The aha. 30 happened; 10 were reported.

**16:9:** Side-by-side: counter A left, counter B right, the 30-slot bar spanning full width beneath. Spacious.
**9:16:** Stacked: counter A on top (number ≥ 180 px), counter B below, slot bar wraps into a 6×5 grid of phone icons in the lower third — easier to read vertically.

---

### Scene 4 — Google's Verdict: Underperforming
**Master 00:19.40 – 00:22.90 (3.5 s)**

**VO:** "Now Google thinks your campaign is underperforming."

**Visual concept:** A generic ad-platform campaign card: campaign name, conversions (10), cost per conversion (high), a flat line chart. A status pill flips to "Underperforming."

**3D elements:** Campaign card (glass, "Search · Local Services" label, generic "Ads" glyph) · line chart flattening · status pill · cost-per-conversion figure.

**Camera:** Gentle orbit 10° left around the card; subtle rack focus from the card's header to the status pill.

**Animation:**
- 19.62 The "10" from Scene 3 docks into the conversions field.
- 20.2 Cost per conversion ticks up (`$84` → `$252`).
- 20.6 Chart line sags and flattens.
- 21.46 "underperforming": status pill flips from neutral grey to amber with a soft 3D card-flip.

**On-screen text:** "Underperforming" (pill) — nothing else.

**Transition:** Camera continues orbit to reveal the budget slider and toggle on the card's side panel; same object, new focus — flows straight into Scene 5.

**Sound:** Soft UI flip "tick" on the pill · faint downward synth gesture (two notes) under "underperforming."

**Purpose:** Show the consequence: bad data → wrong verdict.

**16:9:** Card center-left, chart extends right; generous whitespace.
**9:16:** Card fills 85% of width, centered; pill enlarged directly under the campaign name.

---

### Scene 5 — The Wrong Decision: Cut, Pause, Lose
**Master 00:22.90 – 00:31.00 (8.1 s)**

**VO:** "You cut the budget or pause the campaign, when the campaign may actually be bringing your best customers."

**Visual concept:** The business owner's decision, shown through a simple hand/cursor interacting with the card. Budget drops, campaign pauses. Behind the card, the high-value lead cards that were quietly arriving fade away.

**3D elements:** Minimal stylized hand (neutral, semi-realistic, light sleeve) or a clean pointer · budget meter/slider · On/Off toggle · lead cards with names and job values ("Roof replacement · $14,800," "Auto accident case," "AC install · $7,200," "Water heater · $1,900") · three small loss tiles.

**Camera:** Slow push toward the slider; at 26.1 pull back gently to reveal the lead cards floating behind the campaign card.

**Animation:**
- 23.56 "cut": hand enters.
- 23.94 "budget": slider drags down from `$150/day` to `$40/day`; meter fill drains.
- 24.54 "pause": toggle clicks off → campaign card desaturates; "Campaign Paused" label in `loss` red, small.
- 26.14 Pull-back reveals 4–5 lead cards behind the card, softly glowing in brand color — they *were* coming in.
- 27.0–29.5 One by one, lead cards lose their glow, turn grey and drift away.
- 29.58 "best customers": the brightest, highest-value card (e.g., "Personal injury case") dissolves last.
- 30.0 Three small tiles appear in a row: "Lost leads · Lost customers · Lost revenue" — muted, not dramatic.

**On-screen text:** "Campaign Paused" → then "Lost customers" (or the three tiles if layout allows)

**Transition:** Camera begins a long, smooth pull-back from the greyed card (continues into Scene 6).

**Sound:** Soft slider drag (friction texture) · crisp toggle click · gentle "dim" sweep as the card desaturates · one soft, low, falling tone per lost lead (decreasing volume) · music drops to sparse pad for the realization.

**Purpose:** Make the cost real: a working campaign gets switched off.

**16:9:** Campaign card left third, lead cards cascade right; loss tiles bottom-right.
**9:16:** Campaign card top half; lead cards stack vertically below it like a feed and fade from bottom up; loss tiles as one horizontal row at y ≈ 72%.

---

### Scene 6 — The Reveal: It's Not the Ads
**Master 00:31.00 – 00:37.30 (6.3 s)**

**VO:** "The problem may not be your ads. Your tracking may be hiding the real performance."

**Visual concept:** Central educational moment. The camera pulls back from the paused card to reveal the whole system as a clean pipeline:

`Ads → Website / Phone → Tracking → Google Ads → CRM`

The Ads node is fine. The Tracking layer has broken, dashed connections — and the black hole from Scene 2 is sitting inside it.

**3D elements:** Five pipeline nodes on the grid · connector streams · Tracking node as a translucent glass slab with the miniature vortex inside · amber dashed/broken connectors from Tracking → Google Ads and Tracking → CRM.

**Camera:** Long pull-back + crane up to a 3/4 elevated view of the full pipeline (the widest shot in the film). Then a slow push toward the Tracking node.

**Animation:**
- 31.36 Pipeline revealed, nodes lifting into place left to right.
- 32.26–32.88 "not your ads": the Ads node gets a calm brand-color check; its stream into Website/Phone flows strongly.
- 33.98 "tracking": Tracking node highlights; its outbound connectors flicker and show visible gaps.
- 34.90 "hiding": camera push reveals the vortex inside the Tracking slab, calls slipping in.
- 35.92 "real performance": a faint ghost "30" appears behind the paused campaign's "10" — the real number hidden.

**On-screen text:** "Not your ads." (32.3) → "Your tracking." (34.0) — the first fades as the second appears.

**Transition:** Hold 1.0 s on the Tracking node during the natural pause (36.64–37.96) — music thins to near-silence. Then the deliberate beat (Scene 7).

**Sound:** Soft whoosh on the pull-back (low, airy) · gentle chime on the Ads check · brittle, quiet electrical crackle (very subtle) on broken connectors · music: tension peaks, then breathes out.

**VO direction:** emphasize "The problem may not be your ads." and "Your tracking may be hiding the real performance." Keep the 1.3 s pause before "Here's the fix."

**Purpose:** Reframe the problem. The viewer's mental model shifts from "my ads are bad" to "my data is incomplete."

**16:9:** Full pipeline left-to-right across the frame — the payoff of the horizontal flow language.
**9:16:** Pipeline runs top-to-bottom as a vertical spine; nodes centered, labels to the right of each node. Tracking node sits at the vertical center for the push-in.

---

### Scene 7 — The Guide Enters: Here's the Fix
**Master 00:37.30 – 00:39.60 (2.3 s)**

**VO:** "Here's the fix:"

**Visual concept:** The energy turns. The consultant's identity card glides in beside the Tracking node — calm, credible, present. The vortex begins to close.

**3D elements:** Consultant identity card: glass card, portrait photo (unaltered, natural color grade matched to the scene lighting), name, a small brand-color tracking-status dot that turns green · Tracking node.

**Camera:** Brief, controlled ease to a slightly lower, more confident angle. Very small push.

**Animation:**
- 37.96 Card slides in on a soft spring with a gentle shadow landing on the grid.
- 38.50 "fix": status dot on the card blinks from amber to brand-primary; the vortex in the Tracking node starts to flatten back into grid.

**On-screen text:** "Here's the fix." (small, on the card) — portrait + name only. Full title is saved for the final card.

**Transition:** The card shrinks into a small presenter badge anchored in the top-left corner (16:9) / top-center (9:16) for Scene 8, then exits after Step 3.

**Sound:** Music shift: the minor pad resolves to a major chord; light pulse becomes a forward beat · soft confident UI "click-in" for the card.

**Purpose:** Introduce the guide without turning the video into a talking head.

**16:9:** Card right of the Tracking node, portrait at roughly the same height as the node.
**9:16:** Card centered, upper half; Tracking node visible below it.

**Portrait handling:** Use the supplied photo as-is. No face redesign, no stylization, no cartoon. Cut out the subject cleanly, keep the soft aqua backdrop or replace with `brand-tint`. Treat the photo like a premium ID card: rounded 20 px corners, subtle inner border, soft drop shadow.

---

### Scene 8 — The Plan: Track · Qualify · Send
**Master 00:39.60 – 00:48.30 (8.7 s)**

**VO:** "Track your calls properly. Identify which calls become qualified leads. Then send those conversion signals back to Google Ads."

**Visual concept:** Fragmented becomes connected. Three clear steps, each one fixing part of the pipeline, built from the same call cards we've followed all along.

**3D elements:** Step badges "1 · 2 · 3" · phone + call cards · filter gate (a thin glass plane with a brand-color scan line) · lead cards splitting into "Qualified" (brand glow) and "Not a fit" (neutral grey, small: spam, wrong number, job seeker) · return data stream (thin bright line) from CRM back to Google Ads node.

**Camera:** Smooth lateral dolly across the three steps (16:9) / vertical crane down through the steps (9:16). One continuous move.

**Animation:**
- 39.76 **Step 1 — Track calls.** Every call card now passes through the Tracking node with a check; the vortex is gone; connectors snap solid with a soft magnetic click.
- 41.50 **Step 2 — Identify qualified leads.** Calls pass through the filter gate; at 43.38 "qualified" they split — qualified cards glow and continue, irrelevant ones slide aside and fade.
- 44.78 **Step 3 — Send conversion signals.** At 45.04 "send" a bright signal stream travels *backwards* from CRM to the Google Ads node; at 47.46 "Google Ads" the node pulses and its counter starts to tick.
- Steps stay visible as a checklist; each badge fills with brand color as completed.

**On-screen text:** "1 Track calls" · "2 Identify qualified leads" · "3 Send signals to Google Ads"

**Transition:** The Google Ads node grows and becomes the hero object of Scene 9 (push-in onto it).

**Sound:** Satisfying soft "connect" click as each broken link closes · gentle scanner sweep through the filter · light, rising data-transfer shimmer on the return stream · music builds momentum (light percussion enters).

**Purpose:** A plan simple enough for a non-technical owner: three verbs.

**16:9:** Steps laid out left → right; return stream visibly flows right → left, making the "feedback loop" obvious.
**9:16:** Steps stacked top → bottom, each as a large card (full width minus margins); return stream rises bottom → top along the right side.

---

### Scene 9 — Success: Google Sees What Matters
**Master 00:48.30 – 00:58.70 (10.4 s)**

**VO:** "When Google sees the leads that actually matter, it can optimize toward more qualified customers and more revenue."

**Visual concept:** The campaign card from Scene 4 returns — now fed with complete, qualified data. Counters match reality. Performance rises with quiet elegance.

**3D elements:** Same campaign card (now crisp, brand color) · Tracked conversions counter · "Qualified" quality indicator · performance curve · three stacked outcome tiles: Qualified leads, Customers, Revenue · stream of glowing qualified call cards arriving.

**Camera:** Slow push-in, then a smooth upward crane as the outcome tiles stack — upward movement replaces any arrow.

**Animation:**
- 48.56 Card re-forms; status pill reads "Active."
- 49.08 "sees": Tracked conversions climbs 10 → 30 and matches Actual calls; a fine brand line connects the two numbers ("Matched").
- 50.42–51.90 "leads that actually matter": qualified lead cards line up and glow.
- 53.50 "optimize": performance curve lifts gently and smoothly; cost per conversion eases down (`$252` → `$84`).
- 54.92 "qualified customers": outcome tile 1 and 2 rise into place (Qualified leads ↑, Customers ↑).
- 57.90 "revenue": Revenue tile resolves at top of the stack with a soft brand glow.

**On-screen text:** "Better data. Better results." (enters at 53.5) — plus tile labels.

**Transition:** Camera pulls back; the bright campaign card shrinks into the background. A *ghost* of the paused card from Scene 5 slides in front — the alternative future (Scene 10).

**Sound:** Light, positive confirmation tones as counters match · smooth ascending synth arpeggio under the curve · warm, quiet "success" chime on Revenue. Music at its fullest — still under the VO.

**VO direction:** emphasize "When Google sees the leads that actually matter…"

**Purpose:** Show the payoff: better data → better optimization → better business.

**16:9:** Campaign card left; outcome tiles stack on the right as a rising column; curve spans the card.
**9:16:** Big matched counter "30 = 30" top; curve middle; tiles stacked bottom-to-top in the lower half (large type).

---

### Scene 10 — The Stakes: Competitors Capture Them
**Master 00:58.70 – 01:05.80 (7.1 s)**

**VO:** "Otherwise, you may keep pausing campaigns that are working while your competitors capture those customers."

**Visual concept:** The cost of doing nothing. A paused, grey campaign card sits in the foreground. Calls still arrive from the city — but they curve away to a neutral competitor marker.

**3D elements:** Ghosted paused campaign card · simplified, minimal 3D local map tile (light, abstract blocks) · two location pins: "You" (paused, grey) and "Competitor" (neutral dark ink — not branded, not red) · call cards drifting.

**Camera:** Slow lateral dolly from the paused card to the map; slight tilt down to the competitor pin.

**Animation:**
- 58.98 Ghost card fades in front of the success scene.
- 60.44 "pausing": a second toggle on the card clicks off — repetition, quiet.
- 62.54 "working": a faint "Working" tag on the card, showing it was a good campaign.
- 63.76 "competitors": call cards curve away from "You" toward the competitor pin, which brightens subtly.
- 64.90 "those customers": last call card lands at the competitor. Map desaturates slightly.

**On-screen text:** "Paused campaigns that work" → "Competitors capture the calls"

**Transition:** The map gently lifts and dissolves into the clean canvas; call cards reassemble into the shape of the final consultant card (Scene 11).

**Sound:** Single soft toggle click · faint call ring passing by (pan away from center) · music pulls back to a single piano/pad line, ready to resolve.

**Purpose:** Loss aversion — but professional, not fear-driven.

**16:9:** Paused card left, map with two pins right; calls travel left → right away from "You."
**9:16:** "You" pin top, competitor pin bottom; calls fall past "You" to the competitor; paused card small at the very top.

---

### Scene 11 — Final Brand + CTA
**Master 01:05.80 – 01:11.50 (5.7 s)**

**VO:** None (music resolves). Optional: a soft room-tone breath.

**Visual concept:** Clean, confident, premium. The consultant identity card centered, title in full, the key line large, the CTA beneath.

**Final frame layout:** see Section 16.

**Camera:** Very slow push-in (~3% scale over 5 s). Subtle parallax between card and grid. Settles before the end.

**Animation:**
- 65.80 Card assembles from the call cards (they fly in and become the card's edge glow).
- 66.30 Title fades up with the card.
- 66.90 Statement enters word-group by word-group (two lines).
- 68.80 CTA fades up.
- 69.50 – 71.50 Hold. Everything still except a slow breath of the grid.

**On-screen text:**
- Title: Google Ads, Web Analytics, Paid Ads, Web Analytics and Conversion Tracking Consultant
- Statement: **If Google can't see your real leads, it can't optimize for them.**
- CTA: Check your call tracking before you pause your campaign.

**Transition:** Hard hold to end. Optional 0.5 s fade to `canvas`.

**Sound:** Music resolves on a warm major chord; one clean, low-volume confirmation tone at card lock. No logo sting, no impact.

**Purpose:** Brand recall + the one thing to do next.

---

## 13. 16:9 composition instructions (1920×1080)

- **Grid:** 12-column layout, 120 px outer margins, 24 px gutters.
- **Title-safe:** inner 90% (96 px from edges); action-safe 95%.
- **Flow direction:** left → right for problem (calls to nodes), right → left for the fix (signals back to Ads). This visual "loop" is the landscape version's signature.
- **Comparisons:** side by side (30 vs 10, paused vs active).
- **Camera:** wider moves — lateral dollies up to 1.5 frame widths; the Scene 6 pipeline reveal is the widest shot.
- **Text:** headline 64–80 px; data numbers 140–200 px; labels 22–26 px.
- **Captions (if burned in):** lower 15% of frame, max two lines, 40 px, on a soft white pill at 85% opacity.
- **Portrait card:** right third in Scene 7; centered in Scene 11.

## 14. 9:16 composition instructions (1080×1920)

Designed as a separate composition, not a crop.

- **Safe zone:** keep all key visuals and text within **x 90–990 px, y 250–1500 px**. Top 250 px = platform UI/profile; bottom 420 px = captions, CTA buttons, description; right 120 px between y 1100–1700 = like/comment icons.
- **Hierarchy:** one subject per shot, centered. UI cards stacked vertically, each ≥ 85% of safe width.
- **Numbers:** 30 / 10 counters ≥ 180 px tall. Labels ≥ 34 px. Headlines 72–88 px.
- **Flow direction:** top → bottom for problem (calls fall toward the vortex and nodes); bottom → top for the fix (signals rise back to Google Ads) and success (tiles stack upward).
- **Camera:** tighter framing, shorter moves; vertical cranes instead of lateral dollies.
- **Captions:** strongly recommended (sound-off viewing). Place at y ≈ 1180–1380 px, inside the safe zone, max two lines, 44 px, white pill. Do not overlap the main number in Scenes 3 and 9 — move the number up when captions are on.
- **Hook:** first frame must already show the phone ringing (no fade from white) — vertical feeds decide in under a second.
- **Scene-specific changes:**
  - Scene 1: chips in a 2×2 grid below the phone.
  - Scene 3: 30-slot bar becomes a 6×5 icon grid.
  - Scene 6: pipeline becomes a vertical spine.
  - Scene 8: steps become three stacked full-width cards.
  - Scene 11: card upper half, statement middle, CTA lower — all above y 1500.

## 15. Brand integration instructions

- **Colors:** apply brand tokens (Section 2) to data streams, tracked call cards, step badges, node glyphs, chart lines, buttons, title accents, the portrait card edge. Replace the provisional hex values with the brand reference once supplied; do not add any extra hues.
- **Warning colors:** `warn` and `loss` only on untracked call rims, the "Underperforming" pill, "Campaign Paused," lost-revenue tiles. Never on the consultant card, the plan, or the success scene.
- **Portrait:** three appearances only — Scene 7 (identity card), Scene 8 (small badge, top corner, until Step 3 completes), Scene 11 (hero card). Never altered, never stylized, color-matched to scene lighting.
- **Title:** use exactly "Google Ads, Web Analytics, Paid Ads, Web Analytics and Conversion Tracking Consultant." Full title appears in Scene 11. In 9:16 it may wrap to three lines; do not shorten.
- **Logo:** if a personal logo/wordmark exists, place it small on the final card (bottom of card), never as an animated sting.
- **Typeface:** brand typeface if one exists; otherwise Inter/Manrope.
- **Google references:** generic "Ads" glyph and layout only. No Google logo, Google colors, or exact interface reproduction.

## 16. Final frame design

**16:9 (1920×1080)**
```
┌──────────────────────────────────────────────────────────────┐
│  faint grid floor, canvas #F7F9FB                            │
│                                                              │
│   ┌───────────────┐    If Google can't see your real leads,  │
│   │   [PORTRAIT]  │    it can't optimize for them.           │
│   │               │    (Headline, ink, 600, ~64 px)          │
│   │  Name         │                                          │
│   │  Google Ads,  │    ─────                                 │
│   │  Web Analytics│    Check your call tracking before you   │
│   │  , Paid Ads,  │    pause your campaign.                  │
│   │  Web Analytics│    (Supporting, ink-2, 400, ~30 px)      │
│   │  and Conv.    │                                          │
│   │  Tracking     │    ● status dot (brand-primary, steady)  │
│   │  Consultant   │                                          │
│   └───────────────┘                                          │
└──────────────────────────────────────────────────────────────┘
```
- Card: left 40%, glass, 24 px radius, soft shadow on grid. Title in full, 22–24 px, 3–4 lines.
- Statement: right 55%, left-aligned, two lines.
- A thin brand-primary data line runs from the card's edge into the underline of the statement — the "connected" motif.

**9:16 (1080×1920)**
```
┌────────────────────────┐
│   (top 250 px clear)   │
│    ┌──────────────┐    │
│    │  [PORTRAIT]  │    │
│    │  Name        │    │
│    │  Full title  │    │
│    │  (3 lines)   │    │
│    └──────────────┘    │
│                        │
│  If Google can't see   │
│  your real leads, it   │
│  can't optimize for    │
│  them.                 │
│                        │
│  Check your call       │
│  tracking before you   │
│  pause your campaign.  │
│  (all above y 1500)    │
│   (bottom 420 px clear)│
└────────────────────────┘
```

---

## 17. Music direction

- **Genre:** minimal modern corporate-tech — soft synth pads, felt piano, light plucks, gentle percussion. No EDM drops, no trailer hits.
- **Tempo:** ~92–100 BPM.
- **Key arc:** minor-leaning (Scenes 1–6) → resolves to relative major at "Here's the fix" (37.96).

| Section | Master time | Music |
|---|---|---|
| Hook | 0.0–9.3 | Calm, curious: plucked motif + airy pad |
| Problem | 9.3–22.9 | Minor pad, light tension, soft pulse |
| Consequence | 22.9–31.0 | Thinner; sparse, slightly melancholic |
| Reveal | 31.0–37.9 | Tension peak, then drop to near-silence in the 1.3 s pause |
| Fix | 37.9–48.3 | Major resolve, forward beat, momentum |
| Success | 48.3–58.7 | Fullest point, warm and confident |
| Stakes | 58.7–65.8 | Pull back to piano + pad |
| End card | 65.8–71.5 | Warm resolve, clean tail |

**Mix:** music −22 to −26 LUFS short-term under VO; duck an extra 3 dB on emphasized lines. Final master −14 LUFS integrated (social), true peak −1 dBTP. Optionally deliver a −16 LUFS version for YouTube/web.

## 18. Sound effects — master cue list

| Master | SFX | Level |
|---|---|---|
| 0.00 | Soft phone ring (one cycle) + haptic buzz | Medium-low |
| 1.88 / 3.12 / 3.86 / 4.32 | Notification tick per chip (rising pitch) | Low |
| 5.90 | Light pops as call cards appear | Low |
| 7.92 | Subtle value shimmer | Very low |
| 9.4–10.7 | Data-transfer ticks on arrivals | Low |
| 11.92 → 13.2 | Soft descending "whoom" per lost call | Low |
| 14.90 | Counter tick-roll | Low |
| 18.02 | Clean lock click on "10" | Medium-low |
| 18.4 | Hollow "tock" as slots drain | Low |
| 21.46 | UI flip on status pill | Low |
| 23.94 | Slider drag | Low |
| 24.54 | Toggle click (campaign pause) | Medium-low |
| 27.0–29.6 | Soft falling tones per lost lead | Very low |
| 31.2 | Airy whoosh on pull-back | Low |
| 32.6 | Gentle chime on Ads check | Low |
| 34.0 | Faint crackle on broken connectors | Very low |
| 37.96 | Card click-in | Low |
| 39.76 / 41.5 / 44.78 | Connector "snap" per step | Low |
| 42.5 | Scanner sweep through filter | Very low |
| 45.0–47.5 | Rising data shimmer on return stream | Low |
| 49.08 | Counter roll + match confirmation | Low |
| 57.90 | Warm success chime | Low |
| 60.44 | Toggle click | Very low |
| 63.76 | Passing phone ring, panning away | Very low |
| 66.0 | Single soft confirmation tone (card lock) | Low |

All SFX sit below the VO (≈ −10 dB relative). No lasers, no game sounds, no impacts.

## 19. Voiceover direction (for reference or pickups)

Confident, conversational, consultative — an experienced consultant talking to one owner across a desk. Not a commercial read. Keep the recorded pauses. Emphasis words:
- "Google **only sees 10** conversions."
- "The problem may **not** be your ads."
- "Your tracking may be **hiding** the real performance."
- "When Google sees the leads that **actually matter**…"

---

## 20. Consolidated master production prompt

Use this as the single master prompt for an AI video workflow. Generate each scene as its own shot using the scene block that follows, then assemble on the master timeline locked to the voiceover.

> **MASTER PROMPT — "The Phone Call Black Hole"**
>
> Create a premium, light-themed 3D motion-graphics explainer for a Google Ads, Web Analytics, Paid Ads, Web Analytics and Conversion Tracking Consultant. Audience: local service business owners (personal injury law firms, HVAC, roofing, plumbing) who rely on phone calls from Google Ads. Runtime 71.5 seconds, locked to the supplied voiceover placed at 0.5 s. Deliver two separately composed versions: 16:9 (1920×1080) and 9:16 (1080×1920) — the vertical version is re-composed, not cropped.
>
> **Look:** bright near-white canvas (#F7F9FB) with a faint perspective grid floor; realistic-but-simplified 3D; frosted-glass UI panels with soft shadows, subtle reflections, clean edges and controlled depth; large soft key light from top-left. Palette restrained to brand colors (provisional: brand-primary #20B4CE, brand-deep #0B5F78, brand-tint #E3F6FA, ink #0E1A2B); amber #F08A24 and red #E5484D only on small elements for untracked calls, "Underperforming," "Campaign Paused," and lost revenue. Modern sans-serif type, 3–7 words per scene. Premium SaaS/editorial feel — not cartoon, not flat infographic, not whiteboard, not cyberpunk, not gaming, not dark cinematic.
>
> **Central metaphor:** phone calls are luminous call cards. Tracked calls flow into Ads, Analytics and CRM nodes. Untracked calls slip into a soft, elegant, pearl-grey vortex in the grid — "the phone call black hole" — a calm data visualization of missing conversion data, never scary or sci-fi.
>
> **Story (11 shots):**
> 1. (0.0–9.3) Satin-white smartphone ringing on the grid; four industry chips (Law Firm, HVAC, Roofing, Plumbing) land in sync with the VO; call cards fan out with value tags. One card flickers amber.
> 2. (9.3–13.6) Calls stream toward Ads/Analytics/CRM nodes; the grid bends into the soft vortex; some calls arrive with checks, others slip in. Text: "Your best leads may be disappearing."
> 3. (13.6–19.4) Clean glass dashboard: Actual calls 30 vs Tracked conversions 10; a 30-slot bar where 20 slots drain to hollow. Text: "20 missing."
> 4. (19.4–22.9) Generic ad-platform campaign card (no Google branding); cost per conversion rises; line flattens; amber pill flips to "Underperforming."
> 5. (22.9–31.0) A hand drags the budget slider down and toggles "Campaign Paused"; behind the card, glowing high-value lead cards fade to grey one by one; tiles: Lost leads, Lost customers, Lost revenue.
> 6. (31.0–37.3) Long pull-back to reveal the pipeline Ads → Website/Phone → Tracking → Google Ads → CRM. Ads node gets a calm check ("Not your ads."); Tracking node shows broken dashed connectors and the vortex inside it ("Your tracking."). Hold during the pause.
> 7. (37.3–39.6) The consultant's identity card (real, unaltered portrait photo in a glass card) slides in; status dot turns from amber to brand color; music resolves to major.
> 8. (39.6–48.3) Three steps, one continuous move: 1 Track calls (connectors snap solid, vortex closes), 2 Identify qualified leads (filter gate splits qualified vs not-a-fit), 3 Send signals to Google Ads (a bright stream flows back from CRM to the Ads node).
> 9. (48.3–58.7) Campaign card returns crisp: tracked conversions climb 10 → 30 and match actual calls; performance curve lifts smoothly; Qualified leads, Customers, Revenue tiles stack upward. Text: "Better data. Better results."
> 10. (58.7–65.8) Ghosted paused card; minimal light 3D map; calls curve away from "You" to a neutral "Competitor" pin.
> 11. (65.8–71.5) Final card: portrait identity card with the full title "Google Ads, Web Analytics, Paid Ads, Web Analytics and Conversion Tracking Consultant"; headline "If Google can't see your real leads, it can't optimize for them."; CTA "Check your call tracking before you pause your campaign." Calm hold.
>
> **Camera:** slow push-ins, smooth dollies, gentle 10–15° orbits, parallax, controlled zoom. No fast spins, whip pans, extreme zooms, glitches, explosions or lens flares. Every transition is a continuous match-move: call cards → vortex → dashboard → campaign card → pipeline → plan → success → map → final card.
>
> **Portrait rules:** use the supplied photo exactly. Do not redesign, stylize or cartoon the face. Appears only in shots 7, 8 (small badge) and 11.
>
> **Sound:** natural, soft UI sounds (phone ring, ticks, toggle click, data shimmer, connect snaps, success chime). Music: minimal modern tech score, 92–100 BPM, calm → tense → resolves at "Here's the fix" → confident → warm finish. Always under the voiceover.
>
> **16:9:** horizontal flows (problem left→right, fix right→left), side-by-side comparisons, spacious dashboards, wider camera moves.
> **9:16:** centered subjects, vertically stacked cards, numbers ≥ 180 px, flows top→bottom for the problem and bottom→top for the fix; keep text inside x 90–990, y 250–1500.

### Per-shot generation prompts (for clip-based AI tools)

Append the master "Look" paragraph to each.

1. *Premium white smartphone floating above a light grid floor, incoming call glowing on screen, four rounded glass chips with line icons (scales, snowflake, roof, pipe) orbiting into place, small glowing call cards fanning out with dollar value tags, soft studio light, slow pull-back with slight orbit.*
2. *Stream of small luminous call cards flowing across a light grid toward three rounded tiles (ad glyph, chart glyph, contact glyph); the grid floor gently bends into a soft pearl-grey spiral vortex; some cards arrive with a teal check, others curve elegantly into the vortex with a faint amber trail; calm lateral dolly.*
3. *Frosted glass analytics panel on a light background, two large numbers "30" and "10" with labels "Actual calls" and "Tracked conversions," a bar of 30 small phone icons where 20 drain to hollow outlines, slow push-in.*
4. *Generic glass advertising campaign card with a flat line chart and a status pill flipping to amber "Underperforming," gentle 10° orbit, no real brand logos.*
5. *Stylized hand lowering a budget slider and switching a campaign toggle off on a glass card; behind it, glowing lead cards ("Roof replacement $14,800," "AC install $7,200") fade to grey one by one; soft pull-back.*
6. *Wide elevated view of five rounded nodes connected by light streams on a grid: Ads, Website/Phone, Tracking, Google Ads, CRM; the Tracking node is a translucent glass slab with a small soft vortex inside and broken amber dashed connectors; slow crane up then push toward Tracking.*
7. *Glass professional identity card with the supplied portrait photo (unaltered) slides in beside the Tracking node; a small status dot turns from amber to teal; the vortex flattens.*
8. *Three-step sequence on a light grid: calls pass through a tracking node with checks and connectors snap solid; calls pass through a glass filter plane and split into glowing qualified cards and grey discarded cards; a bright teal data stream flows back into an ads node; continuous dolly.*
9. *Crisp glass campaign card with counter rising from 10 to 30 matching a second counter, smooth rising performance curve, three tiles (Qualified leads, Customers, Revenue) stacking upward with soft glow; slow crane up.*
10. *Grey paused campaign card in foreground, minimal light 3D map with two pins "You" and "Competitor," small call cards curving away to the competitor pin; slow lateral dolly.*
11. *Clean final card: glass identity card with portrait and full title, headline text beside it, thin teal line connecting them, faint grid floor, very slow push-in, calm hold.*

---

## Delivery checklist

- [ ] Replace provisional palette with brand reference
- [ ] Confirm the two flagged VO words by ear (Section 0)
- [ ] Trim VO tail silence (file 65.5–66.7 s)
- [ ] 16:9 master — 1920×1080, 30 fps (or 25), H.264/ProRes
- [ ] 9:16 master — 1080×1920, re-composed, captions burned in
- [ ] SRT for 16:9 uploads (YouTube/LinkedIn)
- [ ] Loudness: −14 LUFS social / −16 LUFS web, −1 dBTP
