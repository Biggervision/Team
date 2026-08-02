/* ═══════════════ 00_Config.gs ═══════════════ */

/**
 * ============================================================================
 *  ASCENSION OS™ — Executive 168-Hour Operating System (v2.0)
 *  Module 00 — Configuration (single source of truth for structure)
 * ============================================================================
 *  Install: paste ALL .gs modules (or dist/AscensionOS.gs) into Extensions →
 *  Apps Script, save, reload the sheet, then ⚡ Ascension OS → Build / Rebuild.
 *  Apps Script only BUILDS the workbook — day-to-day it runs on pure formulas.
 * ============================================================================
 */

const SHEETS = {
  dashboard: '📊 Dashboard',
  ideal:     '🌟 Ideal Week',
  current:   '📆 Current Week',
  daily:     '📅 Daily Tracker',
  monthly:   '🗓️ Monthly Review',
  annual:    '🎯 Annual Review',
  settings:  '⚙️ Settings',
  guide:     '📖 Guide',
};

/* 17 default life areas (+ Free Time, computed; + 5 custom slots).
 * min/max = default healthy band in h/week, editable on ⚙️ Settings. */
const CATEGORIES = [
  { key: 'SLEEP',   emoji: '😴', name: 'Sleep',                 productive: false, min: 49,  max: 63 },
  { key: 'WORK',    emoji: '💼', name: 'Work',                  productive: true,  min: '',  max: 40 },
  { key: 'DEEPWORK',emoji: '🎯', name: 'Deep Work',             productive: true,  min: 5,   max: '' },
  { key: 'MEETINGS',emoji: '🗣️', name: 'Meetings',              productive: true,  min: '',  max: 15 },
  { key: 'FOOD',    emoji: '🍕', name: 'Food',                  productive: false, min: 3.5, max: 21 },
  { key: 'CHORES',  emoji: '🧹', name: 'Household Chores',      productive: false, min: '',  max: 15 },
  { key: 'CHILD',   emoji: '👶', name: 'Childcare',             productive: false, min: '',  max: '' },
  { key: 'FIT',     emoji: '🏋️', name: 'Fitness',               productive: true,  min: 3,   max: 20 },
  { key: 'ENT',     emoji: '📺', name: 'Entertainment',         productive: false, min: '',  max: 25 },
  { key: 'REL',     emoji: '❤️', name: 'Relationships',         productive: false, min: 3,   max: '' },
  { key: 'LEARN',   emoji: '📚', name: 'Learning',              productive: true,  min: 1,   max: '' },
  { key: 'PD',      emoji: '🌱', name: 'Personal Development',  productive: true,  min: 1,   max: '' },
  { key: 'SPIRIT',  emoji: '🙏', name: 'Spiritual',             productive: false, min: '',  max: '' },
  { key: 'TRAVEL',  emoji: '🚗', name: 'Travel',                productive: false, min: '',  max: '' },
  { key: 'ADMIN',   emoji: '🗂️', name: 'Admin',                 productive: true,  min: '',  max: '' },
  { key: 'BIZDEV',  emoji: '📈', name: 'Business Development',  productive: true,  min: '',  max: '' },
  { key: 'CONTENT', emoji: '🎬', name: 'Content Creation',      productive: true,  min: '',  max: '' },
];
const CUSTOM_SLOTS = 5;
const TRACKER_ROWS = CATEGORIES.length + CUSTOM_SLOTS;  // 22
const LOG_ROWS = 200;                                    // daily-log capacity

/* Guided sentences for 🌟 Ideal Week. [label, default, unit, mode]
 * Work days live on ⚙️ Settings (mode 'ref_display' just shows them). */
