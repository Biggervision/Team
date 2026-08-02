/**
 * ============================================================================
 *  168-HOUR EXECUTIVE TIME OPERATING SYSTEM — one-click builder
 * ============================================================================
 *
 *  WHAT THIS IS
 *  A generator that builds a complete, formula-driven Executive Time OS
 *  inside the Google Sheet it is attached to. Apps Script is used ONLY to
 *  construct the workbook (tabs, formulas, named ranges, validation,
 *  conditional formatting, charts). Once built, everything runs on native
 *  Google Sheets formulas — no scripts are needed for day-to-day use.
 *
 *  HOW TO INSTALL (≈2 minutes)
 *  1. Open your Google Sheet.
 *  2. Extensions → Apps Script.
 *  3. Delete any code in the editor, paste this entire file, press Save.
 *  4. Reload the spreadsheet. A new menu "⚡ Executive OS" appears.
 *  5. Click ⚡ Executive OS → Build / Rebuild System. Authorise when asked.
 *
 *  The build is idempotent: running it again rebuilds the OS tabs from
 *  scratch (any other tabs you own are untouched).
 *
 *  ARCHITECTURE — "Input once → calculate everywhere"
 *    ⚙️ Inputs .......... the ONLY place you type your planned life numbers
 *    🔧 Settings ........ master category table + constants (single source
 *                         of truth; custom categories are added here)
 *    📅 Daily Tracker ... log ACTUAL hours per category, Mon–Sun
 *    📈 Weekly Tracker .. planned vs actual vs difference (auto)
 *    🗓️ Monthly Tracker . monthly projections + variance (auto)
 *    🎯 Annual Tracker .. yearly hours / days / weeks (auto)
 *    📊 Dashboard ....... KPI cards, horizons, allocation, signals, charts
 *    📉 Charts .......... large-format charts + their (auto) data feeds
 *    📖 Guide ........... in-sheet user manual
 * ============================================================================
 */

/* ----------------------------------------------------------------------------
 * DESIGN TOKENS
 * ------------------------------------------------------------------------- */
const UI = {
  navy:      '#0F172A', // headers / bands
  navySoft:  '#1E293B',
  ink:       '#0F172A',
  slate:     '#475569',
  faint:     '#94A3B8',
  line:      '#E2E8F0',
  paper:     '#FFFFFF',
  card:      '#F8FAFC',
  inputBg:   '#EAF3FF', // every editable cell uses this colour
  inputLine: '#BFDBFE',
  accent:    '#4F46E5', // indigo
  teal:      '#0E7490',
  good:      '#16A34A',
  goodBg:    '#DCFCE7',
  warn:      '#D97706',
  warnBg:    '#FEF3C7',
  bad:       '#DC2626',
  badBg:     '#FEE2E2',
  chartColors: ['#6366F1', '#0EA5E9', '#F59E0B', '#10B981', '#F472B6',
                '#8B5CF6', '#14B8A6', '#F97316', '#84CC16', '#E11D48',
                '#06B6D4', '#A855F7', '#64748B', '#22C55E', '#EAB308',
                '#3B82F6', '#FB7185', '#94A3B8'],
};

const SHEETS = {
  dashboard: '📊 Dashboard',
  inputs:    '⚙️ Inputs',
  daily:     '📅 Daily Tracker',
  weekly:    '📈 Weekly Tracker',
  monthly:   '🗓️ Monthly Tracker',
  annual:    '🎯 Annual Tracker',
  charts:    '📉 Charts',
  settings:  '🔧 Settings',
  guide:     '📖 Guide',
};

/* Master category definitions. min/max are the DEFAULT healthy thresholds
 * (h/week) — they land in editable cells on 🔧 Settings, so users can tune
 * them without touching any formula. '' = no threshold. */
const CATEGORIES = [
  { key: 'SLEEP',  emoji: '😴', name: 'Sleep',                productive: false, min: 49,  max: 63 },
  { key: 'WORK',   emoji: '💼', name: 'Work',                 productive: true,  min: '',  max: 55 },
  { key: 'FOOD',   emoji: '🍽️', name: 'Food',                 productive: false, min: 3.5, max: 21 },
  { key: 'CHORES', emoji: '🧹', name: 'Household Chores',     productive: false, min: '',  max: 15 },
  { key: 'CHILD',  emoji: '👶', name: 'Childcare',            productive: false, min: '',  max: '' },
  { key: 'FIT',    emoji: '🏋️', name: 'Fitness',              productive: true,  min: 3,   max: 20 },
  { key: 'ENT',    emoji: '🎬', name: 'Entertainment',        productive: false, min: '',  max: 25 },
  { key: 'REL',    emoji: '❤️', name: 'Relationships',        productive: false, min: 3,   max: '' },
  { key: 'LEARN',  emoji: '📚', name: 'Learning',             productive: true,  min: 1,   max: '' },
  { key: 'PD',     emoji: '🌱', name: 'Personal Development', productive: true,  min: 1,   max: '' },
  { key: 'SPIRIT', emoji: '🙏', name: 'Spiritual',            productive: false, min: '',  max: '' },
  { key: 'TRAVEL', emoji: '🚗', name: 'Travel',               productive: false, min: '',  max: '' },
  { key: 'ADMIN',  emoji: '🗂️', name: 'Admin',                productive: true,  min: '',  max: '' },
];
const CUSTOM_SLOTS = 5;           // extra user-defined category rows
const TRACKER_ROWS = CATEGORIES.length + CUSTOM_SLOTS; // rows in tracker grids

/* Guided-sentence input lines per category.
 * [label, defaultValue, unitText, mode]
 * mode drives the auto-generated "hours per week" formula for that line. */
