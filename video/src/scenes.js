// One draw function per storyboard scene. t is master time in seconds.
// Each layout branches on V (vertical 9:16) vs landscape 16:9.

const INDUSTRIES = [
  ['scale', 'Personal Injury Law', 1.88],
  ['snow', 'HVAC', 3.12],
  ['house', 'Roofing', 3.86],
  ['drop', 'Plumbing', 4.32],
];
// ---------------- Scene 2: the black hole ----------------
function s2(c, t) {
  const vx = V ? 540 : 880, vy = V ? 760 : 640, R = V ? 330 : 360;
  const nodes = V
    ? [[240, 1180], [540, 1180], [840, 1180]]
    : [[1660, 330], [1660, 540], [1660, 750]];
  const nodeIcons = [['mega', 'Google Ads'], ['chart', 'Analytics'], ['user', 'CRM']];
  const open = pr(t, 11.2, 1.1);

  c.save();
  if (V) c.translate(0, lerp(-20, 20, pr(t, 9.3, 4.3)));
  else c.translate(lerp(30, -30, pr(t, 9.3, 4.3)), 0);
  zoomAt(c, vx, vy, lerp(1, 1.04, pr(t, 11, 2.5)));

  const calls = [];
  let heat = 0;
  const arrivals = [0, 0, 0], lastArrive = [-9, -9, -9];
  for (let i = 0; i < 34; i++) {
    const ts = 8.3 + i * 0.16;
    const dur = 1.75;
    const p = (t - ts) / dur;
    const lost = ts > 10.6 && i % 3 !== 0;
    const j = i % 3;
    const start = V ? [150 + hash(i) * 780, 380] : [-80, 420 + hash(i) * 260];
    if (p >= 1 && !lost) { arrivals[j]++; lastArrive[j] = Math.max(lastArrive[j], ts + dur); continue; }
    if (p < 0 || p >= 1) continue;
    if (!lost) {
      const ctrl = V ? [lerp(start[0], nodes[j][0], 0.5), vy - 30] : [vx, vy - 260 + j * 60];
      const [x, y] = quad(start, ctrl, nodes[j], eio(p));
      calls.push({ x, y, s: 1, a: clamp(p * 6) * clamp((1 - p) * 8), tone: 'brand' });
    } else {
      const side = hash(i + 7) > 0.5 ? 1 : -1;
      const rim = [vx + side * R * 0.75, vy - R * 0.1];
      if (p < 0.5) {
        const [x, y] = quad(start, [lerp(start[0], rim[0], 0.6), V ? rim[1] - 120 : start[1]], rim, eio(p / 0.5));
        calls.push({ x, y, s: 1, a: clamp(p * 6), tone: 'brand' });
      } else {
        const q = (p - 0.5) / 0.5;
        const ang = (side > 0 ? 0 : Math.PI) + q * 4.2;
        const r = R * 0.75 * (1 - eo(q));
        heat = Math.max(heat, Math.sin(q * Math.PI));
        calls.push({ x: vx + r * Math.cos(ang), y: vy + r * Math.sin(ang) * 0.38 - (1 - q) * 20, s: 1 - q * 0.75, a: 1 - q * q, tone: 'warn', trail: q });
      }
    }
  }

  // the AC replacement lead from the opening — the one that gets lost
  let hero = null;
  const hp = (t - 10.2) / 2.8;
  if (hp > 0 && hp < 1) {
    const start = V ? [540, 380] : [-220, 560];
    const rim = V ? [vx + R * 0.55, vy - R * 0.12] : [vx - R * 0.72, vy - R * 0.08];
    if (hp < 0.55) {
      const [x, y] = quad(start, V ? [vx + R * 0.7, vy - 260] : [vx - R * 1.2, vy - 120], rim, eio(hp / 0.55));
      hero = { x, y, s: 1, a: clamp(hp * 8), tone: 'brand' };
    } else {
      const q = (hp - 0.55) / 0.45;
      const ang = (V ? 0 : Math.PI) + q * 4.4;
      const r = R * 0.72 * (1 - eo(q));
      heat = Math.max(heat, Math.sin(q * Math.PI));
      hero = { x: vx + r * Math.cos(ang), y: vy + r * Math.sin(ang) * 0.38 - (1 - q) * 30, s: 1 - q * 0.8, a: 1 - q * q, tone: 'warn' };
    }
  }

  vortex(c, vx, vy, R, t, open, heat * open);

  nodes.forEach(([x, y], j) => {
    const k = pr(t, 9.0 + j * 0.1, 0.5, eo);
    const glow = clamp(1 - (t - lastArrive[j]) / 0.5);
    node(c, x, y, V ? 120 : 130, nodeIcons[j][0], nodeIcons[j][1], k, { glow, labelSize: V ? 24 : 22 });
    if (j === 0) {
      const count = 6 + arrivals[0];
      const bx = V ? x : x - 108, by = V ? y - 102 : y;
      pill(c, bx, by, `${count} conv.`, P.deep, k, { size: 18, align: V ? 'center' : 'right' });
    }
  });

  for (const cl of calls) miniCall(c, cl.x, cl.y, (V ? 1.3 : 1.25) * cl.s, cl.a, cl.tone);
  if (hero) callCard(c, hero.x, hero.y, (V ? 1.15 : 1.1) * hero.s, 'AC replacement', '$8,500', hero.a, hero.tone);
  c.restore();

  headline(c, V ? 'Your best leads may be\ndisappearing.' : 'Your best leads may be disappearing.', V ? 540 : 960, V ? 270 : 135, V ? 50 : 54, t, 12.0);
}