const INPUT_BLOCKS = [
  { key: 'SLEEP', lines: [
    ['I sleep for around',                       8,  'hours per night.',                          'h_night'],
    ['I wind down for',                          10, 'minutes before sleeping.',                  'min_night'],
    ['My wake-up routine takes',                 0,  'minutes each morning.',                     'min_day'],
  ]},
  { key: 'WORK', lines: [
    ['I work',                                   '', 'days per week  (change in ⚙️ Settings).',   'ref_display'],
    ['Outside meetings & deep work, general work takes me', 3, 'hours per working day.',          'h_workday'],
    ['My lunch break is',                        30, 'minutes per working day.',                  'min_workday'],
    ['My commute is',                            0,  'minutes each way.',                         'commute_min'],
    ['Getting ready for work takes',             10, 'minutes per working day.',                  'min_workday'],
    ['Switching off after work takes',           10, 'minutes per working day.',                  'min_workday'],
  ]},
  { key: 'DEEPWORK', lines: [
    ['I do',                                     2,  'hours of deep, focused work per working day.', 'h_workday'],
  ]},
  { key: 'MEETINGS', lines: [
    ['I spend',                                  5,  'hours in meetings per week.',               'h_week'],
  ]},
  { key: 'FOOD', lines: [
    ['Breakfast takes',                          15, 'minutes per day (eating + prep).',          'min_day'],
    ['Lunch takes',                              40, 'minutes per non-working day.',              'min_nonworkday'],
    ['Dinner takes',                             30, 'minutes per day (eating + prep).',          'min_day'],
  ]},
  { key: 'CHORES', lines: [
    ['I do groceries',                           2,  'times per week.',                           'sessions'],
    ['Each grocery run takes',                   60, 'minutes (incl. travel).',                   'per_session_min'],
    ['I clean the house',                        1,  'times per week.',                           'sessions'],
    ['Each cleaning session takes',              60, 'minutes.',                                  'per_session_min'],
    ['Other misc. chores take',                  1,  'hours per week.',                           'h_week'],
  ]},
  { key: 'CHILD', lines: [
    ['Each weekday I spend',                     0,  'hours actively on childcare.',              'h_weekday5'],
    ['Each weekend day I spend',                 0,  'hours actively on childcare.',              'h_weekendday'],
    ['Child admin & logistics take',             0,  'hours per week.',                           'h_week'],
  ]},
  { key: 'FIT', lines: [
    ['Each week, I spend',                       8,  'hours exercising (incl. commute time).',    'h_week'],
    ['Each week, I spend',                       2,  'hours on other fitness-related things.',    'h_week'],
  ]},
  { key: 'ENT', lines: [
    ['Each week, I spend',                       0,  'hours watching TV shows / movies.',         'h_week'],
    ['Each week, I spend',                       7,  'hours on social media apps.',               'h_week'],
    ['Each week, I spend',                       2,  'hours reading.',                            'h_week'],
    ['Each week, I spend',                       3,  'hours on other entertainment.',             'h_week'],
  ]},
  { key: 'REL', lines: [
    ['Each week, I spend',                       3,  'hours on quality family time.',             'h_week'],
    ['Each week, I spend',                       3,  'hours on other socialising time.',          'h_week'],
  ]},
  { key: 'LEARN', lines: [
    ['Courses & structured learning take',       1,  'hours per week.',                           'h_week'],
    ['Books, articles & study take',             1,  'hours per week.',                           'h_week'],
    ['I listen to podcasts / audiobooks for',    20, 'minutes per day.',                          'min_day'],
  ]},
  { key: 'PD', lines: [
    ['I journal for',                            10, 'minutes per day.',                          'min_day'],
    ['I meditate for',                           10, 'minutes per day.',                          'min_day'],
    ['Weekly planning & review takes',           1,  'hours per week.',                           'h_week'],
  ]},
  { key: 'SPIRIT', lines: [
    ['Daily practice takes',                     0,  'minutes per day.',                          'min_day'],
    ['Services & community take',                0,  'hours per week.',                           'h_week'],
  ]},
  { key: 'TRAVEL', lines: [
    ['Errands & getting around (non-commute) take', 1.5, 'hours per week.',                       'h_week'],
    ['Trips & other travel take',                0,  'hours per week.',                           'h_week'],
  ]},
  { key: 'ADMIN', lines: [
    ['Finances, email & life admin take',        2,  'hours per week.',                           'h_week'],
    ['Appointments & paperwork take',            30, 'minutes per week.',                         'min_week'],
  ]},
  { key: 'BIZDEV', lines: [
    ['I spend',                                  4,  'hours per week on sales, partnerships & growth.', 'h_week'],
  ]},
  { key: 'CONTENT', lines: [
    ['I create content for',                     6,  'hours per week.',                           'h_week'],
  ]},
];

