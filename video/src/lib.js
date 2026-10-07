// Shared math, drawing primitives and 3D-styled objects.
let W = 1920, H = 1080, V = false;
const IMG = {};

const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, k) => a + (b - a) * k;
const eio = k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const eo = k => 1 - Math.pow(1 - k, 3);
const spring = k => { const c1 = 1.1, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
// eased progress of t through [a, a+d]
const pr = (t, a, d, e = eio) => e(clamp((t - a) / d));
const hash = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const money = n => '$' + Math.round(n).toLocaleString('en-US');

function zoomAt(c, x, y, s) { c.translate(x, y); c.scale(s, s); c.translate(-x, -y); }

function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, Math.min(r, h / 2, w / 2)); }

function glass(c, x, y, w, h, r = 22, a = 1, o = {}) {
  if (a <= 0.001) return;
  c.save();
  c.globalAlpha *= a;
  c.shadowColor = o.shadow || 'rgba(14,26,43,0.10)';
  c.shadowBlur = o.blur ?? 40;
  c.shadowOffsetY = o.off ?? 16;
  rr(c, x, y, w, h, r);
  c.fillStyle = o.fill || 'rgba(255,255,255,0.88)';
  c.fill();
  c.shadowColor = 'transparent';
  c.lineWidth = o.lw || 1.5;
  c.strokeStyle = o.stroke || 'rgba(14,26,43,0.07)';
  c.stroke();
  const g = c.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, 'rgba(255,255,255,0.75)');
  g.addColorStop(0.35, 'rgba(255,255,255,0)');
  rr(c, x + 1.5, y + 1.5, w - 3, h - 3, r - 1);
  c.fillStyle = g;
  c.fill();
  c.restore();
}

function txt(c, s, x, y, size, weight = 500, color = P.ink, align = 'left', a = 1, ls = 0) {
  if (a <= 0.001) return;
  c.save();
  c.globalAlpha *= a;
  c.font = `${weight} ${size}px Inter`;
  c.fillStyle = color;
  c.textAlign = align;
  c.textBaseline = 'middle';
  c.letterSpacing = ls + 'px';
  c.fillText(s, x, y);
  c.restore();
}

function measure(c, s, size, weight = 500) { c.save(); c.font = `${weight} ${size}px Inter`; const w = c.measureText(s).width; c.restore(); return w; }

function wrap(c, s, maxW, size, weight) {
  const words = s.split(' '), lines = [];
  let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (measure(c, test, size, weight) > maxW && cur) { lines.push(cur); cur = w; } else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
}

// Text that rises into place as it fades in.
function headline(c, s, x, y, size, t, at, o = {}) {
  const k = pr(t, at, 0.6, eo);
  const out = o.out != null ? 1 - pr(t, o.out, 0.45) : 1;
  const a = k * out;
  if (a <= 0.001) return;
  const lines = o.maxW ? wrap(c, s, o.maxW, size, o.weight || 600) : s.split('\n');
  const lh = size * 1.18;
  lines.forEach((ln, i) => {
    const kk = pr(t, at + i * 0.12, 0.6, eo) * out;
    txt(c, ln, x, y + i * lh + (1 - kk) * 18, size, o.weight || 600, o.color || P.ink, o.align || 'center', kk, -0.5);
  });
}