const INPUT_BLOCKS = [
  { key: 'SLEEP', lines: [
    ['I sleep for around',                    7.5, 'hours per night',                       'h_night'],
    ['I wind down for',                       15,  'minutes before bed',                    'min_night'],
    ['My wake-up routine takes',              15,  'minutes each morning',                  'min_day'],
  ]},
  { key: 'WORK', split: true, lines: [
    ['I work',                                5,   'days per week',                         'days'],
    ['I work around',                         8,   'hours per working day (excl. lunch)',   'h_workday'],
    ['My lunch break is',                     30,  'minutes per working day',               'min_workday'],
    ['My commute is',                         0,   'minutes each way',                      'commute_min'],
    ['Getting ready for work takes',          5,   'minutes per working day',               'min_workday'],
    ['Switching off after work takes',        5,   'minutes per working day',               'min_workday'],
  ]},
  { key: 'FOOD', lines: [
    ['Breakfast takes',                       15,  'minutes per day (eating + prep)',       'min_day'],
    ['Lunch takes',                           40,  'minutes per non-working day',           'min_nonworkday'],
    ['Dinner takes',                          40,  'minutes per day (eating + prep)',       'min_day'],
    ['Extra cooking & meal prep is',          60,  'minutes per week',                      'min_week'],
  ]},
  { key: 'CHORES', lines: [
    ['I do groceries',                        2,   'times per week',                        'sessions'],
    ['Each grocery run takes',                60,  'minutes (incl. travel)',                'per_session_min'],
    ['I clean the house',                     1,   'times per week',                        'sessions'],
    ['Each cleaning session takes',           60,  'minutes',                               'per_session_min'],
    ['I do laundry',                          2,   'times per week',                        'sessions'],
    ['Each laundry session takes',            30,  'minutes of active time',                'per_session_min'],
    ['Other misc. chores take',               1,   'hours per week',                        'h_week'],
  ]},
  { key: 'CHILD', lines: [
    ['Each weekday I spend',                  2,   'hours actively on childcare',           'h_weekday5'],
    ['Each weekend day I spend',              3,   'hours actively on childcare',           'h_weekendday'],
    ['Child admin & logistics take',          0,   'hours per week',                        'h_week'],
    ['Other child-related time is',           0,   'hours per week',                        'h_week'],
  ]},
  { key: 'FIT', lines: [
    ['I exercise',                            3,   'times per week',                        'sessions'],
    ['Each session takes',                    60,  'minutes (incl. travel & shower)',       'per_session_min'],
    ['Other fitness-related time is',         1,   'hours per week',                        'h_week'],
  ]},
  { key: 'ENT', lines: [
    ['TV shows & movies',                     3,   'hours per week',                        'h_week'],
    ['Social media',                          4,   'hours per week',                        'h_week'],
    ['Reading for fun',                       2,   'hours per week',                        'h_week'],
    ['Gaming',                                0,   'hours per week',                        'h_week'],
    ['Other entertainment',                   1,   'hours per week',                        'h_week'],
  ]},
  { key: 'REL', lines: [
    ['Quality time with partner & family',    4,   'hours per week',                        'h_week'],
    ['Socialising with friends',              2.5, 'hours per week',                        'h_week'],
    ['Calls & catch-ups',                     60,  'minutes per week',                      'min_week'],
  ]},
  { key: 'LEARN', lines: [
    ['Courses & structured learning',         1.5, 'hours per week',                        'h_week'],
    ['Books, articles & study',               2,   'hours per week',                        'h_week'],
    ['Podcasts & audiobooks',                 20,  'minutes per day',                       'min_day'],
  ]},
  { key: 'PD', lines: [
    ['Journaling & reflection',               10,  'minutes per day',                       'min_day'],
    ['Meditation & mindfulness',              10,  'minutes per day',                       'min_day'],
    ['Weekly planning & review',              1,   'hours per week',                        'h_week'],
  ]},
  { key: 'SPIRIT', lines: [
    ['Daily practice',                        0,   'minutes per day',                       'min_day'],
    ['Services & community',                  0,   'hours per week',                        'h_week'],
  ]},
  { key: 'TRAVEL', lines: [
    ['Errands & getting around (non-commute)',1.5, 'hours per week',                        'h_week'],
    ['Trips & other travel',                  0,   'hours per week',                        'h_week'],
  ]},
  { key: 'ADMIN', lines: [
    ['Finances, email & life admin',          2,   'hours per week',                        'h_week'],
    ['Appointments & paperwork',              30,  'minutes per week',                      'min_week'],
  ]},
];

/* Named ranges owned by the builder (cleaned up on every rebuild). */
const OWNED_NAMES = [
  'HOURS_DAY', 'HOURS_WEEK', 'WEEKS_YEAR', 'WEEKS_MONTH', 'WORK_DAYS',
  'TOTAL_USED', 'FREE_TIME', 'PRODUCTIVE_H',
  'CAT_EMOJI', 'CAT_NAMES', 'CAT_HOURS',
].concat(CATEGORIES.map(c => 'PLAN_' + c.key));

/* ----------------------------------------------------------------------------
 * MENU + ENTRY POINT
 * ------------------------------------------------------------------------- */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('⚡ Executive OS')
    .addItem('Build / Rebuild System', 'buildExecutiveOS')
    .addToUi();
}

function buildExecutiveOS() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ctx = { ss: ss, plan: {} }; // plan: key -> A1 of weekly-total cell on Inputs

  // -- Reset: drop owned named ranges, then owned sheets (via a temp keeper) --
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

  // -- Build (order matters only for named-range registration convenience) --
  buildInputs(ctx);
  buildSettings(ctx);
  buildDaily(ctx);
  buildWeekly(ctx);
  buildMonthly(ctx);
  buildAnnual(ctx);
  buildChartsTab(ctx);
  buildDashboard(ctx);
  buildGuide(ctx);

  // -- Tab order + colours ---------------------------------------------------
  const order = [SHEETS.dashboard, SHEETS.inputs, SHEETS.daily, SHEETS.weekly,
                 SHEETS.monthly, SHEETS.annual, SHEETS.charts, SHEETS.settings,
                 SHEETS.guide];
  order.forEach((name, i) => {
    const sh = ss.getSheetByName(name);
    ss.setActiveSheet(sh);
    ss.moveActiveSheet(i + 1);
  });
  const tabColors = {};
  tabColors[SHEETS.dashboard] = UI.navy;
  tabColors[SHEETS.inputs]    = UI.accent;
  tabColors[SHEETS.daily]     = UI.teal;
  tabColors[SHEETS.weekly]    = UI.teal;
  tabColors[SHEETS.monthly]   = UI.teal;
  tabColors[SHEETS.annual]    = UI.teal;
  tabColors[SHEETS.charts]    = UI.slate;
  tabColors[SHEETS.settings]  = UI.slate;
  tabColors[SHEETS.guide]     = UI.faint;
  Object.keys(tabColors).forEach(n => ss.getSheetByName(n).setTabColor(tabColors[n]));

  ss.deleteSheet(keeper);
  ss.setActiveSheet(ss.getSheetByName(SHEETS.dashboard));
  SpreadsheetApp.flush();
  SpreadsheetApp.getActiveSpreadsheet().toast(
    'Your 168-Hour Executive OS is ready. Start on ⚙️ Inputs.', '⚡ Build complete', 8);
}

/* ----------------------------------------------------------------------------
 * SMALL HELPERS
 * ------------------------------------------------------------------------- */
function freshSheet(ctx, name) {
  const sh = ctx.ss.insertSheet(name);
  sh.setHiddenGridlines(true);
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns())
    .setFontFamily('Inter').setFontSize(10).setFontColor(UI.ink)
    .setVerticalAlignment('middle');
  return sh;
}

/** Full-width section band (dark). */
function band(sh, row, c1, c2, text) {
  const r = sh.getRange(row, c1, 1, c2 - c1 + 1);
  r.merge().setValue(text)
    .setBackground(UI.navy).setFontColor('#FFFFFF')
    .setFontWeight('bold').setFontSize(11).setHorizontalAlignment('left');
  sh.setRowHeight(row, 30);
  return r;
}

/** Style a cell as an editable input. */
function inputCell(range) {
  range.setBackground(UI.inputBg).setFontWeight('bold')
       .setHorizontalAlignment('center')
       .setBorder(true, true, true, true, false, false, UI.inputLine,
                  SpreadsheetApp.BorderStyle.SOLID);
  return range;
}

function numberValidation(range, min, max) {
  range.setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireNumberBetween(min, max)
      .setAllowInvalid(false)
      .setHelpText('Enter a number between ' + min + ' and ' + max + '.')
      .build());
}

function warnProtect(range, note) {
  try { range.protect().setWarningOnly(true).setDescription(note); } catch (e) {}
}

function pageTitle(sh, row, c1, c2, title, subtitle) {
  sh.getRange(row, c1, 1, c2 - c1 + 1).merge().setValue(title)
    .setFontSize(18).setFontWeight('bold').setFontColor(UI.ink);
  sh.setRowHeight(row, 34);
  if (subtitle) {
    sh.getRange(row + 1, c1, 1, c2 - c1 + 1).merge().setValue(subtitle)
      .setFontSize(10).setFontColor(UI.slate).setFontStyle('italic');
  }
}

/* ----------------------------------------------------------------------------
 * ⚙️ INPUTS — guided sentence inputs, one block per category
 *    Cols: B label · C value(INPUT) · D unit · E — · F h/week (auto) · G note
 * ------------------------------------------------------------------------- */