/* Named ranges owned (and cleaned up) by the builder. */
const OWNED_NAMES = [
  'HOURS_DAY', 'HOURS_WEEK', 'WEEKS_MONTH', 'WEEKS_YEAR', 'WORK_DAYS',
  'SLEEP_GOAL', 'WEEKLY_TARGET', 'THEME_NAME',
  'TOTAL_USED', 'FREE_TIME', 'PRODUCTIVE_H',
  'CAT_EMOJI', 'CAT_NAMES', 'CAT_HOURS', 'CAT_PROD',
  'WEEK_START', 'CW_EFF', 'CW_ACT', 'CW_VAR',
  'LOG_DATE', 'LOG_CAT', 'LOG_ACT', 'LOG_PROD',
].concat(CATEGORIES.map(c => 'PLAN_' + c.key));


/* ═══════════════ 01_Theme.gs ═══════════════ */

/**
 * Module 01 — Theme
 * Palettes + the active UI object. The theme is chosen on ⚙️ Settings
 * (THEME_NAME named range); ⚡ Apply Theme recolors bands/tabs in place.
 */

const THEMES = {
  'Teal (classic)': {
    band: '#2BB5AE', tab: '#2BB5AE', hero: '#0F172A', chartBar: '#F6A21D',
  },
  'Navy (executive)': {
    band: '#0F172A', tab: '#0F172A', hero: '#0F172A', chartBar: '#4F46E5',
  },
  'Forest (calm)': {
    band: '#2F855A', tab: '#2F855A', hero: '#1C4532', chartBar: '#DD6B20',
  },
};
const DEFAULT_THEME = 'Teal (classic)';

let UI = null;  // resolved at build / theme-apply time

function themePalette(name) {
  const t = THEMES[name] || THEMES[DEFAULT_THEME];
  return {
    band:      t.band,
    hero:      t.hero,
    tab:       t.tab,
    chartBar:  t.chartBar,
    navy:      '#0F172A',
    ink:       '#0F172A',
    slate:     '#475569',
    faint:     '#94A3B8',
    line:      '#E2E8F0',
    card:      '#F8FAFC',
    inputBg:   '#DDEBF7',
    inputLine: '#9DC3E6',
    accent:    '#4F46E5',
    good:      '#16A34A', goodBg: '#DCFCE7',
    warn:      '#D97706', warnBg: '#FEF3C7',
    bad:       '#DC2626', badBg:  '#FEE2E2',
    chartColors: ['#6366F1', '#0EA5E9', '#F59E0B', '#10B981', '#F472B6',
                  '#8B5CF6', '#14B8A6', '#F97316', '#84CC16', '#E11D48',
                  '#06B6D4', '#A855F7', '#64748B', '#22C55E', '#EAB308',
                  '#3B82F6', '#FB7185', '#94A3B8', '#F59E0B', '#10B981',
                  '#6366F1', '#0EA5E9', '#2BB5AE'],
  };
}

function currentThemeName(ss) {
  try {
    const nr = ss.getNamedRanges().filter(n => n.getName() === 'THEME_NAME')[0];
    if (nr) {
      const v = String(nr.getRange().getValue());
      if (THEMES[v]) return v;
    }
  } catch (e) {}
  return DEFAULT_THEME;
}

/** Band registry — every band() call records itself so Apply Theme can
 *  recolor without a destructive rebuild. */
const BAND_REGISTRY = [];

function applyTheme() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  UI = themePalette(currentThemeName(ss));
  const props = PropertiesService.getDocumentProperties();
  const saved = JSON.parse(props.getProperty('ASC_BANDS') || '[]');
  saved.forEach(entry => {
    const sh = ss.getSheetByName(entry.sheet);
    if (sh) sh.getRange(entry.a1).setBackground(UI.band);
  });
  Object.keys(SHEETS).forEach(k => {
    const sh = ss.getSheetByName(SHEETS[k]);
    if (sh) sh.setTabColor(k === 'dashboard' ? UI.hero : UI.tab);
  });
  ss.toast('Theme "' + currentThemeName(ss) + '" applied.', '⚡ Ascension OS', 5);
}

