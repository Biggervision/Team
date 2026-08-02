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