// ---------------- Scene 3: 30 calls vs 10 conversions ----------------
function s3(c, t) {
  const pnl = V ? { x: 70, y: 270, w: 940, h: 1060 } : { x: 330, y: 160, w: 1260, h: 760 };
  c.save();
  zoomAt(c, W / 2, pnl.y + pnl.h / 2, lerp(1, 1.05, pr(t, 13.6, 5.8)));
  const k = pr(t, 13.4, 0.7, eo);
  glass(c, pnl.x, pnl.y + (1 - k) * 30, pnl.w, pnl.h, 28, k);
  txt(c, 'CALL PERFORMANCE · LAST 30 DAYS', pnl.x + 50, pnl.y + 56, 18, 600, P.ink2, 'left', k, 2);

  const A = V ? [540, pnl.y + 230] : [pnl.x + 340, pnl.y + 270];
  const B = V ? [540, pnl.y + 520] : [pnl.x + 920, pnl.y + 270];
  const ka = pr(t, 13.8, 0.5, eo), kb = pr(t, 16.9, 0.5, eo);
  const va = Math.round(30 * pr(t, 14.85, 0.6, eo));
  const vb = Math.round(10 * pr(t, 17.35, 0.67, eo));
  const ns = V ? 170 : 180;
  txt(c, 'Actual calls', A[0], A[1] - ns * 0.68, 28, 500, P.ink2, 'center', ka);
  txt(c, String(va), A[0], A[1] + 10, ns, 700, P.ink, 'center', ka, -4);
  txt(c, 'Tracked conversions', B[0], B[1] - ns * 0.68, 28, 500, P.ink2, 'center', kb);
  txt(c, String(vb), B[0], B[1] + 10, ns, 700, P.ink, 'center', kb, -4);
  const km = pr(t, 18.4, 0.5, eo);
  if (V) pill(c, 540, B[1] + 125, '20 calls missing', P.warn, km, { size: 26, align: 'center' });
  else pill(c, B[0], B[1] + 130, '20 calls missing', P.warn, km, { size: 24, align: 'center' });

  // 30 call slots
  const slot = (i) => {
    if (V) { const col = i % 6, row = Math.floor(i / 6); return [540 - 300 + col * 120, pnl.y + 760 + row * 64, 92, 50]; }
    return [960 - 566 + i * 38 + 15, pnl.y + 560, 30, 52];
  };
  for (let i = 0; i < 30; i++) {
    const [x, y, w, h] = slot(i);
    const fill = pr(t, 14.85 + i * 0.022, 0.25);
    const drain = i >= 10 ? pr(t, 18.0 + (i - 10) * 0.018, 0.3) : 0;
    c.save(); c.globalAlpha *= ka;
    rr(c, x - w / 2, y - h / 2, w, h, 10);
    c.fillStyle = '#EDF1F5'; c.fill();
    if (fill > 0) {
      c.globalAlpha *= fill * (1 - drain);
      rr(c, x - w / 2, y - h / 2, w, h, 10); c.fillStyle = P.brand; c.fill();
    }
    c.restore();
    if (drain > 0) {
      c.save(); c.globalAlpha *= drain * ka;
      c.setLineDash([5, 5]); rr(c, x - w / 2, y - h / 2, w, h, 10); c.strokeStyle = rgba(P.warn, 0.8); c.lineWidth = 2; c.stroke();
      c.restore();
    }
    icon(c, 'phone', x, y, V ? 22 : 16, drain > 0.5 ? rgba(P.warn, 0.7) : '#fff', 2.4, ka * Math.max(fill, drain));
  }
  if (!V) {
    const [x1] = slot(10), [x2] = slot(29);
    const kb2 = pr(t, 18.4, 0.5, eo);
    c.save(); c.globalAlpha *= kb2;
    c.strokeStyle = rgba(P.warn, 0.7); c.lineWidth = 2;
    const by = pnl.y + 610;
    c.beginPath(); c.moveTo(x1 - 15, by); c.lineTo(x1 - 15, by + 14); c.lineTo(x2 + 15, by + 14); c.lineTo(x2 + 15, by); c.stroke();
    c.restore();
    txt(c, 'Never reported to Google', (x1 + x2) / 2, pnl.y + 660, 22, 600, P.warn, 'center', kb2);
    const [y1] = [pnl.y + 610];
    c.save(); c.globalAlpha *= kb2; c.strokeStyle = rgba(P.brand, 0.7); c.lineWidth = 2;
    const [a1] = slot(0), [a2] = slot(9);
    c.beginPath(); c.moveTo(a1 - 15, y1); c.lineTo(a1 - 15, y1 + 14); c.lineTo(a2 + 15, y1 + 14); c.lineTo(a2 + 15, y1); c.stroke();
    c.restore();
    txt(c, 'Reported', (a1 + a2) / 2, pnl.y + 660, 22, 600, P.deep, 'center', kb2);
  }
  c.restore();
}

// ---------------- Scene 4: Underperforming ----------------
const GOOD = [0.25, 0.3, 0.28, 0.38, 0.42, 0.4, 0.5, 0.55, 0.52, 0.6, 0.64, 0.7];
const FLAT = [0.25, 0.3, 0.28, 0.33, 0.31, 0.27, 0.3, 0.26, 0.24, 0.27, 0.23, 0.22];
const mix = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));

function statusPill(c, x, y, t, at, from, to, fromColor, toColor, a, o = {}) {
  const f = clamp((t - at + 0.16) / 0.32);
  const flip = f <= 0 ? 1 : f >= 1 ? 1 : Math.cos(f * Math.PI);
  const after = f >= 0.5;
  return pill(c, x, y, after ? to : from, after ? toColor : fromColor, a, { ...o, flip });
}

function s4(c, t) {
  const cd = V ? { x: 70, y: 300, w: 940, h: 960 } : { x: 400, y: 220, w: 1120, h: 640 };
  c.save();
  zoomAt(c, W / 2, cd.y + cd.h / 2, lerp(1, 1.04, pr(t, 19.4, 3.5)));
  const k = pr(t, 19.2, 0.6, eo);
  glass(c, cd.x, cd.y, cd.w, cd.h, 28, k);
  campaignHeader(c, cd.x + 10, cd.y + 10, cd.w, k);
  const cost = lerp(84, 252, pr(t, 20.2, 0.9));
  if (V) {
    statusPill(c, cd.x + 60, cd.y + 170, t, 21.46, 'Learning', 'Underperforming', '#8A97A6', P.warn, k, { size: 30 });
    metric(c, cd.x + 60, cd.y + 280, 'Conversions', '10', k, { vs: 64, ls: 24 });
    metric(c, cd.x + 500, cd.y + 280, 'Cost / conversion', money(cost), k, { vs: 64, ls: 24 });
    lineChart(c, cd.x + 60, cd.y + 480, cd.w - 120, 380, mix(GOOD, FLAT, pr(t, 20.5, 1.0)), P.brand, k);
  } else {
    statusPill(c, cd.x + cd.w - 50, cd.y + 70, t, 21.46, 'Learning', 'Underperforming', '#8A97A6', P.warn, k, { size: 24, align: 'right' });
    metric(c, cd.x + 60, cd.y + 180, 'Conversions', '10', k);
    metric(c, cd.x + 380, cd.y + 180, 'Cost / conversion', money(cost), k);
    metric(c, cd.x + 720, cd.y + 180, 'Daily budget', '$150', k);
    lineChart(c, cd.x + 60, cd.y + 330, cd.w - 120, 250, mix(GOOD, FLAT, pr(t, 20.5, 1.0)), P.brand, k);
  }
  c.restore();
}

