/**
 * Module 13 — Charts
 * Auto-filtered data feeds (kept out of the way on ⚙️ Settings cols L–P)
 * plus the signature donut / bar / planned-vs-actual charts.
 */

function buildChartFeeds(ctx) {
  const sh = ctx.settings.sh;
  sh.setColumnWidth(12, 170); sh.setColumnWidth(13, 76);
  sh.setColumnWidth(15, 170); sh.setColumnWidth(16, 76); sh.setColumnWidth(17, 76);

  sh.getRange(4, 12, 1, 2).setValues([['Life area', 'Hours']])
    .setFontSize(8).setFontWeight('bold').setFontColor(UI.faint).setBackground(UI.card);
  sh.getRange(5, 12).setFormula(
    '={IFERROR(FILTER({CAT_NAMES,CAT_HOURS},CAT_NAMES<>""),{"—",0});{"Free Time",MAX(0,FREE_TIME)}}');
  sh.getRange(5, 13, TRACKER_ROWS + 1, 1).setNumberFormat('0.0');

  sh.getRange(4, 15, 1, 3).setValues([['Category', 'Planned', 'Actual']])
    .setFontSize(8).setFontWeight('bold').setFontColor(UI.faint).setBackground(UI.card);
  sh.getRange(5, 15).setFormula(
    '=IFERROR(FILTER({CAT_NAMES,CW_EFF,CW_ACT},CAT_NAMES<>""),{"—",0,0})');
  sh.getRange(5, 16, TRACKER_ROWS, 2).setNumberFormat('0.0');

  ctx.chartFeeds = {
    donut: sh.getRange(4, 12, TRACKER_ROWS + 2, 2),
    pva:   sh.getRange(4, 15, TRACKER_ROWS + 1, 3),
  };
  warnProtect(sh.getRange(4, 12, TRACKER_ROWS + 2, 6), 'Chart data feeds — automatic.');
}

function insertDashCharts(ctx, sh, donutRow, barRow, pvaRow) {
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(ctx.chartFeeds.donut).setNumHeaders(1)
    .setPosition(donutRow, 8, 0, 0)
    .setOption('title', 'What does my time split look like by %?')
    .setOption('pieHole', 0.58)
    .setOption('colors', UI.chartColors)
    .setOption('width', 480).setOption('height', 310)
    .build());
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.BAR)
    .addRange(ctx.chartFeeds.donut).setNumHeaders(1)
    .setPosition(barRow, 8, 0, 0)
    .setOption('title', 'What does my time split look like overall?')
    .setOption('colors', [UI.chartBar])
    .setOption('legend', { position: 'none' })
    .setOption('width', 480).setOption('height', 420)
    .build());
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.COLUMN)
    .addRange(ctx.chartFeeds.pva).setNumHeaders(1)
    .setPosition(pvaRow, 2, 0, 0)
    .setOption('title', 'Planned vs actual — this week')
    .setOption('colors', ['#94A3B8', UI.chartBar])
    .setOption('width', 980).setOption('height', 320)
    .build());
}
