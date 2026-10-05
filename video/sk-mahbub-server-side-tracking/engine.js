/* SK Mahbub — Server-Side Tracking video. Deterministic canvas renderer: renderFrame(t). */
const W = 1080, H = 1920;
const cv = document.getElementById('c');
const X = cv.getContext('2d');
const TL = window.TIMELINE;
const SC = {}; TL.scenes.forEach(s => SC[s.id] = s);

// ---------- brand tokens (sampled from website screenshot) ----------
const BG = '#04090B';
const teal = a => `rgba(25,195,177,${a})`;
const tealB = a => `rgba(59,227,207,${a})`;
const wht = a => `rgba(244,247,247,${a})`;
const GREY = a => `rgba(150,166,168,${a})`;

// ---------- math ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const P = (t, a, d) => clamp((t - a) / d);
const E = {
  oc: t => 1 - Math.pow(1 - t, 3),
  oq: t => 1 - Math.pow(1 - t, 5),
  io: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  ox: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
  ob: t => { const c1 = 1.25, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  sine: t => -(Math.cos(Math.PI * t) - 1) / 2,
};
function hash(a, b = 0) { const x = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return x - Math.floor(x); }
const ct = (s, clip) => s.start + clip - s.trim_in;

// ---------- primitives ----------
const font = (size, weight = 800, fam = 'Inter') => `${weight} ${size}px ${fam}`;
function rr(x, y, w, h, r) { X.beginPath(); X.roundRect(x, y, w, h, r); }
function fit(str, weight, size, maxW, fam = 'Inter', ls = 0) {
  X.save(); X.font = font(size, weight, fam); X.letterSpacing = ls + 'px';
  const w = X.measureText(str).width; X.restore();
  return w > maxW ? size * maxW / w : size;
}
function text(s, x, y, o = {}) {
  X.save();
  X.font = font(o.size || 40, o.weight || 700, o.fam || 'Inter');
  X.letterSpacing = (o.ls || 0) + 'px';
  X.textAlign = o.align || 'center'; X.textBaseline = o.base || 'alphabetic';
  X.globalAlpha *= (o.a ?? 1);
  X.fillStyle = o.color || wht(1);
  if (o.glow) { X.shadowColor = o.glowColor || teal(.55); X.shadowBlur = o.glow; }
  X.fillText(s, x, y);
  X.restore();
}
function measure(s, size, weight, fam = 'Inter', ls = 0) {
  X.save(); X.font = font(size, weight, fam); X.letterSpacing = ls + 'px';
  const w = X.measureText(s).width; X.restore(); return w;
}

/* Kinetic line: words mask-reveal from below. [word] = teal accent. */
function kline(str, x, y, o, t0, t) {
  if (t < t0) return;
  const size = o.size || 80, weight = o.weight || 800, fam = o.fam || 'Inter', ls = o.ls ?? -1;
  let q = 0;
  if (o.out !== undefined) { q = E.io(P(t, o.out, o.outDur || .4)); if (q >= 1) return; }
  const words = []; let acc = false;
  for (const raw of str.split(' ')) {
    let w = raw; let a = acc;
    if (w.startsWith('[')) { w = w.slice(1); a = true; acc = true; }
    if (w.endsWith(']')) { w = w.slice(0, -1); acc = false; }
    words.push({ w, a });
  }
  const sp = measure(' ', size, weight, fam, ls);
  words.forEach(o2 => o2.width = measure(o2.w, size, weight, fam, ls));
  const total = words.reduce((s, w) => s + w.width, 0) + sp * (words.length - 1);
  let cx = (o.align === 'left') ? x : x - total / 2;
  const st = o.stagger ?? .07, dur = o.dur ?? .55;
  words.forEach((wd, i) => {
    const p = E.oq(P(t, t0 + i * st, dur));
    if (p > 0) {
      X.save();
      X.globalAlpha *= p * (1 - q) * (o.a ?? 1);
      X.beginPath(); X.rect(cx - 30, y - size * 1.05 - q * size, wd.width + 60, size * 1.42 + q * size); X.clip();
      const dy = (1 - p) * size * .95 - q * size * .55;
      text(wd.w, cx, y + dy, {
        size, weight, fam, ls, align: 'left', color: wd.a ? (o.accent || teal(1)) : (o.color || wht(1)),
        glow: wd.a ? (o.glow ?? 26) : (o.wglow || 0), glowColor: teal(.5)
      });
      X.restore();
    }
    cx += wd.width + sp;
  });
  return total;
}

function card(x, y, w, h, o = {}) {
  const r = o.r ?? 28;
  X.save(); X.globalAlpha *= (o.a ?? 1);
  if (o.glow) { X.shadowColor = teal(.32 * o.glow); X.shadowBlur = 70 * o.glow; }
  const g = X.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, 'rgba(17,31,35,0.96)'); g.addColorStop(1, 'rgba(9,18,21,0.96)');
  rr(x, y, w, h, r); X.fillStyle = g; X.fill();
  X.shadowBlur = 0;
  X.lineWidth = o.lw ?? 1.5; X.strokeStyle = o.stroke || 'rgba(255,255,255,0.075)'; X.stroke();
  // top inner highlight
  const hg = X.createLinearGradient(x, 0, x + w, 0);
  hg.addColorStop(0, 'rgba(255,255,255,0)'); hg.addColorStop(.5, 'rgba(255,255,255,0.10)'); hg.addColorStop(1, 'rgba(255,255,255,0)');
  X.beginPath(); X.moveTo(x + r, y + .75); X.lineTo(x + w - r, y + .75); X.strokeStyle = hg; X.lineWidth = 1.5; X.stroke();
  X.restore();
}

function pill(x, y, label, o = {}) { // x = center
  const size = o.size || 22, fam = o.fam || 'JBM', weight = o.weight || 700, ls = o.ls ?? 1;
  const tw = measure(label, size, weight, fam, ls);
  const w = tw + (o.dot ? 64 : 44), h = o.h || size * 2;
  X.save(); X.globalAlpha *= (o.a ?? 1);
  rr(x - w / 2, y - h / 2, w, h, h / 2);
  X.fillStyle = o.fill || teal(.10); X.fill();
  X.strokeStyle = o.stroke || teal(.38); X.lineWidth = 1.5; X.stroke();
  let tx = x - w / 2 + 22;
  if (o.dot) {
    X.beginPath(); X.arc(tx + 6, y, 6, 0, 7); X.fillStyle = o.dotColor || teal(1);
    X.shadowColor = teal(.8); X.shadowBlur = 12; X.fill(); X.shadowBlur = 0; tx += 22;
  }
  text(label, tx, y + size * .36, { size, weight, fam, ls, align: 'left', color: o.color || teal(1) });
  X.restore();
  return w;
}

function eyebrow(t, t0, label, y = 300, out) {
  if (t < t0) return;
  let p = E.oc(P(t, t0, .6));
  if (out !== undefined) p *= 1 - E.io(P(t, out, .35));
  X.save(); X.globalAlpha *= p; X.translate(0, (1 - p) * 16);
  pill(540, y, label, { size: 22, weight: 700, fam: 'Inter', ls: 4, dot: true, h: 54 });
  X.restore();
}

