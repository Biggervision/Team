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
