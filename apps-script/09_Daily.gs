/**
 * Module 09 — 📅 Daily Tracker (the execution engine)
 * Date-stamped log: pick a category, enter actual hours, add notes.
 * Everything rolls up automatically into Current Week, Monthly and Annual.
 */

function buildDaily(ctx) {
  const sh = freshSheet(ctx, SHEETS.daily);
  const ss = ctx.ss;
  const widths = [18, 92, 52, 190, 76, 76, 260, 70, 20, 130, 76, 76, 84];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  let row = ctxDashboard(sh, '📅 Daily Tracker — the execution engine',
    'Log each block of time: date, category, actual hours, notes. Rollups to week, month and year are automatic.');

  band(sh, row, 2, 8, '  📅  DAILY LOG');
  band(sh, row, 10, 13, '  ⚡ TODAY');
  row++;
  headerRow(sh, row, 2, ['Date', 'Day', 'Category', 'Plan/day', 'Actual h', 'Notes', 'Prod.']);
  const first = row + 1;
  const last = first + LOG_ROWS - 1;

  // Today panel (right)
  const tp = row;
  const today = [
    ['Daily total',       '=SUMIFS(LOG_ACT,LOG_DATE,TODAY())',                      '0.0'],
    ['Remaining today',   '=HOURS_DAY-SUMIFS(LOG_ACT,LOG_DATE,TODAY())',            '0.0'],
    ['Productivity score','=IFERROR(SUMIFS(LOG_ACT,LOG_DATE,TODAY(),LOG_PROD,TRUE)/SUMIFS(LOG_ACT,LOG_DATE,TODAY()),0)', '0%'],
  ];
  today.forEach((k, i) => {
    sh.getRange(tp + 1 + i, 10).setValue(k[0]).setFontColor(UI.slate);
    sh.getRange(tp + 1 + i, 11).setFormula(k[1]).setNumberFormat(k[2])
      .setFontWeight('bold').setHorizontalAlignment('center');
  });
  gridBorder(sh.getRange(tp + 1, 10, 3, 2));
  const todayTotal = sh.getRange(tp + 1, 11);

  // Last-7-days panel
  const l7 = tp + 5;
  band(sh, l7, 10, 13, '  📊  LAST 7 DAYS');
  headerRow(sh, l7 + 1, 10, ['Day', 'Logged', 'Left', 'Prod %']);
  for (let i = 0; i < 7; i++) {
    const r = l7 + 2 + i;
    sh.getRange(r, 10).setFormula('=TEXT(TODAY()-' + i + ',"ddd d mmm")').setFontColor(UI.slate);
    sh.getRange(r, 11).setFormula('=SUMIFS(LOG_ACT,LOG_DATE,TODAY()-' + i + ')')
      .setNumberFormat('0.0').setHorizontalAlignment('center');
    sh.getRange(r, 12).setFormula('=HOURS_DAY-K' + r)
      .setNumberFormat('0.0').setHorizontalAlignment('center').setFontColor(UI.faint);
    sh.getRange(r, 13).setFormula(
      '=IFERROR(SUMIFS(LOG_ACT,LOG_DATE,TODAY()-' + i + ',LOG_PROD,TRUE)/K' + r + ',"")')
      .setNumberFormat('0%').setHorizontalAlignment('center');
  }
  gridBorder(sh.getRange(l7 + 2, 10, 7, 4));
  const loggedCol = sh.getRange(l7 + 2, 11, 7, 1);

  // Log rows
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 3).setFormula('=IF($B' + r + '="","",TEXT($B' + r + ',"ddd"))')
      .setFontColor(UI.faint).setHorizontalAlignment('center');
    sh.getRange(r, 5).setFormula(
      '=IF($D' + r + '="","",IFERROR(ROUND(XLOOKUP($D' + r + ',CAT_NAMES,CW_EFF)/7,2),""))')
      .setFontColor(UI.faint).setNumberFormat('0.00').setHorizontalAlignment('center');
    sh.getRange(r, 8).setFormula(
      '=IF($D' + r + '="","",IFERROR(XLOOKUP($D' + r + ',CAT_NAMES,CAT_PROD),FALSE))')
      .setFontColor(UI.faint).setFontSize(8).setHorizontalAlignment('center');
  }
  const dateCol = sh.getRange(first, 2, LOG_ROWS, 1);
  const catCol  = sh.getRange(first, 4, LOG_ROWS, 1);
  const actCol  = sh.getRange(first, 6, LOG_ROWS, 1);
  const noteCol = sh.getRange(first, 7, LOG_ROWS, 1);
  [dateCol, catCol, actCol, noteCol].forEach(rg => {
    inputCell(rg).setFontWeight('normal');
  });
  noteCol.setHorizontalAlignment('left');
  dateCol.setNumberFormat('yyyy-mm-dd');
  actCol.setNumberFormat('0.0#');
  dateValidation(dateCol);
  listValidation(catCol, ctx.ss.getSheetByName(SHEETS.settings)
    .getRange(ctx.settings.first, 3, TRACKER_ROWS, 1));
  numberValidation(actCol, 0, 24);
  gridBorder(sh.getRange(first, 2, LOG_ROWS, 7));

  ss.setNamedRange('LOG_DATE', dateCol);
  ss.setNamedRange('LOG_CAT',  catCol);
  ss.setNamedRange('LOG_ACT',  actCol);
  ss.setNamedRange('LOG_PROD', sh.getRange(first, 8, LOG_ROWS, 1));
  PropertiesService.getDocumentProperties().setProperty('ASC_LOG_INPUTS',
    JSON.stringify([dateCol.getA1Notation(), catCol.getA1Notation(),
                    actCol.getA1Notation(), noteCol.getA1Notation()]));

  const rules = sh.getConditionalFormatRules();
  rules.push(cfFormula('=$K$' + (tp + 1) + '>24', [todayTotal], UI.badBg, UI.bad));
  rules.push(cfFormula('=AND($K$' + (tp + 1) + '>18,$K$' + (tp + 1) + '<=24)', [todayTotal], UI.warnBg, UI.warn));
  rules.push(cfFormula('=K' + (l7 + 2) + '>24', [loggedCol], UI.badBg, UI.bad));
  sh.setConditionalFormatRules(rules);

  sh.setFrozenRows(first - 1);
  warnProtect(sh.getRange(first, 3, LOG_ROWS, 1), 'Auto-calculated.');
  warnProtect(sh.getRange(first, 5, LOG_ROWS, 1), 'Auto-calculated.');
  warnProtect(sh.getRange(first, 8, LOG_ROWS, 1), 'Auto-calculated.');
  ctx.log = { first: first, last: last };
}