// ---------------- Scene 5: cut, pause, lose ----------------
const LEADS = [['Injury case', '$15,000+'], ['Roof replacement', '$14,800'], ['AC install', '$7,200'], ['Water heater', '$1,900'], ['Furnace repair', '$4,600']];

function s5(c, t) {
  const cd = V ? { x: 70, y: 270, w: 940, h: 560 } : { x: 200, y: 170, w: 960, h: 600 };
  const sl = V ? { x: cd.x + 60, y: cd.y + 330, w: 560 } : { x: cd.x + 60, y: cd.y + 330, w: 600 };
  const tg = V ? { x: cd.x + 60, y: cd.y + 470 } : { x: cd.x + 60, y: cd.y + 490 };
  const budgetK = 1 - 0.73 * pr(t, 23.94, 0.5);
  const paused = pr(t, 24.54, 0.25);

  c.save();
  const push = pr(t, 22.9, 1.6) * (1 - pr(t, 26.0, 1.2));
  zoomAt(c, sl.x + sl.w / 2, sl.y, 1 + 0.08 * push);

  glass(c, cd.x, cd.y, cd.w, cd.h, 28, 1);
  campaignHeader(c, cd.x + 10, cd.y + 10, cd.w, 1);
  const pillX = V ? cd.x + 60 : cd.x + cd.w - 50, pillY = V ? cd.y + 165 : cd.y + 70;
  if (paused < 0.5) pill(c, pillX, pillY, 'Underperforming', P.warn, 1, { size: V ? 28 : 24, align: V ? 'left' : 'right', flip: paused > 0 ? Math.cos(paused * Math.PI) : null });
  else pill(c, pillX, pillY, 'Campaign Paused', P.loss, 1, { size: V ? 28 : 24, align: V ? 'left' : 'right', flip: Math.cos(paused * Math.PI), solid: true });
  if (!V) { metric(c, cd.x + 60, cd.y + 170, 'Conversions', '10'); metric(c, cd.x + 380, cd.y + 170, 'Cost / conversion', '$252'); }

  txt(c, 'Daily budget', sl.x, sl.y - 50, 22, 500, P.ink2);
  txt(c, money(lerp(40, 150, (budgetK - 0.27) / 0.73)) + ' / day', sl.x + sl.w + 40, sl.y, 32, 700, P.ink);
  slider(c, sl.x, sl.y, sl.w, budgetK, 1, paused > 0.5 ? P.mute : P.brand);
  txt(c, 'Campaign status', tg.x, tg.y, 24, 500, P.ink2);
  toggle(c, tg.x + 230, tg.y, 1 - paused, 1, 1.1);
  txt(c, paused > 0.5 ? 'Off' : 'On', tg.x + 345, tg.y, 24, 600, paused > 0.5 ? P.loss : P.deep);

  // desaturate card once paused
  if (paused > 0) { c.save(); c.globalAlpha = 0.28 * paused; rr(c, cd.x, cd.y, cd.w, cd.h, 28); c.fillStyle = '#F2F4F7'; c.fill(); c.restore(); }

  // cursor: to knob, drag, to toggle, click, exit
  const knob0 = [sl.x + sl.w, sl.y], knob1 = [sl.x + sl.w * 0.27, sl.y];
  const tog = [tg.x + 230 + 70, tg.y];
  let cx, cy, press = 0, ca = pr(t, 23.3, 0.3) * (1 - pr(t, 25.0, 0.4));
  if (t < 23.94) { const k = pr(t, 23.3, 0.64); cx = lerp(knob0[0] + 260, knob0[0], k); cy = lerp(knob0[1] + 200, knob0[1], k); }
  else if (t < 24.4) { const k = pr(t, 23.94, 0.46); cx = lerp(knob0[0], knob1[0], eio(k)); cy = knob0[1]; }
  else { const k = pr(t, 24.4, 0.14); cx = lerp(knob1[0], tog[0], k); cy = lerp(knob1[1], tog[1], k); press = t > 24.54 ? clamp((t - 24.54) / 0.4) : 0; }
  cursor(c, cx + 8, cy + 8, press, ca);
  c.restore();

  // lead cards still arriving behind the paused campaign
  const lp = (i) => V ? [540, 950 + i * 95] : [1560, 250 + i * 118];
  const n = V ? 4 : 5;
  const ka = pr(t, 26.0, 0.5, eo);
  txt(c, 'Calls still coming in', V ? 540 : 1560, V ? 860 : 168, 22, 600, P.ink2, 'center', ka * (1 - pr(t, 29.8, 0.5)), 1);
  const fadeAt = [29.58, 27.0, 27.6, 28.2, 28.8];
  for (let i = 0; i < n; i++) {
    const k = pr(t, 26.14 + i * 0.12, 0.6, eo);
    if (k <= 0) continue;
    const [x, y] = lp(i);
    const g = pr(t, fadeAt[i], 0.5);
    const gone = i === 0 ? pr(t, 29.58, 0.6) : pr(t, fadeAt[i] + 0.6, 1.2) * 0.7;
    const sx = x + (1 - k) * 120;
    if (i === 0 && g < 0.2) {
      c.save(); c.globalAlpha *= k * 0.5; c.shadowColor = rgba(P.brand, 0.8); c.shadowBlur = 30;
      rr(c, sx - 160 * (V ? 1.3 : 1.15), y - 38, 320 * (V ? 1.3 : 1.15), 76, 38); c.fillStyle = rgba(P.brand, 0.2); c.fill(); c.restore();
    }
    callCard(c, sx, y - gone * 30, V ? 1.3 : 1.15, LEADS[i][0], LEADS[i][1], k * (1 - gone), g > 0.5 ? 'grey' : 'brand');
  }

  // loss tiles
  const tiles = [['users', 'Lost leads'], ['user', 'Lost customers'], ['dollar', 'Lost revenue']];
  tiles.forEach(([ic, label], i) => {
    const k = pr(t, 30.0 + i * 0.12, 0.5, eo);
    if (k <= 0) return;
    const w = V ? 290 : 330, h = 76;
    const x = V ? 540 + (i - 1) * 305 : 960 + (i - 1) * 360, y = (V ? 1325 : 900) + (1 - k) * 20;
    glass(c, x - w / 2, y - h / 2, w, h, 20, k, { fill: 'rgba(255,255,255,0.92)', stroke: rgba(P.loss, 0.25) });
    icon(c, ic, x - w / 2 + 40, y, 24, P.loss, 2, k);
    txt(c, label, x - w / 2 + 68, y, V ? 24 : 24, 600, P.loss, 'left', k);
  });
}

