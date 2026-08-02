/**
 * Module 10 — 🗓️ Monthly Review
 * Fully automatic: monthly summary, weekly breakdown, category ranking and
 * insights — all derived from the Daily Tracker log.
 */

function buildMonthly(ctx) {
  const sh = freshSheet(ctx, SHEETS.monthly);
  const widths = [18, 190, 82, 92, 100, 82, 86, 60, 20, 70, 70, 70, 70, 70];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  let row = ctxDashboard(sh, '🗓️ Monthly Review',
    'Everything on this page derives automatically from the 📅 Daily Tracker.');

  sh.getRange(row, 2, 1, 4).merge()
    .setFormula('="Reviewing:  "&TEXT(TODAY(),"mmmm yyyy")')
    .setFontWeight('bold').setFontColor(UI.slate);
  row += 2;

  const MS = 'EOMONTH(TODAY(),-1)+1';       // month start
  const ME = 'EOMONTH(TODAY(),0)';          // month end

  band(sh, row, 2, 8, '  🗓️  MONTHLY SUMMARY');
  band(sh, row, 10, 14, '  📆  WEEKLY BREAKDOWN (actual h)');
  row++;
  headerRow(sh, row, 2, ['Category', 'Ideal h/wk', 'Ideal month', 'Actual month',
                         'Variance', '% of month', 'Rank']);
  headerRow(sh, row, 10, ['W1', 'W2', 'W3', 'W4', 'W5']);
  row++;
  const first = row;
  const last = first + TRACKER_ROWS - 1;
  const s = ctx.settings;
  const setRef = quoted(SHEETS.settings);

  for (let i = 0; i < TRACKER_ROWS; i++) {
    const r = first + i, sr = s.first + i;
    sh.getRange(r, 2).setFormula('=IF(' + setRef + '!C' + sr + '="","",' + setRef + '!C' + sr + ')');
    sh.getRange(r, 3).setFormula('=IF($B' + r + '="","",' + setRef + '!D' + sr + ')');
    sh.getRange(r, 4).setFormula('=IF($B' + r + '="","",ROUND($C' + r + '*WEEKS_MONTH,1))');
    sh.getRange(r, 5).setFormula(
      '=IF($B' + r + '="","",SUMIFS(LOG_ACT,LOG_CAT,$B' + r +
      ',LOG_DATE,">="&' + MS + ',LOG_DATE,"<="&' + ME + '))');
    sh.getRange(r, 6).setFormula('=IF($B' + r + '="","",$E' + r + '-$D' + r + ')');
    sh.getRange(r, 7).setFormula('=IF($B' + r + '="","",$D' + r + '/(HOURS_WEEK*WEEKS_MONTH))');
    sh.getRange(r, 8).setFormula(
      '=IF(OR($B' + r + '="",$E' + r + '=0),"",RANK($E' + r + ',$E$' + first + ':$E$' + last + '))');
    for (let w = 0; w < 5; w++) {
      sh.getRange(r, 10 + w).setFormula(
        '=IF($B' + r + '="","",SUMIFS(LOG_ACT,LOG_CAT,$B' + r +
        ',LOG_DATE,">="&' + MS + '+' + (w * 7) + ',LOG_DATE,"<"&MIN(' + ME + '+1,' + MS + '+' + ((w + 1) * 7) + ')))');
    }
  }
  sh.getRange(first, 3, TRACKER_ROWS, 4).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 7, TRACKER_ROWS, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(first, 8, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  sh.getRange(first, 10, TRACKER_ROWS, 5).setNumberFormat('0.0').setHorizontalAlignment('center');
  gridBorder(sh.getRange(first, 2, TRACKER_ROWS, 7));
  gridBorder(sh.getRange(first, 10, TRACKER_ROWS, 5));

  const t = last + 2;
  sh.getRange(t, 2).setValue('Total').setFontWeight('bold');
  sh.getRange(t, 4).setFormula('=SUM(D' + first + ':D' + last + ')');
  sh.getRange(t, 5).setFormula('=SUM(E' + first + ':E' + last + ')');
  sh.getRange(t, 4, 1, 2).setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');

  // insights
  const ins = t + 2;
  band(sh, ins, 2, 8, '  💡  MONTHLY INSIGHTS');
  const E = '$E$' + first + ':$E$' + last;
  const F = '$F$' + first + ':$F$' + last;
  const B = '$B$' + first + ':$B$' + last;
  const lines = [
    '=IF(SUM(' + E + ')=0,"Log days on the 📅 Daily Tracker to unlock monthly insights.",' +
      '"🏆  Biggest time investment this month: "&INDEX(' + B + ',MATCH(MAX(' + E + '),' + E + ',0))&' +
      '"  ("&TEXT(MAX(' + E + '),"0.0")&" h logged)")',
    '=IF(SUM(' + E + ')=0,"",IF(MAX(' + F + ')<=0,"✅  No category is over its monthly plan.",' +
      '"🔺  Most over plan: "&INDEX(' + B + ',MATCH(MAX(' + F + '),' + F + ',0))&' +
      '"  (+"&TEXT(MAX(' + F + '),"0.0")&" h)"))',
    '=IF(SUM(' + E + ')=0,"",' +
      '"🔻  Most behind plan: "&INDEX(' + B + ',MATCH(MIN(' + F + '),' + F + ',0))&' +
      '"  ("&TEXT(MIN(' + F + '),"0.0")&" h)")',
    '="⚖️  Month utilization so far: "&TEXT(SUM(' + E + ')/(HOURS_WEEK*WEEKS_MONTH),"0.0%")&" of "&ROUND(HOURS_WEEK*WEEKS_MONTH,0)&" hours."',
  ];
  lines.forEach((f, i) => {
    sh.getRange(ins + 1 + i, 2, 1, 7).merge().setFormula(f).setFontColor(UI.slate);
  });

  sh.setFrozenRows(first - 1);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 8, 13), 'Fully automatic — nothing to edit here.');
}