// ---------- icons (24px line icons, drawn as Path2D) ----------
const ICON_SRC = {
  phone: ['M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z'],
  scale: ['m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z', 'm2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z', 'M7 21h10', 'M12 3v18', 'M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2'],
  snow: ['m10 20-1.25-2.5L6 18', 'M10 4 8.75 6.5 6 6', 'm14 20 1.25-2.5L18 18', 'm14 4 1.25 2.5L18 6', 'm17 21-3-6h-4', 'm17 3-3 6 1.5 3', 'M2 12h6.5L10 9', 'm20 10-1.5 2 1.5 2', 'M22 12h-6.5L14 15', 'm4 10 1.5 2L4 14', 'm7 21 3-6-1.5-3', 'm7 3 3 6h4'],
  house: ['M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8', 'M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'],
  drop: ['M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z'],
  chart: ['M3 3v16a2 2 0 0 0 2 2h16', 'm19 9-5 5-4-4-3 3'],
  user: ['M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2', 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0'],
  users: ['M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2', 'M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0', 'M22 21v-2a4 4 0 0 0-3-3.87', 'M16 3.13a4 4 0 0 1 0 7.75'],
  mega: ['m3 11 18-5v12L3 14v-3z', 'M11.6 16.8a3 3 0 1 1-5.8-1.6'],
  target: ['M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0', 'M22 12h-4', 'M6 12H2', 'M12 6V2', 'M12 22v-4'],
  check: ['M20 6 9 17l-5-5'],
  x: ['M18 6 6 18', 'm6 6 12 12'],
  filter: ['M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z'],
  send: ['M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z', 'm21.854 2.147-10.94 10.939'],
  pin: ['M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0', 'M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0'],
  dollar: ['M12 2v20', 'M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'],
  trend: ['M22 7 13.5 15.5 8.5 10.5 2 17', 'M16 7h6v6'],
  pause: ['M14 4h4v16h-4z', 'M6 4h4v16H6z'],
};
const ICON = {};
for (const k in ICON_SRC) ICON[k] = ICON_SRC[k].map(d => new Path2D(d));

function icon(c, name, x, y, size, color, lw = 2, a = 1) {
  if (a <= 0.001) return;
  c.save();
  c.globalAlpha *= a;
  c.translate(x - size / 2, y - size / 2);
  c.scale(size / 24, size / 24);
  c.lineWidth = lw;
  c.lineCap = 'round';
  c.lineJoin = 'round';
  c.strokeStyle = color;
  for (const p of ICON[name]) c.stroke(p);
  c.restore();
}

function dotIcon(c, x, y, r, fill, name, iconColor = '#fff', a = 1) {
  if (a <= 0.001) return;
  c.save();
  c.globalAlpha *= a;
  c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fillStyle = fill; c.fill();
  c.restore();
  if (name) icon(c, name, x, y, r * 1.05, iconColor, 2.4, a);
}

// ---------- background: soft canvas, faint grid, perspective floor ----------
function background(c, t) {
  c.fillStyle = P.canvas;
  c.fillRect(0, 0, W, H);
  let g = c.createRadialGradient(W * 0.18, H * 0.06, 0, W * 0.18, H * 0.06, Math.max(W, H) * 0.85);
  g.addColorStop(0, rgba(P.brand, 0.08));
  g.addColorStop(1, rgba(P.brand, 0));
  c.fillStyle = g;
  c.fillRect(0, 0, W, H);

  // flat grid
  const step = 64, drift = (t * 3) % step;
  c.lineWidth = 1;
  c.strokeStyle = 'rgba(14,26,43,0.045)';
  c.beginPath();
  for (let x = -step + drift; x < W + step; x += step) { c.moveTo(x, 0); c.lineTo(x, H); }
  for (let y = 0; y < H + step; y += step) { c.moveTo(0, y); c.lineTo(W, y); }
  c.stroke();

  // perspective floor
  const hy = V ? H * 0.56 : H * 0.58;
  c.save();
  c.beginPath(); c.rect(0, hy, W, H - hy); c.clip();
  c.fillStyle = 'rgba(247,249,251,0.6)';
  c.fillRect(0, hy, W, H - hy);
  c.strokeStyle = 'rgba(14,26,43,0.07)';
  c.beginPath();
  const spread = V ? 150 : 210;
  for (let i = -24; i <= 24; i++) { c.moveTo(W / 2 + i * 28, hy); c.lineTo(W / 2 + i * spread, H); }
  const N = 14;
  for (let j = 0; j < N; j++) {
    const f = ((j + t * 0.25) % N) / N;
    const y = hy + (H - hy) * f * f;
    c.moveTo(0, y); c.lineTo(W, y);
  }
  c.stroke();
  const fg = c.createLinearGradient(0, hy, 0, hy + (H - hy) * 0.55);
  fg.addColorStop(0, P.canvas);
  fg.addColorStop(1, 'rgba(247,249,251,0)');
  c.fillStyle = fg;
  c.fillRect(0, hy, W, H - hy);
  c.restore();
}

function floorShadow(c, x, y, rx, ry, a = 0.14) {
  c.save();
  c.translate(x, y); c.scale(1, ry / rx);
  const g = c.createRadialGradient(0, 0, 0, 0, 0, rx);
  g.addColorStop(0, `rgba(14,26,43,${a})`);
  g.addColorStop(1, 'rgba(14,26,43,0)');
  c.fillStyle = g;
  c.beginPath(); c.arc(0, 0, rx, 0, Math.PI * 2); c.fill();
  c.restore();
}

// ---------- 3D-styled smartphone ----------
function phone(c, x, y, h, t, ring) {
  const w = h * 0.5;
  floorShadow(c, x + 10, y + h * 0.58, w * 0.85, w * 0.14, 0.16);
  c.save();
  c.translate(x, y);
  if (ring > 0) { c.translate(Math.sin(t * 95) * 2.2 * ring, 0); c.rotate(Math.sin(t * 61) * 0.007 * ring); }
  c.transform(1, -0.035, 0.0, 1, 0, 0);
  // side thickness
  rr(c, -w / 2 + 9, -h / 2 + 6, w, h, w * 0.17);
  c.fillStyle = '#C9D3DD'; c.fill();
  // body
  c.shadowColor = 'rgba(14,26,43,0.18)'; c.shadowBlur = 50; c.shadowOffsetY = 24;
  const bg = c.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2);
  bg.addColorStop(0, '#FFFFFF'); bg.addColorStop(1, '#E6ECF1');
  rr(c, -w / 2, -h / 2, w, h, w * 0.17); c.fillStyle = bg; c.fill();
  c.shadowColor = 'transparent';
  c.lineWidth = 2; c.strokeStyle = 'rgba(14,26,43,0.10)'; c.stroke();
  // screen
  const sx = -w / 2 + 11, sy = -h / 2 + 11, sw = w - 22, sh = h - 22;
  const sg = c.createLinearGradient(0, sy, 0, sy + sh);
  sg.addColorStop(0, '#E6F7FA'); sg.addColorStop(1, '#FFFFFF');
  rr(c, sx, sy, sw, sh, w * 0.13); c.fillStyle = sg; c.fill();
  rr(c, -w * 0.12, sy + 12, w * 0.24, h * 0.03, 10); c.fillStyle = P.ink; c.fill();
  // caller
  const cy = -h * 0.16;
  for (let i = 0; i < 3; i++) {
    const f = ((t * 0.9 + i / 3) % 1);
    c.beginPath(); c.arc(0, cy, w * 0.17 + f * w * 0.2, 0, Math.PI * 2);
    c.strokeStyle = rgba(P.brand, (1 - f) * 0.45 * ring); c.lineWidth = 2; c.stroke();
  }
  dotIcon(c, 0, cy, w * 0.16, P.brand, 'phone');
  txt(c, 'Incoming call', 0, cy + w * 0.36, h * 0.03, 500, P.ink2, 'center');
  txt(c, 'Google Ads lead', 0, cy + w * 0.5, h * 0.04, 650, P.ink, 'center');
  // buttons
  const by = h * 0.32;
  dotIcon(c, -w * 0.22, by, w * 0.1, '#C5CED7', 'x');
  dotIcon(c, w * 0.22, by, w * 0.1, P.brand, 'phone');
  c.restore();
}

