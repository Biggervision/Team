// Scene 1 — the hook, told as one HVAC customer journey:
// AC stops cooling → homeowner searches → taps the ad's Call button →
// the business owner's phone rings → a high-value lead → the signal path.

const QUERY = 'ac repair near me';
const ZONE_OFFSET = () => (V ? 1750 : 1700);

// Upright phone. No tilt, no wobble — it only slides and fades.
function device(c, x, y, h, a = 1) {
  const w = h * 0.49;
  floorShadow(c, x, y + h * 0.53, w * 0.8, w * 0.1, 0.12 * a);
  c.save();
  c.globalAlpha *= a;
  c.shadowColor = 'rgba(14,26,43,0.16)'; c.shadowBlur = 48; c.shadowOffsetY = 22;
  rr(c, x - w / 2, y - h / 2, w, h, w * 0.15); c.fillStyle = '#1B2433'; c.fill();
  c.shadowColor = 'transparent';
  rr(c, x - w / 2 + 1.5, y - h / 2 + 1.5, w - 3, h - 3, w * 0.15); c.strokeStyle = 'rgba(255,255,255,0.18)'; c.lineWidth = 2; c.stroke();
  c.restore();
  return { x: x - w / 2 + 9, y: y - h / 2 + 9, w: w - 18, h: h - 18, r: w * 0.12 };
}

function statusBar(c, s, u, a) {
  txt(c, '2:14', s.x + 30 * u, s.y + 22 * u, 13 * u, 650, P.ink, 'left', a);
  c.save(); c.globalAlpha *= a;
  rr(c, s.x + s.w / 2 - 44 * u, s.y + 9 * u, 88 * u, 24 * u, 12 * u); c.fillStyle = '#0B0F16'; c.fill();
  rr(c, s.x + s.w - 52 * u, s.y + 16 * u, 22 * u, 11 * u, 3 * u); c.strokeStyle = P.ink; c.lineWidth = 1.2 * u; c.stroke();
  rr(c, s.x + s.w - 50 * u, s.y + 18 * u, 15 * u, 7 * u, 2 * u); c.fillStyle = P.ink; c.fill();
  c.restore();
}

function fingertip(c, x, y, press, a) {
  if (a <= 0.001) return;
  c.save(); c.globalAlpha *= a;
  c.beginPath(); c.arc(x, y, 26, 0, Math.PI * 2);
  c.fillStyle = 'rgba(14,26,43,0.16)'; c.fill();
  c.lineWidth = 3; c.strokeStyle = 'rgba(255,255,255,0.9)'; c.stroke();
  if (press > 0 && press < 1) {
    c.beginPath(); c.arc(x, y, 26 + press * 34, 0, Math.PI * 2);
    c.strokeStyle = rgba(P.brand, 0.6 * (1 - press)); c.lineWidth = 3; c.stroke();
  }
  c.restore();
}

