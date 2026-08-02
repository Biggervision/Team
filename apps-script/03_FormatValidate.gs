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