function buildInputs(ctx) {
  const sh = freshSheet(ctx, SHEETS.inputs);
  const ss = ctx.ss;
  sh.setColumnWidth(1, 18);   // A spacer
  sh.setColumnWidth(2, 250);  // B label
  sh.setColumnWidth(3, 76);   // C value
  sh.setColumnWidth(4, 250);  // D unit
  sh.setColumnWidth(5, 26);   // E arrow
  sh.setColumnWidth(6, 92);   // F hours/week
  sh.setColumnWidth(7, 250);  // G note

  pageTitle(sh, 2, 2, 7, '⚙️ Inputs — plan your 168 hours',
    'Only ever edit the blue cells. Every other number in this workbook updates automatically.');

  let row = 5;
  const catByKey = {};
  CATEGORIES.forEach(c => catByKey[c.key] = c);

  INPUT_BLOCKS.forEach(block => {
    const cat = catByKey[block.key];
    band(sh, row, 2, 7, '  ' + cat.emoji + '  ' + cat.name.toUpperCase());
    row++;

    // column mini-headers
    sh.getRange(row, 6).setValue('h / week')
      .setFontSize(8).setFontColor(UI.faint).setHorizontalAlignment('center');
    row++;

    const firstLine = row;
    block.lines.forEach(line => {
      const label = line[0], def = line[1], unit = line[2], mode = line[3];
      sh.getRange(row, 2).setValue(label).setFontColor(UI.slate);
      const val = sh.getRange(row, 3).setValue(def);
      inputCell(val);
      numberValidation(val, 0, mode === 'days' ? 7 : 10000);
      sh.getRange(row, 4).setValue(unit).setFontColor(UI.slate);

      const f = lineFormula(mode, row);
      if (f) {
        sh.getRange(row, 5).setValue('→').setFontColor(UI.faint)
          .setHorizontalAlignment('center');
        sh.getRange(row, 6).setFormula(f).setNumberFormat('0.00')
          .setFontColor(UI.ink).setHorizontalAlignment('center');
      }
      if (mode === 'days') {
        ss.setNamedRange('WORK_DAYS', sh.getRange(row, 3));
        sh.getRange(row, 7).setValue('drives lunch, commute & non-work-day lunches')
          .setFontSize(8).setFontColor(UI.faint);
      }
      if (mode === 'sessions') {
        sh.getRange(row, 7).setValue('pairs with the line below')
          .setFontSize(8).setFontColor(UI.faint);
      }
      row++;
    });

    // total row
    sh.getRange(row, 4, 1, 2).merge().setValue('Weekly total  →')
      .setFontWeight('bold').setHorizontalAlignment('right').setFontColor(UI.ink);
    const total = sh.getRange(row, 6)
      .setFormula('=ROUND(SUM($F$' + firstLine + ':$F$' + (row - 1) + '),2)')
      .setNumberFormat('0.0').setFontWeight('bold').setFontSize(11)
      .setHorizontalAlignment('center').setFontColor(UI.accent);
    sh.getRange(row, 2, 1, 5)
      .setBorder(true, false, false, false, false, false, UI.line,
                 SpreadsheetApp.BorderStyle.SOLID);
    sh.getRange(row, 7).setValue('hours per week on ' + cat.name.toLowerCase())
      .setFontSize(9).setFontColor(UI.slate);
    ss.setNamedRange('PLAN_' + cat.key, total);
    ctx.plan[cat.key] = total.getA1Notation();
    row++;

    // WORK gets a sub-analysis of what happens INSIDE working hours
    if (block.split) {
      const officialRow = firstLine + 1; // 'I work around X hours per working day'
      sh.getRange(row, 2).setValue('… of which meetings are').setFontColor(UI.faint)
        .setFontStyle('italic');
      inputCell(sh.getRange(row, 3).setValue(5));
      numberValidation(sh.getRange(row, 3), 0, 168);
      sh.getRange(row, 4).setValue('hours per week').setFontColor(UI.faint).setFontStyle('italic');
      sh.getRange(row, 7).setValue('already inside your working hours — not added again')
        .setFontSize(8).setFontColor(UI.faint);
      const meetRow = row; row++;

      sh.getRange(row, 2).setValue('… of which deep work is').setFontColor(UI.faint)
        .setFontStyle('italic');
      inputCell(sh.getRange(row, 3).setValue(12));
      numberValidation(sh.getRange(row, 3), 0, 168);
      sh.getRange(row, 4).setValue('hours per week').setFontColor(UI.faint).setFontStyle('italic');
      const deepRow = row; row++;

      sh.getRange(row, 2).setValue('… leaving shallow / other work of').setFontColor(UI.faint)
        .setFontStyle('italic');
      sh.getRange(row, 3)
        .setFormula('=MAX(0,ROUND($F$' + officialRow + '-$C$' + meetRow + '-$C$' + deepRow + ',1))')
        .setNumberFormat('0.0').setHorizontalAlignment('center').setFontColor(UI.faint);
      sh.getRange(row, 4).setValue('hours per week').setFontColor(UI.faint).setFontStyle('italic');
      row++;
    }
    row++; // gap between blocks
  });

  sh.setFrozenRows(3);
  warnProtect(sh.getRange('F1:F' + row), 'Auto-calculated — edit the blue cells instead.');
}

/** Formula for one input line's weekly-hours contribution. */
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
    default:               return ''; // 'days', 'sessions'
  }
}

/* ----------------------------------------------------------------------------
 * 🔧 SETTINGS — constants + master category table (single source of truth)
 * ------------------------------------------------------------------------- */