function saveBandRegistry() {
  PropertiesService.getDocumentProperties()
    .setProperty('ASC_BANDS', JSON.stringify(BAND_REGISTRY));
}


/* ═══════════════ 02_Utilities.gs ═══════════════ */

/**
 * Module 02 — Utilities
 * Shared low-level sheet helpers used by every builder module.
 */

function freshSheet(ctx, name) {
  const sh = ctx.ss.insertSheet(name);
  sh.setHiddenGridlines(true);
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns())
    .setFontFamily('Inter').setFontSize(10).setFontColor(UI.ink)
    .setVerticalAlignment('middle');
  return sh;
}

/** Teal section band; registered so Apply Theme can recolor it later. */
function band(sh, row, c1, c2, text) {
  const r = sh.getRange(row, c1, 1, c2 - c1 + 1);
  r.merge().setValue(text)
    .setBackground(UI.band).setFontColor('#FFFFFF')
    .setFontWeight('bold').setFontSize(11).setHorizontalAlignment('left');
  sh.setRowHeight(row, 28);
  BAND_REGISTRY.push({ sheet: sh.getName(), a1: r.getA1Notation() });
  return r;
}

/** Table header row (teal, white, bold). */
function headerRow(sh, row, c1, values) {
  const r = sh.getRange(row, c1, 1, values.length);
  r.setValues([values])
    .setBackground(UI.band).setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(9).setHorizontalAlignment('center');
  sh.getRange(row, c1).setHorizontalAlignment('left');
  sh.setRowHeight(row, 26);
  BAND_REGISTRY.push({ sheet: sh.getName(), a1: r.getA1Notation() });
  return r;
}

function inputCell(range) {
  range.setBackground(UI.inputBg).setFontWeight('bold')
       .setHorizontalAlignment('center')
       .setBorder(true, true, true, true, false, false, UI.inputLine,
                  SpreadsheetApp.BorderStyle.SOLID);
  return range;
}

function gridBorder(range) {
  range.setBorder(true, true, true, true, true, true, UI.line,
                  SpreadsheetApp.BorderStyle.SOLID);
  return range;
}

function warnProtect(range, note) {
  try { range.protect().setWarningOnly(true).setDescription(note); } catch (e) {}
}

function pageTitle(sh, row, c1, c2, title, subtitle) {
  sh.getRange(row, c1, 1, c2 - c1 + 1).merge().setValue(title)
    .setFontSize(16).setFontWeight('bold').setFontColor(UI.ink);
  sh.setRowHeight(row, 30);
  if (subtitle) {
    sh.getRange(row + 1, c1, 1, c2 - c1 + 1).merge().setValue(subtitle)
      .setFontSize(10).setFontColor(UI.slate).setFontStyle('italic');
  }
}

function colLetter(n) {
  let s = '';
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = (n - m - 1) / 26; }
  return s;
}

function quoted(sheetName) { return "'" + sheetName + "'"; }


/* ═══════════════ 03_FormatValidate.gs ═══════════════ */

/**
 * Module 03 — Formatting & Validation
 * Conditional-format rule factories + data-validation helpers.
 */

function numberValidation(range, min, max) {
  range.setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireNumberBetween(min, max)
      .setAllowInvalid(false)
      .setHelpText('Enter a number between ' + min + ' and ' + max + '.')
      .build());
}

function dateValidation(range) {
  range.setDataValidation(
    SpreadsheetApp.newDataValidation().requireDate().setAllowInvalid(false)
      .setHelpText('Enter a date.').build());
}

function listValidation(range, sourceRange) {
  range.setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireValueInRange(sourceRange, true).setAllowInvalid(false)
      .setHelpText('Pick a category from the list.').build());
}

/* -- conditional-format rule factories -------------------------------------- */
function cfFormula(formula, ranges, bg, fc) {
  const rule = SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied(formula);
  if (bg) rule.setBackground(bg);
  if (fc) rule.setFontColor(fc);
  return rule.setRanges(ranges).build();
}

function cfTextContains(text, ranges, fc) {
  return SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains(text).setFontColor(fc).setRanges(ranges).build();
}