// ---------- icons (stroke, centered on cx,cy; s = box size) ----------
function icon(name, cx, cy, s, col = teal(1), lw = 3) {
  const k = s / 64;
  X.save(); X.translate(cx, cy); X.scale(k, k);
  X.strokeStyle = col; X.fillStyle = col; X.lineWidth = lw / k * k * 1.0; X.lineCap = 'round'; X.lineJoin = 'round';
  X.lineWidth = lw;
  X.beginPath();
  switch (name) {
    case 'globe': X.arc(0, 0, 16, 0, 7); X.moveTo(-16, 0); X.lineTo(16, 0); X.stroke(); X.beginPath(); X.ellipse(0, 0, 7, 16, 0, 0, 7); break;
    case 'browser': X.roundRect(-19, -15, 38, 30, 5); X.moveTo(-19, -6); X.lineTo(19, -6); X.stroke(); X.beginPath();
      [-14, -9, -4].forEach(x => { X.moveTo(x + 1.2, -10.5); X.arc(x, -10.5, 1.2, 0, 7); }); break;
    case 'server': X.roundRect(-18, -17, 36, 14, 4); X.roundRect(-18, 3, 36, 14, 4); X.stroke(); X.beginPath();
      X.moveTo(10, -10); X.arc(9, -10, 1.6, 0, 7); X.moveTo(10, 10); X.arc(9, 10, 1.6, 0, 7); X.moveTo(-12, -10); X.lineTo(0, -10); X.moveTo(-12, 10); X.lineTo(0, 10); break;
    case 'target': X.arc(0, 0, 17, 0, 7); X.moveTo(9, 0); X.arc(0, 0, 9, 0, 7); X.stroke(); X.beginPath(); X.arc(0, 0, 2.5, 0, 7); X.fill(); break;
    case 'chart': X.moveTo(-17, 17); X.lineTo(17, 17); X.moveTo(-10, 12); X.lineTo(-10, 0); X.moveTo(0, 12); X.lineTo(0, -8); X.moveTo(10, 12); X.lineTo(10, -16); break;
    case 'trend': X.moveTo(-18, 12); X.lineTo(-6, 0); X.lineTo(3, 7); X.lineTo(18, -10); X.moveTo(9, -10); X.lineTo(18, -10); X.lineTo(18, -1); break;
    case 'doc': X.roundRect(-14, -18, 28, 36, 4); X.moveTo(-7, -7); X.lineTo(7, -7); X.moveTo(-7, 1); X.lineTo(7, 1); X.moveTo(-7, 9); X.lineTo(2, 9); break;
    case 'money': X.roundRect(-20, -12, 40, 24, 5); X.moveTo(5, 0); X.arc(0, 0, 5, 0, 7); break;
    case 'cart': X.moveTo(-19, -14); X.lineTo(-13, -14); X.lineTo(-8, 8); X.lineTo(14, 8); X.lineTo(18, -7); X.lineTo(-11, -7); X.stroke(); X.beginPath();
      X.arc(-5, 15, 2.5, 0, 7); X.moveTo(13.5, 15); X.arc(11, 15, 2.5, 0, 7); break;
    case 'check': X.moveTo(-12, 1); X.lineTo(-4, 9); X.lineTo(13, -9); break;
    case 'user': X.arc(0, -7, 8, 0, 7); X.moveTo(-15, 17); X.quadraticCurveTo(0, -2, 15, 17); break;
    case 'signal': [[-14, 6], [-5, -2], [4, -10], [13, -18]].forEach(([x, y]) => { X.moveTo(x, 17); X.lineTo(x, y); }); break;
    case 'shield': X.moveTo(0, -18); X.lineTo(15, -12); X.lineTo(15, 0); X.quadraticCurveTo(14, 13, 0, 19); X.quadraticCurveTo(-14, 13, -15, 0); X.lineTo(-15, -12); X.closePath(); break;
    case 'flow': X.moveTo(-18, 0); X.lineTo(18, 0); X.moveTo(10, -8); X.lineTo(18, 0); X.lineTo(10, 8); break;
    case 'ads': X.moveTo(-16, -6); X.lineTo(-4, -6); X.lineTo(12, -16); X.lineTo(12, 16); X.lineTo(-4, 6); X.lineTo(-16, 6); X.closePath(); X.moveTo(-10, 6); X.lineTo(-6, 17); break;
    case 'stream': X.moveTo(-18, 0); X.bezierCurveTo(-9, -12, -3, -12, 0, 0); X.bezierCurveTo(3, 12, 9, 12, 18, 0); break;
  }
  X.stroke();
  X.restore();
}
function iconBox(x, y, s, name, o = {}) {
  X.save(); X.globalAlpha *= (o.a ?? 1);
  rr(x, y, s, s, s * .28); X.fillStyle = o.fill || teal(.12); X.fill();
  X.strokeStyle = o.stroke || teal(.28); X.lineWidth = 1.5; X.stroke();
  icon(name, x + s / 2, y + s / 2, s * .78, o.col || teal(1), o.lw || 3);
  X.restore();
}
function checkMark(cx, cy, r, p, o = {}) {
  if (p <= 0) return;
  X.save(); X.globalAlpha *= (o.a ?? 1);
  X.beginPath(); X.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * E.oc(clamp(p * 1.6))); X.strokeStyle = o.col || teal(1); X.lineWidth = o.lw || 3; X.stroke();
  X.beginPath(); X.arc(cx, cy, r, 0, 7); X.fillStyle = teal(.14 * clamp(p * 2)); X.fill();
  const q = E.oc(P(p, .35, .65));
  if (q > 0) {
    const pts = [[-r * .42, r * .02], [-r * .12, r * .32], [r * .45, -r * .3]];
    const l1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]), l2 = Math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]);
    X.beginPath(); X.setLineDash([l1 + l2]); X.lineDashOffset = (l1 + l2) * (1 - q);
    X.moveTo(cx + pts[0][0], cy + pts[0][1]); X.lineTo(cx + pts[1][0], cy + pts[1][1]); X.lineTo(cx + pts[2][0], cy + pts[2][1]);
    X.lineWidth = o.lw2 || 4; X.lineCap = 'round'; X.lineJoin = 'round'; X.strokeStyle = o.col || teal(1);
    X.shadowColor = teal(.8); X.shadowBlur = 14; X.stroke();
  }
  X.restore();
}
function packet(x, y, o = {}) {
  X.save(); X.globalAlpha *= (o.a ?? 1);
  const r = o.r || 7;
  if (o.trail) {
    const g = X.createLinearGradient(x - o.trail[0], y - o.trail[1], x, y);
    g.addColorStop(0, teal(0)); g.addColorStop(1, o.grey ? GREY(.4) : teal(.55));
    X.beginPath(); X.moveTo(x - o.trail[0], y - o.trail[1]); X.lineTo(x, y); X.strokeStyle = g; X.lineWidth = r * 1.1; X.lineCap = 'round'; X.stroke();
  }
  X.beginPath(); X.arc(x, y, r, 0, 7);
  X.fillStyle = o.grey ? GREY(.8) : tealB(1);
  if (!o.grey) { X.shadowColor = teal(.9); X.shadowBlur = 18; }
  X.fill(); X.restore();
}
function node(cx, cy, w, h, label, sub, ic, o = {}) {
  const x = cx - w / 2, y = cy - h / 2;
  card(x, y, w, h, { a: o.a ?? 1, glow: o.glow || 0, stroke: o.stroke, r: o.r ?? 24 });
  X.save(); X.globalAlpha *= (o.a ?? 1);
  const s = Math.min(h - 36, 68);
  iconBox(x + 22, cy - s / 2, s, ic);
  text(label, x + 22 + s + 22, cy + (sub ? -4 : 11), { size: o.size || 30, weight: 800, align: 'left', ls: o.ls ?? 1 });
  if (sub) text(sub, x + 22 + s + 22, cy + 28, { size: 19, weight: 500, fam: 'JBM', align: 'left', color: o.subColor || wht(.5) });
  X.restore();
}
function line(x1, y1, x2, y2, o = {}) {
  X.save(); X.globalAlpha *= (o.a ?? 1);
  X.beginPath(); X.moveTo(x1, y1); X.lineTo(lerp(x1, x2, o.p ?? 1), lerp(y1, y2, o.p ?? 1));
  X.strokeStyle = o.col || teal(.35); X.lineWidth = o.lw || 2.5; if (o.dash) X.setLineDash(o.dash);
  X.stroke(); X.restore();
}
function radialFlash(x, y, r, a) {
  if (a <= 0) return;
  const g = X.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, teal(.42 * a)); g.addColorStop(.4, teal(.12 * a)); g.addColorStop(1, teal(0));
  X.fillStyle = g; X.fillRect(x - r, y - r, r * 2, r * 2);
}

// ---------- background ----------
const grid = document.createElement('canvas'); grid.width = W; grid.height = H + 60;
(() => {
  const g = grid.getContext('2d');
  for (let y = 0; y < grid.height; y += 60) for (let x = 30; x < W; x += 60) {
    g.fillStyle = 'rgba(255,255,255,0.055)'; g.fillRect(x - 1, y - 1, 2, 2);
  }
})();
function background(t) {
  X.fillStyle = BG; X.fillRect(0, 0, W, H);
  const gx = 230 + Math.sin(t * .13) * 140, gy = 220 + Math.cos(t * .1) * 90;
  let g = X.createRadialGradient(gx, gy, 0, gx, gy, 1150);
  g.addColorStop(0, 'rgba(20,92,94,0.42)'); g.addColorStop(.45, 'rgba(10,44,48,0.20)'); g.addColorStop(1, 'rgba(4,9,11,0)');
  X.fillStyle = g; X.fillRect(0, 0, W, H);
  const hx = 900 + Math.sin(t * .09 + 2) * 80, hy = 1650;
  g = X.createRadialGradient(hx, hy, 0, hx, hy, 900);
  g.addColorStop(0, 'rgba(25,195,177,0.085)'); g.addColorStop(1, 'rgba(25,195,177,0)');
  X.fillStyle = g; X.fillRect(0, 0, W, H);
  X.drawImage(grid, 0, -((t * 7) % 60));
  for (let i = 0; i < 44; i++) {
    const sp = 8 + hash(i, 3) * 16;
    const x = hash(i) * W + Math.sin(t * .25 + i) * 18;
    const y = ((hash(i, 2) * (H + 100) - t * sp) % (H + 100) + H + 100) % (H + 100) - 50;
    X.beginPath(); X.arc(x, y, 1 + hash(i, 4) * 1.8, 0, 7);
    X.fillStyle = teal(.06 + .14 * hash(i, 5)); X.fill();
  }
  g = X.createRadialGradient(W / 2, H * .45, H * .3, W / 2, H * .5, H * .78);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  X.fillStyle = g; X.fillRect(0, 0, W, H);
}

// ---------- images ----------
const IMG = new Image(); IMG.src = 'assets/portrait.jpg';
window.assetsReady = Promise.all([document.fonts.ready, new Promise(r => { if (IMG.complete) r(); else IMG.onload = r; })]);

// =====================================================================
const S = {};

