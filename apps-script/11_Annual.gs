/**
 * Module 11 — 🎯 Annual Review
 * The year at a glance: projections from the Ideal Week, actual YTD from the
 * Daily Tracker, pace, life balance and a Year-in-Review narrative.
 */

function buildAnnual(ctx) {
  const sh = freshSheet(ctx, SHEETS.annual);
  const widths = [18, 190, 82, 96, 92, 76, 92, 86, 92];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  let row = ctxDashboard(sh, '🎯 Annual Review',
    'Ideal Week × 52 versus what you actually logged this year. Small weekly numbers become life-sized here.');

  const YS = 'DATE(YEAR(TODAY()),1,1)';
  const WKS = 'MAX(1,ROUNDUP((TODAY()-' + YS + '+1)/7,0))';   // weeks elapsed

  band(sh, row, 2, 9, '  🎯  YEAR ' + '— PLAN VS REALITY');
  row++;
  headerRow(sh, row, 2, ['Category', 'Weekly h', 'Annual plan', 'Actual YTD',
                         'On pace', 'Annual days', '% of year', 'Balance']);
  row++;
  const first = row;
  const last = first + TRACKER_ROWS - 1;
  const s = ctx.settings;
  const setRef = quoted(SHEETS.settings);

  for (let i = 0; i < TRACKER_ROWS; i++) {
    const r = first + i, sr = s.first + i;
    sh.getRange(r, 2).setFormula('=IF(' + setRef + '!C' + sr + '="","",' + setRef + '!C' + sr + ')');
    sh.getRange(r, 3).setFormula('=IF($B' + r + '="","",' + setRef + '!D' + sr + ')');
    sh.getRange(r, 4).setFormula('=IF($B' + r + '="","",ROUND($C' + r + '*WEEKS_YEAR,0))');
    sh.getRange(r, 5).setFormula(
      '=IF($B' + r + '="","",SUMIFS(LOG_ACT,LOG_CAT,$B' + r + ',LOG_DATE,">="&' + YS + '))');
    sh.getRange(r, 6).setFormula(
      '=IF(OR($B' + r + '="",$C' + r + '=0),"",$E' + r + '/($C' + r + '*' + WKS + '))');
    sh.getRange(r, 7).setFormula('=IF($B' + r + '="","",ROUND($D' + r + '/HOURS_DAY,1))');
    sh.getRange(r, 8).setFormula('=IF($B' + r + '="","",$C' + r + '/HOURS_WEEK)');
    sh.getRange(r, 9).setFormula('=IF($B' + r + '="","",' + setRef + '!J' + sr + ')');
  }
  sh.getRange(first, 3, TRACKER_ROWS, 1).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 4, TRACKER_ROWS, 2).setNumberFormat('#,##0').setHorizontalAlignment('center');
  sh.getRange(first, 6, TRACKER_ROWS, 1).setNumberFormat('0%').setHorizontalAlignment('center');
  sh.getRange(first, 7, TRACKER_ROWS, 1).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 8, TRACKER_ROWS, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(first, 9, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  gridBorder(sh.getRange(first, 2, TRACKER_ROWS, 8));

  const statusCol = sh.getRange(first, 9, TRACKER_ROWS, 1);
  const rules = sh.getConditionalFormatRules();
  rules.push(cfTextContains('OK', [statusCol], UI.good));
  rules.push(cfTextContains('Low', [statusCol], UI.warn));
  rules.push(cfTextContains('High', [statusCol], UI.bad));
  sh.setConditionalFormatRules(rules);

  const t = last + 2;
  band(sh, t, 2, 9, '  📖  YEAR IN REVIEW');
  const E = '$E$' + first + ':$E$' + last;
  const B = '$B$' + first + ':$B$' + last;
  const lines = [
    '="You have logged "&TEXT(SUM(' + E + '),"#,##0")&" hours so far this year across "&' + WKS + '&" weeks."',
    '=IF(SUM(' + E + ')=0,"Log days on the 📅 Daily Tracker to unlock your Year in Review.",' +
      '"🏆  Your year so far is defined by: "&INDEX(' + B + ',MATCH(MAX(' + E + '),' + E + ',0))&' +
      '"  ("&TEXT(MAX(' + E + '),"#,##0")&" h logged)")',
    '="😴  At your ideal pace you will sleep "&ROUND(PLAN_SLEEP*WEEKS_YEAR/24,0)&" full days this year."',
    '="💼  Work + deep work + meetings project to "&TEXT((PLAN_WORK+PLAN_DEEPWORK+PLAN_MEETINGS)*WEEKS_YEAR,"#,##0")&" hours — "&ROUND((PLAN_WORK+PLAN_DEEPWORK+PLAN_MEETINGS)*WEEKS_YEAR/24,0)&" days."',
    '="✅  Free, unallocated time compounds to "&TEXT(MAX(0,FREE_TIME)*WEEKS_YEAR,"#,##0")&" hours a year. Spend them on purpose."',
  ];
  lines.forEach((f, i) => {
    sh.getRange(t + 1 + i, 2, 1, 8).merge().setFormula(f).setFontColor(UI.slate);
  });

  sh.setFrozenRows(first - 1);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 8, 8), 'Fully automatic — nothing to edit here.');
}
