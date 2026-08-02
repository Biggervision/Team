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