// ---------------- SCENE 01 — HOOK ----------------
S['01'] = (t, s, c) => {
  eyebrow(t, .35, 'PAID ADS  ·  CONVERSION TRACKING', 300);
  const outA = c.sure - .2;
  kline('Running [Facebook]', 540, 470, { size: 92, weight: 800, out: outA }, c.running, t);
  kline('or [Google Ads?]', 540, 578, { size: 92, weight: 800, out: outA }, c.google - .25, t);
  const sB = fit('Are you missing data?', 800, 88, 940);
  kline('Are you [missing data?]', 540, 530, { size: sB, weight: 800, out: c.actually - .15 }, c.sure + .05, t);

  // dashboard
  const dp = E.oc(P(t, .2, 1.3));
  const uns = P(t, c.lead - .1, .3);
  const jit = uns > 0 ? (hash(Math.floor(t * 20)) - .5) * 5 * uns * (hash(Math.floor(t * 7), 4) > .55 ? 1 : 0) : 0;
  const dim = 1 - .5 * E.oc(P(t, c.actually, .5));
  X.save(); X.globalAlpha *= dp * dim; X.translate(jit, (1 - dp) * 80);
  const cy0 = 680;
  card(90, cy0, 900, 650);
  text('Campaign Signals', 140, cy0 + 72, { size: 36, weight: 800, align: 'left', ls: -.5 });
  const blink = .55 + .45 * Math.sin(t * 6);
  const stw = measure(uns > .5 ? 'UNSTABLE' : 'LIVE', 20, 700, 'JBM', 2);
  X.beginPath(); X.arc(940 - stw - 18, cy0 + 61, 7, 0, 7); X.fillStyle = uns > .5 ? GREY(.9) : teal(blink); X.fill();
  text(uns > .5 ? 'UNSTABLE' : 'LIVE', 940, cy0 + 69, { size: 20, weight: 700, fam: 'JBM', align: 'right', color: uns > .5 ? GREY(1) : teal(1), ls: 2 });
  // source chips (conceptual, no platform UI)
  X.save(); X.translate(0, 0);
  const w1 = measure('Meta Ads', 19, 700, 'JBM', 1) + 44;
  pill(140 + w1 / 2, cy0 + 122, 'Meta Ads', { size: 19, fill: 'rgba(255,255,255,0.04)', stroke: 'rgba(255,255,255,0.12)', color: wht(.8) });
  const w2 = measure('Google Ads', 19, 700, 'JBM', 1) + 44;
  pill(140 + w1 + 14 + w2 / 2, cy0 + 122, 'Google Ads', { size: 19, fill: 'rgba(255,255,255,0.04)', stroke: 'rgba(255,255,255,0.12)', color: wht(.8) });
  X.restore();
  // chart
  const chx = 140, chy = cy0 + 170, chw = 800, chh = 170;
  for (let i = 0; i <= 3; i++) line(chx, chy + chh * i / 3, chx + chw, chy + chh * i / 3, { col: 'rgba(255,255,255,0.05)', lw: 1 });
  const n = 30, cp = E.io(P(t, .5, 2.4));
  const pts = [];
  for (let i = 0; i < n; i++) {
    const v = .18 + .62 * Math.pow(i / (n - 1), 1.15) + .06 * Math.sin(i * 1.7) + .03 * Math.sin(i * 3.1 + t * 2);
    pts.push([chx + chw * i / (n - 1), chy + chh * (1 - v)]);
  }
  const shown = Math.max(2, Math.floor(cp * n));
  // area
  X.beginPath(); X.moveTo(pts[0][0], chy + chh);
  for (let i = 0; i < shown; i++) X.lineTo(pts[i][0], pts[i][1]);
  X.lineTo(pts[shown - 1][0], chy + chh); X.closePath();
  const ag = X.createLinearGradient(0, chy, 0, chy + chh); ag.addColorStop(0, teal(.22)); ag.addColorStop(1, teal(0));
  X.fillStyle = ag; X.fill();
  for (let i = 1; i < shown; i++) {
    const broken = uns > 0 && i > 15 && hash(i, 9) < .55 * uns;
    if (broken && hash(Math.floor(t * 12), i) < .5) continue;
    X.beginPath(); X.moveTo(pts[i - 1][0], pts[i - 1][1]); X.lineTo(pts[i][0], pts[i][1]);
    X.strokeStyle = (uns > 0 && i > 15) ? GREY(.55 + .45 * (1 - uns)) : tealB(1); X.lineWidth = 3.5;
    if (!(uns > 0 && i > 15)) { X.shadowColor = teal(.7); X.shadowBlur = 10; }
    X.stroke(); X.shadowBlur = 0;
  }
  // event rows
  const rows = [['LEAD', 'Meta Ads', 'user', c.lead], ['PURCHASE', 'Google Ads', 'cart', c.purchase], ['CONVERSION', 'Meta Ads', 'target', c.actually]];
  rows.forEach(([lab, src, ic, tf], i) => {
    const ta = ct(s, .95 + i * .6), y = cy0 + 380 + i * 88;
    const rp = E.oc(P(t, ta, .45)); if (rp <= 0) return;
    const fp = P(t, tf, .3);
    let a = rp;
    if (t > tf && t < tf + .45) a *= hash(Math.floor(t * 30), i) > .45 ? 1 : .2;
    X.save(); X.globalAlpha *= a; X.translate((1 - rp) * 40, 0);
    rr(130, y, 820, 74, 18); X.fillStyle = 'rgba(255,255,255,0.03)'; X.fill(); X.strokeStyle = 'rgba(255,255,255,0.06)'; X.lineWidth = 1.2; X.stroke();
    iconBox(146, y + 11, 52, ic, { a: 1 - .6 * fp, col: fp > .5 ? GREY(1) : teal(1), fill: fp > .5 ? 'rgba(255,255,255,0.04)' : teal(.12), stroke: fp > .5 ? GREY(.3) : teal(.28) });
    text(lab, 220, y + 36, { size: 28, weight: 800, align: 'left', ls: 1.5, a: 1 - .55 * fp });
    text(fp > .5 ? `${src} · signal lost` : `${src} · received`, 220, y + 60, { size: 17, weight: 500, fam: 'JBM', align: 'left', color: fp > .5 ? GREY(.9) : wht(.45) });
    if (fp < 1) checkMark(905, y + 37, 20, P(t, ta + .1, .45), { a: 1 - fp });
    if (fp > 0) {
      X.save(); X.globalAlpha *= fp; X.beginPath(); X.setLineDash([5, 6]); X.arc(905, y + 37, 20, 0, 7); X.strokeStyle = GREY(.8); X.lineWidth = 2.5; X.stroke(); X.restore();
      text('?', 905, y + 46, { size: 24, weight: 800, color: GREY(1), a: fp });
    }
    X.restore();
  });
  X.restore();

  // ARE YOU SURE?
  if (t > c.actually - .05) {
    const p = E.ox(P(t, c.actually, .55));
    const sz = fit('ARE YOU SURE?', 900, 132, 960);
    X.save(); X.globalAlpha *= clamp(p * 1.4);
    const sc = 1.22 - .22 * p; X.translate(540, 1000); X.scale(sc, sc);
    X.fillStyle = 'rgba(4,9,11,0.55)'; X.fillRect(-540, -150, 1080, 230);
    text('ARE YOU', 0, -40, { size: sz, weight: 900, ls: -1 });
    text('SURE?', 0, sz * .95 - 40, { size: sz, weight: 900, ls: -1, color: teal(1), glow: 40 });
    X.restore();
  }
};