function cfGte(v, ranges, fc, bg) {
  const rule = SpreadsheetApp.newConditionalFormatRule().whenNumberGreaterThanOrEqualTo(v);
  if (fc) rule.setFontColor(fc);
  if (bg) rule.setBackground(bg);
  return rule.setRanges(ranges).build();
}

function cfLt(v, ranges, fc, bg) {
  const rule = SpreadsheetApp.newConditionalFormatRule().whenNumberLessThan(v);
  if (fc) rule.setFontColor(fc);
  if (bg) rule.setBackground(bg);
  return rule.setRanges(ranges).build();
}

function cfBetween(a, b, ranges, fc, bg) {
  const rule = SpreadsheetApp.newConditionalFormatRule().whenNumberBetween(a, b);
  if (fc) rule.setFontColor(fc);
  if (bg) rule.setBackground(bg);
  return rule.setRanges(ranges).build();
}


/* ═══════════════ 04_ContextDash.gs ═══════════════ */

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


/* ═══════════════ 05_Builder.gs ═══════════════ */

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


/* ═══════════════ 06_Settings.gs ═══════════════ */

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


/* ═══════════════ 07_IdealWeek.gs ═══════════════ */

/**
 * Module 07 — 🌟 Ideal Week
 * Guided conversational design of the 168-hour week (v1 questionnaire style,
 * now with a contextual dashboard on top and monthly/annual estimates per
 * section). Structure: dashboard → guided inputs → analysis.
 */