function buildSettings(ctx) {
  const sh = freshSheet(ctx, SHEETS.settings);
  const ss = ctx.ss;
  const widths = [18, 46, 190, 92, 82, 78, 88, 82, 82, 100];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 10, '🔧 Settings & Master Data',
    'Single source of truth. Add custom categories in the blue rows — every tracker and chart picks them up automatically.');

  // -- Constants -------------------------------------------------------------
  band(sh, 5, 2, 10, '  ⏱️  CONSTANTS');
  const constants = [
    ['Hours per day',   '24',            'HOURS_DAY'],
    ['Hours per week',  '=HOURS_DAY*7',  'HOURS_WEEK'],
    ['Weeks per year',  '=365.25/7',     'WEEKS_YEAR'],
    ['Weeks per month', '=WEEKS_YEAR/12','WEEKS_MONTH'],
  ];
  constants.forEach((c, i) => {
    const r = 6 + i;
    sh.getRange(r, 2, 1, 2).merge().setValue(c[0]).setFontColor(UI.slate);
    const cell = sh.getRange(r, 4);
    if (String(c[1]).charAt(0) === '=') cell.setFormula(c[1]); else cell.setValue(Number(c[1]));
    cell.setNumberFormat('0.###').setFontWeight('bold').setHorizontalAlignment('center');
    ss.setNamedRange(c[2], cell);
  });

  // -- Master category table -------------------------------------------------
  const tbl = 12;
  band(sh, tbl, 2, 10, '  🗂️  MASTER CATEGORY TABLE');
  const headers = ['', 'Category', 'Planned h/wk', '% of week', 'Per day',
                   'Productive', 'Min h/wk', 'Max h/wk', 'Status'];
  sh.getRange(tbl + 1, 2, 1, 9).setValues([headers])
    .setFontSize(9).setFontWeight('bold').setFontColor(UI.slate)
    .setBackground(UI.card).setHorizontalAlignment('center');
  sh.getRange(tbl + 1, 3).setHorizontalAlignment('left');

  const first = tbl + 2;                       // first category row
  const lastCore = first + CATEGORIES.length - 1;
  const last = lastCore + CUSTOM_SLOTS;        // last custom row

  CATEGORIES.forEach((cat, i) => {
    const r = first + i;
    sh.getRange(r, 2).setValue(cat.emoji).setHorizontalAlignment('center');
    sh.getRange(r, 3).setValue(cat.name);
    sh.getRange(r, 4).setFormula('=ROUND(PLAN_' + cat.key + ',2)');
    sh.getRange(r, 8).setValue(cat.min === '' ? '' : cat.min);
    sh.getRange(r, 9).setValue(cat.max === '' ? '' : cat.max);
  });
  // custom slots: fully editable rows
  for (let i = 0; i < CUSTOM_SLOTS; i++) {
    const r = lastCore + 1 + i;
    inputCell(sh.getRange(r, 2, 1, 2)).setHorizontalAlignment('left');
    sh.getRange(r, 2).setHorizontalAlignment('center');
    inputCell(sh.getRange(r, 4));
    numberValidation(sh.getRange(r, 4), 0, 168);
    sh.getRange(r, 3).setNote('Type a custom category name here — it flows into every tracker and chart.');
  }
  // shared formula columns
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 5).setFormula('=IF($C' + r + '="","",$D' + r + '/HOURS_WEEK)');
    sh.getRange(r, 6).setFormula('=IF($C' + r + '="","",$D' + r + '/7)');
    sh.getRange(r, 10).setFormula(
      '=IF($C' + r + '="","",IFS(AND($H' + r + '<>"",$D' + r + '<$H' + r + '),"🔻 Low",' +
      'AND($I' + r + '<>"",$D' + r + '>$I' + r + '),"🔺 High",TRUE,"✅ OK"))');
  }
  // productive checkboxes
  const prodRange = sh.getRange(first, 7, TRACKER_ROWS, 1);
  prodRange.insertCheckboxes();
  CATEGORIES.forEach((cat, i) => sh.getRange(first + i, 7).setValue(cat.productive));
  // min/max are editable thresholds
  inputCell(sh.getRange(first, 8, TRACKER_ROWS, 2));
  sh.getRange(first, 8, TRACKER_ROWS, 2).setNote(
    'Optional healthy range (h/week). Drives the Status column and colour warnings.');

  sh.getRange(first, 4, TRACKER_ROWS, 3).setNumberFormat('0.0')
    .setHorizontalAlignment('center');
  sh.getRange(first, 5, TRACKER_ROWS, 1).setNumberFormat('0.0%');
  sh.getRange(first, 8, TRACKER_ROWS, 2).setNumberFormat('0.0');
  sh.getRange(first, 10, TRACKER_ROWS, 1).setHorizontalAlignment('center');
  sh.getRange(first, 2, TRACKER_ROWS, 9)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  // named ranges for the whole system
  ss.setNamedRange('CAT_EMOJI', sh.getRange(first, 2, TRACKER_ROWS, 1));
  ss.setNamedRange('CAT_NAMES', sh.getRange(first, 3, TRACKER_ROWS, 1));
  ss.setNamedRange('CAT_HOURS', sh.getRange(first, 4, TRACKER_ROWS, 1));

  // -- Totals ----------------------------------------------------------------
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
    .setFormula('=SUMIFS(CAT_HOURS,' +
      "'" + SHEETS.settings + "'!G" + first + ':G' + last + ',TRUE)')
    .setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center'));

  // -- Conditional formatting -----------------------------------------------
  const rules = [];
  const hoursCol = sh.getRange(first, 4, TRACKER_ROWS, 1);
  const mk = (formula, bg, fc) => SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(formula).setBackground(bg).setFontColor(fc)
    .setRanges([hoursCol]).build();
  rules.push(mk('=AND($C' + first + '="Work",$D' + first + '>60)', UI.badBg, UI.bad));
  rules.push(mk('=AND($C' + first + '="Sleep",$D' + first + '<49,$D' + first + '<>"")', UI.badBg, UI.bad));
  rules.push(mk('=AND($C' + first + '="Fitness",$D' + first + '<3)', UI.warnBg, UI.warn));
  rules.push(mk('=AND($I' + first + '<>"",$D' + first + '>$I' + first + ')', UI.badBg, UI.bad));
  rules.push(mk('=AND($H' + first + '<>"",$D' + first + '<$H' + first + ')', UI.warnBg, UI.warn));
  const statusCol = sh.getRange(first, 10, TRACKER_ROWS, 1);
  const mkText = (txt, fc) => SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains(txt).setFontColor(fc).setRanges([statusCol]).build();
  rules.push(mkText('OK', UI.good));
  rules.push(mkText('Low', UI.warn));
  rules.push(mkText('High', UI.bad));
  const freeCell = sh.getRange(tot + 1, 4);
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0).setBackground(UI.badBg).setFontColor(UI.bad)
    .setRanges([freeCell]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(5).setBackground(UI.warnBg).setFontColor(UI.warn)
    .setRanges([freeCell]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThanOrEqualTo(5).setBackground(UI.goodBg).setFontColor(UI.good)
    .setRanges([freeCell]).build());
  sh.setConditionalFormatRules(rules);

  sh.setFrozenRows(tbl + 1);
  warnProtect(sh.getRange(first, 4, CATEGORIES.length, 1),
    'Core category hours come from ⚙️ Inputs — edit them there.');
  warnProtect(sh.getRange(first, 5, TRACKER_ROWS, 2), 'Auto-calculated.');
  warnProtect(sh.getRange(first, 10, TRACKER_ROWS, 1), 'Auto-calculated.');

  ctx.settings = { first: first, last: last, lastCore: lastCore, tot: tot };
}

/* ----------------------------------------------------------------------------
 * 📅 DAILY TRACKER — log actual hours per category per day
 * ------------------------------------------------------------------------- */
function buildDaily(ctx) {
  const sh = freshSheet(ctx, SHEETS.daily);
  const widths = [18, 190, 78, 62, 62, 62, 62, 62, 62, 62, 84, 84];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 12, '📅 Daily Tracker — log what actually happened',
    'Type real hours in the blue grid. Categories arrive automatically from 🔧 Settings.');

  const head = 4;
  const first = head + 1;
  const last = first + TRACKER_ROWS - 1;
  const headers = ['Category', 'Plan / day', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri',
                   'Sat', 'Sun', 'Week actual', 'vs plan'];
  sh.getRange(head, 2, 1, 11).setValues([headers])
    .setBackground(UI.navy).setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(9).setHorizontalAlignment('center');
  sh.getRange(head, 2).setHorizontalAlignment('left');
  sh.setRowHeight(head, 28);

  sh.getRange(first, 2).setFormula('=IFERROR(FILTER(CAT_NAMES,CAT_NAMES<>""),"")');
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 3).setFormula(
      '=IF($B' + r + '="","",ROUND(XLOOKUP($B' + r + ',CAT_NAMES,CAT_HOURS,0)/7,2))');
    sh.getRange(r, 11).setFormula(
      '=IF($B' + r + '="","",SUM($D' + r + ':$J' + r + '))');
    sh.getRange(r, 12).setFormula(
      '=IF($B' + r + '="","",ROUND($K' + r + '-XLOOKUP($B' + r + ',CAT_NAMES,CAT_HOURS,0),1))');
  }
  const grid = sh.getRange(first, 4, TRACKER_ROWS, 7);
  inputCell(grid).setFontWeight('normal');
  numberValidation(grid, 0, 24);
  grid.setNumberFormat('0.0#');
  sh.getRange(first, 3, TRACKER_ROWS, 1).setNumberFormat('0.00').setHorizontalAlignment('center');
  sh.getRange(first, 11, TRACKER_ROWS, 2).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 2, TRACKER_ROWS, 11)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  // day totals + free time
  const tRow = last + 1;
  sh.getRange(tRow, 2, 1, 2).merge().setValue('Hours logged').setFontWeight('bold')
    .setHorizontalAlignment('right');
  sh.getRange(tRow + 1, 2, 1, 2).merge().setValue('Unlogged (24 − logged)')
    .setFontColor(UI.slate).setHorizontalAlignment('right');
  for (let c = 4; c <= 10; c++) {
    const L = String.fromCharCode(64 + c);
    sh.getRange(tRow, c).setFormula('=SUM(' + L + first + ':' + L + last + ')');
    sh.getRange(tRow + 1, c).setFormula('=HOURS_DAY-' + L + tRow);
  }
  sh.getRange(tRow, 11).setFormula('=SUM(K' + first + ':K' + last + ')');
  sh.getRange(tRow + 1, 11).setFormula('=HOURS_WEEK-K' + tRow);
  sh.getRange(tRow, 4, 2, 8).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(tRow, 2, 1, 10).setFontWeight('bold');
  sh.getRange(tRow, 2, 1, 11)
    .setBorder(true, false, false, false, false, false, UI.navy, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  // CF: impossible / heavy days
  const dayTotals = sh.getRange(tRow, 4, 1, 7);
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule().whenNumberGreaterThan(24)
      .setBackground(UI.badBg).setFontColor(UI.bad).setRanges([dayTotals]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenNumberGreaterThan(18)
      .setBackground(UI.warnBg).setFontColor(UI.warn).setRanges([dayTotals]).build(),
  ]);

  sh.setFrozenRows(head);
  sh.setFrozenColumns(2);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 2, 2), 'Auto-fed from Settings.');
  warnProtect(sh.getRange(first, 11, TRACKER_ROWS + 2, 2), 'Auto-calculated.');
  ctx.daily = { first: first, last: last };
}