// ---------------- Scene 6: the reveal ----------------
function pipelinePos(i) {
  return V ? [330, 480 + i * 170] : [240 + i * 360, 520];
}
const PIPE = [['mega', 'Ads'], ['phone', 'Website / Phone'], ['target', 'Tracking'], ['chart', 'Google Ads'], ['user', 'CRM']];

function s6(c, t) {
  c.save();
  const pull = pr(t, 30.8, 1.7);
  const [ax, ay] = pipelinePos(0);
  const [tx, ty] = pipelinePos(2);
  const push = pr(t, 34.0, 2.6);
  const sc = lerp(1.9, 1, pull) * lerp(1, V ? 1.04 : 1.2, push);
  const fx = lerp(lerp(ax, W / 2, pull), tx, push), fy = lerp(lerp(ay, ty, pull), ty, push);
  c.translate(W / 2, ty); c.scale(sc, sc); c.translate(-fx, -fy);

  const broken = pr(t, 33.98, 0.4);
  for (let i = 0; i < 4; i++) {
    const [x1, y1] = pipelinePos(i), [x2, y2] = pipelinePos(i + 1);
    const off = V ? [0, 75] : [75, 0];
    const st = i >= 2 && broken > 0.5 ? 'broken' : i === 0 && t > 32.3 ? 'ok' : 'idle';
    connector(c, x1 + off[0], y1 + off[1], x2 - off[0], y2 - off[1], t, st, pr(t, 31.0 + i * 0.15, 0.5));
  }
  PIPE.forEach(([ic, label], i) => {
    const [x, y] = pipelinePos(i);
    const k = pr(t, 30.9 + i * 0.15, 0.5, eo);
    const isT = i === 2;
    const size = isT ? (V ? 150 : 170) : (V ? 120 : 130);
    const o = { labelSide: V, labelSize: V ? 30 : 24 };
    if (i === 0) { o.check = pr(t, 32.26, 0.5); o.glow = pr(t, 32.26, 0.4) * (1 - pr(t, 33.5, 0.6)) * 0.7; }
    if (isT) { o.border = broken > 0 ? rgba(P.warn, 0.7 * broken) : undefined; o.iconColor = broken > 0.5 ? P.warn : P.deep; }
    node(c, x, y, size, ic, label, k, o);
    if (isT) {
      const vo = pr(t, 34.9, 0.8);
      if (vo > 0) {
        c.save(); rr(c, x - size / 2 + 6, y - size / 2 + 6, size - 12, size - 12, size * 0.22); c.clip();
        c.globalAlpha *= 0.9;
        vortex(c, x, y + size * 0.18, size * 0.5, t, vo, 0.6);
        c.restore();
        icon(c, 'target', x, y - size * 0.1, size * 0.34, P.warn, 2, 1 - vo * 0.5);
      }
    }
  });
  // hidden real number behind the reported one
  const [gx, gy] = pipelinePos(3);
  const kg = pr(t, 35.92, 0.6, eo);
  if (kg > 0) {
    const bx = V ? gx + 520 : gx, by = V ? gy - 30 : gy - 150;
    txt(c, '30 real', bx, by - 40, 30, 700, rgba(P.ink, 0.3), 'center', kg);
    txt(c, '10 reported', bx, by + 6, 34, 700, P.ink, 'center', kg);
  }
  c.restore();

  const hy = V ? 285 : 150;
  headline(c, 'Not your ads.', W / 2, hy, V ? 60 : 60, t, 32.2, { out: 33.7, color: P.deep });
  headline(c, 'Your tracking.', W / 2, hy, V ? 60 : 60, t, 33.95, { color: P.ink });
}

// ---------------- Scene 7: here's the fix ----------------
function s7(c, t) {
  const tn = V ? [540, 1080, 190] : [600, 540, 230];
  const fixing = pr(t, 38.4, 0.8);
  const k0 = pr(t, 37.0, 0.5);
  const border = fixing > 0.5 ? rgba(P.brand, 0.8) : rgba(P.warn, 0.7);
  node(c, tn[0], tn[1], tn[2], 'target', 'Tracking', k0, { border, iconColor: fixing > 0.5 ? P.deep : P.warn, labelSize: 26 });
  const vo = 1 - pr(t, 38.5, 1.0);
  if (vo > 0.02) {
    c.save(); rr(c, tn[0] - tn[2] / 2 + 6, tn[1] - tn[2] / 2 + 6, tn[2] - 12, tn[2] - 12, tn[2] * 0.22); c.clip();
    vortex(c, tn[0], tn[1] + tn[2] * 0.18, tn[2] * 0.5, t, vo * k0, 0.4 * vo);
    c.restore();
  }

  const k = pr(t, 37.9, 0.7, x => x);
  const ks = spring(k);
  if (k <= 0) return;
  const cd = V ? { x: 150, y: 300, w: 780, h: 560 } : { x: 900, y: 360, w: 640, h: 330 };
  c.save();
  c.translate((1 - ks) * (V ? 0 : 260), (1 - ks) * (V ? -60 : 0));
  glass(c, cd.x, cd.y, cd.w, cd.h, 28, clamp(k * 2));
  const a = clamp(k * 2);
  if (V) {
    portrait(c, 540 - 150, cd.y + 40, 300, 300, 24, a);
    txt(c, "Here's the fix.", 540, cd.y + 410, 48, 650, P.ink, 'center', a);
    const dc = fixing > 0.5 ? P.brand : P.warn;
    c.save(); c.globalAlpha *= a; c.beginPath(); c.arc(540 - 130, cd.y + 490, 9, 0, Math.PI * 2); c.fillStyle = dc; c.fill(); c.restore();
    txt(c, fixing > 0.5 ? 'Tracking check: on' : 'Tracking check', 540 - 110, cd.y + 490, 24, 500, P.ink2, 'left', a);
  } else {
    portrait(c, cd.x + 30, cd.y + 30, 270, 270, 22, a);
    txt(c, "Here's the fix.", cd.x + 330, cd.y + 130, 44, 650, P.ink, 'left', a);
    const dc = fixing > 0.5 ? P.brand : P.warn;
    c.save(); c.globalAlpha *= a; c.beginPath(); c.arc(cd.x + 342, cd.y + 205, 9, 0, Math.PI * 2); c.fillStyle = dc; c.fill(); c.restore();
    txt(c, fixing > 0.5 ? 'Tracking check: on' : 'Tracking check', cd.x + 362, cd.y + 205, 22, 500, P.ink2, 'left', a);
  }
  c.restore();
}