function buildIdealWeek(ctx) {
  const sh = freshSheet(ctx, SHEETS.ideal);
  const ss = ctx.ss;
  const widths = [18, 250, 76, 250, 26, 92, 300];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));
  for (let c = 8; c <= 10; c++) sh.setColumnWidth(c, 60);

  let row = ctxDashboard(sh, '🌟 Ideal Week — design your 168 hours',
    'Answer the sentences below (blue cells only). This is your ideal allocation — the whole OS measures reality against it.');

  const catByKey = {};
  CATEGORIES.forEach(c => catByKey[c.key] = c);
  let prevLeaves = null;

  INPUT_BLOCKS.forEach(block => {
    const cat = catByKey[block.key];
    band(sh, row, 2, 7, '  ' + cat.emoji + '  ' + cat.name.toUpperCase());
    row++;
    sh.getRange(row, 6).setValue('h / week')
      .setFontSize(8).setFontColor(UI.faint).setHorizontalAlignment('center');
    row++;

    const firstLine = row;
    block.lines.forEach(line => {
      const label = line[0], def = line[1], unit = line[2], mode = line[3];
      sh.getRange(row, 2).setValue(label).setFontColor(UI.slate);
      if (mode === 'ref_display') {
        sh.getRange(row, 3).setFormula('=WORK_DAYS')
          .setFontColor(UI.faint).setHorizontalAlignment('center').setNumberFormat('0');
      } else {
        const val = sh.getRange(row, 3).setValue(def);
        inputCell(val);
        numberValidation(val, 0, 10000);
      }
      sh.getRange(row, 4).setValue(unit).setFontColor(UI.slate);
      const f = lineFormula(mode, row);
      if (f) {
        sh.getRange(row, 5).setValue('→').setFontColor(UI.faint).setHorizontalAlignment('center');
        sh.getRange(row, 6).setFormula(f).setNumberFormat('0.00')
          .setHorizontalAlignment('center');
      }
      if (mode === 'sessions') {
        sh.getRange(row, 7).setValue('pairs with the line below')
          .setFontSize(8).setFontColor(UI.faint);
      }
      row++;
    });

    // total row + monthly/annual estimate + weekly %
    sh.getRange(row, 4, 1, 2).merge().setValue('In total  →')
      .setFontWeight('bold').setHorizontalAlignment('right');
    const total = sh.getRange(row, 6)
      .setFormula('=ROUND(SUM($F$' + firstLine + ':$F$' + (row - 1) + '),2)')
      .setNumberFormat('0.0').setFontWeight('bold').setFontSize(11)
      .setHorizontalAlignment('center').setFontColor(UI.accent);
    sh.getRange(row, 7).setFormula(
      '="h/week on ' + cat.name.toLowerCase() + '  ·  ≈ "&ROUND($F$' + row +
      '*WEEKS_MONTH,0)&" h/month  ·  "&ROUND($F$' + row +
      '*WEEKS_YEAR,0)&" h/year  ·  "&TEXT($F$' + row + '/HOURS_WEEK,"0.0%")&" of your week"')
      .setFontSize(9).setFontColor(UI.slate);
    sh.getRange(row, 2, 1, 5).setBorder(true, false, false, false, false, false,
      UI.line, SpreadsheetApp.BorderStyle.SOLID);
    ss.setNamedRange('PLAN_' + cat.key, total);
    ctx.plan[cat.key] = total.getA1Notation();
    row++;

    // cascading remainder (reference style)
    sh.getRange(row, 4, 1, 2).merge().setValue('✅ That leaves me with  →')
      .setFontWeight('bold').setHorizontalAlignment('right').setFontColor(UI.good);
    const base = prevLeaves === null ? 'HOURS_WEEK' : '$F$' + prevLeaves;
    sh.getRange(row, 6).setFormula('=ROUND(' + base + '-$F$' + (row - 1) + ',2)')
      .setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center')
      .setFontColor(UI.good);
    sh.getRange(row, 7).setValue('hours per week for everything else.')
      .setFontSize(9).setFontColor(UI.slate);
    prevLeaves = row;
    row += 2;
  });

  // -- Analysis: allocation summary -----------------------------------------
  band(sh, row, 2, 7, '  🗂️  YOUR IDEAL ALLOCATION AT A GLANCE');
  row++;
  headerRow(sh, row, 2, ['', 'Life area', 'Hours', '% of week', 'Per day', 'Status']);
  row++;
  const s = ctx.settings;
  const setRef = quoted(SHEETS.settings);
  sh.getRange(row, 2).setFormula(
    '=IFERROR(FILTER({' + setRef + '!$B$' + s.first + ':$B$' + s.last + ',' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + ',' +
    setRef + '!$D$' + s.first + ':$D$' + s.last + ',' +
    setRef + '!$E$' + s.first + ':$E$' + s.last + ',' +
    setRef + '!$F$' + s.first + ':$F$' + s.last + ',' +
    setRef + '!$J$' + s.first + ':$J$' + s.last + '},' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + '<>""),"")');
  sh.getRange(row, 4, TRACKER_ROWS, 2).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(row, 5, TRACKER_ROWS, 1).setNumberFormat('0.0%');
  sh.getRange(row, 7, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  const ftRow = row + TRACKER_ROWS + 1;
  sh.getRange(ftRow, 3).setValue('Free Time').setFontWeight('bold').setFontColor(UI.good);
  sh.getRange(ftRow, 4).setFormula('=ROUND(FREE_TIME,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setFontColor(UI.good).setHorizontalAlignment('center');
  sh.getRange(ftRow + 1, 3).setValue('Total allocated').setFontWeight('bold');
  sh.getRange(ftRow + 1, 4).setFormula('=ROUND(TOTAL_USED,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setHorizontalAlignment('center');

  sh.setFrozenRows(7);
  warnProtect(sh.getRange('F1:F' + (row + TRACKER_ROWS + 4)),
    'Auto-calculated — edit the blue cells instead.');
}

/** Weekly-hours formula for one guided input line. */
function lineFormula(mode, row) {
  const c = '$C$' + row;
  switch (mode) {
    case 'h_night':
    case 'h_day':          return '=ROUND(' + c + '*7,2)';
    case 'min_night':
    case 'min_day':        return '=ROUND(' + c + '*7/60,2)';
    case 'h_workday':      return '=ROUND(' + c + '*WORK_DAYS,2)';
    case 'min_workday':    return '=ROUND(' + c + '*WORK_DAYS/60,2)';
    case 'min_nonworkday': return '=ROUND(' + c + '*(7-WORK_DAYS)/60,2)';
    case 'commute_min':    return '=ROUND(' + c + '*2*WORK_DAYS/60,2)';
    case 'h_week':         return '=' + c;
    case 'min_week':       return '=ROUND(' + c + '/60,2)';
    case 'h_weekday5':     return '=ROUND(' + c + '*5,2)';
    case 'h_weekendday':   return '=ROUND(' + c + '*2,2)';
    case 'per_session_min':return '=ROUND($C$' + (row - 1) + '*' + c + '/60,2)';
    default:               return ''; // 'sessions', 'ref_display'
  }
}


/* ═══════════════ 08_CurrentWeek.gs ═══════════════ */

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


/* ═══════════════ 09_Daily.gs ═══════════════ */

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


/* ═══════════════ 10_Monthly.gs ═══════════════ */

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


/* ═══════════════ 11_Annual.gs ═══════════════ */

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


/* ═══════════════ 12_Dashboard.gs ═══════════════ */

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


/* ═══════════════ 13_Charts.gs ═══════════════ */

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


/* ═══════════════ 14_Reports.gs ═══════════════ */

/**
 * Module 14 — Reports
 * Shared formula factories for the Balance Score, Signals and Executive
 * Insights, so every sheet computes them identically.
 */

/** Balance Score 0–100 (7 humane-week checks). */
function balanceFormulaStr() {
  return '=ROUND(100*(' +
    '(PLAN_SLEEP>=SLEEP_GOAL*7*0.95)*(PLAN_SLEEP<=63)' +
    '+((PLAN_WORK+PLAN_DEEPWORK+PLAN_MEETINGS)<=55)*1' +
    '+(PLAN_FIT>=3)*1' +
    '+(PLAN_REL>=3)*1' +
    '+((PLAN_LEARN+PLAN_PD)>=2)*1' +
    '+(FREE_TIME>=5)*1' +
    '+(FREE_TIME>=0)*1' +
    ')/7,0)';
}

/** Traffic-light signals for the Dashboard. */
function signalFormulaStrs() {
  const W = '(PLAN_WORK+PLAN_DEEPWORK+PLAN_MEETINGS)';
  return [
    '=IF(' + W + '>60,"🔴  Total work is over 60 h/week — burnout territory. Cut or delegate.",' +
      'IF(' + W + '>55,"🟠  Total work is above 55 h/week — watch the load.","🟢  Work load is sustainable."))',
    '=IF(PLAN_SLEEP<SLEEP_GOAL*7,"🔴  Sleep is below your "&SLEEP_GOAL&" h/night goal — recovery first.","🟢  Sleep is on target.")',
    '=IF(PLAN_FIT<3,"🟡  Fitness is under 3 h/week — schedule workouts first, not last.","🟢  Fitness habit is funded.")',
    '=IF(FREE_TIME<0,"🔴  You have allocated MORE than 168 hours — something must give.",' +
      'IF(FREE_TIME<5,"🟡  Under 5 h of true free time — build in slack.","🟢  Healthy buffer of free time."))',
    '=IF(PLAN_DEEPWORK<5,"🟡  Deep work is under 5 h/week — protect focus blocks.","🟢  Deep-work practice is funded.")',
  ];
}

/** Executive insights for the Dashboard (driven by Current Week variance). */
function insightFormulaStrs() {
  return [
    '="🏆  Largest planned investment: "&INDEX(CAT_NAMES,MATCH(MAX(CAT_HOURS),CAT_HOURS,0))&' +
      '"  ("&TEXT(MAX(CAT_HOURS),"0.0")&" h/week)"',
    '=IF(SUM(CW_ACT)=0,"📅  Log your first day on the Daily Tracker to unlock live insights.",' +
      'IF(MAX(CW_VAR)<=0,"✅  No category is over plan this week.",' +
      '"🔺  Most over plan this week: "&INDEX(CAT_NAMES,MATCH(MAX(CW_VAR),CW_VAR,0))&' +
      '"  (+"&TEXT(MAX(CW_VAR),"0.0")&" h)"))',
    '=IF(SUM(CW_ACT)=0,"",' +
      '"🔻  Most behind plan this week: "&INDEX(CAT_NAMES,MATCH(MIN(CW_VAR),CW_VAR,0))&' +
      '"  ("&TEXT(MIN(CW_VAR),"0.0")&" h)")',
  ];
}


/* ═══════════════ 15_Guide.gs ═══════════════ */

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

