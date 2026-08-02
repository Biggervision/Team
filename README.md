# ⚡ 168-Hour Executive Time Operating System

A complete, formula-driven **Executive Time OS for Google Sheets** — built for founders,
freelancers, digital nomads and remote professionals who need to see exactly where all
168 hours of their week go.

This repo contains a **one-click builder**: paste a single script into your Google Sheet,
click one menu item, and the entire system is generated natively inside your sheet.
After the build, everything runs on pure Google Sheets formulas (`LET`, `XLOOKUP`,
`FILTER`, `SUMIFS`, named ranges) — **no scripts are needed for day-to-day use**.

---

## 🚀 Install (≈2 minutes)

1. Open your Google Sheet
   (e.g. [your Ascension OS sheet](https://docs.google.com/spreadsheets/d/1Qqj0B21HB2ksWDyqNOPW_tYsrpyKMaT7m-qUOtnyZJM/edit)
   — or a fresh blank sheet; existing tabs you created are untouched).
2. Menu: **Extensions → Apps Script**.
3. Delete any code in the editor, paste the full contents of
   [`apps-script/Code.gs`](apps-script/Code.gs), press **Save** (💾).
4. **Reload the spreadsheet tab** in your browser. A new menu **⚡ Executive OS** appears
   after a few seconds.
5. Click **⚡ Executive OS → Build / Rebuild System** and authorise when Google asks
   (it only touches this spreadsheet).
6. ~30 seconds later the full OS is built and you land on the Dashboard.

> **Why a builder script?** Google Sheets can't be generated from outside your account
> without access to it. The script is only the *installer* — the finished spreadsheet is
> 100 % native formulas, charts and formatting, exactly as if it had been hand-built.

---

## 🧭 What gets built

| Tab | Role |
|---|---|
| **📊 Dashboard** | KPI cards (Hours Used, Hours Free, Utilization %, Balance Score, Productive Hours, Sleep), Daily/Weekly/Monthly/Yearly horizons table, live Signals panel, allocation table, donut + bar charts |
| **⚙️ Inputs** | The *only* place you plan. Guided sentences per life area ("I sleep for around `7.5` hours per night") — edit blue cells only, weekly hours compute per line |
| **📅 Daily Tracker** | Log actual hours per category, Mon–Sun. Day totals warn when a day exceeds 18 h / 24 h |
| **📈 Weekly Tracker** | Planned vs Actual vs Difference, % of plan, % of week, in-cell progress bars, utilization & remaining hours |
| **🗓️ Monthly Tracker** | Monthly projections (× 4.35 weeks), extrapolated actuals, variance, plan-vs-actual sparklines |
| **🎯 Annual Tracker** | Annual hours / days / weeks / % per category + "perspective" facts ("you will sleep 121 full days this year") |
| **📉 Charts** | Large-format donut, bar and planned-vs-actual column charts + their auto data feeds |
| **🔧 Settings** | Single source of truth: constants (24 h/day, 168 h/week, weeks/month, weeks/year), master category table, **5 custom category slots**, editable healthy Min/Max thresholds, productive-hours flags |
| **📖 Guide** | In-sheet user manual |

### Default life areas
Sleep · Work · Food · Household Chores · Childcare · Fitness · Entertainment ·
Relationships · Learning · Personal Development · Spiritual · Travel · Admin
(+ Free Time, computed) — plus **5 blank custom slots** that flow into every tracker
and chart automatically the moment you name them.

---

## 🧱 Architecture — *input once, calculate everywhere*

```
⚙️ Inputs ──► PLAN_* named ranges ──► 🔧 Settings master table
                                        │  (CAT_NAMES / CAT_HOURS /
                                        │   TOTAL_USED / FREE_TIME / PRODUCTIVE_H)
              ┌─────────────┬───────────┼─────────────┬──────────────┐
              ▼             ▼           ▼             ▼              ▼
        📅 Daily      📈 Weekly    🗓️ Monthly    🎯 Annual      📊 Dashboard
        (FILTER +     (XLOOKUP     (× WEEKS_    (× WEEKS_      + 📉 Charts
         XLOOKUP)      vs Daily)    MONTH)       YEAR)          (auto feeds)
```

Design rules the build follows:

- **Zero hardcoded values in formulas.** 24, 168, 4.35, 52.18 all live as named
  constants on Settings (`HOURS_DAY`, `HOURS_WEEK`, `WEEKS_MONTH`, `WEEKS_YEAR`).
- **Categories are data, not structure.** Trackers pull the category list via
  `FILTER(CAT_NAMES, …)` and match hours via `XLOOKUP`, so adding a custom category
  never breaks anything.
- **Blue cell = editable. Everything else = formula.** Formula areas carry
  warning-only protection so accidental edits prompt before overwriting.
- **Validation everywhere.** Inputs accept only sane numbers (0–7 for days/week,
  0–24 for daily logs); productive flags are checkboxes.
- **Conditional formatting as an early-warning system:** Work > 60 h → red,
  Sleep < 49 h → red, Fitness < 3 h → yellow, over-allocating past 168 h → red,
  healthy free-time buffer → green, neglected categories (< 50 % of plan) → amber.

### Balance Score (0–100)
One glanceable number for how humane the week is. Checks: sleep within 49–63 h,
work ≤ 55 h, fitness ≥ 3 h, relationships ≥ 3 h, learning + personal development ≥ 2 h,
free time ≥ 5 h, and nothing over-allocated. **80+ = sustainable executive week.**

---

## 🔁 Everyday use

- **Plan:** adjust blue cells on ⚙️ Inputs — dashboard, trackers and charts update live.
- **Track:** type real hours into the blue grid on 📅 Daily Tracker.
- **Review:** 📈 Weekly Tracker shows the plan-vs-reality gap; 🚦 Signals on the
  Dashboard tell you what to fix first.
- **New week:** select the blue grid on 📅 Daily Tracker and press Delete. Plans stay.
- **Add a category:** type a name + hours in a blue row at the bottom of the
  🔧 Settings master table. Done — it's everywhere.
- **Factory reset:** ⚡ Executive OS → Build / Rebuild System (this resets inputs to
  defaults, so note yours down first).

---

## 📁 Repo layout

```
apps-script/
  Code.gs           ← the entire builder (paste this into Extensions → Apps Script)
docs/
  DEPLOYMENT.md     ← full deployment & integration guide (auth flow, clasp CLI,
                      template distribution, troubleshooting)
README.md           ← you are here
```

Deploying for the first time? Follow **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** —
it covers the exact click path, the Google authorization screens, CLI deployment
with `clasp`, how to distribute the finished sheet as a template, and fixes for
every common hiccup.