// ---------- homeowner's phone ----------
function customerScreen(c, s, t, a) {
  const u = s.w / 300;
  const res = pr(t, 3.45, 0.45, eo);
  const calling = pr(t, 5.65, 0.35);
  c.save(); c.globalAlpha *= a;
  rr(c, s.x, s.y, s.w, s.h, s.r); c.clip();
  c.fillStyle = '#fff'; c.fillRect(s.x, s.y, s.w, s.h);
  const L = s.x + 16 * u, R = s.x + s.w - 16 * u;
  let call = null;

  if (calling < 1) {
    // search bar + typed query
    const by = s.y + 52 * u;
    rr(c, L, by, R - L, 42 * u, 21 * u); c.fillStyle = '#F1F4F7'; c.fill();
    icon(c, 'search', L + 22 * u, by + 21 * u, 16 * u, P.ink2, 2.2);
    const nch = Math.floor(QUERY.length * pr(t, 2.1, 1.2, x => x));
    const q = QUERY.slice(0, nch);
    if (nch === 0) txt(c, 'Search', L + 40 * u, by + 21 * u, 14 * u, 500, P.mute);
    txt(c, q, L + 40 * u, by + 21 * u, 14 * u, 500, P.ink);
    if (t < 3.45 && Math.floor(t * 2.5) % 2 === 0) {
      const cx = L + 40 * u + measure(c, q, 14 * u, 500) + 2 * u;
      c.fillStyle = P.brand; c.fillRect(cx, by + 11 * u, 2 * u, 20 * u);
    }
    // tabs
    const ty = by + 64 * u;
    ['All', 'Maps', 'Images', 'News'].forEach((tb, i) => {
      txt(c, tb, L + 4 * u + i * 58 * u, ty, 12 * u, i === 0 ? 650 : 500, i === 0 ? P.deep : P.ink2, 'left', res);
    });
    c.save(); c.globalAlpha *= res; c.fillStyle = P.deep; c.fillRect(L + 4 * u, ty + 11 * u, 18 * u, 2.5 * u); c.restore();

    // results
    c.save(); c.globalAlpha *= res; c.translate(0, (1 - res) * 40 * u);
    const y0 = s.y + 146 * u, cw = R - L;
    const glow = pr(t, 4.3, 0.4);
    if (glow > 0) { c.save(); c.globalAlpha *= glow * 0.6; c.shadowColor = rgba(P.brand, 0.8); c.shadowBlur = 24 * u; rr(c, L, y0, cw, 196 * u, 14 * u); c.fillStyle = rgba(P.brand, 0.12); c.fill(); c.restore(); }
    rr(c, L, y0, cw, 196 * u, 14 * u); c.fillStyle = '#fff'; c.fill();
    c.strokeStyle = glow > 0 ? rgba(P.brand, 0.35 + 0.4 * glow) : 'rgba(14,26,43,0.10)'; c.lineWidth = 1.5 * u; c.stroke();
    txt(c, 'Sponsored', L + 14 * u, y0 + 20 * u, 11 * u, 700, P.ink);
    dotIcon(c, L + 23 * u, y0 + 44 * u, 9 * u, P.tint);
    icon(c, 'fan', L + 23 * u, y0 + 44 * u, 11 * u, P.deep, 2.2);
    txt(c, 'CoolAir HVAC', L + 38 * u, y0 + 40 * u, 11 * u, 600, P.ink);
    txt(c, 'coolairhvac.com', L + 38 * u, y0 + 53 * u, 10 * u, 500, P.ink2);
    txt(c, 'Same-Day AC Repair &', L + 14 * u, y0 + 80 * u, 16 * u, 650, P.deep);
    txt(c, 'Replacement – Open 24/7', L + 14 * u, y0 + 100 * u, 16 * u, 650, P.deep);
    txt(c, '4.9 ★★★★★ (312) · Licensed & insured', L + 14 * u, y0 + 124 * u, 11 * u, 500, P.ink2);
    const bx = L + 14 * u, bY = y0 + 142 * u, bw = 120 * u, bh = 38 * u;
    const press = pr(t, 5.45, 0.25);
    rr(c, bx, bY, bw, bh, bh / 2); c.fillStyle = press > 0 && press < 1 ? P.deep : P.brand; c.fill();
    icon(c, 'phone', bx + 30 * u, bY + bh / 2, 15 * u, '#fff', 2.4);
    txt(c, 'Call', bx + 50 * u, bY + bh / 2 + 1, 14 * u, 650, '#fff');
    rr(c, bx + bw + 10 * u, bY, 110 * u, bh, bh / 2); c.strokeStyle = 'rgba(14,26,43,0.18)'; c.lineWidth = 1.5 * u; c.stroke();
    txt(c, 'Website', bx + bw + 65 * u, bY + bh / 2 + 1, 13 * u, 600, P.ink, 'center');
    call = { x: bx + bw / 2, y: bY + bh / 2 + (1 - res) * 40 * u, press };

    // local map pack
    const y1 = y0 + 212 * u;
    rr(c, L, y1, cw, 104 * u, 14 * u); c.fillStyle = '#EEF3F6'; c.fill();
    c.save(); rr(c, L, y1, cw, 104 * u, 14 * u); c.clip();
    c.strokeStyle = '#FFFFFF'; c.lineWidth = 7 * u;
    c.beginPath(); c.moveTo(L - 10 * u, y1 + 70 * u); c.lineTo(R + 10 * u, y1 + 30 * u); c.stroke();
    c.beginPath(); c.moveTo(L + 90 * u, y1 - 10 * u); c.lineTo(L + 140 * u, y1 + 120 * u); c.stroke();
    c.lineWidth = 4 * u;
    c.beginPath(); c.moveTo(L + 180 * u, y1 - 10 * u); c.lineTo(L + 230 * u, y1 + 120 * u); c.stroke();
    [[60, 40, P.brand], [170, 64, P.mute], [222, 30, P.mute]].forEach(([px, py, col]) => {
      c.beginPath(); c.arc(L + px * u, y1 + py * u, 7 * u, 0, Math.PI * 2); c.fillStyle = col; c.fill();
      c.lineWidth = 2 * u; c.strokeStyle = '#fff'; c.stroke();
    });
    c.restore();
    [['Desert Air Co.', '4.6 ★ · Closes 6 PM'], ['Valley Cooling', '4.4 ★ · Open now']].forEach(([n1, n2], i) => {
      const ly = y1 + 128 * u + i * 50 * u;
      txt(c, n1, L + 4 * u, ly, 13 * u, 600, P.ink2);
      txt(c, n2, L + 4 * u, ly + 18 * u, 11 * u, 500, P.mute);
      c.fillStyle = 'rgba(14,26,43,0.06)'; c.fillRect(L, ly + 32 * u, cw, 1);
    });
    c.restore();

    // keyboard while typing
    const kb = pr(t, 1.85, 0.35, eo) * (1 - pr(t, 3.35, 0.35));
    if (kb > 0) {
      const kh = 200 * u, ky = s.y + s.h - kh * kb;
      c.fillStyle = '#E8ECF0'; c.fillRect(s.x, ky, s.w, kh);
      const rows = [10, 9, 7];
      rows.forEach((nk, r) => {
        const kw = 24 * u, gap = 4.5 * u, total = nk * kw + (nk - 1) * gap;
        for (let k = 0; k < nk; k++) {
          const kx = s.x + (s.w - total) / 2 + k * (kw + gap), kyy = ky + 12 * u + r * 44 * u;
          const hit = Math.floor(t * 14) % 26 === r * 10 + k && t > 2.1 && t < 3.3;
          rr(c, kx, kyy, kw, 36 * u, 5 * u); c.fillStyle = hit ? '#CDD5DD' : '#FFFFFF'; c.fill();
        }
      });
      rr(c, s.x + 70 * u, ky + 144 * u, s.w - 140 * u, 36 * u, 5 * u); c.fillStyle = '#fff'; c.fill();
    }
  }

  // calling screen
  if (calling > 0) {
    c.save(); c.globalAlpha *= calling;
    const g = c.createLinearGradient(0, s.y, 0, s.y + s.h);
    g.addColorStop(0, '#E4F6FA'); g.addColorStop(1, '#FFFFFF');
    c.fillStyle = g; c.fillRect(s.x, s.y, s.w, s.h);
    const cx = s.x + s.w / 2, ay = s.y + 170 * u;
    for (let i = 0; i < 2; i++) {
      const f = (t * 0.8 + i / 2) % 1;
      c.beginPath(); c.arc(cx, ay, 44 * u + f * 40 * u, 0, Math.PI * 2);
      c.strokeStyle = rgba(P.brand, 0.4 * (1 - f)); c.lineWidth = 2 * u; c.stroke();
    }
    dotIcon(c, cx, ay, 44 * u, P.tint);
    icon(c, 'fan', cx, ay, 40 * u, P.deep, 1.8);
    txt(c, 'CoolAir HVAC', cx, ay + 80 * u, 22 * u, 650, P.ink, 'center');
    txt(c, t < 6.5 ? 'Calling…' : 'Ringing…', cx, ay + 108 * u, 14 * u, 500, P.ink2, 'center');
    ['Mute', 'Keypad', 'Speaker'].forEach((lb, i) => {
      const bx = cx + (i - 1) * 76 * u, by = s.y + s.h - 190 * u;
      dotIcon(c, bx, by, 26 * u, '#E3E8EE');
      txt(c, lb, bx, by + 42 * u, 10 * u, 500, P.ink2, 'center');
    });
    dotIcon(c, cx, s.y + s.h - 80 * u, 30 * u, P.ink, 'x');
    c.restore();
  }
  statusBar(c, s, u, 1);
  c.restore();
  return call;
}