// ---------- the phone call black hole ----------
function vortex(c, x, y, R, t, open, heat = 0) {
  if (open <= 0.01) return;
  R *= eo(open);
  const k = 0.38;
  c.save();
  c.translate(x, y); c.scale(1, k);
  const g = c.createRadialGradient(0, 0, 0, 0, 0, R);
  g.addColorStop(0, 'rgba(96,112,130,0.55)');
  g.addColorStop(0.25, 'rgba(150,166,182,0.42)');
  g.addColorStop(0.6, 'rgba(205,215,225,0.25)');
  g.addColorStop(1, 'rgba(247,249,251,0)');
  c.fillStyle = g;
  c.beginPath(); c.arc(0, 0, R, 0, Math.PI * 2); c.fill();
  // rings drifting inward
  for (let i = 0; i < 10; i++) {
    const f = ((i / 10) + t * 0.16) % 1;
    const r = R * (1 - f) * 0.96;
    c.beginPath(); c.arc(0, 0, r, 0, Math.PI * 2);
    c.strokeStyle = `rgba(14,26,43,${Math.sin(f * Math.PI) * 0.16})`;
    c.lineWidth = 1.6; c.stroke();
  }
  // spiral arms
  for (let a = 0; a < 12; a++) {
    c.beginPath();
    for (let s = 0; s <= 1.0001; s += 0.04) {
      const r = R * (1 - s) * 0.96;
      const th = a * (Math.PI * 2 / 12) + t * 0.5 + s * 3.4;
      const px = r * Math.cos(th), py = r * Math.sin(th);
      s === 0 ? c.moveTo(px, py) : c.lineTo(px, py);
    }
    c.strokeStyle = 'rgba(14,26,43,0.09)'; c.lineWidth = 1.4; c.stroke();
  }
  if (heat > 0.01) {
    c.beginPath(); c.arc(0, 0, R * 0.9, 0, Math.PI * 2);
    c.strokeStyle = rgba(P.warn, 0.5 * heat); c.lineWidth = 3; c.stroke();
  }
  const core = c.createRadialGradient(0, 0, 0, 0, 0, R * 0.16);
  core.addColorStop(0, 'rgba(40,52,68,0.55)'); core.addColorStop(1, 'rgba(40,52,68,0)');
  c.fillStyle = core; c.beginPath(); c.arc(0, 0, R * 0.16, 0, Math.PI * 2); c.fill();
  c.restore();
}