/* ----------------------------------------------------------------------------
 * 📈 WEEKLY TRACKER — planned vs actual
 * ------------------------------------------------------------------------- */
function buildWeekly(ctx) {
  const sh = freshSheet(ctx, SHEETS.weekly);
  const widths = [18, 190, 90, 90, 80, 84, 84, 140];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 8, '📈 Weekly Tracker — planned vs actual',
    'Planned comes from ⚙️ Inputs; actual comes from 📅 Daily Tracker. Nothing to type here.');

  const head = 4, first = head + 1, last = first + TRACKER_ROWS - 1;
  const d = ctx.daily;
  const headers = ['Category', 'Planned', 'Actual', 'Diff', '% of plan', '% of week', 'Progress'];
  sh.getRange(head, 2, 1, 7).setValues([headers])
    .setBackground(UI.navy).setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(9).setHorizontalAlignment('center');
  sh.getRange(head, 2).setHorizontalAlignment('left');
  sh.setRowHeight(head, 28);

  const dailyRef = "'" + SHEETS.daily + "'";
  sh.getRange(first, 2).setFormula('=IFERROR(FILTER(CAT_NAMES,CAT_NAMES<>""),"")');
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 3).setFormula(
      '=IF($B' + r + '="","",XLOOKUP($B' + r + ',CAT_NAMES,CAT_HOURS,0))');
    sh.getRange(r, 4).setFormula(
      '=IF($B' + r + '="","",IFERROR(XLOOKUP($B' + r + ',' + dailyRef + '!$B$' + d.first +
      ':$B$' + d.last + ',' + dailyRef + '!$K$' + d.first + ':$K$' + d.last + ',0),0))');
    sh.getRange(r, 5).setFormula('=IF($B' + r + '="","",$D' + r + '-$C' + r + ')');
    sh.getRange(r, 6).setFormula(
      '=IF(OR($B' + r + '="",$C' + r + '=0),"",$D' + r + '/$C' + r + ')');
    sh.getRange(r, 7).setFormula('=IF($B' + r + '="","",$C' + r + '/HOURS_WEEK)');
    sh.getRange(r, 8).setFormula(
      '=IF($B' + r + '="","",SPARKLINE($D' + r + ',{"charttype","bar";"max",MAX($C' + r +
      ',$D' + r + ',0.01);"color1","' + UI.accent + '"}))');
  }
  sh.getRange(first, 3, TRACKER_ROWS, 3).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 6, TRACKER_ROWS, 2).setNumberFormat('0%').setHorizontalAlignment('center');
  sh.getRange(first, 2, TRACKER_ROWS, 7)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  const t = last + 2;
  const rows = [
    ['Total allocated / logged', '=SUM(C' + first + ':C' + last + ')', '=SUM(D' + first + ':D' + last + ')'],
    ['Free / remaining hours',   '=HOURS_WEEK-C' + t,                  '=HOURS_WEEK-D' + t],
    ['Utilization',              '=C' + t + '/HOURS_WEEK',             '=D' + t + '/HOURS_WEEK'],
  ];
  rows.forEach((row, i) => {
    sh.getRange(t + i, 2).setValue(row[0]).setFontWeight('bold');
    sh.getRange(t + i, 3).setFormula(row[1]);
    sh.getRange(t + i, 4).setFormula(row[2]);
  });
  sh.getRange(t, 3, 2, 2).setNumberFormat('0.0');
  sh.getRange(t + 2, 3, 1, 2).setNumberFormat('0.0%');
  sh.getRange(t, 3, 3, 2).setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(t, 2, 1, 7)
    .setBorder(true, false, false, false, false, false, UI.navy, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  // CF: neglected (<50% of plan) amber, overrun (>120%) red — on % of plan
  const pct = sh.getRange(first, 6, TRACKER_ROWS, 1);
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($B' + first + '<>"",$F' + first + '<>"",$F' + first + '<0.5)')
      .setBackground(UI.warnBg).setFontColor(UI.warn).setRanges([pct]).build(),
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($B' + first + '<>"",$F' + first + '<>"",$F' + first + '>1.2)')
      .setBackground(UI.badBg).setFontColor(UI.bad).setRanges([pct]).build(),
  ]);

  sh.setFrozenRows(head);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 5, 7), 'Fully automatic — nothing to edit here.');
  ctx.weekly = { first: first, last: last, totals: t };
}

/* ----------------------------------------------------------------------------
 * 🗓️ MONTHLY TRACKER — projections + variance
 * ------------------------------------------------------------------------- */
function buildMonthly(ctx) {
  const sh = freshSheet(ctx, SHEETS.monthly);
  const widths = [18, 190, 90, 100, 100, 90, 90, 140];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 8, '🗓️ Monthly Tracker — the month, projected',
    'Weekly plan × ' + '4.35 weeks/month. Actuals extrapolate the current week — all automatic.');

  const head = 4, first = head + 1, last = first + TRACKER_ROWS - 1;
  const w = ctx.weekly;
  const weeklyRef = "'" + SHEETS.weekly + "'";
  const headers = ['Category', 'Weekly plan', 'Monthly plan', 'Monthly actual*',
                   'Variance', '% of month', 'Plan vs actual'];
  sh.getRange(head, 2, 1, 7).setValues([headers])
    .setBackground(UI.navy).setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(9).setHorizontalAlignment('center');
  sh.getRange(head, 2).setHorizontalAlignment('left');
  sh.setRowHeight(head, 28);

  sh.getRange(first, 2).setFormula('=IFERROR(FILTER(CAT_NAMES,CAT_NAMES<>""),"")');
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 3).setFormula(
      '=IF($B' + r + '="","",XLOOKUP($B' + r + ',CAT_NAMES,CAT_HOURS,0))');
    sh.getRange(r, 4).setFormula('=IF($B' + r + '="","",ROUND($C' + r + '*WEEKS_MONTH,1))');
    sh.getRange(r, 5).setFormula(
      '=IF($B' + r + '="","",ROUND(IFERROR(XLOOKUP($B' + r + ',' + weeklyRef + '!$B$' + w.first +
      ':$B$' + w.last + ',' + weeklyRef + '!$D$' + w.first + ':$D$' + w.last + ',0),0)*WEEKS_MONTH,1))');
    sh.getRange(r, 6).setFormula('=IF($B' + r + '="","",$E' + r + '-$D' + r + ')');
    sh.getRange(r, 7).setFormula(
      '=IF($B' + r + '="","",$D' + r + '/(HOURS_WEEK*WEEKS_MONTH))');
    sh.getRange(r, 8).setFormula(
      '=IF($B' + r + '="","",SPARKLINE({$D' + r + ',$E' + r + '},{"charttype","bar";"max",MAX($D' +
      r + ',$E' + r + ',0.01);"color1","' + UI.faint + '";"color2","' + UI.accent + '"}))');
  }
  sh.getRange(first, 3, TRACKER_ROWS, 4).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 7, TRACKER_ROWS, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(first, 2, TRACKER_ROWS, 7)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  const t = last + 2;
  sh.getRange(t, 2).setValue('Total').setFontWeight('bold');
  sh.getRange(t, 4).setFormula('=SUM(D' + first + ':D' + last + ')');
  sh.getRange(t, 5).setFormula('=SUM(E' + first + ':E' + last + ')');
  sh.getRange(t, 4, 1, 2).setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(t + 1, 2).setValue('Free time per month').setFontWeight('bold');
  sh.getRange(t + 1, 4).setFormula('=HOURS_WEEK*WEEKS_MONTH-D' + t)
    .setNumberFormat('0.0').setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(t + 2, 2, 1, 5).merge()
    .setValue('* Monthly actual extrapolates the current Daily Tracker week across the month.')
    .setFontSize(8).setFontColor(UI.faint).setFontStyle('italic').setHorizontalAlignment('left');
  sh.getRange(t, 2, 1, 7)
    .setBorder(true, false, false, false, false, false, UI.navy, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  sh.setFrozenRows(head);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 4, 7), 'Fully automatic — nothing to edit here.');
}