// ---------- business owner's phone ----------
function ownerScreen(c, s, t, a) {
  const u = s.w / 300;
  const answered = pr(t, 7.45, 0.3);
  c.save(); c.globalAlpha *= a;
  rr(c, s.x, s.y, s.w, s.h, s.r); c.clip();
  const g = c.createLinearGradient(0, s.y, 0, s.y + s.h);
  g.addColorStop(0, '#EAF7FA'); g.addColorStop(1, '#FFFFFF');
  c.fillStyle = g; c.fillRect(s.x, s.y, s.w, s.h);
  const cx = s.x + s.w / 2;
  txt(c, answered > 0.5 ? 'On call' : 'Incoming call', cx, s.y + 100 * u, 14 * u, 500, P.ink2, 'center');
  txt(c, '(602) 555-0148', cx, s.y + 134 * u, 23 * u, 650, P.ink, 'center');
  pill(c, cx, s.y + 172 * u, 'via Google Ads · AC repair', P.deep, 1, { size: 12 * u, align: 'center' });
  const ay = s.y + 280 * u;
  if (answered < 0.5) {
    for (let i = 0; i < 2; i++) {
      const f = (t * 0.9 + i / 2) % 1;
      c.beginPath(); c.arc(cx, ay, 40 * u + f * 42 * u, 0, Math.PI * 2);
      c.strokeStyle = rgba(P.brand, 0.45 * (1 - f)); c.lineWidth = 2 * u; c.stroke();
    }
  }
  dotIcon(c, cx, ay, 40 * u, P.tint);
  icon(c, 'user', cx, ay, 36 * u, P.deep, 1.8);
  if (answered > 0.5) {
    const secs = Math.max(0, Math.floor(t - 7.45));
    txt(c, `00:0${Math.min(9, secs)}`, cx, ay + 70 * u, 18 * u, 600, P.deep, 'center');
  }
  const by = s.y + s.h - 90 * u;
  if (answered < 0.5) {
    dotIcon(c, cx - 70 * u, by, 30 * u, '#C5CED7', 'x');
    const pulse = 1 + 0.06 * Math.sin(t * 9);
    dotIcon(c, cx + 70 * u, by, 30 * u * pulse, P.brand, 'phone');
  } else dotIcon(c, cx, by, 30 * u, P.ink, 'x');
  c.restore();
  statusBar(c, s, u, a);
}

