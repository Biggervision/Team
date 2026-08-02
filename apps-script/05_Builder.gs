/**
 * Module 05 — Builder (orchestrator + menu)
 */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('⚡ Ascension OS')
    .addItem('Build / Rebuild System', 'buildAscensionOS')
    .addItem('Apply Theme', 'applyTheme')
    .addSeparator()
    .addItem("Clear This Week's Plan", 'clearWeekPlan')
    .addItem('Clear Daily Log', 'clearDailyLog')
    .addToUi();
}

/** Kept as an alias so v1 users' triggers keep working. */
function buildExecutiveOS() { buildAscensionOS(); }

function buildAscensionOS() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const themeName = currentThemeName(ss);   // capture BEFORE named ranges reset
  UI = themePalette(themeName);
  const ctx = { ss: ss, plan: {}, themeName: themeName };

  ss.getNamedRanges().forEach(nr => {
    if (OWNED_NAMES.indexOf(nr.getName()) !== -1) nr.remove();
  });
  const stale = ss.getSheetByName('__building__');
  if (stale) ss.deleteSheet(stale);
  const keeper = ss.insertSheet('__building__');
  Object.keys(SHEETS).forEach(k => {
    const sh = ss.getSheetByName(SHEETS[k]);
    if (sh) ss.deleteSheet(sh);
  });
  BAND_REGISTRY.length = 0;

  buildSettings(ctx);
  buildIdealWeek(ctx);
  buildCurrentWeek(ctx);
  buildDaily(ctx);
  buildMonthly(ctx);
  buildAnnual(ctx);
  buildChartFeeds(ctx);
  buildDashboard(ctx);
  buildGuide(ctx);

  const order = [SHEETS.dashboard, SHEETS.ideal, SHEETS.current, SHEETS.daily,
                 SHEETS.monthly, SHEETS.annual, SHEETS.settings, SHEETS.guide];
  order.forEach((name, i) => {
    ss.setActiveSheet(ss.getSheetByName(name));
    ss.moveActiveSheet(i + 1);
  });
  Object.keys(SHEETS).forEach(k => {
    const sh = ss.getSheetByName(SHEETS[k]);
    if (sh) sh.setTabColor(k === 'dashboard' ? UI.hero : UI.tab);
  });

  saveBandRegistry();
  ss.deleteSheet(keeper);
  ss.setActiveSheet(ss.getSheetByName(SHEETS.dashboard));
  SpreadsheetApp.flush();
  ss.toast('ASCENSION OS™ is ready. Design your week on 🌟 Ideal Week.',
           '⚡ Build complete', 8);
}

function clearWeekPlan() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEETS.current);
  if (!sh) return;
  const props = PropertiesService.getDocumentProperties();
  const a1 = props.getProperty('ASC_CW_INPUTS');
  if (a1) { sh.getRange(a1).clearContent(); ss.toast('Weekly plan cleared — ideal values apply again.', '⚡ Ascension OS', 5); }
}

function clearDailyLog() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEETS.daily);
  if (!sh) return;
  const props = PropertiesService.getDocumentProperties();
  const stored = props.getProperty('ASC_LOG_INPUTS');
  if (stored) {
    JSON.parse(stored).forEach(a1 => sh.getRange(a1).clearContent());
    ss.toast('Daily log cleared.', '⚡ Ascension OS', 5);
  }
}