// ---------------- Scene 8: the plan ----------------
const REJECT = ['Spam', 'Wrong number', 'Job seeker'];

function s8(c, t) {
  const L = V
    ? { b: [[540, 290], [540, 385], [540, 480]], n1: [540, 660], gate: [540, 910], crm: [300, 1190], ads: [780, 1190], start: [-60, 660], drop: [930, 1000] }
    : { b: [[380, 170], [960, 170], [1540, 170]], n1: [380, 560], gate: [960, 560], crm: [1540, 760], ads: [1540, 400], start: [-80, 560], drop: [960, 880] };
  const steps = [['Track calls', 39.76], ['Identify qualified leads', 41.5], ['Send signals to Google Ads', 44.78]];

  // step badges
  steps.forEach(([label, at], i) => {
    const k = pr(t, at - 0.2, 0.5, eo);
    if (k <= 0) return;
    const [x, y] = L.b[i];
    const w = V ? 800 : 480, h = V ? 78 : 84;
    glass(c, x - w / 2, y - h / 2 + (1 - k) * 20, w, h, 22, k);
    const done = t > at ? 1 : 0;
    dotIcon(c, x - w / 2 + 44, y + (1 - k) * 20, 22, done ? P.brand : P.mute, null, null, k);
    txt(c, String(i + 1), x - w / 2 + 44, y + (1 - k) * 20 + 1, 22, 700, '#fff', 'center', k);
    txt(c, label, x - w / 2 + 84, y + (1 - k) * 20, V ? 29 : 26, 650, P.ink, 'left', k);
  });

  // presenter badge
  const pb = V ? 0 : pr(t, 39.6, 0.5, eo) * (1 - pr(t, 47.0, 0.6));
  portraitCircle(c, V ? 150 : 96, V ? 320 : 100, V ? 52 : 46, pb);

  // structure
  const k1 = pr(t, 39.6, 0.5, eo), k2 = pr(t, 41.4, 0.5, eo), k3 = pr(t, 44.7, 0.5, eo);
  const kCrm = pr(t, 42.6, 0.5, eo);
  connector(c, L.start[0] + 60, L.start[1], L.n1[0] - 80, L.n1[1], t, 'ok', k1, pr(t, 39.76, 0.5));
  connector(c, L.n1[0] + (V ? 0 : 80), L.n1[1] + (V ? 80 : 0), L.gate[0] - (V ? 0 : 40), L.gate[1] - (V ? 30 : 0), t, 'ok', k1, pr(t, 39.9, 0.6));
  connector(c, L.gate[0] + (V ? -40 : 40), L.gate[1] + (V ? 30 : 0), L.crm[0] + (V ? 40 : -80), L.crm[1] - (V ? 70 : 0), t, 'ok', kCrm, pr(t, 42.6, 0.6));
  node(c, L.n1[0], L.n1[1], V ? 130 : 150, 'target', V ? null : 'Tracking', k1, { border: rgba(P.brand, 0.8), labelSize: 22 });
  // filter gate
  if (k2 > 0) {
    c.save(); c.globalAlpha *= k2;
    const gw = V ? 300 : 26, gh = V ? 26 : 300;
    glass(c, L.gate[0] - gw / 2, L.gate[1] - gh / 2, gw, gh, 13, 1, { fill: rgba(P.tint, 0.9), stroke: rgba(P.brand, 0.5) });
    const sp = (t * 0.8) % 1;
    c.fillStyle = rgba(P.brand, 0.8);
    if (V) c.fillRect(L.gate[0] - gw / 2 + sp * gw, L.gate[1] - gh / 2, 3, gh); else c.fillRect(L.gate[0] - gw / 2, L.gate[1] - gh / 2 + sp * gh, gw, 3);
    c.restore();
    icon(c, 'filter', V ? L.gate[0] - 190 : L.gate[0], V ? L.gate[1] : L.gate[1] - 190, 34, P.deep, 2, k2);
  }
  node(c, L.crm[0], L.crm[1], V ? 110 : 140, 'user', 'CRM', kCrm, { labelSize: 22 });
  const adsGlow = pr(t, 47.4, 0.3) * (1 - pr(t, 47.9, 0.8));
  node(c, L.ads[0], L.ads[1], V ? 110 : 140, 'chart', 'Google Ads', k3, { glow: adsGlow, labelSize: 22, border: rgba(P.brand, 0.6) });

  // return signal stream CRM -> Google Ads
  const sig = pr(t, 45.04, 1.4);
  if (sig > 0) {
    const a0 = V ? [L.crm[0] + 70, L.crm[1]] : [L.crm[0], L.crm[1] - 85];
    const a1 = V ? [L.ads[0] - 70, L.ads[1]] : [L.ads[0], L.ads[1] + 85];
    c.save();
    c.shadowColor = rgba(P.brand, 0.9); c.shadowBlur = 18;
    c.strokeStyle = P.brand; c.lineWidth = 6; c.lineCap = 'round';
    c.beginPath(); c.moveTo(a0[0], a0[1]); c.lineTo(lerp(a0[0], a1[0], sig), lerp(a0[1], a1[1], sig)); c.stroke();
    c.restore();
    for (let i = 0; i < 5; i++) {
      const f = ((t * 1.2 + i / 5) % 1);
      if (f > sig) continue;
      c.beginPath(); c.arc(lerp(a0[0], a1[0], f), lerp(a0[1], a1[1], f), 7, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill();
    }
    const lab = V ? [(a0[0] + a1[0]) / 2, a0[1] - 34] : [a0[0] + 110, (a0[1] + a1[1]) / 2];
    txt(c, 'Qualified conversions', lab[0], lab[1], 20, 600, P.deep, V ? 'center' : 'left', pr(t, 45.6, 0.5));
    icon(c, 'send', V ? lab[0] : lab[0] - 30, V ? lab[1] - 34 : lab[1], 22, P.deep, 2, pr(t, 45.6, 0.5));
  }
  if (k3 > 0) {
    const cnt = Math.round(lerp(10, 30, pr(t, 46.4, 1.6)));
    pill(c, L.ads[0] + (V ? 0 : 0), L.ads[1] - (V ? 100 : 118), `${cnt} conversions`, P.deep, k3, { size: 18, align: 'center' });
  }

  // calls flowing through the system
  for (let i = 0; i < 28; i++) {
    const ts = 39.3 + i * 0.3, dur = 2.7;
    const p = (t - ts) / dur;
    if (p < 0 || p > 1) continue;
    const gateT = ts + dur * 0.55;
    const reject = i % 3 === 2 && gateT > 43.2;
    const toCrm = gateT > 42.7;
    let x, y, tone = 'brand', a = 1, label = '';
    if (p < 0.28) { const q = eio(p / 0.28); x = lerp(L.start[0], L.n1[0], q); y = lerp(L.start[1], L.n1[1], q); a = clamp(p * 10); }
    else if (p < 0.55) { const q = eio((p - 0.28) / 0.27); x = lerp(L.n1[0], L.gate[0], q); y = lerp(L.n1[1], L.gate[1], q); }
    else if (!toCrm) { const q = (p - 0.55) / 0.45; x = lerp(L.gate[0], L.gate[0] + (V ? 0 : 200), q); y = lerp(L.gate[1], L.gate[1] + (V ? 200 : 0), q); a = 1 - q; }
    else if (reject) { const q = (p - 0.55) / 0.45; x = lerp(L.gate[0], L.drop[0], eo(q)); y = lerp(L.gate[1], L.drop[1], eo(q)); tone = 'grey'; a = 1 - q * q; label = REJECT[i % 3 === 2 ? Math.floor(i / 3) % 3 : 0]; }
    else { const q = eio((p - 0.55) / 0.45); x = lerp(L.gate[0], L.crm[0], q); y = lerp(L.gate[1], L.crm[1], q); a = 1 - clamp((q - 0.85) / 0.15); label = q > 0.05 ? 'Qualified' : ''; }
    if (p > 0.27 && p < 0.33) { const q = (p - 0.27) / 0.06; dotIcon(c, L.n1[0] + 52, L.n1[1] - 52, 14 * Math.sin(q * Math.PI), P.brand, 'check'); }
    miniCall(c, x, y, V ? 1.05 : 1.05, a, tone, label);
  }
}

// ---------------- Scene 9: success ----------------
const RISE = [0.22, 0.26, 0.25, 0.33, 0.38, 0.44, 0.5, 0.57, 0.63, 0.7, 0.78, 0.86];
const FLAT2 = [0.24, 0.26, 0.24, 0.27, 0.26, 0.25, 0.27, 0.26, 0.25, 0.27, 0.26, 0.26];

function s9(c, t) {
  const k = pr(t, 48.2, 0.6, eo);
  const match = pr(t, 49.08, 0.8, eo);
  const vb = Math.round(lerp(10, 30, match));
  const curve = mix(FLAT2, RISE, pr(t, 53.4, 2.0));
  const cost = lerp(252, 84, pr(t, 53.5, 1.6));
  c.save();
  c.translate(0, lerp(10, -10, pr(t, 48.3, 10.4)));

  if (V) {
    // matched counters
    txt(c, 'Actual calls', 300, 410, 26, 500, P.ink2, 'center', k);
    txt(c, '30', 300, 500, 150, 700, P.ink, 'center', k, -3);
    txt(c, 'Tracked', 780, 410, 26, 500, P.ink2, 'center', k);
    txt(c, String(vb), 780, 500, 150, 700, match > 0.99 ? P.deep : P.ink, 'center', k, -3);
    txt(c, '=', 540, 500, 90, 500, P.brand, 'center', match);
    pill(c, 540, 600, 'Matched', P.brand, pr(t, 49.9, 0.5), { size: 22, align: 'center' });
    const cd = { x: 70, y: 660, w: 940, h: 330 };
    glass(c, cd.x, cd.y, cd.w, cd.h, 28, k);
    pill(c, cd.x + 40, cd.y + 50, 'Active', P.brand, k, { size: 20 });
    txt(c, 'Cost / conversion  ' + money(cost), cd.x + cd.w - 40, cd.y + 50, 22, 600, P.ink, 'right', k);
    lineChart(c, cd.x + 40, cd.y + 100, cd.w - 80, 200, curve, P.brand, k);
  } else {
    const cd = { x: 150, y: 200, w: 980, h: 680 };
    glass(c, cd.x, cd.y, cd.w, cd.h, 28, k);
    campaignHeader(c, cd.x + 10, cd.y + 10, cd.w, k);
    pill(c, cd.x + cd.w - 50, cd.y + 70, 'Active', P.brand, k, { size: 24, align: 'right' });
    txt(c, 'Actual calls', cd.x + 200, cd.y + 190, 22, 500, P.ink2, 'center', k);
    txt(c, '30', cd.x + 200, cd.y + 265, 110, 700, P.ink, 'center', k, -3);
    txt(c, 'Tracked conversions', cd.x + 620, cd.y + 190, 22, 500, P.ink2, 'center', k);
    txt(c, String(vb), cd.x + 620, cd.y + 265, 110, 700, match > 0.99 ? P.deep : P.ink, 'center', k, -3);
    c.save(); c.globalAlpha *= match; c.strokeStyle = P.brand; c.lineWidth = 3;
    c.beginPath(); c.moveTo(cd.x + 300, cd.y + 265); c.lineTo(lerp(cd.x + 300, cd.x + 520, match), cd.y + 265); c.stroke(); c.restore();
    pill(c, cd.x + 410, cd.y + 330, 'Matched', P.brand, pr(t, 49.9, 0.5), { size: 20, align: 'center' });
    txt(c, 'Cost / conversion', cd.x + 840, cd.y + 190, 20, 500, P.ink2, 'center', k);
    txt(c, money(cost), cd.x + 840, cd.y + 255, 48, 700, P.ink, 'center', k);
    lineChart(c, cd.x + 60, cd.y + 400, cd.w - 120, 230, curve, P.brand, k);
  }

  // qualified leads streaming in
  for (let i = 0; i < 5; i++) {
    const ts = 50.3 + i * 0.3, p = (t - ts) / 1.1;
    if (p < 0 || p > 1) continue;
    const target = V ? [540, 820] : [640, 720];
    const start = V ? [-80, 300 + i * 30] : [-80, 520 + i * 40];
    const [x, y] = quad(start, [target[0] - 200, start[1] - 80], target, eio(p));
    miniCall(c, x, y, 1.05, clamp(p * 8) * (1 - clamp((p - 0.85) / 0.15)), 'brand', 'Qualified');
  }

  // outcome tiles stacking upward
  const tiles = [['users', 'Qualified leads', 54.92], ['user', 'Customers', 55.48], ['dollar', 'Revenue', 57.9]];
  tiles.forEach(([ic, label, at], i) => {
    const kk = pr(t, at - 0.15, 0.7, eo);
    if (kk <= 0) return;
    const w = V ? 860 : 520, h = V ? 92 : 130;
    const x = V ? 540 : 1500, y = (V ? 1290 - i * 108 : 720 - i * 165) + (1 - kk) * 50;
    glass(c, x - w / 2, y - h / 2, w, h, 24, kk);
    dotIcon(c, x - w / 2 + (V ? 48 : 60), y, V ? 24 : 30, P.tint, null, null, kk);
    icon(c, ic, x - w / 2 + (V ? 48 : 60), y, V ? 24 : 28, P.deep, 2, kk);
    txt(c, label, x - w / 2 + (V ? 90 : 112), y, V ? 30 : 32, 650, P.ink, 'left', kk);
    sparkUp(c, x + w / 2 - (V ? 200 : 190), y - (V ? 22 : 30), V ? 160 : 150, V ? 44 : 60, kk, pr(t, at, 0.9));
    if (i === 2) { c.save(); c.globalAlpha *= kk * 0.5; c.shadowColor = rgba(P.brand, 0.7); c.shadowBlur = 40; rr(c, x - w / 2, y - h / 2, w, h, 24); c.strokeStyle = rgba(P.brand, 0.5); c.lineWidth = 2; c.stroke(); c.restore(); }
  });
  c.restore();

  headline(c, 'Better data. Better results.', W / 2, V ? 285 : 110, V ? 52 : 52, t, 53.5, { color: P.deep });
}

// ---------------- Scene 10: the stakes ----------------
function s10(c, t) {
  const cd = V ? { x: 140, y: 360, w: 800, h: 230 } : { x: 120, y: 330, w: 680, h: 400 };
  const k = pr(t, 58.6, 0.6, eo);
  c.save();
  c.translate(V ? 0 : lerp(20, -20, pr(t, 58.7, 7)), 0);
  glass(c, cd.x, cd.y, cd.w, cd.h, 26, k * 0.95);
  campaignHeader(c, cd.x + 10, cd.y + 10, cd.w, k * 0.7);
  if (V) {
    pill(c, cd.x + 60, cd.y + 165, 'Paused', P.loss, k, { size: 22 });
    toggle(c, cd.x + cd.w - 150, cd.y + 165, 1 - pr(t, 60.44, 0.25), k);
    pill(c, cd.x + 240, cd.y + 165, 'Was working', P.brand, pr(t, 62.54, 0.5), { size: 22, dot: true });
  } else {
    pill(c, cd.x + 60, cd.y + 180, 'Paused', P.loss, k, { size: 24 });
    toggle(c, cd.x + 60, cd.y + 280, 1 - pr(t, 60.44, 0.25), k, 1.1);
    txt(c, 'Campaign status', cd.x + 180, cd.y + 280, 22, 500, P.ink2, 'left', k);
    pill(c, cd.x + 230, cd.y + 180, 'Was working', P.brand, pr(t, 62.54, 0.5), { size: 24 });
  }
  c.save(); c.globalAlpha = 0.3 * k; rr(c, cd.x, cd.y, cd.w, cd.h, 26); c.fillStyle = '#F2F4F7'; c.fill(); c.restore();

  // minimal iso map
  const m = V ? { x: 540, y: 1000, hw: 430, hh: 240 } : { x: 1330, y: 600, hw: 480, hh: 270 };
  const km = pr(t, 58.9, 0.7, eo);
  c.save(); c.globalAlpha *= km;
  c.beginPath(); c.moveTo(m.x, m.y - m.hh); c.lineTo(m.x + m.hw, m.y); c.lineTo(m.x, m.y + m.hh); c.lineTo(m.x - m.hw, m.y); c.closePath();
  c.shadowColor = 'rgba(14,26,43,0.10)'; c.shadowBlur = 40; c.shadowOffsetY = 18;
  c.fillStyle = '#FFFFFF'; c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = 'rgba(14,26,43,0.08)'; c.lineWidth = 1.5; c.stroke();
  c.clip();
  c.strokeStyle = 'rgba(14,26,43,0.05)';
  const T = [m.x, m.y - m.hh], Rr = [m.x + m.hw, m.y], B = [m.x, m.y + m.hh], Lf = [m.x - m.hw, m.y];
  const lp2 = (p, q, f) => [lerp(p[0], q[0], f), lerp(p[1], q[1], f)];
  for (let i = 1; i < 10; i++) {
    const f = i / 10;
    let a1 = lp2(Lf, T, f), b1 = lp2(B, Rr, f);
    c.beginPath(); c.moveTo(a1[0], a1[1]); c.lineTo(b1[0], b1[1]); c.stroke();
    a1 = lp2(T, Rr, f); b1 = lp2(Lf, B, f);
    c.beginPath(); c.moveTo(a1[0], a1[1]); c.lineTo(b1[0], b1[1]); c.stroke();
  }
  c.restore();
  const blocks = [[-0.45, -0.1, 70, 50, 40], [-0.2, 0.25, 60, 60, 70], [0.25, -0.3, 80, 50, 55], [0.4, 0.15, 60, 70, 35], [-0.05, -0.45, 50, 50, 50], [0.05, 0.5, 70, 50, 45]];
  blocks.forEach(([u, v, w, d, h], i) => {
    const bx = m.x + u * m.hw, by = m.y + v * m.hh;
    isoBox(c, bx, by, w, d, h * pr(t, 59.0 + i * 0.06, 0.6, eo), km);
  });
  const you = V ? [m.x - 170, m.y - 70] : [m.x - 190, m.y - 50];
  const comp = V ? [m.x + 170, m.y + 100] : [m.x + 200, m.y + 90];
  const capture = pr(t, 63.76, 0.6);
  const pinAt = (p, color, label, a, glowK) => {
    if (glowK > 0) floorShadow(c, p[0], p[1] + 6, 70, 22, 0.25 * glowK);
    floorShadow(c, p[0], p[1] + 6, 30, 10, 0.2 * a);
    c.save(); c.globalAlpha *= a;
    c.translate(p[0], p[1] - 46);
    const pp = new Path2D('M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0');
    c.translate(-36, -30); c.scale(3, 3);
    c.fillStyle = color; c.fill(pp);
    c.beginPath(); c.arc(12, 10, 3.2, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill();
    c.restore();
    pill(c, p[0], p[1] + 44, label, color === P.ink ? P.ink : P.ink2, a, { size: 20, align: 'center', dot: false });
  };
  pinAt(you, '#B7C1CC', 'You (paused)', km, 0);
  pinAt(comp, P.ink, 'Competitor', km, capture);

  // calls arriving in the area
  let won = 0;
  for (let i = 0; i < 18; i++) {
    const ts = 59.0 + i * 0.36, dur = 1.6;
    const p = (t - ts) / dur;
    const goComp = ts + dur * 0.5 > 63.5;
    if (p >= 1 && goComp) won++;
    if (p < 0 || p > 1) continue;
    const start = V ? [120 + hash(i) * 840, 680] : [880 + hash(i) * 900, 230];
    const target = goComp ? comp : you;
    const [x, y] = quad(start, [lerp(start[0], target[0], 0.3), lerp(start[1], target[1], 0.8) - 60], [target[0], target[1] - 70], eio(p));
    const a = clamp(p * 6) * (goComp ? 1 - clamp((p - 0.85) / 0.15) : 1 - clamp((p - 0.7) / 0.3));
    miniCall(c, x, y, 0.95, a, goComp ? 'brand' : 'grey');
  }
  if (won > 0) pill(c, comp[0], comp[1] - 150, `+${won} calls`, P.ink, 1, { size: 20, align: 'center' });
  c.restore();

  const hy = V ? 285 : 150;
  headline(c, 'Paused campaigns that work', W / 2, hy, V ? 50 : 52, t, 60.3, { out: 63.55 });
  headline(c, 'Competitors capture the calls', W / 2, hy, V ? 50 : 52, t, 63.76, { color: P.ink });
}

// ---------------- Scene 11: final card ----------------
const TITLE = 'Paid Ads, Web Analytics & Conversion Tracking Consultant';
const STATEMENT = "If Google can't see your real leads, it can't optimize for them.";
const CTA = 'Check your call tracking before you pause your campaign.';

function s11(c, t) {
  c.save();
  zoomAt(c, W / 2, H / 2, lerp(1, 1.03, pr(t, 65.8, 5.7, x => x)));
  const k = pr(t, 65.7, 0.8, x => x), ks = spring(k), a = clamp(k * 2);
  const kt = pr(t, 66.3, 0.6, eo), kc = pr(t, 68.8, 0.7, eo);
  if (V) {
    const cd = { x: 150, y: 300, w: 780, h: 580 };
    c.save(); c.translate(0, (1 - ks) * 50);
    glass(c, cd.x, cd.y, cd.w, cd.h, 30, a);
    portrait(c, cd.x + 230, cd.y + 36, 320, 320, 26, a);
    const lines = wrap(c, TITLE, cd.w - 100, 30, 650);
    lines.forEach((ln, i) => txt(c, ln, 540, cd.y + 410 + i * 40, 30, 650, P.ink, 'center', kt));
    c.save(); c.globalAlpha *= kt; rr(c, 540 - 40, cd.y + 410 + lines.length * 40 + 6, 80, 5, 3); c.fillStyle = P.brand; c.fill(); c.restore();
    c.restore();
    const sl = wrap(c, STATEMENT, 900, 56, 700);
    sl.forEach((ln, i) => {
      const kk = pr(t, 66.9 + i * 0.25, 0.6, eo);
      txt(c, ln, 540, 980 + i * 68 + (1 - kk) * 16, 56, 700, P.ink, 'center', kk, -0.5);
    });
    const cl = wrap(c, CTA, 860, 32, 500);
    cl.forEach((ln, i) => txt(c, ln, 540, 980 + sl.length * 68 + 50 + i * 44 + (1 - kc) * 12, 32, 500, P.ink2, 'center', kc));
  } else {
    const lines = wrap(c, TITLE, 620 - 90, 27, 650);
    const ch = 560 + lines.length * 37 + 70;
    const cd = { x: 170, y: 540 - ch / 2, w: 620, h: ch };
    c.save(); c.translate(0, (1 - ks) * 50);
    glass(c, cd.x, cd.y, cd.w, cd.h, 30, a);
    portrait(c, cd.x + 40, cd.y + 40, cd.w - 80, 470, 24, a, 0.3);
    lines.forEach((ln, i) => txt(c, ln, cd.x + 45, cd.y + 560 + i * 37, 27, 650, P.ink, 'left', kt));
    c.save(); c.globalAlpha *= kt; rr(c, cd.x + 45, cd.y + 560 + lines.length * 37 + 4, 70, 5, 3); c.fillStyle = P.brand; c.fill(); c.restore();
    c.restore();
    const sx = 900;
    const sl = wrap(c, STATEMENT, 860, 64, 700);
    const sy = 400;
    sl.forEach((ln, i) => {
      const kk = pr(t, 66.9 + i * 0.25, 0.6, eo);
      txt(c, ln, sx, sy + i * 78 + (1 - kk) * 16, 64, 700, P.ink, 'left', kk, -1);
    });
    const ly = sy + sl.length * 78 + 10;
    const kl = pr(t, 67.8, 0.8);
    c.save(); c.strokeStyle = P.brand; c.lineWidth = 3; c.lineCap = 'round';
    c.beginPath(); c.moveTo(cd.x + cd.w, ly); c.lineTo(lerp(cd.x + cd.w, sx + 120, kl), ly); c.stroke(); c.restore();
    const cl = wrap(c, CTA, 860, 32, 500);
    cl.forEach((ln, i) => txt(c, ln, sx, ly + 60 + i * 44 + (1 - kc) * 12, 32, 500, P.ink2, 'left', kc));
  }
  c.restore();
}

const SCENE_FN = { s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11 };