function thermostat(c, x, y, size, t, a) {
  if (a <= 0.001) return;
  const r = size / 2;
  floorShadow(c, x, y + r + 30, r * 0.9, r * 0.12, 0.08 * a);
  glass(c, x - r, y - r, size, size, size * 0.22, a, { fill: '#FFFFFF' });
  c.save(); c.globalAlpha *= a;
  const fr = r * 0.74;
  const fg = c.createRadialGradient(x, y - fr * 0.3, fr * 0.1, x, y, fr);
  fg.addColorStop(0, '#2A3547'); fg.addColorStop(1, '#141C28');
  c.beginPath(); c.arc(x, y, fr, 0, Math.PI * 2); c.fillStyle = fg; c.fill();
  const temp = Math.round(lerp(84, 89, pr(t, 0.3, 1.8)));
  const k = (temp - 60) / 40;
  c.beginPath(); c.arc(x, y, fr * 0.86, Math.PI * 0.75, Math.PI * (0.75 + 1.5 * k));
  c.strokeStyle = P.warn; c.lineWidth = fr * 0.06; c.lineCap = 'round'; c.stroke();
  c.beginPath(); c.arc(x, y, fr * 0.86, Math.PI * (0.75 + 1.5 * k), Math.PI * 2.25);
  c.strokeStyle = 'rgba(255,255,255,0.12)'; c.stroke();
  c.restore();
  txt(c, 'INSIDE', x, y - fr * 0.38, fr * 0.11, 600, 'rgba(255,255,255,0.6)', 'center', a, 2);
  txt(c, `${temp}°`, x + fr * 0.04, y + fr * 0.02, fr * 0.5, 600, '#FFFFFF', 'center', a, -2);
  const blink = t > 0.9 ? (Math.floor(t * 2) % 2 === 0 ? 1 : 0.45) : 0;
  icon(c, 'snow', x - fr * 0.2, y + fr * 0.46, fr * 0.16, P.warn, 2.2, a * blink);
  txt(c, 'Off', x + fr * 0.02, y + fr * 0.46, fr * 0.13, 650, P.warn, 'left', a * blink);
}

