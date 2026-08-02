/**
 * Module 08 — 📆 Current Week
 * Plan THIS week (defaults to the Ideal Week), then watch actuals flow in
 * from the Daily Tracker. Structure: dashboard → plan inputs → totals.
 */

function buildCurrentWeek(ctx) {
  const sh = freshSheet(ctx, SHEETS.current);
  const ss = ctx.ss;
  const widths = [18, 190, 78, 82, 84, 78, 78, 84, 78, 130];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  let row = ctxDashboard(sh, '📆 Current Week — plan, then perform',
    'Leave "My plan" blank to use your Ideal Week. Actuals arrive automatically from the 📅 Daily Tracker.');

  // week window
  sh.getRange(row, 2, 1, 4).merge().setFormula(
    '="Week of "&TEXT(WEEK_START,"ddd d mmm")&" – "&TEXT(WEEK_START+6,"ddd d mmm yyyy")')
    .setFontWeight('bold').setFontColor(UI.slate);
  const wsCell = sh.getRange(row, 10).setFormula('=TODAY()-WEEKDAY(TODAY(),2)+1')
    .setNumberFormat('yyyy-mm-dd').setFontColor(UI.faint).setFontSize(8)
    .setHorizontalAlignment('center');
  sh.getRange(row, 9).setValue('week starts:').setFontSize(8).setFontColor(UI.faint)
    .setHorizontalAlignment('right');
  ss.setNamedRange('WEEK_START', wsCell);
  row += 2;

  band(sh, row, 2, 10, '  📆  THIS WEEK BY LIFE AREA');
  row++;
  headerRow(sh, row, 2, ['Category', 'Ideal', 'My plan', 'Planned', 'Actual',
                         'Variance', 'Remaining', '% of plan', 'Progress']);
  row++;
  const first = row;
  const last = first + TRACKER_ROWS - 1;
  const s = ctx.settings;
  const setRef = quoted(SHEETS.settings);

  for (let i = 0; i < TRACKER_ROWS; i++) {
    const r = first + i, sr = s.first + i;
    sh.getRange(r, 2).setFormula(
      '=IF(' + setRef + '!C' + sr + '="","",' + setRef + '!C' + sr + ')');
    sh.getRange(r, 3).setFormula('=IF($B' + r + '="","",' + setRef + '!D' + sr + ')');
    inputCell(sh.getRange(r, 4)).setFontWeight('normal');
    numberValidation(sh.getRange(r, 4), 0, 168);
    sh.getRange(r, 5).setFormula('=IF($B' + r + '="","",IF($D' + r + '="",$C' + r + ',$D' + r + '))');
    sh.getRange(r, 6).setFormula(
      '=IF($B' + r + '="","",SUMIFS(LOG_ACT,LOG_CAT,$B' + r +
      ',LOG_DATE,">="&WEEK_START,LOG_DATE,"<"&WEEK_START+7))');
    sh.getRange(r, 7).setFormula('=IF($B' + r + '="","",$F' + r + '-$E' + r + ')');
    sh.getRange(r, 8).setFormula('=IF($B' + r + '="","",MAX(0,$E' + r + '-$F' + r + '))');
    sh.getRange(r, 9).setFormula(
      '=IF(OR($B' + r + '="",$E' + r + '=0),"",$F' + r + '/$E' + r + ')');
    sh.getRange(r, 10).setFormula(
      '=IF($B' + r + '="","",SPARKLINE($F' + r + ',{"charttype","bar";"max",MAX($E' + r +
      ',$F' + r + ',0.01);"color1","' + UI.accent + '"}))');
  }
  sh.getRange(first, 3, TRACKER_ROWS, 6).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 9, TRACKER_ROWS, 1).setNumberFormat('0%').setHorizontalAlignment('center');
  gridBorder(sh.getRange(first, 2, TRACKER_ROWS, 9));

  ss.setNamedRange('CW_EFF', sh.getRange(first, 5, TRACKER_ROWS, 1));
  ss.setNamedRange('CW_ACT', sh.getRange(first, 6, TRACKER_ROWS, 1));
  ss.setNamedRange('CW_VAR', sh.getRange(first, 7, TRACKER_ROWS, 1));
  PropertiesService.getDocumentProperties().setProperty(
    'ASC_CW_INPUTS', sh.getRange(first, 4, TRACKER_ROWS, 1).getA1Notation());

  const t = last + 2;
  const rows = [
    ['Total planned / logged', '=SUM(E' + first + ':E' + last + ')', '=SUM(F' + first + ':F' + last + ')'],
    ['Free / remaining hours', '=HOURS_WEEK-E' + t, '=HOURS_WEEK-F' + t],
    ['Utilization', '=E' + t + '/HOURS_WEEK', '=F' + t + '/HOURS_WEEK'],
  ];
  rows.forEach((rw, i) => {
    sh.getRange(t + i, 2, 1, 3).merge().setValue(rw[0]).setFontWeight('bold')
      .setHorizontalAlignment('right');
    sh.getRange(t + i, 5).setFormula(rw[1]);
    sh.getRange(t + i, 6).setFormula(rw[2]);
  });
  sh.getRange(t, 5, 2, 2).setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(t + 2, 5, 1, 2).setNumberFormat('0.0%').setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(t, 2, 1, 9).setBorder(true, false, false, false, false, false,
    UI.band, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  const pct = sh.getRange(first, 9, TRACKER_ROWS, 1);
  const rules = sh.getConditionalFormatRules();
  rules.push(cfFormula('=AND($B' + first + '<>"",$I' + first + '<>"",$I' + first + '>1.2)',
    [pct], UI.badBg, UI.bad));
  rules.push(cfFormula('=AND($B' + first + '<>"",$I' + first + '<>"",$I' + first + '<0.5)',
    [pct], UI.warnBg, UI.warn));
  sh.setConditionalFormatRules(rules);

  sh.setFrozenRows(7);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 5, 2), 'Auto-fed from Settings.');
  warnProtect(sh.getRange(first, 5, TRACKER_ROWS + 5, 6), 'Auto-calculated.');
  ctx.cw = { first: first, last: last };
}