// ---------- UI pieces ----------
// tone: 'brand' | 'warn' | 'grey'
function toneColor(tone) { return tone === 'warn' ? P.warn : tone === 'grey' ? P.mute : tone === 'loss' ? P.loss : P.brand; }

function callCard(c, x, y, s, label, value, a = 1, tone = 'brand') {
  if (a <= 0.001) return;
  const w = 270 * s, h = 76 * s;
  glass(c, x - w / 2, y - h / 2, w, h, h / 2, a, { blur: 26, off: 10 });
  dotIcon(c, x - w / 2 + h / 2, y, h * 0.33, toneColor(tone), 'phone', '#fff', a);
  txt(c, label, x - w / 2 + h * 0.98, y - h * 0.17, 19 * s, 500, P.ink2, 'left', a);
  txt(c, value, x - w / 2 + h * 0.98, y + h * 0.2, 25 * s, 700, tone === 'grey' ? P.mute : P.ink, 'left', a);
}

function miniCall(c, x, y, s, a = 1, tone = 'brand', label = '') {
  if (a <= 0.001) return;
  const w = (label ? 168 : 92) * s, h = 46 * s;
  glass(c, x - w / 2, y - h / 2, w, h, h / 2, a, { blur: 18, off: 6 });
  dotIcon(c, x - w / 2 + h / 2, y, h * 0.32, toneColor(tone), 'phone', '#fff', a);
  if (label) txt(c, label, x - w / 2 + h * 0.95, y, 17 * s, 600, tone === 'grey' ? P.mute : P.ink, 'left', a);
  else { rr(c, x - w / 2 + h * 0.95, y - 4 * s, w * 0.38, 8 * s, 4); c.save(); c.globalAlpha *= a * 0.6; c.fillStyle = P.line; c.fill(); c.restore(); }
}

function node(c, x, y, size, ic, label, a = 1, o = {}) {
  if (a <= 0.001) return;
  const r = size * 0.26;
  if (o.glow > 0) {
    c.save(); c.globalAlpha *= a * o.glow;
    c.shadowColor = rgba(o.glowColor || P.brand, 0.7); c.shadowBlur = 40;
    rr(c, x - size / 2, y - size / 2, size, size, r); c.fillStyle = rgba(o.glowColor || P.brand, 0.25); c.fill();
    c.restore();
  }
  glass(c, x - size / 2, y - size / 2, size, size, r, a, { stroke: o.border || 'rgba(14,26,43,0.07)', lw: o.border ? 3 : 1.5 });
  icon(c, ic, x, y, size * 0.4, o.iconColor || P.deep, 2, a);
  if (label) {
    if (o.labelSide) txt(c, label, x + size * 0.7, y, o.labelSize || 28, 600, P.ink, 'left', a);
    else txt(c, label, x, y + size * 0.5 + (o.labelSize || 24) * 1.1, o.labelSize || 24, 600, P.ink, 'center', a);
  }
  if (o.check > 0.01) {
    const k = o.check;
    dotIcon(c, x + size * 0.42, y - size * 0.42, size * 0.16 * spring(k), P.brand, 'check', '#fff', a * clamp(k * 2));
  }
}