// ---------------- SCENE 02 — PROBLEM ----------------
const S2 = { nodeY: [520, 880, 1240], pipeTop: 580, pipeBot: 1180, spawn: .17, travel: 1.75 };
S['02'] = (t, s, c) => {
  const aout = c.ios - .6;
  kline('Often,', 540, 860, { size: 140, weight: 900, out: aout, ls: -2 }, c.often - .08, t);
  kline("they're [not.]", 540, 1010, { size: 140, weight: 900, out: aout, ls: -2 }, c.often + .3, t);
  if (t < aout + .05) return;
  eyebrow(t, aout + .1, 'WHERE CONVERSION DATA GETS LOST', 300);
  const T0 = aout + .25;
  const L = S2.pipeBot - S2.pipeTop;
  const obs = [
    { lab: 'iOS PRIVACY', y: 680, side: -1, t: c.ios },
    { lab: 'AD BLOCKERS', y: 770, side: 1, t: c.adblock },
    { lab: 'BROWSER RESTRICTIONS', y: 1040, side: -1, t: c.browser },
    { lab: 'TRACKING ISSUES', y: 1130, side: 1, t: c.issues },
  ];
  const lossFocus = P(t, c.lost - .75, .25);
  const pa = E.oc(P(t, aout + .15, .6)) * (1 - .6 * lossFocus);
  X.save(); X.globalAlpha *= pa;
  // pipe
  line(540, S2.pipeTop, 540, S2.pipeBot, { col: teal(.22), lw: 3, p: E.io(P(t, aout + .2, .8)) });
  // packets
  let sent = 0, recv = 0, lost = 0;
  const kmax = Math.floor((t - T0) / S2.spawn);
  for (let k = 0; k <= kmax; k++) {
    const ts = T0 + k * S2.spawn; const age = t - ts; if (age < 0) continue;
    sent++;
    let deathT = null, deathSide = 1;
    for (let j = 0; j < obs.length; j++) {
      const tr = ts + (obs[j].y - S2.pipeTop) / L * S2.travel;
      if (tr >= obs[j].t + .25 && hash(k, j + 1) < .16) { deathT = tr; deathSide = obs[j].side; break; }
    }
    const y = S2.pipeTop + age / S2.travel * L;
    if (deathT !== null && t >= deathT) {
      lost++;
      const q = (t - deathT) / .6;
      if (q < 1) {
        const dy = S2.pipeTop + (deathT - ts) / S2.travel * L;
        packet(540 + deathSide * 70 * E.oc(q), dy + 20 * q, { grey: true, a: 1 - q, r: 7 });
        X.save(); X.globalAlpha *= (1 - q) * .6; X.beginPath(); X.arc(540, dy, 8 + 30 * q, 0, 7); X.strokeStyle = GREY(.7); X.lineWidth = 2; X.stroke(); X.restore();
      }
      continue;
    }
    if (age >= S2.travel) { recv++; continue; }
    packet(540, y, { trail: [0, 46] });
  }
  // nodes
  const labels = [['WEBSITE', 'Conversion happens', 'globe'], ['BROWSER', 'Pixel / tag fires', 'browser'], ['AD PLATFORM', 'Receives the signal', 'ads']];
  labels.forEach(([l, sb, ic], i) => {
    const p = E.oc(P(t, aout + .15 + i * .15, .55));
    X.save(); X.globalAlpha *= p; X.translate(0, (1 - p) * 30);
    node(540, S2.nodeY[i], 470, 120, l, sb, ic);
    X.restore();
  });
  // obstacles
  obs.forEach((o, j) => {
    const p = E.oq(P(t, o.t - .05, .5)); if (p <= 0) return;
    const tw = measure(o.lab, 22, 800, 'Inter', 2);
    const w = tw + 92, h = 54;
    const edge = 540 + o.side * 62;
    const x = o.side > 0 ? edge : edge - w;
    X.save(); X.globalAlpha *= p; X.translate(o.side * (1 - p) * 70, 0);
    line(540, o.y, edge, o.y, { col: wht(.35), lw: 2, dash: [4, 5] });
    X.beginPath(); X.moveTo(540 - 11, o.y - 11); X.lineTo(540 + 11, o.y + 11); X.moveTo(540 + 11, o.y - 11); X.lineTo(540 - 11, o.y + 11);
    X.strokeStyle = wht(.85); X.lineWidth = 3; X.lineCap = 'round'; X.stroke();
    rr(x, o.y - h / 2, w, h, 14); X.fillStyle = 'rgba(16,24,27,0.95)'; X.fill(); X.strokeStyle = wht(.18); X.lineWidth = 1.5; X.stroke();
    // warning glyph
    const gx = x + 30, gy = o.y;
    X.beginPath(); X.moveTo(gx, gy - 11); X.lineTo(gx + 11, gy + 9); X.lineTo(gx - 11, gy + 9); X.closePath(); X.strokeStyle = wht(.75); X.lineWidth = 2; X.stroke();
    text('!', gx, gy + 6, { size: 14, weight: 900, color: wht(.85) });
    text(o.lab, x + 56, o.y + 8, { size: 22, weight: 800, ls: 2, align: 'left', color: wht(.92) });
    X.restore();
  });
  // counter
  const cpb = E.oc(P(t, c.ios - .1, .6));
  if (cpb > 0) {
    X.save(); X.globalAlpha *= cpb; X.translate(0, (1 - cpb) * 30);
    card(90, 1360, 900, 140, { r: 24 });
    const cols = [['EVENTS SENT', sent, wht(1)], ['RECEIVED', recv, teal(1)], ['LOST', lost, GREY(1)]];
    cols.forEach(([l, v, col], i) => {
      const x = 90 + 150 + i * 300;
      text(l, x, 1410, { size: 18, weight: 700, fam: 'JBM', ls: 2, color: wht(.45) });
      text(String(v), x, 1468, { size: 50, weight: 800, color: col, ls: -1, glow: i === 1 ? 18 : 0 });
    });
    line(390, 1385, 390, 1475, { col: 'rgba(255,255,255,0.07)', lw: 1.5 });
    line(690, 1385, 690, 1475, { col: 'rgba(255,255,255,0.07)', lw: 1.5 });
    X.restore();
  }
  X.restore();
  // DATA LOSS
  if (lossFocus > 0) {
    const p = E.ox(P(t, c.lost - .75, .5));
    const g = t - (c.lost - .75) < .16;
    X.save(); X.globalAlpha *= clamp(p * 1.5);
    X.fillStyle = 'rgba(4,9,11,0.72)'; X.fillRect(0, 760, W, 300);
    line(0, 760, W, 760, { col: 'rgba(255,255,255,0.08)', lw: 1.5 }); line(0, 1060, W, 1060, { col: 'rgba(255,255,255,0.08)', lw: 1.5 });
    const sc = 1.15 - .15 * p; X.translate(540, 960); X.scale(sc, sc);
    const sz = fit('DATA LOSS', 900, 170, 940);
    if (g) {
      for (let i = 0; i < 5; i++) {
        X.save(); X.beginPath(); X.rect(-540, -150 + i * 44, 1080, 44); X.clip();
        text('DATA LOSS', (hash(i, Math.floor(t * 40)) - .5) * 40, 58, { size: sz, weight: 900, ls: -2 }); X.restore();
      }
    } else text('DATA LOSS', 0, 58, { size: sz, weight: 900, ls: -2 });
    X.restore();
  }
};

// ---------------- SCENE 03 — WHY IT MATTERS ----------------
S['03'] = (t, s, c) => {
  eyebrow(t, s.vs + .2, 'WHY IT MATTERS', 300);
  const cp = E.oc(P(t, s.vs + .1, .7));
  const x0 = 90, y0 = 380, w0 = 900, h0 = 640;
  X.save(); X.globalAlpha *= cp; X.translate(0, (1 - cp) * 50);
  card(x0, y0, w0, h0);
  const wv = E.io(P(t, c.wasted - .1, .6));
  text(wv < .5 ? 'Campaign Optimization' : 'Budget vs. Signal', 140, y0 + 72, { size: 34, weight: 800, align: 'left', ls: -.5, a: wv < .5 ? 1 - wv * 2 : (wv - .5) * 2 });
  const bad = P(t, c.platforms + .4, .3);
  if (bad < 1) pill(860, y0 + 60, 'GOOD DATA', { size: 18, a: 1 - bad, dot: true });
  if (bad > 0) pill(845, y0 + 60, 'SIGNAL LOSS', { size: 18, a: bad, dot: true, color: GREY(1), stroke: GREY(.4), fill: 'rgba(255,255,255,0.04)', dotColor: GREY(1) });
  // signal quality
  const dq = E.io(P(t, c.platforms + .2, 2.2));
  const q = lerp(.94, .46, dq);
  text('SIGNAL QUALITY', 140, y0 + 140, { size: 18, weight: 700, fam: 'JBM', ls: 2, align: 'left', color: wht(.45) });
  text(Math.round(q * 100) + '%', 940, y0 + 140, { size: 22, weight: 700, fam: 'JBM', align: 'right', color: dq > .3 ? GREY(1) : teal(1) });
  rr(140, y0 + 158, 800, 10, 5); X.fillStyle = 'rgba(255,255,255,0.06)'; X.fill();
  rr(140, y0 + 158, 800 * q, 10, 5); X.fillStyle = dq > .3 ? GREY(.8) : teal(1); X.fill();
  // chart area
  const ax = 140, ay = y0 + 210, aw = 800, ah = 370;
  X.save(); X.globalAlpha *= 1 - wv;
  const nb = 8, bw = 64, gap = (aw - nb * bw) / (nb - 1);
  const tops = [];
  for (let i = 0; i < nb; i++) {
    const grow = E.oc(P(t, s.vs + .2 + i * .05, .7));
    const hh = (.32 + .58 * Math.pow(i / (nb - 1), .9)) * ah * grow;
    const lostF = dq * (.22 + .5 * hash(i, 3)) * (i >= 2 ? 1 : .35);
    const bx = ax + i * (bw + gap), by = ay + ah - hh;
    const solid = hh * (1 - lostF);
    rr(bx, ay + ah - solid, bw, solid, 8); X.fillStyle = teal(.85); X.fill();
    if (lostF > 0) { X.save(); rr(bx + 1, by, bw - 2, hh - solid, 8); X.setLineDash([6, 6]); X.strokeStyle = GREY(.6 * lostF / .7 + .1); X.lineWidth = 2; X.stroke(); X.restore(); }
    tops.push([bx + bw / 2, by - 40]);
  }
  // optimization line
  const fl = E.io(P(t, c.campaign, 1.2));
  const op = E.oc(P(t, s.vs + .6, 1.0));
  X.beginPath();
  tops.forEach(([x, y], i) => {
    const flat = ay + ah * .55 + Math.sin(i * 1.9 + t * 2.2) * 26;
    const yy = lerp(y, flat, fl);
    if (i === 0) X.moveTo(x, yy); else X.lineTo(x, yy);
  });
  X.setLineDash([2000]); X.lineDashOffset = 2000 * (1 - op);
  X.strokeStyle = fl > .3 ? wht(.7) : wht(.95); X.lineWidth = 3.5; X.stroke(); X.setLineDash([]);
  text(fl > .4 ? 'OPTIMIZATION: LIMITED' : 'OPTIMIZATION', 940, ay + 10, { size: 17, weight: 700, fam: 'JBM', ls: 2, align: 'right', color: fl > .4 ? GREY(1) : wht(.6), a: op });
  X.restore();
  // budget vs signal viz
  if (wv > 0) {
    X.save(); X.globalAlpha *= wv;
    for (let i = 0; i <= 4; i++) line(ax, ay + ah * i / 4, ax + aw, ay + ah * i / 4, { col: 'rgba(255,255,255,0.05)', lw: 1 });
    const dp = E.io(P(t, c.wasted, 1.3));
    const N = 40, sp = [], cv2 = [];
    for (let i = 0; i < N; i++) {
      const u = i / (N - 1);
      sp.push([ax + aw * u, ay + ah - ah * .9 * u]);
      cv2.push([ax + aw * u, ay + ah - ah * .9 * (u < .3 ? u : .3 + (u - .3) * .12) + Math.sin(u * 14) * 6 * u]);
    }
    const m = Math.max(2, Math.floor(dp * N));
    X.beginPath(); X.moveTo(sp[0][0], sp[0][1]);
    for (let i = 0; i < m; i++) X.lineTo(sp[i][0], sp[i][1]);
    for (let i = m - 1; i >= 0; i--) X.lineTo(cv2[i][0], cv2[i][1]);
    X.closePath(); X.fillStyle = 'rgba(255,255,255,0.055)'; X.fill();
    const stroke = (arr, col, glow) => { X.beginPath(); for (let i = 0; i < m; i++) i ? X.lineTo(arr[i][0], arr[i][1]) : X.moveTo(arr[i][0], arr[i][1]); X.strokeStyle = col; X.lineWidth = 4; if (glow) { X.shadowColor = teal(.7); X.shadowBlur = 12; } X.stroke(); X.shadowBlur = 0; };
    stroke(sp, wht(.9)); stroke(cv2, tealB(1), true);
    if (dp > .6) {
      const a = P(dp, .6, .4);
      text('AD SPEND', 940, sp[N - 1][1] - 18, { size: 18, weight: 700, fam: 'JBM', ls: 2, align: 'right', a });
      text('CONVERSION SIGNAL', 940, cv2[N - 1][1] + 40, { size: 18, weight: 700, fam: 'JBM', ls: 2, align: 'right', color: teal(1), a });
      text('SPEND WITHOUT SIGNAL', ax + aw * .72, ay + ah * .52, { size: 17, weight: 700, fam: 'JBM', ls: 2, color: wht(.5), a });
    }
    X.restore();
  }
  X.restore();
  // statements
  const st = [['INACCURATE REPORTING', c.inaccurate, 'doc'], ['WEAKER OPTIMIZATION', c.weaker, 'trend'], ['WASTED AD SPEND', c.wasted, 'money']];
  st.forEach(([lab, ts, ic], i) => {
    const p = E.oq(P(t, ts - .05, .5)); if (p <= 0) return;
    const y = 1075 + i * 132;
    const active = i === 2 ? 1 : 1 - P(t, st[i + 1][1], .3);
    X.save();
    X.beginPath(); X.rect(80, y - 10, 920 * p, 130); X.clip();
    X.globalAlpha *= .55 + .45 * active;
    card(90, y, 900, 112, { r: 22, stroke: active > .5 ? teal(.45) : undefined, glow: active * .4 });
    iconBox(116, y + 24, 64, ic);
    const sz = fit(lab, 900, 46, 640, 'Inter', -.5);
    text(lab, 206, y + 72, { size: sz, weight: 900, align: 'left', ls: -.5, color: i === 2 ? teal(1) : wht(1), glow: i === 2 ? 22 : 0 });
    text('0' + (i + 1), 955, y + 66, { size: 20, weight: 700, fam: 'JBM', align: 'right', color: wht(.3) });
    X.restore();
  });
};