/* ----------------------------------------------------------------------------
 * 🎯 ANNUAL TRACKER — the year at a glance
 * ------------------------------------------------------------------------- */
function buildAnnual(ctx) {
  const sh = freshSheet(ctx, SHEETS.annual);
  const widths = [18, 190, 90, 104, 96, 96, 90];
  widths.forEach((w, i) => sh.setColumnWidth(i + 1, w));

  pageTitle(sh, 2, 2, 7, '🎯 Annual Tracker — what a year of this plan adds up to',
    'Weekly plan × 52.18 weeks. This is where small weekly numbers become life-sized.');

  const head = 4, first = head + 1, last = first + TRACKER_ROWS - 1;
  const headers = ['Category', 'Weekly h', 'Annual hours', 'Annual days', 'Annual weeks', '% of year'];
  sh.getRange(head, 2, 1, 6).setValues([headers])
    .setBackground(UI.navy).setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(9).setHorizontalAlignment('center');
  sh.getRange(head, 2).setHorizontalAlignment('left');
  sh.setRowHeight(head, 28);

  sh.getRange(first, 2).setFormula('=IFERROR(FILTER(CAT_NAMES,CAT_NAMES<>""),"")');
  for (let r = first; r <= last; r++) {
    sh.getRange(r, 3).setFormula('=IF($B' + r + '="","",XLOOKUP($B' + r + ',CAT_NAMES,CAT_HOURS,0))');
    sh.getRange(r, 4).setFormula('=IF($B' + r + '="","",ROUND($C' + r + '*WEEKS_YEAR,0))');
    sh.getRange(r, 5).setFormula('=IF($B' + r + '="","",ROUND($D' + r + '/HOURS_DAY,1))');
    sh.getRange(r, 6).setFormula('=IF($B' + r + '="","",ROUND($D' + r + '/HOURS_WEEK,1))');
    sh.getRange(r, 7).setFormula('=IF($B' + r + '="","",$C' + r + '/HOURS_WEEK)');
  }
  sh.getRange(first, 3, TRACKER_ROWS, 1).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 4, TRACKER_ROWS, 1).setNumberFormat('#,##0').setHorizontalAlignment('center');
  sh.getRange(first, 5, TRACKER_ROWS, 2).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(first, 7, TRACKER_ROWS, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(first, 2, TRACKER_ROWS, 6)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  const t = last + 2;
  band(sh, t, 2, 7, '  💡  PERSPECTIVE');
  const facts = [
    '="At this pace you will sleep "&ROUND(PLAN_SLEEP*WEEKS_YEAR/24,0)&" full days this year."',
    '="You will work "&ROUND(PLAN_WORK*WEEKS_YEAR,0)&" hours — that is "&ROUND(PLAN_WORK*WEEKS_YEAR/24,0)&" days."',
    '="Free, unallocated time adds up to "&ROUND(MAX(0,FREE_TIME)*WEEKS_YEAR,0)&" hours a year ("&ROUND(MAX(0,FREE_TIME)*WEEKS_YEAR/24,1)&" days). Spend them on purpose."',
    '="Learning & personal development compound to "&ROUND((PLAN_LEARN+PLAN_PD)*WEEKS_YEAR,0)&" hours a year."',
  ];
  facts.forEach((f, i) => {
    sh.getRange(t + 1 + i, 2, 1, 6).merge().setFormula(f)
      .setFontColor(UI.slate).setFontStyle('italic');
  });

  sh.setFrozenRows(head);
  warnProtect(sh.getRange(first, 2, TRACKER_ROWS + 7, 6), 'Fully automatic — nothing to edit here.');
}

/* ----------------------------------------------------------------------------
 * 📉 CHARTS — data feeds (auto) + large-format charts
 * ------------------------------------------------------------------------- */
function buildChartsTab(ctx) {
  const sh = freshSheet(ctx, SHEETS.charts);
  const w = ctx.weekly;
  sh.setColumnWidth(1, 18);
  sh.setColumnWidth(2, 190);
  sh.setColumnWidth(3, 90);
  sh.setColumnWidth(4, 30);
  sh.setColumnWidth(5, 190);
  sh.setColumnWidth(6, 90);
  sh.setColumnWidth(7, 90);

  pageTitle(sh, 2, 2, 7, '📉 Charts — data feeds',
    'These little tables feed every chart automatically (blank category rows are filtered out). Charts float below.');

  // Feed 1: allocation incl. free time
  const f1 = 5;
  sh.getRange(f1 - 1, 2, 1, 2).setValues([['Life area', 'Hours / week']])
    .setFontWeight('bold').setFontSize(9).setBackground(UI.card);
  sh.getRange(f1, 2).setFormula(
    '={IFERROR(FILTER({CAT_NAMES,CAT_HOURS},CAT_NAMES<>""),{"—",0});{"Free Time",MAX(0,FREE_TIME)}}');
  sh.getRange(f1, 3, TRACKER_ROWS + 1, 1).setNumberFormat('0.0');

  // Feed 2: planned vs actual (from Weekly Tracker)
  const weeklyRef = "'" + SHEETS.weekly + "'";
  sh.getRange(f1 - 1, 5, 1, 3).setValues([['Category', 'Planned', 'Actual']])
    .setFontWeight('bold').setFontSize(9).setBackground(UI.card);
  sh.getRange(f1, 5).setFormula(
    '=IFERROR(FILTER(' + weeklyRef + '!$B$' + w.first + ':$D$' + w.last + ',' +
    weeklyRef + '!$B$' + w.first + ':$B$' + w.last + '<>""),{"—",0,0})');
  sh.getRange(f1, 6, TRACKER_ROWS, 2).setNumberFormat('0.0');

  const feedRows = TRACKER_ROWS + 2; // header + rows + free-time line
  const donutRange = sh.getRange(f1 - 1, 2, feedRows, 2);
  const barRange   = sh.getRange(f1 - 1, 2, feedRows, 2);
  const pvaRange   = sh.getRange(f1 - 1, 5, TRACKER_ROWS + 1, 3);
  ctx.chartFeeds = { donut: donutRange, bar: barRange, pva: pvaRange, sheet: sh };

  const anchor = f1 + TRACKER_ROWS + 4;
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(donutRange).setNumHeaders(1)
    .setPosition(anchor, 2, 0, 0)
    .setOption('title', 'Time allocation — where the 168 hours go')
    .setOption('pieHole', 0.58)
    .setOption('colors', UI.chartColors)
    .setOption('width', 520).setOption('height', 360)
    .build());
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.BAR)
    .addRange(barRange).setNumHeaders(1)
    .setPosition(anchor, 6, 0, 0)
    .setOption('title', 'Hours per week by life area')
    .setOption('colors', [UI.accent])
    .setOption('legend', { position: 'none' })
    .setOption('width', 520).setOption('height', 360)
    .build());
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.COLUMN)
    .addRange(pvaRange).setNumHeaders(1)
    .setPosition(anchor + 19, 2, 0, 0)
    .setOption('title', 'Planned vs actual — this week')
    .setOption('colors', [UI.faint, UI.accent])
    .setOption('width', 1000).setOption('height', 340)
    .build());

  warnProtect(sh.getRange(f1 - 1, 2, feedRows, 6), 'Chart data feeds — automatic.');
}