function pill(c, x, y, text, color, a = 1, o = {}) {
  if (a <= 0.001) return;
  const size = o.size || 22;
  const w = measure(c, text, size, 600) + size * 2.2 + (o.dot === false ? -size * 0.7 : 0), h = size * 2;
  let px = o.align === 'right' ? x - w : o.align === 'center' ? x - w / 2 : x;
  c.save();
  c.globalAlpha *= a;
  if (o.flip != null) { c.translate(px + w / 2, y); c.scale(1, Math.max(0.02, Math.abs(o.flip))); c.translate(-(px + w / 2), -y); }
  rr(c, px, y - h / 2, w, h, h / 2);
  c.fillStyle = o.solid ? color : rgba(color, 0.13); c.fill();
  if (o.dot !== false) { c.beginPath(); c.arc(px + size * 0.9, y, size * 0.27, 0, Math.PI * 2); c.fillStyle = o.solid ? '#fff' : color; c.fill(); }
  txt(c, text, px + (o.dot === false ? size * 0.8 : size * 1.5), y + 1, size, 600, o.solid ? '#fff' : color, 'left');
  c.restore();
  return w;
}

// Line chart in a box; values 0..1
function lineChart(c, x, y, w, h, vals, color, a = 1, upto = 1) {
  if (a <= 0.001) return;
  c.save(); c.globalAlpha *= a;
  c.strokeStyle = 'rgba(14,26,43,0.06)'; c.lineWidth = 1;
  for (let i = 0; i <= 3; i++) { c.beginPath(); c.moveTo(x, y + h * i / 3); c.lineTo(x + w, y + h * i / 3); c.stroke(); }
  const n = vals.length, last = Math.max(1, Math.floor((n - 1) * upto));
  const px = i => x + w * i / (n - 1), py = v => y + h * (1 - v);
  c.beginPath(); c.moveTo(px(0), py(vals[0]));
  for (let i = 1; i <= last; i++) c.lineTo(px(i), py(vals[i]));
  const g = c.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, rgba(color, 0.22)); g.addColorStop(1, rgba(color, 0));
  c.save(); c.lineTo(px(last), y + h); c.lineTo(px(0), y + h); c.closePath(); c.fillStyle = g; c.fill(); c.restore();
  c.beginPath(); c.moveTo(px(0), py(vals[0]));
  for (let i = 1; i <= last; i++) c.lineTo(px(i), py(vals[i]));
  c.strokeStyle = color; c.lineWidth = 3.5; c.lineJoin = 'round'; c.stroke();
  c.beginPath(); c.arc(px(last), py(vals[last]), 7, 0, Math.PI * 2); c.fillStyle = color; c.fill();
  c.restore();
}

function campaignHeader(c, x, y, w, a = 1, title = 'Search · Local Services') {
  dotIcon(c, x + 58, y + 62, 30, P.tint, null, null, a);
  icon(c, 'mega', x + 58, y + 62, 30, P.deep, 2, a);
  txt(c, title, x + 104, y + 50, 28, 650, P.ink, 'left', a);
  txt(c, 'Ad campaign · Calls & leads', x + 104, y + 82, 19, 500, P.ink2, 'left', a);
}

function metric(c, x, y, label, value, a = 1, o = {}) {
  txt(c, label, x, y, o.ls || 19, 500, P.ink2, 'left', a);
  txt(c, value, x, y + (o.vs || 44) * 0.95, o.vs || 44, 700, o.color || P.ink, 'left', a);
}