// ---------------- shared: server node ----------------
function serverNode(cx, cy, w, h, t, o = {}) {
  const pulse = o.pulse || 0;
  if (pulse > 0) {
    for (let r = 0; r < 2; r++) {
      const q = ((t * .7 + r * .5) % 1);
      X.save(); X.globalAlpha *= pulse * (1 - q) * .55;
      rr(cx - w / 2 - q * 60, cy - h / 2 - q * 60, w + q * 120, h + q * 120, 30 + q * 40);
      X.strokeStyle = teal(.8); X.lineWidth = 2; X.stroke(); X.restore();
    }
  }
  card(cx - w / 2, cy - h / 2, w, h, { glow: .6 + .6 * pulse, stroke: teal(.55), r: 30, a: o.a ?? 1 });
  X.save(); X.globalAlpha *= (o.a ?? 1);
  const s = Math.min(h - 50, 96);
  iconBox(cx - w / 2 + 30, cy - s / 2, s, 'server', { fill: teal(.16), stroke: teal(.5), lw: 3.2 });
  text('SERVER', cx - w / 2 + 30 + s + 26, cy + (o.sub ? -6 : 14), { size: o.size || 42, weight: 900, align: 'left', ls: 2 });
  if (o.sub) text(o.sub, cx - w / 2 + 30 + s + 26, cy + 30, { size: 19, weight: 500, fam: 'JBM', align: 'left', color: teal(.85) });
  X.restore();
}

// ---------------- SCENE 04 — SOLUTION ----------------
S['04'] = (t, s, c) => {
  const ts = c.server - .32;
  const lp = E.io(P(t, s.vs + .15, .7)) * (1 - E.io(P(t, ts, .3)));
  if (lp > 0) line(540 - 160 * lp, 960, 540 + 160 * lp, 960, { col: teal(.7 * lp), lw: 2 });
  const push = 1 + .055 * E.sine(P(t, ts, 3.0));
  X.save(); X.translate(540, 960); X.scale(push, push); X.translate(-540, -960);
  const fl = P(t, c.server, 1.1);
  if (fl > 0 && fl < 1) {
    radialFlash(540, 660, 760, 1 - fl);
    X.save(); X.globalAlpha *= (1 - fl) * .6; X.beginPath(); X.arc(540, 660, 120 + E.oc(fl) * 760, 0, 7); X.strokeStyle = teal(.8); X.lineWidth = 2.5; X.stroke(); X.restore();
  }
  const sz = fit('SERVER-SIDE', 900, 150, 960, 'Inter', -3);
  kline('SERVER-SIDE', 540, 640, { size: sz, weight: 900, ls: -3, stagger: 0, dur: .6, wglow: 0 }, ts, t);
  kline('[TRACKING]', 540, 640 + sz * 1.02, { size: sz, weight: 900, ls: -3, dur: .6, glow: 40 }, ts + .12, t);
  // architecture
  const y1 = 1020, y2 = 1230, y3 = 1440;
  const a1 = E.oc(P(t, c.server + .2, .5)), a2 = E.oc(P(t, c.server + .4, .55)), a3 = E.oc(P(t, c.server + .6, .5));
  line(540, y1 + 55, 540, y2 - 80, { p: E.io(P(t, c.server + .4, .4)), col: teal(.4), lw: 3 });
  line(540, y2 + 80, 540, y3 - 55, { p: E.io(P(t, c.server + .6, .4)), col: teal(.4), lw: 3 });
  for (let k = 0; k < 8; k++) {
    const tk = c.server + .9 + k * .28; const q = (t - tk) / 1.1; if (q < 0 || q > 1) continue;
    const yy = lerp(y1 + 55, y3 - 55, q); if (yy > y2 - 80 && yy < y2 + 80) continue;
    packet(540, yy, { trail: [0, 36], r: 6 });
  }
  X.save(); X.globalAlpha *= a1; X.translate(0, (1 - a1) * 30); node(540, y1, 420, 110, 'BROWSER', null, 'browser'); X.restore();
  X.save(); X.globalAlpha *= a2; const sc2 = .9 + .1 * E.ob(P(t, c.server + .4, .6)); X.translate(540, y2); X.scale(sc2, sc2); X.translate(-540, -y2);
  serverNode(540, y2, 520, 160, t, { pulse: P(t, c.server + .8, .6), sub: 'Your tracking layer' }); X.restore();
  X.save(); X.globalAlpha *= a3; X.translate(0, (1 - a3) * 30); node(540, y3, 420, 110, 'AD PLATFORMS', null, 'ads'); X.restore();
  X.restore();
};

