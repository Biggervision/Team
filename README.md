# ⚡ ASCENSION OS™ — Executive 168-Hour Operating System (v2.0)

A complete, formula-driven **Personal Operating System for Google Sheets** — built for
founders, freelancers, consultants, agency owners, creators and remote professionals
who want to intentionally design, execute and review every one of their 168 weekly hours.

This is not a time tracker. It is a full operating loop:
**Design → Commit → Execute → Review**, with a contextual executive dashboard on
every sheet so you never switch tabs just to know where you stand.

---

## 🚀 Install the v2.0 system (≈2 minutes)

1. Open your Google Sheet → **Extensions → Apps Script**.
2. Delete the placeholder code, paste the full contents of
   **[`dist/AscensionOS.gs`](dist/AscensionOS.gs)** (single-file bundle of all
   modules), press **Save**.
3. Reload the spreadsheet → a **⚡ Ascension OS** menu appears.
4. **⚡ Ascension OS → Build / Rebuild System** → authorize → ~60 s later the OS is live.

Full illustrated walkthrough (with screenshots of every step, the authorization
screens, `clasp` CLI deployment and troubleshooting):
**[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

### ⚡ No-code path (recommended): upload the ready-made file

**[`Ascension-OS-v2.xlsx`](Ascension-OS-v2.xlsx)** is the complete v2.0 system as a
file — 1,400+ formulas, verified error-free:

1. [drive.google.com](https://drive.google.com) → **New → File upload** → pick the file.
2. Double-click it → opens in Google Sheets → **File → Save as Google Sheets**. Done.

Everything below is already inside (KPI strip on every sheet, all 8 tabs, charts,
warnings, category dropdowns). Only two v2 features need the Apps Script build
instead: switchable themes and the ⚡ menu utilities.
(Built by `tools/build_xlsx_v2.py`; the v1 file `168-Hour-Executive-OS.xlsx`
remains for reference.)

---

## 🧭 What v2.0 builds

Every operational sheet opens with the **same executive dashboard strip** — Hours
Used, Remaining, Weekly/Monthly/Annual Hours, Productive, Free Time, Utilization %,
Balance Score — plus a live line of what you've logged **today · this week · this
month · this year**. Then: guided inputs in the middle, analysis at the bottom.

| Sheet | Role |
|---|---|
| **📊 Dashboard** | Executive overview only (no inputs): 🚦 Signals, 🎯 Goal Progress vs your targets, 📈 4-week logged-hours trend, 💡 Executive Insights, ⚖️ Life Balance table, donut + bar + planned-vs-actual charts |
| **🌟 Ideal Week** | Conversational design of your 168 hours ("I sleep for around `8` hours per night…") across 17 life areas; every section shows weekly + monthly + annual estimates, % of week, and the cascading *"That leaves me with…"* |
| **📆 Current Week** | Commit this week's plan (blank = ideal), watch Actual / Variance / Remaining / % of plan / progress bars fill in live from the Daily Tracker |
| **📅 Daily Tracker** | The execution engine: date-stamped log (Date, Day, Category, Planned, Actual, Notes) with a live **Today panel** (daily total, remaining, productivity score) and a Last-7-Days scoreboard |
| **🗓️ Monthly Review** | Auto-built from the log: monthly summary, weekly breakdown (W1–W5), category ranking, variance, monthly insights |
| **🎯 Annual Review** | Annual plan vs actual YTD, on-pace %, annual days, life balance, Year-in-Review narrative |
| **⚙️ Settings** | Lightweight config: Work Days, Sleep Goal, Weekly Productive Target, **Theme** (Teal / Navy / Forest — apply without rebuilding), constants, master category table + **5 custom category slots** |
| **📖 Guide** | The operating manual, inside the sheet |

### Life areas (17 defaults + custom)
Sleep · Work · **Deep Work** · **Meetings** · Food · Household Chores · Childcare ·
Fitness · Entertainment · Relationships · Learning · Personal Development · Spiritual ·
Travel · Admin · **Business Development** · **Content Creation** (+ Free Time, computed,
and 5 custom slots that propagate everywhere instantly).

---

## 🧱 Architecture

**Input once → calculate everywhere.** 24 h/day and 168 h/week are the only axioms;
everything else is derived through named ranges — no hardcoded values in formulas.

```
🌟 Ideal Week ──► PLAN_* ──► ⚙️ Settings master table (CAT_NAMES / CAT_HOURS / CAT_PROD)
                                      │
📆 Current Week (CW_EFF plan) ◄───────┤
        ▲  actuals via SUMIFS         │
📅 Daily Tracker log (LOG_DATE / LOG_CAT / LOG_ACT / LOG_PROD)
        │
        └──► 🗓️ Monthly Review · 🎯 Annual Review · 📊 Dashboard · charts
```

### Modular Apps Script codebase (`apps-script/`)
`00_Config` · `01_Theme` · `02_Utilities` · `03_FormatValidate` · `04_ContextDash` ·
`05_Builder` · `06_Settings` · `07_IdealWeek` · `08_CurrentWeek` · `09_Daily` ·
`10_Monthly` · `11_Annual` · `12_Dashboard` · `13_Charts` · `14_Reports` · `15_Guide`

Each module is independent; `tools/build_gs_bundle.py` concatenates them into the
pasteable **`dist/AscensionOS.gs`**. Apps Script is used **only to build** — after the
build the workbook runs on native formulas (SUMIFS, FILTER, XLOOKUP, INDEX/MATCH,
SPARKLINE, named ranges).

### Guardrails
- **Blue cell = editable; everything else is a formula** (with warning-only protection).
- Data validation everywhere (dates, 0–24 h logs, category dropdowns, checkboxes).
- Conditional formatting: day > 24 h red / > 18 h amber, sleep below goal red, work
  above target orange, fitness below goal yellow, over-allocation red, healthy
  balance green, category over/under plan flags.
- **Balance Score (0–100):** sleep at goal, total work (work + deep work + meetings)
  ≤ 55 h, fitness ≥ 3 h, relationships ≥ 3 h, learning + PD ≥ 2 h, free time ≥ 5 h,
  nothing over-allocated. 80+ = sustainable executive week.
- ⚡ menu utilities: Apply Theme, Clear This Week's Plan, Clear Daily Log.

---

## 📁 Repo layout

```
apps-script/          ← 16 modular .gs source files (v2.0)
dist/AscensionOS.gs   ← single-file bundle: paste THIS into Apps Script
tools/
  build_gs_bundle.py  ← regenerates dist/AscensionOS.gs from the modules
  build_xlsx.py       ← builds the v1 no-code xlsx
168-Hour-Executive-OS.xlsx  ← v1 no-code quick start (Drive upload)
docs/
  DEPLOYMENT.md       ← illustrated install & distribution guide
  images/             ← step-by-step install illustrations
```