function industryChips(c, t) {
  const out = 1 - pr(t, 5.5, 0.5);
  if (out <= 0) return;
  const size = V ? 21 : 19, y = V ? 290 : 82, gap = 14;
  const ws = INDUSTRIES.map(([, label]) => measure(c, label, size, 600) + size * 3.2);
  let x = W / 2 - (ws.reduce((a, b) => a + b, 0) + gap * 3) / 2;
  INDUSTRIES.forEach(([ic, label, at], i) => {
    const k = pr(t, at - 0.1, 0.45, eo) * out;
    const w = ws[i], h = size * 2.1;
    if (k > 0) {
      const hv = label === 'HVAC' && t > at;
      c.save(); c.translate(0, (1 - k) * 10);
      glass(c, x, y - h / 2, w, h, h / 2, k, { blur: 16, off: 6, fill: hv ? P.brand : 'rgba(255,255,255,0.9)', stroke: hv ? P.brand : undefined });
      icon(c, ic, x + size * 1.25, y, size * 0.95, hv ? '#fff' : P.deep, 2, k);
      txt(c, label, x + size * 2.2, y + 1, size, 600, hv ? '#fff' : P.ink, 'left', k);
      c.restore();
    }
    x += w + gap;
  });
}

const PATH_STEPS = [['search', 'Search'], ['mega', 'Google Ad'], ['phone', 'Phone call'], ['store', 'Business'], ['target', 'Conversion tracking']];

