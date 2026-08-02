/**
 * Module 04 — Contextual Executive Dashboard
 * The same compact KPI strip is rendered at the top of every operational
 * sheet, so users never switch tabs just to know where they stand.
 * Shows all four reporting levels (daily / weekly / monthly / annual).
 */

/**
 * Renders title + subtitle + 9 KPI cards + a live "logged" line.
 * Returns the next free row.
 */
function ctxDashboard(sh, title, subtitle) {
  pageTitle(sh, 2, 2, 10, title, subtitle);

  const r = 4;                       // label row; values on r+1; logged line r+2
  const kpis = [
    ['HOURS USED',   '=ROUND(TOTAL_USED,1)',                          '0.0'],
    ['REMAINING',    '=ROUND(MAX(0,HOURS_WEEK-SUM(CW_ACT)),1)',       '0.0'],
    ['WEEKLY HRS',   '=HOURS_WEEK',                                   '0'],
    ['MONTHLY HRS',  '=ROUND(TOTAL_USED*WEEKS_MONTH,0)',              '#,##0'],
    ['ANNUAL HRS',   '=ROUND(TOTAL_USED*WEEKS_YEAR,0)',               '#,##0'],
    ['PRODUCTIVE',   '=ROUND(PRODUCTIVE_H,1)',                        '0.0'],
    ['FREE TIME',    '=ROUND(FREE_TIME,1)',                           '0.0'],
    ['UTILIZATION',  '=TOTAL_USED/HOURS_WEEK',                        '0.0%'],
    ['BALANCE',      balanceFormulaStr(),                             '0'],
  ];
  kpis.forEach((k, i) => {
    const c = 2 + i;
    sh.getRange(r, c).setValue(k[0])
      .setFontSize(7).setFontWeight('bold').setFontColor(UI.faint)
      .setBackground(UI.card).setHorizontalAlignment('center');
    sh.getRange(r + 1, c).setFormula(k[1])
      .setFontSize(13).setFontWeight('bold').setNumberFormat(k[2])
      .setBackground(UI.card).setHorizontalAlignment('center');
    sh.getRange(r, c, 2, 1).setBorder(true, true, true, true, false, false,
      UI.line, SpreadsheetApp.BorderStyle.SOLID);
  });
  sh.setRowHeight(r, 16);
  sh.setRowHeight(r + 1, 28);

  sh.getRange(r + 2, 2, 1, 9).merge().setFormula(
    '="⏱  Logged — today: "&TEXT(SUMIFS(LOG_ACT,LOG_DATE,TODAY()),"0.0")&' +
    '" h   ·   this week: "&TEXT(SUM(CW_ACT),"0.0")&' +
    '" h   ·   this month: "&TEXT(SUMIFS(LOG_ACT,LOG_DATE,">="&EOMONTH(TODAY(),-1)+1,LOG_DATE,"<="&EOMONTH(TODAY(),0)),"0.0")&' +
    '" h   ·   this year: "&TEXT(SUMIFS(LOG_ACT,LOG_DATE,">="&DATE(YEAR(TODAY()),1,1)),"0.0")&" h"')
    .setFontSize(9).setFontColor(UI.slate);

  // status colours on Balance + Free Time cards
  const balance = sh.getRange(r + 1, 10);
  const free = sh.getRange(r + 1, 8);
  const rules = sh.getConditionalFormatRules();
  rules.push(cfGte(80, [balance], UI.good, null));
  rules.push(cfBetween(60, 79, [balance], UI.warn, null));
  rules.push(cfLt(60, [balance], UI.bad, null));
  rules.push(cfLt(0, [free], UI.bad, UI.badBg));
  sh.setConditionalFormatRules(rules);

  return r + 4;
}