function toggle(c, x, y, on, a = 1, s = 1) {
  const w = 84 * s, h = 46 * s;
  c.save(); c.globalAlpha *= a;
  rr(c, x, y - h / 2, w, h, h / 2);
  c.fillStyle = on > 0.5 ? P.brand : '#CBD3DC'; c.fill();
  const kx = lerp(x + h / 2, x + w - h / 2, on);
  c.shadowColor = 'rgba(14,26,43,0.2)'; c.shadowBlur = 8; c.shadowOffsetY = 2;
  c.beginPath(); c.arc(kx, y, h * 0.4, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill();
  c.restore();
}

function slider(c, x, y, w, k, a = 1, color = P.brand) {
  c.save(); c.globalAlpha *= a;
  rr(c, x, y - 5, w, 10, 5); c.fillStyle = '#E3E8EE'; c.fill();
  rr(c, x, y - 5, w * k, 10, 5); c.fillStyle = color; c.fill();
  c.shadowColor = 'rgba(14,26,43,0.22)'; c.shadowBlur = 12; c.shadowOffsetY = 3;
  c.beginPath(); c.arc(x + w * k, y, 16, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill();
  c.shadowColor = 'transparent';
  c.lineWidth = 3; c.strokeStyle = color; c.stroke();
  c.restore();
}

function cursor(c, x, y, press = 0, a = 1) {
  if (a <= 0.001) return;
  c.save(); c.globalAlpha *= a;
  c.translate(x, y); c.scale(1.9 - press * 0.2, 1.9 - press * 0.2); c.translate(-4, -4);
  c.shadowColor = 'rgba(14,26,43,0.25)'; c.shadowBlur = 8; c.shadowOffsetY = 3;
  const p = new Path2D('M4.037 4.688a.495.495 0 0 1 .651-.651l16 6.5a.5.5 0 0 1-.063.947l-6.124 1.58a2 2 0 0 0-1.438 1.435l-1.579 6.126a.5.5 0 0 1-.947.063z');
  c.fillStyle = P.ink; c.fill(p);
  c.shadowColor = 'transparent';
  c.lineWidth = 1.4; c.strokeStyle = '#fff'; c.stroke(p);
  c.restore();
  if (press > 0) {
    c.save(); c.globalAlpha *= a * (1 - press);
    c.beginPath(); c.arc(x, y, 14 + press * 30, 0, Math.PI * 2); c.strokeStyle = rgba(P.ink, 0.35); c.lineWidth = 2; c.stroke();
    c.restore();
  }
}

// Portrait drawn cover-fit into a rounded rect; fy biases the crop vertically.
function portrait(c, x, y, w, h, r, a = 1, fy = 0.35) {
  const img = IMG.portrait;
  if (!img || a <= 0.001) return;
  c.save(); c.globalAlpha *= a;
  c.shadowColor = 'rgba(14,26,43,0.14)'; c.shadowBlur = 30; c.shadowOffsetY = 12;
  rr(c, x, y, w, h, r); c.fillStyle = '#fff'; c.fill();
  c.shadowColor = 'transparent';
  rr(c, x, y, w, h, r); c.clip();
  const s = Math.max(w / img.width, h / img.height);
  const dw = img.width * s, dh = img.height * s;
  c.drawImage(img, x + (w - dw) / 2, y + (h - dh) * fy, dw, dh);
  c.restore();
  c.save(); c.globalAlpha *= a;
  rr(c, x, y, w, h, r); c.lineWidth = 2; c.strokeStyle = 'rgba(255,255,255,0.9)'; c.stroke();
  c.restore();
}

function portraitCircle(c, x, y, r, a = 1) {
  const img = IMG.portrait;
  if (!img || a <= 0.001) return;
  c.save(); c.globalAlpha *= a;
  c.shadowColor = 'rgba(14,26,43,0.18)'; c.shadowBlur = 20; c.shadowOffsetY = 8;
  c.beginPath(); c.arc(x, y, r + 4, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill();
  c.shadowColor = 'transparent';
  c.beginPath(); c.arc(x, y, r + 4, 0, Math.PI * 2); c.lineWidth = 3; c.strokeStyle = P.brand; c.stroke();
  c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.clip();
  const s = (r * 2.3) / img.width;
  c.drawImage(img, x - img.width * s / 2, y - img.height * s * 0.4, img.width * s, img.height * s);
  c.restore();
}

// Connector between two points. state: 'ok' | 'broken' | 'idle'
function connector(c, x1, y1, x2, y2, t, state, a = 1, draw = 1) {
  if (a <= 0.001 || draw <= 0) return;
  const ex = lerp(x1, x2, draw), ey = lerp(y1, y2, draw);
  c.save(); c.globalAlpha *= a;
  c.lineCap = 'round';
  if (state === 'broken') {
    c.setLineDash([10, 12]);
    c.strokeStyle = rgba(P.warn, 0.75); c.lineWidth = 3;
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(lerp(x1, x2, 0.4), lerp(y1, y2, 0.4)); c.stroke();
    c.beginPath(); c.moveTo(lerp(x1, x2, 0.62), lerp(y1, y2, 0.62)); c.lineTo(ex, ey); c.stroke();
    c.setLineDash([]);
    for (let i = 0; i < 3; i++) {
      const f = ((t * 0.7 + i / 3) % 1);
      const fa = f < 0.4 ? 1 : clamp(1 - (f - 0.4) / 0.12);
      const drop = f > 0.4 ? (f - 0.4) * 160 : 0;
      c.beginPath(); c.arc(lerp(x1, x2, Math.min(f, 0.52)), lerp(y1, y2, Math.min(f, 0.52)) + drop, 6, 0, Math.PI * 2);
      c.fillStyle = rgba(P.warn, fa * 0.9); c.fill();
    }
  } else {
    c.strokeStyle = state === 'ok' ? rgba(P.brand, 0.85) : 'rgba(14,26,43,0.16)';
    c.lineWidth = state === 'ok' ? 4 : 3;
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(ex, ey); c.stroke();
    for (let i = 0; i < 3; i++) {
      const f = ((t * 0.7 + i / 3) % 1);
      if (f > draw) continue;
      c.beginPath(); c.arc(lerp(x1, x2, f), lerp(y1, y2, f), state === 'ok' ? 7 : 5, 0, Math.PI * 2);
      c.fillStyle = state === 'ok' ? P.brand : 'rgba(14,26,43,0.28)'; c.fill();
    }
  }
  c.restore();
}

function quad(p0, p1, p2, k) {
  const a = lerp(p0[0], p1[0], k), b = lerp(p0[1], p1[1], k);
  const d = lerp(p1[0], p2[0], k), e = lerp(p1[1], p2[1], k);
  return [lerp(a, d, k), lerp(b, e, k)];
}

function sparkUp(c, x, y, w, h, a = 1, k = 1) {
  lineChart(c, x, y, w, h, [0.15, 0.2, 0.18, 0.32, 0.36, 0.5, 0.55, 0.72, 0.8, 0.92], P.brand, a, k);
}

function isoBox(c, x, y, w, d, h, a = 1, tone = '#E9EEF3') {
  // x,y = ground centre; w along +x iso, d along -x iso
  c.save(); c.globalAlpha *= a;
  const ix = w * 0.5, iy = w * 0.28, jx = d * 0.5, jy = d * 0.28;
  const top = [[x, y - h], [x + ix, y - h + iy], [x + ix - jx, y - h + iy + jy], [x - jx, y - h + jy]];
  c.beginPath(); c.moveTo(x + ix, y + iy - h); c.lineTo(x + ix, y + iy); c.lineTo(x + ix - jx, y + iy + jy); c.lineTo(x + ix - jx, y + iy + jy - h); c.closePath();
  c.fillStyle = '#D9E0E7'; c.fill();
  c.beginPath(); c.moveTo(x - jx, y + jy - h); c.lineTo(x - jx, y + jy); c.lineTo(x + ix - jx, y + iy + jy); c.lineTo(x + ix - jx, y + iy + jy - h); c.closePath();
  c.fillStyle = '#E4E9EF'; c.fill();
  c.beginPath(); top.forEach((p, i) => (i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]))); c.closePath();
  c.fillStyle = tone; c.fill();
  c.restore();
}
