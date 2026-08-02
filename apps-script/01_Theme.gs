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