// ---------------- SCENE 05 — HOW IT WORKS ----------------
S['05'] = (t, s, c) => {
  eyebrow(t, s.vs + .15, 'HOW IT WORKS', 300);
  const yW = 470, yB = 640, yS = 880, yP = 1240;
  const ap = i => E.oc(P(t, s.vs + .1 + i * .12, .5));
  // connectors
  line(540, yW + 50, 540, yB - 50, { col: teal(.35), lw: 3, a: ap(1) });
  line(540, yB + 50, 540, yS - 95, { col: teal(.35), lw: 3, a: ap(2) });
  const outs = [225, 540, 855];
  const dl = E.io(P(t, c.sent - .1, .7));
  const bez = (i, u) => {
    const x0 = 540, y0 = yS + 95, x3 = outs[i], y3 = yP - 75;
    const x1 = 540, y1 = y0 + 120, x2 = x3, y2 = y3 - 120;
    const m = 1 - u;
    return [m * m * m * x0 + 3 * m * m * u * x1 + 3 * m * u * u * x2 + u * u * u * x3, m * m * m * y0 + 3 * m * m * u * y1 + 3 * m * u * u * y2 + u * u * u * y3];
  };
  if (dl > 0) outs.forEach((_, i) => {
    X.beginPath();
    for (let k = 0; k <= 30; k++) { const [x, y] = bez(i, k / 30 * dl); k ? X.lineTo(x, y) : X.moveTo(x, y); }
    X.strokeStyle = teal(.4); X.lineWidth = 3; X.stroke();
  });
  // outbound packets
  if (t > c.sent + .5) for (let k = 0; k < 40; k++) {
    for (let i = 0; i < 3; i++) {
      const tk = c.sent + .5 + k * .33 + i * .11; const q = (t - tk) / .9; if (q < 0 || q > 1) continue;
      const [x, y] = bez(i, E.sine(q)); packet(x, y, { r: 6 });
    }
  }
  // nodes
  X.save(); X.globalAlpha *= ap(0); node(540, yW, 430, 100, 'WEBSITE', null, 'globe', { size: 28 }); X.restore();
  X.save(); X.globalAlpha *= ap(1); node(540, yB, 430, 100, 'BROWSER', null, 'browser', { size: 28 }); X.restore();
  // server
  const proc = P(t, c.processed, .4);
  const pulse = Math.max(proc * .6, 1 - P(t, c.server, .9));
  X.save(); X.globalAlpha *= ap(2);
  serverNode(540, yS, 620, 190, t, { pulse: t > c.server ? 1 : proc * .5, sub: proc > .5 ? 'Processing events' : 'Processing layer', size: 46 });
  // processing log lines inside server (right side)
  if (proc > 0) {
    const logs = ['validate', 'enrich', 'deduplicate', 'forward'];
    const step = Math.floor((t - c.processed) / .45);
    for (let j = 0; j < 3; j++) {
      const idx = step - 2 + j; if (idx < 0) continue;
      const yy = yS - 48 + j * 38;
      text('› ' + logs[idx % 4], 668, yy + 6, { size: 17, weight: 500, fam: 'JBM', align: 'left', color: wht(.35 + .2 * j), a: proc });
    }
    // spinner
    X.save(); X.globalAlpha *= proc; X.beginPath(); X.arc(540 - 310 + 30 + 48, yS, 60, t * 4, t * 4 + 1.6); X.strokeStyle = tealB(.9); X.lineWidth = 3; X.stroke(); X.restore();
  }
  X.restore();
  // event lane (right of nodes, into server)
  line(880, yW - 20, 880, yS - 150, { col: teal(.18), lw: 2, dash: [3, 8], a: ap(1) });
  // inbound event chips
  const names = ['LEAD', 'PURCHASE', 'SIGNUP', 'FORM SUBMIT'];
  for (let k = 0; k < 16; k++) {
    const tk = c.conversion - .1 + k * .5; const q = (t - tk) / 1.25; if (q < 0 || q > 1 || tk > c.tiktok + .3) continue;
    const y = lerp(yW + 10, yS - 60, E.sine(q));
    const a = clamp(q * 5) * (1 - P(q, .82, .18));
    const cx = lerp(880, 700, E.io(P(q, .62, .38)));
    pill(cx, y, names[k % 4], { size: 19, a, fill: 'rgba(8,30,32,0.95)', stroke: teal(.7) });
  }
  // platforms
  const plats = [['Google', c.google], ['Meta', c.meta], ['TikTok', c.tiktok]];
  plats.forEach(([nm, tp], i) => {
    const a = E.oc(P(t, c.sent - .1 + i * .1, .5)); if (a <= 0) return;
    const on = E.oc(P(t, tp - .05, .45));
    const cx = outs[i], w = 290, h = 150;
    X.save(); X.globalAlpha *= a * (.55 + .45 * on); X.translate(0, (1 - a) * 30);
    card(cx - w / 2, yP - h / 2, w, h, { glow: on * .7, stroke: on > .3 ? teal(.5) : undefined, r: 26 });
    iconBox(cx - w / 2 + 22, yP - 46, 56, 'target');
    text(nm, cx - w / 2 + 96, yP - 6, { size: 34, weight: 800, align: 'left', ls: -.5 });
    text(on > .5 ? 'received' : 'waiting', cx - w / 2 + 96, yP + 24, { size: 17, fam: 'JBM', weight: 500, align: 'left', color: on > .5 ? teal(1) : wht(.4) });
    checkMark(cx + w / 2 - 34, yP - h / 2 + 34, 16, P(t, tp, .45), { lw: 2.5, lw2: 3 });
    X.restore();
  });
  // caption
  const capY = 1480;
  kline('Processed through [a server] first', 540, capY, { size: 44, weight: 800, out: c.sent - .2, ls: -.5 }, c.processed - .1, t);
  kline('then sent to [your ad platforms]', 540, capY, { size: 44, weight: 800, ls: -.5 }, c.sent + .1, t);
};

// ---------------- SCENE 06 — BENEFITS ----------------
S['06'] = (t, s, c) => {
  eyebrow(t, s.vs + .1, 'THE RESULT', 300);
  kline('The [result]', 540, 430, { size: 82, weight: 900, ls: -2 }, c.result - .05, t);
  const items = [
    ['MORE RELIABLE TRACKING', 'Stable, consistent data stream', c.reliable, 'stream'],
    ['LESS DATA LOSS', 'More events reach their destination', c.less, 'shield'],
    ['BETTER SIGNALS', 'Stronger signals for your campaigns', c.better, 'signal'],
  ];
  items.forEach(([title, sub, ti, ic], i) => {
    const p = E.oq(P(t, ti - .08, .6)); if (p <= 0) return;
    const y = 510 + i * 335, h = 305;
    const nextT = items[i + 1] ? items[i + 1][2] : 1e9;
    const dim = 1 - .4 * P(t, nextT - .05, .4);
    X.save(); X.globalAlpha *= p * dim;
    const sc = .94 + .06 * p; X.translate(540 + (1 - p) * 90, y + h / 2); X.scale(sc, sc); X.translate(-540, -(y + h / 2));
    card(90, y, 900, h, { glow: (1 - P(t, nextT, .4)) * .55, stroke: dim > .8 ? teal(.42) : undefined });
    iconBox(122, y + 32, 72, ic);
    const sz = fit(title, 900, 50, 640, 'Inter', -1);
    text(title, 218, y + 80, { size: sz, weight: 900, align: 'left', ls: -1 });
    text(sub, 220, y + 116, { size: 20, weight: 500, fam: 'JBM', align: 'left', color: wht(.5) });
    checkMark(935, y + 68, 24, P(t, ti + .05, .5));
    const vx = 130, vy = y + 160, vw = 820, vh = 110;
    rr(vx, vy, vw, vh, 18); X.fillStyle = 'rgba(255,255,255,0.025)'; X.fill(); X.strokeStyle = 'rgba(255,255,255,0.05)'; X.lineWidth = 1; X.stroke();
    const lt = t - ti;
    if (i === 0) { // stable stream
      X.save(); X.beginPath(); X.rect(vx, vy, vw, vh); X.clip();
      X.beginPath();
      for (let x = 0; x <= vw; x += 8) { const yy = vy + vh / 2 + Math.sin(x / 60 - lt * 3) * 14; x ? X.lineTo(vx + x, yy) : X.moveTo(vx + x, yy); }
      X.strokeStyle = teal(.35); X.lineWidth = 2.5; X.stroke();
      for (let k = 0; k < 12; k++) {
        const x = ((k * 80 + lt * 200) % (vw + 80)) - 40;
        packet(vx + x, vy + vh / 2 + Math.sin(x / 60 - lt * 3) * 14, { r: 7, a: clamp(lt * 3) });
      }
      X.restore();
    } else if (i === 1) { // dots reaching destination
      const n = 14;
      for (let k = 0; k < n; k++) {
        const x = vx + 50 + k * (vw - 180) / (n - 1), yy = vy + vh / 2;
        const f = E.ob(P(lt, .1 + k * .07, .3));
        const reached = k !== 9;
        X.beginPath(); X.arc(x, yy, 13, 0, 7); X.strokeStyle = 'rgba(255,255,255,0.12)'; X.lineWidth = 2; X.stroke();
        if (reached && f > 0) { X.save(); X.beginPath(); X.arc(x, yy, 13 * f, 0, 7); X.fillStyle = tealB(1); X.shadowColor = teal(.8); X.shadowBlur = 14; X.fill(); X.restore(); }
      }
      icon('flow', vx + vw - 70, vy + vh / 2, 50, teal(1), 3);
    } else { // signal bars
      const n = 7;
      for (let k = 0; k < n; k++) {
        const f = E.ob(P(lt, .05 + k * .08, .45));
        const bh = (22 + k * 11) * f, x = vx + 60 + k * 62;
        rr(x, vy + vh - 18 - bh, 40, bh, 8); X.fillStyle = teal(.5 + .5 * k / n); X.fill();
      }
      icon('flow', vx + 540, vy + vh / 2, 50, teal(1), 3);
      text('AD PLATFORMS', vx + 590, vy + vh / 2 + 8, { size: 20, weight: 700, fam: 'JBM', ls: 2, align: 'left', color: wht(.8), a: P(lt, .5, .4) });
    }
    X.restore();
  });
};

