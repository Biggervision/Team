/**
 * Module 12 — 📊 Dashboard (executive overview — no manual inputs)
 * Weekly / monthly / annual overview, goal progress, trends, life balance,
 * executive insights and the two signature charts.
 */

function buildDashboard(ctx) {
  const sh = freshSheet(ctx, SHEETS.dashboard);
  sh.setColumnWidth(1, 18);
  for (let c = 2; c <= 10; c++) sh.setColumnWidth(c, 96);
  sh.setColumnWidth(6, 110);
  for (let c = 11; c <= 16; c++) sh.setColumnWidth(c, 96);

  let row = ctxDashboard(sh, 'ASCENSION OS™ — Executive Dashboard',
    'Read-only command centre. Change inputs on 🌟 Ideal Week, 📆 Current Week and 📅 Daily Tracker.');
  sh.getRange(2, 9, 1, 2).merge().setFormula(
    '="Week "&WEEKNUM(TODAY(),21)&" · "&TEXT(TODAY(),"ddd d mmm yyyy")')
    .setFontSize(9).setFontColor(UI.faint).setHorizontalAlignment('right');

  // -- Signals ---------------------------------------------------------------
  band(sh, row, 2, 6, '  🚦  SIGNALS');
  signalFormulaStrs().forEach((f, i) => {
    sh.getRange(row + 1 + i, 2, 1, 5).merge().setFormula(f).setFontSize(10);
  });
  const afterSignals = row + 7;

  // -- Goal progress ---------------------------------------------------------
  band(sh, afterSignals, 2, 6, '  🎯  GOAL PROGRESS');
  const goals = [
    ['Productive hours', '=ROUND(PRODUCTIVE_H,1)', '=WEEKLY_TARGET',
     '=SPARKLINE(PRODUCTIVE_H,{"charttype","bar";"max",MAX(WEEKLY_TARGET,PRODUCTIVE_H,0.01);"color1","' + '#4F46E5' + '"})',
     '=PRODUCTIVE_H/WEEKLY_TARGET'],
    ['Sleep (h/week)', '=ROUND(PLAN_SLEEP,1)', '=SLEEP_GOAL*7',
     '=SPARKLINE(PLAN_SLEEP,{"charttype","bar";"max",MAX(SLEEP_GOAL*7,PLAN_SLEEP,0.01);"color1","' + '#0EA5E9' + '"})',
     '=PLAN_SLEEP/(SLEEP_GOAL*7)'],
    ['Free time buffer', '=ROUND(MAX(0,FREE_TIME),1)', 5,
     '=SPARKLINE(MAX(0,FREE_TIME),{"charttype","bar";"max",MAX(5,FREE_TIME,0.01);"color1","' + '#16A34A' + '"})',
     '=MAX(0,FREE_TIME)/5'],
  ];
  sh.getRange(afterSignals + 1, 2, 1, 5).setValues(
    [['Goal', 'Now', 'Target', 'Progress', '%']])
    .setFontSize(9).setFontWeight('bold').setFontColor(UI.slate).setBackground(UI.card)
    .setHorizontalAlignment('center');
  goals.forEach((g, i) => {
    const r = afterSignals + 2 + i;
    sh.getRange(r, 2).setValue(g[0]).setFontColor(UI.slate);
    sh.getRange(r, 3).setFormula(g[1]).setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');
    if (typeof g[2] === 'string') sh.getRange(r, 4).setFormula(g[2]); else sh.getRange(r, 4).setValue(g[2]);
    sh.getRange(r, 4).setNumberFormat('0.0').setFontColor(UI.faint).setHorizontalAlignment('center');
    sh.getRange(r, 5).setFormula(g[3]);
    sh.getRange(r, 6).setFormula(g[4]).setNumberFormat('0%').setHorizontalAlignment('center');
  });
  gridBorder(sh.getRange(afterSignals + 1, 2, 4, 5));
  const afterGoals = afterSignals + 7;

  // -- Trends (last 4 weeks, logged hours) -----------------------------------
  band(sh, afterGoals, 2, 6, '  📈  TRENDS — LOGGED HOURS, LAST 4 WEEKS');
  const wf = i =>
    'SUMIFS(LOG_ACT,LOG_DATE,">="&(WEEK_START-' + (7 * i) + '),LOG_DATE,"<"&(WEEK_START-' + (7 * i - 7) + '))';
  const labels = ['3 weeks ago', '2 weeks ago', 'Last week', 'This week'];
  labels.forEach((lab, i) => {
    const c = 2 + i;
    sh.getRange(afterGoals + 1, c).setValue(lab).setFontSize(8).setFontColor(UI.faint)
      .setHorizontalAlignment('center');
    sh.getRange(afterGoals + 2, c).setFormula('=' + wf(3 - i))
      .setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');
  });
  sh.getRange(afterGoals + 3, 2, 1, 4).merge().setFormula(
    '=SPARKLINE({' + wf(3) + ',' + wf(2) + ',' + wf(1) + ',' + wf(0) +
    '},{"charttype","column";"color","' + '#2BB5AE' + '"})');
  sh.setRowHeight(afterGoals + 3, 36);
  const afterTrends = afterGoals + 5;

  // -- Executive insights ----------------------------------------------------
  band(sh, afterTrends, 2, 6, '  💡  EXECUTIVE INSIGHTS');
  insightFormulaStrs().forEach((f, i) => {
    sh.getRange(afterTrends + 1 + i, 2, 1, 5).merge().setFormula(f).setFontSize(10)
      .setFontColor(UI.slate);
  });
  const afterInsights = afterTrends + 5;

  // -- Life-balance allocation table ----------------------------------------
  band(sh, afterInsights, 2, 6, '  ⚖️  LIFE BALANCE — WHERE THE HOURS GO');
  headerRow(sh, afterInsights + 1, 2, ['', 'Life area', 'Hours', '% of week', 'Status']);
  const s = ctx.settings;
  const setRef = quoted(SHEETS.settings);
  sh.getRange(afterInsights + 2, 2).setFormula(
    '=IFERROR(FILTER({' + setRef + '!$B$' + s.first + ':$B$' + s.last + ',' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + ',' +
    setRef + '!$D$' + s.first + ':$D$' + s.last + ',' +
    setRef + '!$E$' + s.first + ':$E$' + s.last + ',' +
    setRef + '!$J$' + s.first + ':$J$' + s.last + '},' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + '<>""),"")');
  sh.getRange(afterInsights + 2, 4, TRACKER_ROWS, 1).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(afterInsights + 2, 5, TRACKER_ROWS, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(afterInsights + 2, 6, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  const ft = afterInsights + 2 + TRACKER_ROWS + 1;
  sh.getRange(ft, 3).setValue('Free Time').setFontWeight('bold').setFontColor(UI.good);
  sh.getRange(ft, 4).setFormula('=ROUND(FREE_TIME,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setFontColor(UI.good).setHorizontalAlignment('center');
  sh.getRange(ft + 1, 3).setValue('Total Non-Free Time').setFontWeight('bold').setFontColor(UI.bad);
  sh.getRange(ft + 1, 4).setFormula('=ROUND(TOTAL_USED,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setFontColor(UI.bad).setHorizontalAlignment('center');

  const statusCol = sh.getRange(afterInsights + 2, 6, TRACKER_ROWS, 1);
  const rules = sh.getConditionalFormatRules();
  rules.push(cfTextContains('OK', [statusCol], UI.good));
  rules.push(cfTextContains('Low', [statusCol], UI.warn));
  rules.push(cfTextContains('High', [statusCol], UI.bad));
  sh.setConditionalFormatRules(rules);

  // -- Charts (right column, fed by Settings chart feeds) --------------------
  insertDashCharts(ctx, sh, row, row + 17, ft + 3);

  warnProtect(sh.getRange('A1:R80'), 'The dashboard is fully automatic — change inputs on the operational sheets.');
}
