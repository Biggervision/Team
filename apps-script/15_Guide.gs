/**
 * Module 15 — 📖 Guide (in-sheet manual)
 */

function buildGuide(ctx) {
  const sh = freshSheet(ctx, SHEETS.guide);
  sh.setColumnWidth(1, 18);
  sh.setColumnWidth(2, 30);
  sh.setColumnWidth(3, 900);
  pageTitle(sh, 2, 2, 3, '📖 Guide — how to run ASCENSION OS™', '');

  const sections = [
    ['🧭', 'THE OPERATING SYSTEM', [
      'Everyone gets 24 hours a day and 168 hours a week. ASCENSION OS™ treats them like a budget: design the allocation on 🌟 Ideal Week, commit this week\'s version on 📆 Current Week, execute and log on 📅 Daily Tracker — and every dashboard, review and chart reconciles automatically.',
      'Every operational sheet carries the same executive dashboard at the top (used, remaining, weekly/monthly/annual hours, productive, free, utilization, balance) plus a live line showing what you have logged today, this week, this month and this year — so you never switch tabs just to know where you stand.',
    ]],
    ['✏️', 'RULE #1 — ONLY EDIT BLUE CELLS', [
      'Every editable cell has a light-blue background. Everything else is a formula. If a cell is not blue, you never need to touch it.',
    ]],
    ['🚀', 'THE OPERATING LOOP', [
      '1.  DESIGN — answer the guided sentences on 🌟 Ideal Week (once, then refine).',
      '2.  COMMIT — on 📆 Current Week, optionally override any category for this specific week ("My plan"). Blank = ideal.',
      '3.  EXECUTE — log real blocks on 📅 Daily Tracker: date, category, hours, notes. The Today panel scores your day live.',
      '4.  REVIEW — 🗓️ Monthly Review and 🎯 Annual Review build themselves from your log. 📊 Dashboard is the command centre.',
    ]],
    ['➕', 'CUSTOM CATEGORIES & GOALS', [
      'Add categories in the blue rows at the bottom of the ⚙️ Settings master table — they appear everywhere instantly.',
      'Work days, sleep goal, weekly productive target and the visual theme also live on ⚙️ Settings. After changing the theme, run ⚡ Ascension OS → Apply Theme.',
    ]],
    ['🎯', 'BALANCE SCORE', [
      'A 0–100 gauge of how humane the week is: sleep at goal, total work (work + deep work + meetings) ≤ 55 h, fitness ≥ 3 h, relationships ≥ 3 h, learning + personal development ≥ 2 h, free time ≥ 5 h, nothing over-allocated. 80+ = sustainable executive week.',
    ]],
    ['🔁', 'MAINTENANCE', [
      'New week: nothing to do — the week window follows today\'s date automatically. Use ⚡ menu → "Clear This Week\'s Plan" to drop overrides.',
      'The Daily Tracker holds 200 log rows; archive or clear old rows via ⚡ menu → "Clear Daily Log" when you start a fresh period.',
      'Factory reset: ⚡ Ascension OS → Build / Rebuild System (this resets inputs — note them first).',
    ]],
  ];

  let row = 4;
  sections.forEach(sec => {
    band(sh, row, 2, 3, '  ' + sec[0] + '  ' + sec[1]);
    row++;
    sec[2].forEach(p => {
      sh.getRange(row, 3).setValue(p).setFontColor(UI.slate).setWrap(true);
      sh.setRowHeight(row, Math.max(24, Math.ceil(p.length / 110) * 16 + 8));
      row++;
    });
    row++;
  });
}
