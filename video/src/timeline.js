// Master timeline (seconds). Voiceover sits at 0.50 s; every cue below is
// the measured word time from the recording + 0.50 s.
const DURATION = 71.5;

const SCENES = [
  ['s1', 0.0, 9.3],
  ['s2', 9.3, 13.6],
  ['s3', 13.6, 19.4],
  ['s4', 19.4, 22.9],
  ['s5', 22.9, 31.0],
  ['s6', 31.0, 37.3],
  ['s7', 37.3, 39.6],
  ['s8', 39.6, 48.3],
  ['s9', 48.3, 58.7],
  ['s10', 58.7, 65.8],
  ['s11', 65.8, 71.5],
];

// Burned-in captions (vertical version). Script wording.
const CAPTIONS = [
  [0.5, 4.9, "If you run a personal injury law firm,\nHVAC, roofing, or plumbing business,"],
  [5.7, 9.16, "your phone calls can be worth\nthousands of dollars."],
  [9.36, 13.16, "But what if Google Ads\nisn't tracking all of them?"],
  [13.84, 18.76, "You might receive 30 serious calls,\nwhile Google only sees 10 conversions."],
  [19.62, 22.38, "Now Google thinks your campaign\nis underperforming."],
  [23.12, 26.0, "You cut the budget\nor pause the campaign,"],
  [26.0, 30.62, "when the campaign may actually be\nbringing your best customers."],
  [31.36, 33.2, "The problem may not be your ads."],
  [33.86, 36.64, "Your tracking may be hiding\nthe real performance."],
  [37.96, 38.78, "Here's the fix:"],
  [39.76, 41.3, "Track your calls properly."],
  [41.5, 44.5, "Identify which calls\nbecome qualified leads."],
  [44.78, 47.98, "Then send those conversion signals\nback to Google Ads."],
  [48.56, 52.3, "When Google sees the leads\nthat actually matter,"],
  [52.86, 58.44, "it can optimize toward more qualified\ncustomers and more revenue."],
  [58.98, 62.9, "Otherwise, you may keep pausing\ncampaigns that are working"],
  [62.9, 65.76, "while your competitors\ncapture those customers."],
];
