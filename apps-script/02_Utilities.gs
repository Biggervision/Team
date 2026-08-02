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