// ---------------- SCENE 07 — PERSONAL INTRODUCTION ----------------
function drawPortrait(x, y, w, h, z, reveal, t) {
  if (reveal <= 0) return;
  X.save();
  // glow + frame behind
  X.save(); X.shadowColor = teal(.35); X.shadowBlur = 90; rr(x, y, w, h, 34); X.fillStyle = '#0a1518'; X.fill(); X.restore();
  X.beginPath(); X.roundRect(x, y + h * (1 - reveal), w, h * reveal, 34); X.clip();
  // source crop keeps aspect; image itself untouched (no face edits)
  const sw = 800 * (w / h), sh = 800;
  const sx = (800 - sw) / 2;
  X.translate(x + w / 2, y + h / 2 + (1 - reveal) * 40); X.scale(z, z);
  X.drawImage(IMG, sx, 0, sw, sh, -w / 2, -h / 2, w, h);
  X.setTransform(1, 0, 0, 1, 0, 0);
  X.restore();
  X.save(); X.globalAlpha *= reveal;
  // blend portrait background into the dark brand world (edges only)
  X.beginPath(); X.roundRect(x, y, w, h, 34); X.clip();
  let g = X.createLinearGradient(0, y + h * .62, 0, y + h);
  g.addColorStop(0, 'rgba(4,9,11,0)'); g.addColorStop(1, 'rgba(4,9,11,0.92)');
  X.fillStyle = g; X.fillRect(x, y, w, h);
  g = X.createLinearGradient(0, y, 0, y + h * .3);
  g.addColorStop(0, 'rgba(4,20,24,0.35)'); g.addColorStop(1, 'rgba(4,20,24,0)');
  X.fillStyle = g; X.fillRect(x, y, w, h);
  X.restore();
  X.save(); X.globalAlpha *= reveal; rr(x, y, w, h, 34); X.strokeStyle = teal(.45); X.lineWidth = 2; X.stroke(); X.restore();
}
S['07'] = (t, s, c) => {
  // subtle infrastructure behind portrait
  const bgA = E.oc(P(t, s.vs + .2, 1.2)) * .5;
  X.save(); X.globalAlpha *= bgA;
  const side = [[110, 420, 'WEBSITE'], [110, 760, 'SERVER'], [970, 420, 'ANALYTICS'], [970, 760, 'ADS']];
  side.forEach(([x, y, l], i) => {
    const tx = x < 540 ? 240 : 840;
    line(x, y, tx, y, { col: teal(.3), lw: 2, dash: [3, 7] });
    X.beginPath(); X.arc(x, y, 8, 0, 7); X.fillStyle = teal(.8); X.fill();
    text(l, x, y - 24, { size: 15, weight: 700, fam: 'JBM', ls: 2, color: wht(.55) });
    const q = ((t * .6 + i * .27) % 1);
    packet(lerp(x, tx, q), y, { r: 4, a: .9 });
  });
  X.restore();
  // portrait
  const rv = E.io(P(t, s.vs + .05, 1.15));
  const z = 1.1 - .05 * rv - .035 * P(t, s.vs, 17);
  drawPortrait(240, 250, 600, 740, z, rv, t);
  // name
  const nameSz = 118;
  kline('SK MAHBUB', 540, 1130, { size: nameSz, weight: 900, ls: 6, stagger: .09, wglow: 0 }, c.name - .12, t);
  const ul = E.io(P(t, c.name + .3, .7));
  if (ul > 0) { rr(540 - 90 * ul, 1162, 180 * ul, 5, 3); X.fillStyle = teal(1); X.shadowColor = teal(.8); X.shadowBlur = 16; X.fill(); X.shadowBlur = 0; }
  // positioning line with segment timing
  const parts = [['Paid Ads', c.paid], ['  |  ', c.paid + .1, 1], ['Web Analytics', c.web], ['  |  ', c.web + .1, 1], ['Conversion Tracking', c.conv]];
  const tsz = 36;
  const tot = parts.reduce((a, p) => a + measure(p[0], tsz, 700), 0);
  let px = 540 - tot / 2;
  parts.forEach(([str, tp, sep]) => {
    const w = measure(str, tsz, 700);
    const p = E.oc(P(t, tp - .05, .45));
    if (p > 0) text(str, px, 1232 + (1 - p) * 16, { size: tsz, weight: 700, align: 'left', color: sep ? teal(1) : wht(.95), a: p });
    px += w;
  });
  const cp = E.oc(P(t, c.consultant - .05, .6));
  if (cp > 0) text('Paid Ads, Web Analytics & Conversion Tracking Consultant', 540, 1286, { size: fit('Paid Ads, Web Analytics & Conversion Tracking Consultant', 500, 26, 900), weight: 500, color: wht(.6), a: cp });
  // infra strip: Website -> Server -> Analytics -> Ads
  const xs = [190, 423, 657, 890], lab = ['Website', 'Server', 'Analytics', 'Ads'], ics = ['globe', 'server', 'chart', 'ads'], yI = 1410;
  xs.forEach((x, i) => {
    const p = E.ob(P(t, c.build + i * .22, .5)); if (p <= 0) return;
    if (i < 3) line(x + 44, yI, xs[i + 1] - 44, yI, { col: teal(.35), lw: 2.5, p: E.io(P(t, c.build + i * .22 + .2, .4)) });
    X.save(); X.globalAlpha *= clamp(p); X.translate(x, yI); X.scale(p, p); X.translate(-x, -yI);
    iconBox(x - 36, yI - 36, 72, ics[i], { fill: i === 1 ? teal(.2) : teal(.1), stroke: i === 1 ? teal(.6) : teal(.28) });
    text(lab[i], x, yI + 70, { size: 20, weight: 700, fam: 'JBM', color: wht(.65) });
    X.restore();
  });
  if (t > c.build + 1) for (let k = 0; k < 3; k++) {
    const q = ((t - c.build) * .45 + k / 3) % 1;
    const x = lerp(xs[0] + 44, xs[3] - 44, q);
    if (xs.some(xx => Math.abs(xx - x) < 40)) continue;
    packet(x, yI, { r: 6 });
  }
  // keyword caption
  const kw = [['SERVER-SIDE TRACKING', c.server, c.reliable], ['MORE RELIABLE CONVERSION DATA', c.reliable, c.infra], ['DEPENDABLE AD INFRASTRUCTURE', c.infra, 1e9]];
  kw.forEach(([w, a, b]) => {
    const sz = fit(w, 800, 30, 900, 'Inter', 3);
    kline(w, 540, 1560, { size: sz, weight: 800, ls: 3, color: teal(1), out: b - .2, outDur: .3, stagger: .04 }, a - .05, t);
  });
};

// ---------------- SCENE 08 — FINANCIAL CONSEQUENCE ----------------
S['08'] = (t, s, c) => {
  const shk = Math.exp(-Math.max(0, t - c.losing) * 7) * (t > c.losing ? 1 : 0);
  X.save(); X.translate((hash(Math.floor(t * 60)) - .5) * 14 * shk, (hash(Math.floor(t * 60), 2) - .5) * 14 * shk);
  const pd = P(t, c.pause + .05, .35) * (1 - P(t, c.losing - .04, .06));
  eyebrow(t, s.vs + .2, 'THE REAL COST', 300);
  const big = 156;
  // phase 1: WRONG TRACKING
  const o1 = c.missing - .25;
  kline('[TRACKING]', 540, 800, { size: big, weight: 900, ls: -3, out: o1, glow: 30 }, c.tracking - .1, t);
  if (t >= c.wrong - .05 && t < o1 + .4) {
    const q = E.io(P(t, o1, .4));
    const p = E.ox(P(t, c.wrong - .05, .35));
    const g = t - c.wrong < .18;
    X.save(); X.globalAlpha *= p * (1 - q); X.translate(540, 640 - q * 60); const sc = 1.12 - .12 * p; X.scale(sc, sc);
    if (g) for (let i = 0; i < 4; i++) { X.save(); X.beginPath(); X.rect(-540, -150 + i * 42, 1080, 42); X.clip(); text('WRONG', (hash(i, Math.floor(t * 40)) - .5) * 46, 0, { size: big, weight: 900, ls: -3 }); X.restore(); }
    else text('WRONG', 0, 0, { size: big, weight: 900, ls: -3 });
    X.restore();
  }
  // phase 2: MISSING DATA
  const o2 = c.losing - .12;
  X.save(); X.globalAlpha *= 1 - .65 * pd;
  kline('MISSING', 540, 640, { size: big, weight: 900, ls: -3, out: o2, outDur: .12 }, c.missing - .05, t);
  kline('[DATA]', 540, 800, { size: big, weight: 900, ls: -3, out: o2, outDur: .12, glow: 30 }, c.missing + .1, t);
  X.restore();
  // data drop particles
  for (let k = 0; k < 14; k++) {
    const tk = c.missing + .2 + hash(k) * .8, q = (t - tk) / 1.4; if (q < 0 || q > 1) continue;
    packet(200 + hash(k, 2) * 680, 860 + E.sine(q) * q * 700, { grey: true, a: (1 - q) * (1 - pd * .7), r: 5 + hash(k, 3) * 4 });
  }
  // phase 3: LOSING MONEY
  if (t > c.losing - .04) {
    const p = E.ox(P(t, c.losing - .04, .4));
    radialFlash(540, 820, 900, (1 - P(t, c.losing, 1)) * .9);
    X.save(); X.globalAlpha *= clamp(p * 1.5); X.translate(540, 760); const sc = 1.2 - .2 * p; X.scale(sc, sc);
    const sz = fit('LOSING', 900, 200, 980, 'Inter', -4);
    text('LOSING', 0, -10, { size: sz, weight: 900, ls: -4 });
    text('MONEY', 0, sz * .98 - 10, { size: sz, weight: 900, ls: -4 });
    const ul = E.io(P(t, c.losing + .25, .5));
    rr(-300 * ul, sz * .98 + 30, 600 * ul, 8, 4); X.fillStyle = teal(1); X.shadowColor = teal(.8); X.shadowBlur = 20; X.fill();
    X.restore();
  }
  // phase 4: WASTING AD SPEND
  const wsz = fit('WASTING AD SPEND', 900, 96, 960, 'Inter', -2);
  kline('[WASTING AD SPEND]', 540, 1150, { size: wsz, weight: 900, ls: -2, stagger: .08, glow: 34 }, c.wasting - .05, t);
  // budget panel
  const bp = E.oc(P(t, c.missing + .1, .6));
  if (bp > 0) {
    X.save(); X.globalAlpha *= bp * (1 - .4 * pd); X.translate(0, (1 - bp) * 40);
    card(90, 1250, 900, 250, { r: 26 });
    const spend = clamp(.42 + (t - c.missing) * .055, 0, .97);
    const conv = lerp(.78, .26, E.io(P(t, c.missing + .2, (c.wasting + .6) - (c.missing + .2))));
    const rows = [['AD SPEND', spend, wht(.9), '↑'], ['TRACKED CONVERSIONS', conv, teal(1), '↓']];
    rows.forEach(([l, v, col, ar], i) => {
      const y = 1312 + i * 104;
      text(l, 140, y, { size: 19, weight: 700, fam: 'JBM', ls: 2, align: 'left', color: wht(.55) });
      text(ar, 940, y, { size: 24, weight: 700, fam: 'JBM', align: 'right', color: col });
      rr(140, y + 22, 800, 18, 9); X.fillStyle = 'rgba(255,255,255,0.06)'; X.fill();
      rr(140, y + 22, 800 * v, 18, 9); X.fillStyle = col; if (i) { X.shadowColor = teal(.7); X.shadowBlur = 14; } X.fill(); X.shadowBlur = 0;
    });
    X.restore();
  }
  X.restore();
};