/* ----------------------------------------------------------------------------
 * 📊 DASHBOARD — the executive view
 * ------------------------------------------------------------------------- */
function buildDashboard(ctx) {
  const sh = freshSheet(ctx, SHEETS.dashboard);
  sh.setColumnWidth(1, 18);
  for (let c = 2; c <= 13; c++) sh.setColumnWidth(c, 92);

  // -- Header ----------------------------------------------------------------
  sh.getRange(2, 2, 1, 8).merge().setValue('168-HOUR EXECUTIVE OS')
    .setFontSize(22).setFontWeight('bold').setFontColor(UI.ink);
  sh.getRange(3, 2, 1, 8).merge()
    .setFormula('="Week "&ISOWEEKNUM(TODAY())&"  ·  "&TEXT(TODAY(),"dddd, d mmmm yyyy")&"  ·  Every week resets to 168 hours. This is how you are spending yours."')
    .setFontSize(10).setFontColor(UI.slate).setFontStyle('italic');
  sh.setRowHeight(2, 38);

  // -- KPI cards -------------------------------------------------------------
  const cards = [
    { c: 2,  label: 'HOURS USED',    formula: '=ROUND(TOTAL_USED,1)',        sub: 'of 168 allocated',    fmt: '0.0',  hero: false },
    { c: 4,  label: 'HOURS FREE',    formula: '=ROUND(FREE_TIME,1)',         sub: 'unallocated buffer',  fmt: '0.0',  hero: true  },
    { c: 6,  label: 'UTILIZATION',   formula: '=TOTAL_USED/HOURS_WEEK',      sub: 'of your week',        fmt: '0.0%', hero: false },
    { c: 8,  label: 'BALANCE SCORE', formula:
        '=LET(s,PLAN_SLEEP,w,PLAN_WORK,f,PLAN_FIT,r,PLAN_REL,l,PLAN_LEARN+PLAN_PD,ft,FREE_TIME,' +
        'ROUND(100*((s>=49)*(s<=63)+(w<=55)+(f>=3)+(r>=3)+(l>=2)+(ft>=5)+(ft>=0))/7,0))',
        sub: 'out of 100',          fmt: '0',    hero: false },
    { c: 10, label: 'PRODUCTIVE',    formula: '=ROUND(PRODUCTIVE_H,1)',      sub: 'productive h / week', fmt: '0.0',  hero: false },
    { c: 12, label: 'SLEEP',         formula: '=ROUND(PLAN_SLEEP,1)',        sub: 'sleep h / week',      fmt: '0.0',  hero: false },
  ];
  const cr = 5; // card top row
  sh.setRowHeight(cr, 20); sh.setRowHeight(cr + 1, 40); sh.setRowHeight(cr + 2, 20);
  cards.forEach(card => {
    const block = sh.getRange(cr, card.c, 3, 2);
    block.setBackground(card.hero ? UI.navy : UI.card)
         .setBorder(true, true, true, true, false, false,
                    card.hero ? UI.navy : UI.line, SpreadsheetApp.BorderStyle.SOLID);
    sh.getRange(cr, card.c, 1, 2).merge().setValue(card.label)
      .setFontSize(8).setFontWeight('bold')
      .setFontColor(card.hero ? '#A5B4FC' : UI.faint).setHorizontalAlignment('center');
    sh.getRange(cr + 1, card.c, 1, 2).merge().setFormula(card.formula)
      .setFontSize(24).setFontWeight('bold').setNumberFormat(card.fmt)
      .setFontColor(card.hero ? '#FFFFFF' : UI.ink).setHorizontalAlignment('center');
    sh.getRange(cr + 2, card.c, 1, 2).merge().setValue(card.sub)
      .setFontSize(8).setFontColor(card.hero ? '#C7D2FE' : UI.faint)
      .setHorizontalAlignment('center');
  });
  const balanceCell = sh.getRange(cr + 1, 8);
  const freeCardCell = sh.getRange(cr + 1, 4);

  // -- Horizons table --------------------------------------------------------
  const hz = 10;
  band(sh, hz, 2, 6, '  🔭  HORIZONS');
  sh.getRange(hz + 1, 2, 1, 5).setValues([['', 'Daily', 'Weekly', 'Monthly', 'Yearly']])
    .setFontSize(9).setFontWeight('bold').setFontColor(UI.slate)
    .setBackground(UI.card).setHorizontalAlignment('center');
  const horizons = [
    ['Hours used',  'TOTAL_USED'],
    ['Free time',   'MAX(0,FREE_TIME)'],
    ['Productive',  'PRODUCTIVE_H'],
    ['Sleep',       'PLAN_SLEEP'],
  ];
  horizons.forEach((h, i) => {
    const r = hz + 2 + i;
    sh.getRange(r, 2).setValue(h[0]).setFontColor(UI.slate);
    sh.getRange(r, 3).setFormula('=ROUND(' + h[1] + '/7,1)');
    sh.getRange(r, 4).setFormula('=ROUND(' + h[1] + ',1)');
    sh.getRange(r, 5).setFormula('=ROUND(' + h[1] + '*WEEKS_MONTH,0)');
    sh.getRange(r, 6).setFormula('=ROUND(' + h[1] + '*WEEKS_YEAR,0)');
  });
  sh.getRange(hz + 2, 3, 4, 4).setNumberFormat('#,##0.0').setHorizontalAlignment('center');
  sh.getRange(hz + 1, 2, 5, 5)
    .setBorder(true, true, true, true, true, true, UI.line, SpreadsheetApp.BorderStyle.SOLID);

  // -- Signals ---------------------------------------------------------------
  const sg = hz + 8;
  band(sh, sg, 2, 6, '  🚦  SIGNALS');
  const signals = [
    '=IF(PLAN_WORK>60,"🔴  Work is over 60 h/week — burnout territory. Cut or delegate.",IF(PLAN_WORK>55,"🟡  Work is above 55 h/week — watch the load.","🟢  Work load is sustainable."))',
    '=IF(PLAN_SLEEP<49,"🔴  Sleep is under 7 h/night — recovery is your first lever.","🟢  Sleep is on target.")',
    '=IF(PLAN_FIT<3,"🟡  Fitness is under 3 h/week — schedule workouts first, not last.","🟢  Fitness habit is funded.")',
    '=IF(FREE_TIME<0,"🔴  You have allocated MORE than 168 hours — something must give.",IF(FREE_TIME<5,"🟡  Under 5 h of true free time — build in slack.","🟢  Healthy buffer of free time."))',
    '=IF(PLAN_REL<3,"🟡  Relationships get under 3 h/week — book the quality time.","🟢  Relationships are funded.")',
  ];
  signals.forEach((f, i) => {
    sh.getRange(sg + 1 + i, 2, 1, 5).merge().setFormula(f).setFontSize(10);
  });

  // -- Allocation table ------------------------------------------------------
  const al = sg + 8;
  band(sh, al, 2, 6, '  🗂️  WHERE THE HOURS GO');
  sh.getRange(al + 1, 2, 1, 5).setValues([['', 'Life area', 'Hours', '% of week', 'Status']])
    .setFontSize(9).setFontWeight('bold').setFontColor(UI.slate)
    .setBackground(UI.card).setHorizontalAlignment('center');
  const s = ctx.settings;
  const setRef = "'" + SHEETS.settings + "'";
  sh.getRange(al + 2, 2).setFormula(
    '=IFERROR(FILTER({' + setRef + '!$B$' + s.first + ':$B$' + s.last + ',' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + ',' +
    setRef + '!$D$' + s.first + ':$D$' + s.last + ',' +
    setRef + '!$E$' + s.first + ':$E$' + s.last + ',' +
    setRef + '!$J$' + s.first + ':$J$' + s.last + '},' +
    setRef + '!$C$' + s.first + ':$C$' + s.last + '<>""),"")');
  const alRows = TRACKER_ROWS + 2;
  sh.getRange(al + 2, 4, alRows, 1).setNumberFormat('0.0').setHorizontalAlignment('center');
  sh.getRange(al + 2, 5, alRows, 1).setNumberFormat('0.0%').setHorizontalAlignment('center');
  sh.getRange(al + 2, 6, alRows, 1).setHorizontalAlignment('center');
  const ft = al + 2 + TRACKER_ROWS + 1;
  sh.getRange(ft, 3).setValue('Free Time').setFontWeight('bold').setFontColor(UI.good);
  sh.getRange(ft, 4).setFormula('=ROUND(FREE_TIME,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setFontColor(UI.good).setHorizontalAlignment('center');
  sh.getRange(ft, 5).setFormula('=FREE_TIME/HOURS_WEEK').setNumberFormat('0.0%')
    .setFontColor(UI.good).setHorizontalAlignment('center');
  sh.getRange(ft + 1, 3).setValue('Total').setFontWeight('bold');
  sh.getRange(ft + 1, 4).setFormula('=ROUND(TOTAL_USED,1)').setNumberFormat('0.0')
    .setFontWeight('bold').setHorizontalAlignment('center');
  sh.getRange(ft + 1, 2, 1, 5)
    .setBorder(true, false, false, false, false, false, UI.navy, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  // -- Charts (fed from 📉 Charts data feeds) --------------------------------
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(ctx.chartFeeds.donut).setNumHeaders(1)
    .setPosition(hz, 8, 0, 0)
    .setOption('title', 'Time allocation by life area')
    .setOption('pieHole', 0.58)
    .setOption('colors', UI.chartColors)
    .setOption('width', 500).setOption('height', 320)
    .build());
  sh.insertChart(sh.newChart()
    .setChartType(Charts.ChartType.BAR)
    .addRange(ctx.chartFeeds.bar).setNumHeaders(1)
    .setPosition(hz + 17, 8, 0, 0)
    .setOption('title', 'Hours per week by life area')
    .setOption('colors', [UI.accent])
    .setOption('legend', { position: 'none' })
    .setOption('width', 500).setOption('height', 380)
    .build());

  // -- Conditional formatting ------------------------------------------------
  const rules = [];
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThanOrEqualTo(80).setFontColor(UI.good).setRanges([balanceCell]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberBetween(60, 79).setFontColor(UI.warn).setRanges([balanceCell]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(60).setFontColor(UI.bad).setRanges([balanceCell]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0).setFontColor('#FCA5A5').setRanges([freeCardCell]).build());
  const statusCol = sh.getRange(al + 2, 6, TRACKER_ROWS, 1);
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('OK').setFontColor(UI.good).setRanges([statusCol]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('Low').setFontColor(UI.warn).setRanges([statusCol]).build());
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('High').setFontColor(UI.bad).setRanges([statusCol]).build());
  sh.setConditionalFormatRules(rules);

  warnProtect(sh.getRange('A1:N60'), 'The dashboard is fully automatic — change ⚙️ Inputs instead.');
}

/* ----------------------------------------------------------------------------
 * 📖 GUIDE — in-sheet manual
 * ------------------------------------------------------------------------- */
function buildGuide(ctx) {
  const sh = freshSheet(ctx, SHEETS.guide);
  sh.setColumnWidth(1, 18);
  sh.setColumnWidth(2, 30);
  sh.setColumnWidth(3, 900);

  pageTitle(sh, 2, 2, 3, '📖 Guide — how to run your 168 hours', '');

  const sections = [
    ['🧭', 'THE IDEA', [
      'Everyone gets exactly 24 hours a day and 168 hours a week. This workbook treats those 168 hours like a budget: you allocate them on ⚙️ Inputs, track reality on 📅 Daily Tracker, and the system reconciles plan vs actual everywhere else — automatically.',
    ]],
    ['✏️', 'RULE #1 — ONLY EDIT BLUE CELLS', [
      'Every editable cell in this workbook has a light-blue background. Everything else is a formula. If a cell is not blue, you never need to touch it.',
    ]],
    ['🚀', 'GETTING STARTED (10 MINUTES)', [
      '1.  Go to ⚙️ Inputs and answer the guided sentences for each life area (blue cells).',
      '2.  Watch 📊 Dashboard — Hours Used, Free Time, Utilization and Balance Score update live.',
      '3.  If Free Time goes negative, the Signals panel will tell you. Trade hours until the week fits.',
      '4.  During the week, log real hours on 📅 Daily Tracker.',
      '5.  Review 📈 Weekly Tracker at week end: planned vs actual, and where the gap is.',
    ]],
    ['➕', 'ADDING A CUSTOM CATEGORY', [
      '1.  Open 🔧 Settings and find the blue rows at the bottom of the Master Category Table.',
      '2.  Type an emoji, a name (e.g. "Content Creation") and planned hours per week.',
      '3.  Optionally set healthy Min/Max thresholds and tick Productive.',
      '4.  Done. The category now appears in every tracker, the dashboard and all charts.',
    ]],
    ['🎯', 'BALANCE SCORE', [
      'A 0–100 gauge of how humane your plan is. It checks: sleep in the 49–63 h band, work ≤ 55 h, fitness ≥ 3 h, relationships ≥ 3 h, learning + personal development ≥ 2 h, and at least 5 h of true free time. 80+ is a sustainable executive week.',
    ]],
    ['🔧', 'TUNING THE SYSTEM', [
      'Healthy thresholds (Min/Max per category) are editable blue cells on 🔧 Settings — they drive Status flags and colour warnings.',
      'Constants (24 h/day, 168 h/week, weeks per month/year) live on 🔧 Settings as named ranges — every formula references them; nothing is hardcoded.',
      'A new week: clear the blue grid on 📅 Daily Tracker (select it and press Delete). Plans are untouched.',
    ]],
    ['🧱', 'ARCHITECTURE (FOR THE CURIOUS)', [
      'Input once → calculate everywhere. ⚙️ Inputs and 🔧 Settings are the only sources of truth. Named ranges (CAT_NAMES, CAT_HOURS, HOURS_WEEK, PLAN_*, FREE_TIME…) feed the trackers via FILTER and XLOOKUP, so adding categories never breaks a formula.',
      'To rebuild from factory defaults: ⚡ Executive OS menu → Build / Rebuild System. (Rebuilding resets your inputs — note them down first.)',
    ]],
  ];

  let row = 4;
  sections.forEach(sec => {
    band(sh, row, 2, 3, '  ' + sec[0] + '  ' + sec[1]);
    row++;
    sec[2].forEach(p => {
      sh.getRange(row, 3).setValue(p).setFontColor(UI.slate).setWrap(true);
      const lines = Math.ceil(p.length / 110);
      sh.setRowHeight(row, Math.max(24, lines * 16 + 8));
      row++;
    });
    row++;
  });
}
