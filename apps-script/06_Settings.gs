/**
 * Module 06 — Settings
 * Lightweight configuration: goals, theme, constants, master category table
 * (the data hub every other sheet reads), custom categories, chart feeds.
 */

function buildSettings(ctx) {
  const sh = freshSheet(ctx, SHEETS.settings);
  const ss = ctx.ss;
  const widths = [18, 46, 190, 92, 82, 78, 88, 82, 82, 100, 20, 200, 92, 92, 92];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 10, '⚙️ Settings',
    'Goals, theme and master data. Add custom categories in the blue rows — every sheet picks them up automatically.');

  // -- Goals & setup ---------------------------------------------------------
  band(sh, 5, 2, 10, '  🎯  GOALS & SETUP');
  const goals = [
    ['Work days per week',           6,   'WORK_DAYS',     0, 7,
     'Drives lunch, commute, deep-work and non-work-day formulas.'],
    ['Sleep goal (hours per night)', 7.5, 'SLEEP_GOAL',    0, 14,
     'Feeds the Balance Score and sleep warnings.'],
    ['Weekly productive target (h)', 45,  'WEEKLY_TARGET', 0, 120,
     'Goal-progress bars measure productive hours against this.'],
  ];
  goals.forEach((g, i) => {
    const r = 6 + i;
    sh.getRange(r, 2, 1, 2).merge().setValue(g[0]).setFontColor(UI.slate);
    const cell = sh.getRange(r, 4).setValue(g[1]);
    inputCell(cell);
    numberValidation(cell, g[3], g[4]);
    ss.setNamedRange(g[2], cell);
    sh.getRange(r, 5, 1, 5).merge().setValue(g[5])
      .setFontSize(8).setFontColor(UI.faint);
  });
  const themeRow = 9;
  sh.getRange(themeRow, 2, 1, 2).merge().setValue('Theme').setFontColor(UI.slate);
  const themeCell = sh.getRange(themeRow, 4, 1, 2).merge();
  inputCell(themeCell);
  sh.getRange(themeRow, 4).setValue(ctx.themeName || DEFAULT_THEME);
  sh.getRange(themeRow, 4).setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireValueInList(Object.keys(THEMES), true).setAllowInvalid(false).build());
  ss.setNamedRange('THEME_NAME', sh.getRange(themeRow, 4));
  sh.getRange(themeRow, 6, 1, 5).merge()
    .setValue('Pick a theme, then run  ⚡ Ascension OS → Apply Theme.')
    .setFontSize(8).setFontColor(UI.faint);

  // -- Constants -------------------------------------------------------------
  band(sh, 11, 2, 10, '  ⏱️  CONSTANTS');
  const constants = [
    ['Hours per day',   '24',           'HOURS_DAY'],
    ['Hours per week',  '=HOURS_DAY*7', 'HOURS_WEEK'],
    ['Weeks per month', '4',            'WEEKS_MONTH'],
    ['Weeks per year',  '52',           'WEEKS_YEAR'],
  ];
  constants.forEach((c, i) => {
    const r = 12 + i;
    sh.getRange(r, 2, 1, 2).merge().setValue(c[0]).setFontColor(UI.slate);
    const cell = sh.getRange(r, 4);
    if (String(c[1]).charAt(0) === '=') cell.setFormula(c[1]); else cell.setValue(Number(c[1]));
    cell.setNumberFormat('0.###').setFontWeight('bold').setHorizontalAlignment('center');
    ss.setNamedRange(c[2], cell);
  });
  sh.getRange(13, 5, 1, 6).merge()
    .setValue('Executive convention: 4 weeks/month, 52 weeks/year. Use 4.345 / 52.18 for calendar-accurate maths.')
    .setFontSize(8).setFontColor(UI.faint);

  // -- Master category table -------------------------------------------------
  const tbl = 17;
  band(sh, tbl, 2, 10, '  🗂️  MASTER CATEGORY TABLE');
  headerRow(sh, tbl + 1, 2, ['', 'Category', 'Ideal h/wk', '% of week', 'Per day',
                             'Productive', 'Min h/wk', 'Max h/wk', 'Status']);
  const first = tbl + 2;
  const lastCore = first + CATEGORIES.length - 1;
  const last = lastCore + CUSTOM_SLOTS;

  CATEGORIES.forEach((cat, i) => {
    const r = first + i;
    sh.getRange(r, 2).setValue(cat.emoji).setHorizontalAlignment('center');
    sh.getRange(r, 3).setValue(cat.name);
    sh.getRange(r, 4).setFormula('=ROUND(PLAN_' + cat.key + ',2)');
    sh.getRange(r, 8).setValue(cat.min === '' ? '' : cat.min);
    sh.getRange(r, 9).setValue(cat.max === '' ? '' : cat.max);
  });
  for (let i = 0; i < CUSTOM_SLOTS; i++) {
    const r = lastCore + 1 + i;
    inputCell(sh.getRange(r, 2, 1, 2)).setHorizontalAlignment('left');
    sh.getRange(r, 2).setHorizontalAlignment('center');
    inputCell(sh.getRange(r, 4));
    numberValidation(sh.getRange(r, 4), 0, 168);
    sh.getRange(r, 3).setNote('Type a custom category name — it flows into every sheet.');
  }
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 5).setFormula('=IF($C' + r + '="","",$D' + r + '/HOURS_WEEK)');
    sh.getRange(r, 6).setFormula('=IF($C' + r + '="","",$D' + r + '/7)');
    sh.getRange(r, 10).setFormula(
      '=IF($C' + r + '="","",IF(AND($H' + r + '<>"",$D' + r + '<$H' + r + '),"🔻 Low",' +
      'IF(AND($I' + r + '<>"",$D' + r + '>$I' + r + '),"🔺 High","✅ OK")))');
  }
  const prodRange = sh.getRange(first, 7, TRACKER_ROWS, 1);
  prodRange.insertCheckboxes();
  CATEGORIES.forEach((cat, i) => sh.getRange(first + i, 7).setValue(cat.productive));
  inputCell(sh.getRange(first, 8, TRACKER_ROWS, 2));
  sh.getRange(first, 8, TRACKER_ROWS, 2).setNote(
    'Optional healthy range (h/week) — drives Status and colour warnings.');

  sh.getRange(first, 4, TRACKER_ROWS, 3).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 5, TRACKER_ROWS, 1).setNumberFormat('0.0%');
  sh.getRange(first, 8, TRACKER_ROWS, 2).setNumberFormat('0.0');
  sh.getRange(first, 10, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  gridBorder(sh.getRange(first, 2, TRACKER_ROWS, 9));

  ss.setNamedRange('CAT_EMOJI', sh.getRange(first, 2, TRACKER_ROWS, 1));
  ss.setNamedRange('CAT_NAMES', sh.getRange(first, 3, TRACKER_ROWS, 1));
  ss.setNamedRange('CAT_HOURS', sh.getRange(first, 4, TRACKER_ROWS, 1));
  ss.setNamedRange('CAT_PROD',  sh.getRange(first, 7, TRACKER_ROWS, 1));

  const tot = last + 2;
  sh.getRange(tot, 3).setValue('Total allocated').setFontWeight('bold');
  ss.setNamedRange('TOTAL_USED', sh.getRange(tot, 4)
    .setFormula('=SUM(CAT_HOURS)').setNumberFormat('0.0')
    .setFontWeight('bold').setHorizontalAlignment('center'));
  sh.getRange(tot + 1, 3).setValue('Free time (168 − allocated)').setFontWeight('bold');
  ss.setNamedRange('FREE_TIME', sh.getRange(tot + 1, 4)
    .setFormula('=HOURS_WEEK-TOTAL_USED').setNumberFormat('0.0')
    .setFontWeight('bold').setHorizontalAlignment('center'));
  sh.getRange(tot + 2, 3).setValue('Productive hours').setFontWeight('bold');
  ss.setNamedRange('PRODUCTIVE_H', sh.getRange(tot + 2, 4)
    .setFormula('=SUMIFS(CAT_HOURS,CAT_PROD,TRUE)')
    .setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center'));

  // -- Conditional formatting ------------------------------------------------
  const hoursCol = sh.getRange(first, 4, TRACKER_ROWS, 1);
  const statusCol = sh.getRange(first, 10, TRACKER_ROWS, 1);
  const freeCell = sh.getRange(tot + 1, 4);
  sh.setConditionalFormatRules([
    cfFormula('=AND($C' + first + '="Sleep",$D' + first + '<SLEEP_GOAL*7)', [hoursCol], UI.badBg, UI.bad),
    cfFormula('=AND($I' + first + '<>"",$D' + first + '>$I' + first + ')', [hoursCol], UI.badBg, UI.bad),
    cfFormula('=AND($H' + first + '<>"",$D' + first + '<$H' + first + ')', [hoursCol], UI.warnBg, UI.warn),
    cfTextContains('OK', [statusCol], UI.good),
    cfTextContains('Low', [statusCol], UI.warn),
    cfTextContains('High', [statusCol], UI.bad),
    cfLt(0, [freeCell], UI.bad, UI.badBg),
    cfBetween(0, 5, [freeCell], UI.warn, UI.warnBg),
    cfGte(5, [freeCell], UI.good, UI.goodBg),
  ]);

  sh.setFrozenRows(tbl + 1);
  warnProtect(sh.getRange(first, 4, CATEGORIES.length, 1),
    'Core category hours come from 🌟 Ideal Week — edit them there.');
  warnProtect(sh.getRange(first, 5, TRACKER_ROWS, 2), 'Auto-calculated.');
  warnProtect(sh.getRange(first, 10, TRACKER_ROWS, 1), 'Auto-calculated.');

  ctx.settings = { sh: sh, first: first, last: last, lastCore: lastCore, tot: tot };
}