// ---------------- SCENE 09 — FINAL CTA ----------------
S['09'] = (t, s, c) => {
  const audioEnd = s.start + s.dur;
  const endT = audioEnd + .25;
  const o1 = c.fix - .35;
  const sz1 = fit('BEFORE YOU SCALE', 900, 100, 960, 'Inter', -2);
  kline('BEFORE YOU SCALE', 540, 600, { size: sz1, weight: 900, ls: -2, out: o1 }, c.before - .1, t);
  const sz2 = fit('CHECK YOUR TRACKING', 900, 100, 960, 'Inter', -2);
  kline('[CHECK YOUR TRACKING]', 540, 600 + sz1 * 1.1, { size: sz2, weight: 900, ls: -2, out: o1, glow: 28 }, c.make - .05, t);
  const checks = ['Events firing correctly', 'Server-side layer in place', 'Signals reaching ad platforms'];
  checks.forEach((l, i) => {
    const ti = c.make + .35 + i * .5;
    const p = E.oc(P(t, ti, .45)); if (p <= 0) return;
    const q = E.io(P(t, o1, .4)); if (q >= 1) return;
    const y = 860 + i * 96;
    X.save(); X.globalAlpha *= p * (1 - q); X.translate((1 - p) * 40, -q * 40);
    card(170, y, 740, 76, { r: 20 });
    checkMark(214, y + 38, 18, P(t, ti + .1, .4), { lw: 2.5, lw2: 3 });
    text(l, 256, y + 47, { size: 28, weight: 700, align: 'left', color: wht(.9) });
    X.restore();
  });
  // final statement
  const qEnd = E.io(P(t, endT, .5));
  if (qEnd < 1) {
    X.save(); X.globalAlpha *= 1 - qEnd; X.translate(0, -qEnd * 40);
    const sz = fit('FIX YOUR', 900, 168, 960, 'Inter', -4);
    kline('FIX YOUR', 540, 760, { size: sz, weight: 900, ls: -4, stagger: .1 }, c.fix - .06, t);
    kline('[TRACKING]', 540, 760 + sz * 1.0, { size: sz, weight: 900, ls: -4, glow: 40 }, c.fix + .18, t);
    const s3 = fit('BEFORE IT COSTS YOU MORE.', 800, 66, 940, 'Inter', -1);
    kline('BEFORE IT COSTS YOU MORE.', 540, 760 + sz * 1.0 + 130, { size: s3, weight: 800, ls: -1, color: wht(.92), stagger: .08 }, c.costing - .05, t);
    const ul = E.io(P(t, c.costing + .6, .7));
    if (ul > 0) { rr(540 - 140 * ul, 760 + sz + 175, 280 * ul, 5, 3); X.fillStyle = teal(1); X.fill(); }
    X.restore();
  }
  // end card
  if (t > endT + .2) {
    const p = E.oc(P(t, endT + .2, .8));
    X.save(); X.globalAlpha *= p;
    // circular portrait (unaltered image, circular crop)
    const r = 135, cx = 540, cy = 690;
    X.save(); X.shadowColor = teal(.45); X.shadowBlur = 70; X.beginPath(); X.arc(cx, cy, r + 6, 0, 7); X.fillStyle = '#0a1518'; X.fill(); X.restore();
    X.save(); X.beginPath(); X.arc(cx, cy, r, 0, 7); X.clip();
    const z = 1.04 + .03 * P(t, endT, 5);
    X.drawImage(IMG, 130, 40, 540, 540, cx - r * z, cy - r * z, 2 * r * z, 2 * r * z); X.restore();
    X.beginPath(); X.arc(cx, cy, r + 6, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * E.io(P(t, endT + .3, 1))); X.strokeStyle = teal(.9); X.lineWidth = 3; X.stroke();
    X.restore();
    kline('SK MAHBUB', 540, 960, { size: 112, weight: 900, ls: 6, stagger: .08 }, endT + .35, t);
    const ul = E.io(P(t, endT + .7, .6));
    if (ul > 0) { rr(540 - 80 * ul, 994, 160 * ul, 5, 3); X.fillStyle = teal(1); X.shadowColor = teal(.8); X.shadowBlur = 16; X.fill(); X.shadowBlur = 0; }
    const pp = E.oc(P(t, endT + .8, .6));
    if (pp > 0) {
      const parts = [['Paid Ads', 0], ['  |  ', 1], ['Web Analytics', 0], ['  |  ', 1], ['Conversion Tracking', 0]];
      const tot = parts.reduce((a, p2) => a + measure(p2[0], 36, 700), 0);
      let px = 540 - tot / 2;
      parts.forEach(([str, sep]) => { text(str, px, 1066 + (1 - pp) * 14, { size: 36, weight: 700, align: 'left', color: sep ? teal(1) : wht(.95), a: pp }); px += measure(str, 36, 700); });
    }
    const p3 = E.oc(P(t, endT + 1.1, .6));
    if (p3 > 0) text('Paid Ads, Web Analytics & Conversion Tracking Consultant', 540, 1120, { size: 25, weight: 500, color: wht(.55), a: p3 });
    const p4 = E.oc(P(t, endT + 1.5, .7));
    if (p4 > 0) pill(540, 1230, 'FIX YOUR TRACKING BEFORE IT COSTS YOU MORE', { size: 19, a: p4, dot: true, fam: 'Inter', weight: 700, ls: 2, h: 52 });
  }
};

// =====================================================================
function renderFrame(t) {
  X.setTransform(1, 0, 0, 1, 0, 0); X.globalAlpha = 1; X.filter = 'none';
  background(t);
  for (const s of TL.scenes) {
    if (t < s.vs - .01 || t > s.ve + .45) continue;
    const pin = s.id === '01' ? 1 : E.oc(P(t, s.vs, .45));
    const pout = s.id === '09' ? 0 : E.io(P(t, s.ve, .42));
    if (pin <= 0 || pout >= 1) continue;
    X.save();
    X.globalAlpha = pin * (1 - pout);
    const sc = 1 + (1 - pin) * .03 - pout * .035;
    X.translate(W / 2, H / 2); X.scale(sc, sc); X.translate(-W / 2, -H / 2 + (1 - pin) * 26 - pout * 34);
    if (pout > .02) X.filter = `blur(${(pout * 12).toFixed(1)}px)`;
    S[s.id](t, s, s.cues);
    X.restore(); X.filter = 'none';
  }
  // global fade in/out
  const fi = 1 - E.oc(P(t, 0, .9)), fo = P(t, TL.total - .7, .7);
  const a = Math.max(fi, fo);
  if (a > 0) { X.setTransform(1, 0, 0, 1, 0, 0); X.globalAlpha = 1; X.fillStyle = `rgba(0,0,0,${a})`; X.fillRect(0, 0, W, H); }
}
window.renderFrame = renderFrame;
window.grab = (t, type = 'image/png', q) => { renderFrame(t); return cv.toDataURL(type, q).split(',')[1]; };