function signalPath(c, t) {
  const k = pr(t, 7.9, 0.45, eo);
  if (k <= 0) return;
  const pts = PATH_STEPS.map((_, i) => V ? [140 + i * 200, 1185] : [330 + i * 315, 965]);
  const on = i => t > 8.15 + i * 0.22;
  c.save(); c.translate(0, (1 - k) * 20);
  for (let i = 0; i < 4; i++) {
    const [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
    const d = pr(t, 8.15 + i * 0.22, 0.22, x => x);
    c.save(); c.globalAlpha *= k;
    c.strokeStyle = 'rgba(14,26,43,0.12)'; c.lineWidth = 3;
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
    if (d > 0) {
      c.strokeStyle = P.brand; c.lineWidth = 4;
      c.beginPath(); c.moveTo(x1, y1); c.lineTo(lerp(x1, x2, d), y2); c.stroke();
      if (d < 1) { c.beginPath(); c.arc(lerp(x1, x2, d), y1, 8, 0, Math.PI * 2); c.fillStyle = P.brand; c.shadowColor = rgba(P.brand, 0.8); c.shadowBlur = 16; c.fill(); }
    }
    c.restore();
  }
  PATH_STEPS.forEach(([ic, label], i) => {
    const [x, y] = pts[i];
    const lit = on(i) ? 1 : 0;
    if (V) {
      dotIcon(c, x, y, 34, lit ? P.brand : '#FFFFFF', null, null, k);
      c.save(); c.globalAlpha *= k; c.beginPath(); c.arc(x, y, 34, 0, Math.PI * 2); c.strokeStyle = lit ? P.brand : 'rgba(14,26,43,0.12)'; c.lineWidth = 2; c.stroke(); c.restore();
      icon(c, ic, x, y, 28, lit ? '#fff' : P.ink2, 2, k);
      txt(c, i === 4 ? 'Tracking' : label, x, y + 58, 20, 600, lit ? P.ink : P.ink2, 'center', k);
    } else {
      const w = measure(c, label, 19, 600) + 76, h = 60;
      glass(c, x - w / 2, y - h / 2, w, h, h / 2, k, { blur: 18, off: 6, stroke: lit ? rgba(P.brand, 0.8) : undefined, lw: lit ? 2.5 : 1.5 });
      dotIcon(c, x - w / 2 + 30, y, 18, lit ? P.brand : P.tint, null, null, k);
      icon(c, ic, x - w / 2 + 30, y, 18, lit ? '#fff' : P.deep, 2, k);
      txt(c, label, x - w / 2 + 56, y + 1, 19, 600, P.ink, 'left', k);
    }
  });
  const last = pr(t, 9.03, 0.4);
  if (last > 0 && last < 1) {
    const [x, y] = pts[4];
    c.save(); c.globalAlpha *= (1 - last) * k;
    c.beginPath(); c.arc(x, y, 40 + last * 50, 0, Math.PI * 2); c.strokeStyle = P.brand; c.lineWidth = 3; c.stroke();
    c.restore();
  }
  c.restore();
}

function zonePanel(c, x, y, w, h, label, icn, a = 1) {
  glass(c, x, y, w, h, 34, a, { fill: 'rgba(255,255,255,0.55)', blur: 30, off: 10, shadow: 'rgba(14,26,43,0.05)' });
  icon(c, icn, x + 44, y + 44, 22, P.deep, 2, a);
  txt(c, label, x + 66, y + 45, 20, 600, P.ink2, 'left', a);
}

function s1(c, t) {
  const O = ZONE_OFFSET();
  const pan = pr(t, 6.0, 1.3);

  c.save();
  if (V) c.translate(0, -O * pan); else c.translate(-O * pan, 0);

  // --- homeowner zone ---
  if (V) {
    zonePanel(c, 60, 360, 960, 980, 'Homeowner · Saturday, 2:14 PM', 'house');
    const m = pr(t, 1.55, 0.8);
    const tx = lerp(540, 270, m), ty = lerp(800, 600, m), ts = lerp(420, 250, m);
    thermostat(c, tx, ty, ts, t, 1);
    pill(c, tx, ty + ts / 2 + 50, 'AC not cooling', P.warn, pr(t, 0.7, 0.5, eo), { size: 22, align: 'center' });
    const ko = pr(t, 1.1, 0.5, eo);
    c.save(); c.globalAlpha *= ko;
    icon(c, 'sun', tx - 70, ty + ts / 2 + 110, 24, P.warn, 2);
    txt(c, 'Outside 104°F', tx - 50, ty + ts / 2 + 111, 22, 600, P.ink2);
    c.restore();
  } else {
    zonePanel(c, 140, 150, 1640, 730, 'Homeowner · Saturday, 2:14 PM', 'house');
    thermostat(c, 620, 500, 320, t, 1);
    pill(c, 620, 720, 'AC not cooling', P.warn, pr(t, 0.7, 0.5, eo), { size: 22, align: 'center' });
    const ko = pr(t, 1.1, 0.5, eo);
    icon(c, 'sun', 548, 790, 24, P.warn, 2, ko);
    txt(c, 'Outside 104°F', 570, 791, 22, 600, P.ink2, 'left', ko);
  }
  const kp = pr(t, V ? 1.95 : 1.5, 0.6, eo);
  const php = V ? { x: 700, y: 870, h: 760 } : { x: 1250, y: 515, h: 680 };
  let tap = null;
  if (kp > 0) {
    const yy = php.y + (1 - kp) * 60;
    const scr = device(c, php.x, yy, php.h, kp);
    tap = customerScreen(c, scr, t, kp);
  }
  if (tap) {
    const fa = pr(t, 4.8, 0.3) * (1 - pr(t, 5.75, 0.3));
    const m = pr(t, 4.85, 0.5);
    fingertip(c, lerp(tap.x + 90, tap.x, m), lerp(tap.y + 160, tap.y, m), tap.press, fa);
  }

  // --- business zone ---
  const bz = V ? { x: 60, y: 360 + O, w: 960, h: 760 } : { x: 140 + O, y: 150, w: 1640, h: 730 };
  zonePanel(c, bz.x, bz.y, bz.w, bz.h, 'Your business · CoolAir HVAC', 'store');
  const op = V ? { x: 320, y: 780 + O, h: 560 } : { x: 720 + O, y: 545, h: 600 };
  const ko = pr(t, 5.9, 0.6);
  const oscr = device(c, op.x, op.y, op.h, ko);
  ownerScreen(c, oscr, t, ko);

  // the call signal travelling from customer to business
  const sig = pr(t, 5.75, 1.45);
  if (sig > 0 && sig < 1) {
    const a0 = [php.x, php.y], a1 = [op.x, op.y];
    const ctrl = V ? [php.x + 260, (php.y + op.y) / 2] : [(php.x + op.x) / 2, php.y - 360];
    c.save();
    c.strokeStyle = rgba(P.brand, 0.5); c.lineWidth = 3; c.setLineDash([2, 12]); c.lineCap = 'round';
    c.beginPath();
    for (let i = 0; i <= 40; i++) { const [x, y] = quad(a0, ctrl, a1, i / 40 * sig); i ? c.lineTo(x, y) : c.moveTo(x, y); }
    c.stroke();
    c.restore();
    const [hx, hy] = quad(a0, ctrl, a1, sig);
    c.save(); c.shadowColor = rgba(P.brand, 0.9); c.shadowBlur = 24;
    dotIcon(c, hx, hy, 22, P.brand, 'phone');
    c.restore();
  }

  // the lead it becomes
  const kl = pr(t, 7.55, 0.6, x => x);
  if (kl > 0) {
    const ks = spring(kl), a = clamp(kl * 2);
    const ld = V ? { x: 590, y: 560 + O, w: 400, h: 400 } : { x: 1150 + O, y: 320, w: 520, h: 380 };
    c.save(); c.translate((1 - ks) * (V ? 0 : 60), (1 - ks) * (V ? 40 : 0));
    glass(c, ld.x, ld.y, ld.w, ld.h, 28, a);
    pill(c, ld.x + 34, ld.y + 50, 'New lead', P.brand, a, { size: 20, solid: true });
    txt(c, 'via Google Ads call', ld.x + 34 + measure(c, 'New lead', 20, 600) + 64, ld.y + 51, 17, 500, P.ink2, 'left', a * (V ? 0 : 1));
    txt(c, 'AC replacement', ld.x + 34, ld.y + 120, V ? 32 : 34, 650, P.ink, 'left', a);
    txt(c, 'Estimated job value', ld.x + 34, ld.y + 180, 19, 500, P.ink2, 'left', a);
    const v = Math.round(8500 * pr(t, 7.92, 1.0, eo) / 100) * 100;
    txt(c, money(v), ld.x + 34, ld.y + 245, V ? 66 : 72, 700, P.deep, 'left', a, -2);
    txt(c, V ? 'Source: Google Ads call' : 'Customer called after tapping your ad', ld.x + 34, ld.y + ld.h - 46, 17, 500, P.ink2, 'left', a);
    c.restore();
  }
  c.restore();

  industryChips(c, t);
  signalPath(c, t);
}
