// v2 layer: camera, cursor, tooltips, kinetic captions, ambient data, photo signature.
// Loaded after render.js; function declarations here replace the v1 versions.
const ROLE = 'Paid Ads, Web Analytics & Conversion Tracking Consultant';
const ME = () => document.getElementById('me');
E.spring = p => { const c1 = 1.15, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); };

// ---------------- camera ----------------
// [t, focusX, focusY, scale] — focus point is brought to screen center
const CAM = {
  l: [
    [0, 960, 470, 1.07], [3.2, 960, 520, 1.0], [10.6, 960, 520, 1.0],
    [14.7, 760, 430, 1.2], [16.0, 860, 430, 1.2], [16.8, 1060, 430, 1.2], [17.6, 1160, 430, 1.2], [19.2, 960, 520, 1.0],
    [24.4, 960, 520, 1.0], [26.9, 1180, 500, 1.12], [28.3, 1180, 500, 1.12], [29.4, 960, 470, 1.0],
    [t2(3.3), 960, 520, 1.0], [t2(4.9), 620, 440, 1.1], [t2(7.4), 620, 440, 1.1], [t2(9.6), 1300, 440, 1.1], [t2(11.8), 1300, 440, 1.1],
    [t2(13.2), 960, 510, 1.0], [t2(16.6), 960, 510, 1.0], [t2(17.4), 960, 510, .965], [t2(18.6), 960, 510, .965],
    [t2(20.0), 700, 500, 1.1], [t2(24.8), 700, 500, 1.1], [t2(26.4), 700, 505, 1.1], [t2(30.0), 700, 505, 1.1],
    [t2(31.6), 1220, 500, 1.1], [t2(38.6), 1220, 500, 1.1], [t2(40.2), 1220, 505, 1.1], [t2(42.6), 1220, 505, 1.1],
    [t2(44.2), 960, 520, 1.0], [t2(47.4), 960, 520, 1.0], [t2(48.6), 960, 560, 1.04], [t2(54.5), 960, 540, 1.0],
    [t3(0.6), 960, 540, 1.0], [t3(1.6), 960, 450, 1.08], [t3(4.8), 960, 450, 1.08], [t3(5.6), 960, 520, 1.0],
    [t3(6.5), 720, 470, 1.1], [t3(8.6), 1000, 470, 1.1], [t3(10.8), 1240, 470, 1.1], [t3(11.7), 960, 520, 1.0],
    [t3(13.2), 960, 520, 1.0], [t3(14.2), 1000, 450, 1.12], [t3(16.4), 1040, 520, 1.12], [t3(17.6), 960, 520, 1.0],
    [t3(21.9), 960, 520, 1.0], [t3(22.6), 960, 490, 1.06], [t3(24.8), 960, 520, 1.0],
    [t3(28.6), 960, 520, 1.0], [t3(29.4), 640, 520, 1.09], [t3(30.5), 1290, 520, 1.09], [t3(33.0), 1290, 540, 1.09], [t3(34.5), 960, 540, 1.0],
    [END, 960, 545, 1.035]],
  v: [
    [0, 540, 900, 1.07], [3.2, 540, 960, 1.0], [10.6, 540, 960, 1.0],
    [14.7, 420, 820, 1.14], [16.0, 660, 820, 1.14], [16.8, 420, 900, 1.14], [17.6, 660, 900, 1.14], [19.2, 540, 960, 1.0],
    [24.4, 540, 960, 1.0], [26.9, 540, 930, 1.12], [28.3, 540, 930, 1.12], [29.4, 540, 960, 1.0],
    [t2(3.3), 540, 960, 1.0], [t2(4.9), 540, 860, 1.08], [t2(7.4), 540, 860, 1.08], [t2(9.6), 540, 975, 1.04], [t2(11.8), 540, 975, 1.04],
    [t2(13.2), 540, 960, 1.0], [t2(16.6), 540, 960, 1.0], [t2(17.4), 540, 940, .965], [t2(18.6), 540, 940, .965],
    [t2(20.0), 540, 880, 1.06], [t2(26.4), 540, 900, 1.06], [t2(30.0), 540, 900, 1.06],
    [t2(31.6), 540, 965, 1.03], [t2(40.2), 540, 975, 1.04], [t2(42.6), 540, 975, 1.04],
    [t2(44.2), 540, 960, 1.0], [t2(54.5), 540, 960, 1.0],
    [t3(0.6), 540, 960, 1.0], [t3(1.6), 540, 840, 1.08], [t3(4.8), 540, 840, 1.08], [t3(5.6), 540, 960, 1.0],
    [t3(6.5), 540, 880, 1.05], [t3(8.6), 540, 960, 1.05], [t3(10.8), 540, 985, 1.05], [t3(11.7), 540, 960, 1.0],
    [t3(13.2), 540, 960, 1.0], [t3(14.2), 540, 900, 1.08], [t3(16.4), 540, 960, 1.08], [t3(17.6), 540, 960, 1.0],
    [t3(21.9), 540, 960, 1.0], [t3(22.6), 540, 930, 1.06], [t3(24.8), 540, 960, 1.0],
    [t3(28.6), 540, 960, 1.0], [t3(29.4), 540, 880, 1.05], [t3(30.5), 540, 990, 1.05], [t3(33.0), 540, 990, 1.05], [t3(34.5), 540, 960, 1.0],
    [END, 540, 965, 1.035]]
};
function camAt(t) {
  const K = CAM[V ? 'v' : 'l'];
  if (t <= K[0][0]) return { fx: K[0][1], fy: K[0][2], s: K[0][3] };
  for (let i = 1; i < K.length; i++) if (t <= K[i][0]) {
    const a = K[i - 1], b = K[i], p = E.io((t - a[0]) / (b[0] - a[0]));
    return { fx: lerp(a[1], b[1], p), fy: lerp(a[2], b[2], p), s: lerp(a[3], b[3], p) };
  }
  const k = K[K.length - 1]; return { fx: k[1], fy: k[2], s: k[3] };
}
function applyCam(c, depth = 1) {
  const s = 1 + (c.s - 1) * depth, fx = W / 2 + (c.fx - W / 2) * depth, fy = H / 2 + (c.fy - H / 2) * depth;
  ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-fx, -fy);
}
const toScreen = (c, x, y) => ({ x: W / 2 + (x - c.fx) * c.s, y: H / 2 + (y - c.fy) * c.s });

// ---------------- background: grid with parallax + ambient data ----------------
function background(t, cam) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const ga = keyed(t, [[0, .05], [9, .05], [11, .085], [t3(34.4), .085], [t3(35.6), .045]]);
  const g = 60, ox = (W % g) / 2, oy = (H % g) / 2;
  ctx.save(); applyCam(cam, .45); ctx.lineWidth = 1;
  const M0 = 12;
  for (let i = -M0; i <= W / g + M0; i++) {
    const x = ox + i * g; ctx.strokeStyle = `rgba(74,92,95,${i % 4 === 0 ? ga * 1.5 : ga})`;
    ctx.beginPath(); ctx.moveTo(x + .5, -M0 * g); ctx.lineTo(x + .5, H + M0 * g); ctx.stroke();
  }
  for (let j = -M0; j <= H / g + M0; j++) {
    const y = oy + j * g; ctx.strokeStyle = `rgba(74,92,95,${j % 4 === 0 ? ga * 1.5 : ga})`;
    ctx.beginPath(); ctx.moveTo(-M0 * g, y + .5); ctx.lineTo(W + M0 * g, y + .5); ctx.stroke();
  }
  // ambient data packets travelling along grid lines (the canvas is "live")
  const amb = .55 * (1 - P(t, t3(34.6), 1.0));
  if (amb > 0) {
    for (let k = 0; k < 9; k++) {
      const horiz = k % 2 === 0, sp = 70 + (k * 37) % 60, ph = (k * 431) % 1000;
      const span = (horiz ? W : H) + 600;
      const d = ((t * sp + ph) % span) - 300;
      const lineI = 2 + (k * 7) % Math.floor((horiz ? H : W) / g - 3);
      const x = horiz ? d : ox + lineI * g, y = horiz ? oy + lineI * g : d;
      const tl = 110;
      const gr = horiz ? ctx.createLinearGradient(x - tl, y, x, y) : ctx.createLinearGradient(x, y - tl, x, y);
      gr.addColorStop(0, 'rgba(25,195,177,0)'); gr.addColorStop(1, `rgba(25,195,177,${.45 * amb})`);
      ctx.strokeStyle = gr; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(horiz ? x - tl : x + .5, horiz ? y + .5 : y - tl); ctx.lineTo(x + (horiz ? 0 : .5), y + (horiz ? .5 : 0)); ctx.stroke();
      ctx.beginPath(); ctx.arc(x + .5, y + .5, 3, 0, 7); ctx.fillStyle = `rgba(25,195,177,${.7 * amb})`; ctx.fill();
    }
  }
  ctx.restore();
  const rg = ctx.createRadialGradient(W / 2, H * .45, 0, W / 2, H * .45, Math.max(W, H) * .75);
  rg.addColorStop(0, 'rgba(255,255,255,0.35)'); rg.addColorStop(.6, 'rgba(244,249,248,0)'); rg.addColorStop(1, 'rgba(232,242,240,0.55)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}

// ---------------- cursor ----------------
// [t, x, y, kind]  kind: 'c' click (arrives just before t), 'h' hover
const CUR = {
  l: [
    [1.0, 1700, 700, 'h'], [1.6, 1562, 206, 'c'], [4.7, 1700, 790, 'h'], [9.0, 1380, 560, 'h'],
    [15.12, 446, 347, 'c'], [16.02, 780, 347, 'c'], [16.82, 1114, 347, 'c'], [17.56, 1448, 347, 'c'],
    [21.4, 990, 520, 'h'], [24.6, 1140, 500, 'h'], [26.9, 1268, 487, 'c'], [30.4, 1330, 560, 'h'],
    [t2(2.0), 960, 640, 'h'], [t2(4.9), 300, 335, 'c'], [t2(9.7), 1190, 335, 'c'], [t2(14.2), 760, 230, 'h'], [t2(16.6), 960, 560, 'h'],
    [t2(19.6), 520, 560, 'h'], [t2(22.1), 388, 510, 'c'], [t2(26.2), 330, 770, 'c'],
    [t2(31.3), 1400, 560, 'h'], [t2(34.6), 1152, 510, 'c'], [t2(41.94), 1210, 770, 'c'],
    [t2(45.2), 1320, 440, 'h'], [t2(50.6), 1250, 380, 'h'],
    [t3(1.4), 1060, 470, 'h'], [t3(5.3), 300, 450, 'c'], [t3(6.5), 640, 450, 'c'], [t3(7.7), 980, 450, 'c'], [t3(8.55), 1320, 450, 'c'], [t3(10.8), 1660, 450, 'c'],
    [t3(12.8), 1080, 260, 'h'], [t3(14.4), 1110, 377, 'c'], [t3(15.3), 1110, 455, 'c'], [t3(16.5), 1110, 611, 'c'], [t3(17.4), 1700, 480, 'h'],
    [t3(22.6), 1300, 700, 'h'], [t3(29.1), 690, 570, 'h'], [t3(30.7), 1600, 458, 'c'], [t3(31.9), 1600, 570, 'c'], [t3(33.6), 1450, 860, 'h']],
  v: [
    [1.0, 900, 1250, 'h'], [1.6, 892, 298, 'c'], [4.7, 760, 1240, 'h'], [9.0, 700, 1000, 'h'],
    [15.12, 316, 470, 'c'], [16.02, 763, 470, 'c'], [16.82, 316, 702, 'c'], [17.56, 763, 702, 'c'],
    [21.4, 600, 740, 'h'], [24.6, 600, 860, 'h'], [26.9, 545, 902, 'c'], [30.4, 640, 1000, 'h'],
    [t2(2.0), 700, 810, 'h'], [t2(4.9), 220, 350, 'c'], [t2(9.7), 230, 940, 'c'], [t2(14.2), 900, 290, 'h'], [t2(16.6), 560, 820, 'h'],
    [t2(19.6), 420, 560, 'h'], [t2(22.1), 287, 515, 'c'], [t2(26.2), 280, 730, 'c'],
    [t2(31.3), 420, 1150, 'h'], [t2(34.6), 175, 1105, 'c'], [t2(41.94), 280, 1320, 'c'],
    [t2(45.2), 700, 830, 'h'], [t2(50.6), 760, 900, 'h'],
    [t3(1.4), 660, 760, 'h'], [t3(5.3), 600, 330, 'c'], [t3(6.5), 600, 548, 'c'], [t3(7.7), 600, 766, 'c'], [t3(8.55), 600, 984, 'c'], [t3(10.8), 600, 1202, 'c'],
    [t3(12.8), 700, 560, 'h'], [t3(14.4), 520, 641, 'c'], [t3(15.3), 520, 727, 'c'], [t3(16.5), 520, 899, 'c'], [t3(17.4), 640, 1297, 'h'],
    [t3(22.6), 760, 1000, 'h'], [t3(29.1), 560, 550, 'h'], [t3(30.7), 891, 1108, 'c'], [t3(31.9), 891, 1200, 'c'], [t3(33.6), 760, 1340, 'h']]
};
// tooltips anchored to the cursor: [start, end, text, sub]
const TIPS = [
  [1.75, 4.3, 'Status from platform conversions', 'Not from closed sales'],
  [27.1, 29.4, 'Google Ads stops here', 'No CRM or sales data connected', 'below'],
  [t2(5.2), t2(7.4), '$1,200 ÷ 20 leads', '= $60 cost per lead'],
  [t2(10.0), t2(12.3), '$2,400 ÷ 20 leads', '= $120 cost per lead'],
  [t2(42.2), t2(43.3), 'Lowest cost per qualified lead', null],
  [t3(14.6), t3(15.2), 'Lead qualified in CRM', null],
  [t3(16.7), t3(17.9), 'Deal won · revenue synced', 'Sent back to Google Ads'],
  [t3(30.9), t3(33.5), 'Not visible in Google Ads', 'Lives in your CRM'],
];
function cursorPos(t) {
  const K = CUR[V ? 'v' : 'l'];
  if (t <= K[0][0]) return { x: K[0][1], y: K[0][2], k: K[0] };
  for (let i = 1; i < K.length; i++) {
    const a = K[i - 1], b = K[i];
    if (t <= b[0]) {
      const arrive = b[0] - (b[3] === 'c' ? .12 : 0);
      const dur = Math.min(.85, Math.max(.25, arrive - a[0] - .15));
      const p = E.io(clamp((t - (arrive - dur)) / dur));
      const dx = b[1] - a[1], dy = b[2] - a[2], arc = Math.sin(Math.PI * p) * .08;
      // idle micro-drift while waiting
      const idle = (1 - Math.sin(Math.PI * p)) * 2.5;
      return { x: lerp(a[1], b[1], p) - dy * arc + Math.sin(t * 1.3) * idle, y: lerp(a[2], b[2], p) + dx * arc + Math.cos(t * 1.1) * idle };
    }
  }
  const k = K[K.length - 1]; return { x: k[1], y: k[2] };
}
function drawCursor(t, cam) {
  const a = P(t, 1.0, .5) * (1 - P(t, t3(34.3), .5));
  if (a <= 0) return;
  const K = CUR[V ? 'v' : 'l'];
  const p = cursorPos(t), sp = toScreen(cam, p.x, p.y);
  // click ripples
  for (const k of K) if (k[3] === 'c' && t >= k[0] - .02 && t < k[0] + .7) {
    const q = clamp((t - k[0]) / .7), s2 = toScreen(cam, k[1], k[2]);
    withA(a * (1 - q), () => {
      ctx.beginPath(); ctx.arc(s2.x, s2.y, 8 + 34 * E.out(q), 0, 7); ctx.strokeStyle = C.acc; ctx.lineWidth = 3 * (1 - q) + 1; ctx.stroke();
      ctx.beginPath(); ctx.arc(s2.x, s2.y, 10 * (1 - q), 0, 7); ctx.fillStyle = 'rgba(25,195,177,0.35)'; ctx.fill();
    });
  }
  let press = 1;
  for (const k of K) if (k[3] === 'c') { const d = t - k[0]; if (d > -.08 && d < .16) press = Math.min(press, .84 + .16 * Math.abs(d < 0 ? d / .08 : d / .16)); }
  const sc = (V ? 1.25 : 1.05) * press;
  withA(a, () => {
    ctx.save(); ctx.translate(sp.x, sp.y); ctx.scale(sc, sc);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 30); ctx.lineTo(7.5, 23.5); ctx.lineTo(12.5, 34.5); ctx.lineTo(17.5, 32.5); ctx.lineTo(12.5, 21.5); ctx.lineTo(22, 21.5); ctx.closePath();
    ctx.shadowColor = 'rgba(10,26,29,0.25)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = 4;
    ctx.fillStyle = C.ink; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.2; ctx.lineJoin = 'round'; ctx.stroke();
    ctx.restore();
  });
  // tooltips
  for (const [s, e, txt, sub, place] of TIPS) {
    const ta = P(t, s, .3, E.spring) * (1 - P(t, e, .25));
    if (ta <= 0) continue;
    const fs = V ? 24 : 19, ss = V ? 19 : 15, pad = V ? 20 : 16;
    const tw = Math.max(M(txt, fs, 700), sub ? M(sub, ss, 500) : 0) + pad * 2 + 6;
    const th = sub ? fs + ss + pad * 2 + 8 : fs + pad * 2;
    let x = sp.x + 26, y = sp.y + 40;
    if (place === 'below') { x = sp.x - tw * .75; y = sp.y + (V ? 70 : 90); }
    if (x + tw > W - 30) x = sp.x - tw - 10;
    if (y + th > (V ? 1440 : 900)) y = sp.y - th - 16;
    withA(clamp(ta), () => {
      ctx.save(); xform(x, y, lerp(.9, 1, clamp(ta)));
      card(x, y, tw, th, { r: 14, sh: 1.4, stroke: C.line });
      rr(x, y + 10, 4, th - 20, 2); ctx.fillStyle = C.acc; ctx.fill();
      T(txt, x + pad + 6, y + pad + fs * .82, { size: fs, w: 700, c: C.ink });
      if (sub) T(sub, x + pad + 6, y + pad + fs + 8 + ss * .82, { size: ss, w: 500, c: C.mut });
      ctx.restore();
    });
  }
}

// ---------------- kinetic captions (keyword sweep synced to the voice) ----------------
const norm = s => s.toLowerCase().replace(/[^a-z0-9$]/g, '');
let CAPX = null;
function prepCaps() {
  CAPX = CAPS.map(([s, e, txt]) => {
    const words = [];
    txt.split(/(\*[^*]+\*)/).filter(Boolean).forEach(seg => {
      const hl = seg.startsWith('*');
      seg.replace(/\*/g, '').split(' ').filter(Boolean).forEach(w => words.push({ w, hl }));
    });
    const ww = WORDS.filter(x => x[0] >= s - .15 && x[0] <= e + .1);
    let k = 0;
    words.forEach((q, j) => {
      let tm = null;
      for (let d = 0; d < 4 && k + d < ww.length; d++) if (norm(ww[k + d][1]) === norm(q.w)) { tm = ww[k + d][0]; k = k + d + 1; break; }
      if (tm === null) tm = ww.length ? ww[Math.min(ww.length - 1, Math.round(j * (ww.length - 1) / Math.max(1, words.length - 1)))][0] : s;
      q.t = tm;
    });
    return { s, e, words };
  });
}
function captions(t) {
  if (!CAPX) prepCaps();
  for (const c of CAPX) {
    if (t < c.s - .02 || t > c.e + .35) continue;
    const a = 1 - P(t, c.e, .3);
    if (a <= 0) continue;
    drawCaption2(c, t, a, -P(t, c.e, .3) * 10);
  }
}
function drawCaption2(c, t, a, dyOut) {
  const size = V ? 46 : 40, maxW = V ? 900 : 1480, lh = size * 1.32;
  const sp = M(' ', size, 600);
  const wid = x => M(x.w, size, x.hl ? 800 : 560);
  const lines = []; let cur = [], cw = 0;
  for (const x of c.words) {
    const w = wid(x);
    if (cur.length && cw + sp + w > maxW) { lines.push([cur, cw]); cur = []; cw = 0; }
    cw += (cur.length ? sp : 0) + w; cur.push(x);
  }
  if (cur.length) lines.push([cur, cw]);
  const bw = Math.max(...lines.map(l => l[1])) + (V ? 72 : 80), bh = lines.length * lh + (V ? 40 : 34);
  const enter = P(t, c.s, .45, E.spring);
  const cy = (V ? 1530 : 968) + (1 - P(t, c.s, .45, E.out5)) * 16 + dyOut;
  const bx = W / 2 - bw / 2, by = cy - bh / 2;
  withA(a * clamp(enter * 1.5), () => {
    ctx.save(); xform(W / 2, cy, lerp(.96, 1, clamp(enter)));
    card(bx, by, bw, bh, { r: 20, fill: 'rgba(255,255,255,0.95)', stroke: 'rgba(225,235,233,0.9)', sh: .8 });
    // sentence progress hairline
    const pr = clamp((t - c.s) / Math.max(.5, c.e - c.s));
    ctx.save(); rr(bx, by, bw, bh, 20); ctx.clip();
    ctx.fillStyle = 'rgba(25,195,177,0.55)'; ctx.fillRect(bx, by + bh - 3, bw * pr, 3); ctx.restore();
    let n = 0;
    lines.forEach(([ws, lw], i) => {
      let x = W / 2 - lw / 2; const y = by + (V ? 20 : 17) + lh * i + lh * .5 + size * .35;
      ws.forEach((q, j) => {
        const w = wid(q);
        const ap = P(t, c.s + n * .022, .32, E.out5); n++;
        const dy = (1 - ap) * 14;
        if (q.hl) {
          const k = P(t, q.t - .04, .32, E.out);
          if (k > 0) { rr(x - 6, y - size * .86 + dy, (w + 12) * k, size * 1.12, 8); ctx.fillStyle = `rgba(25,195,177,${.16 * ap})`; ctx.fill(); }
          T(q.w, x, y + dy, { size, w: 800, c: C.ink, a: ap * (1 - k) });
          T(q.w, x, y + dy, { size, w: 800, c: C.deep, a: ap * k });
        } else T(q.w, x, y + dy, { size, w: 560, c: C.ink, a: ap });
        x += w + (j < ws.length - 1 ? sp : 0);
      });
    });
    ctx.restore();
  });
}

// ---------------- signature: logo + photo ----------------
function photo(x, y, r, a = 1, ring = 3) {
  withA(a, () => {
    ctx.save(); ctx.beginPath(); ctx.arc(x, y, r + ring, 0, 7); ctx.fillStyle = '#fff';
    ctx.shadowColor = 'rgba(10,26,29,0.15)'; ctx.shadowBlur = r * .5; ctx.shadowOffsetY = r * .12; ctx.fill(); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.clip(); ctx.drawImage(ME(), x - r, y - r, r * 2, r * 2); ctx.restore();
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = 'rgba(25,195,177,0.9)'; ctx.lineWidth = Math.max(1.5, r * .05); ctx.stroke();
  });
}
function brandGroup(x, y, r, a = 1) { // logo + photo, side by side, slightly overlapping; returns width
  monogram(x + r, y, r, a);
  photo(x + r * 3.25, y, r * 1.08, a, r * .1);
  return r * 4.4;
}
function watermark(t) {
  const a = P(t, 0.3, .8) * (1 - P(t, t3(36.2), .6));
  if (a <= 0) return;
  if (!V) {
    const gw = brandGroup(60, 76, 23, a);
    T('SK Mahbub', 60 + gw + 14, 71, { size: 21, w: 750, c: C.ink, a });
    T(ROLE, 60 + gw + 14, 95, { size: 15, w: 500, c: C.mut, a });
  } else {
    const r = 26, gw = r * 4.4;
    const tw = Math.max(M('SK Mahbub', 27, 750), M(ROLE, 18, 500));
    const x0 = (W - (gw + 16 + tw)) / 2;
    brandGroup(x0, 118, r, a);
    T('SK Mahbub', x0 + gw + 16, 112, { size: 27, w: 750, c: C.ink, a });
    T(ROLE, x0 + gw + 16, 140, { size: 18, w: 500, c: C.mut, a });
  }
}
function ctaScene(t, lt) {
  const a1 = P(lt, 34.85, .8, E.out5), a2 = P(lt, 35.4, .8, E.out5), sg = P(lt, 36.7, 1.0, E.spring), sg2 = P(lt, 37.1, .8, E.out5);
  if (!V) {
    runs([{ s: 'Do your ', size: 70, w: 750, c: C.ink }, { s: 'Google Ads conversions', size: 70, w: 800, c: C.ink }], W / 2, 330 + (1 - a1) * 20, { al: 'center', a: a1, ls: -1.5 });
    runs([{ s: 'match your ', size: 70, w: 750, c: C.ink }, { s: 'qualified & booked leads', size: 70, w: 800, c: C.head }, { s: '?', size: 70, w: 800, c: C.ink }], W / 2, 420 + (1 - a2) * 20, { al: 'center', a: a2, ls: -1.5 });
    line(W / 2 - 60, 505, W / 2 + 60, 505, { c: C.acc, lw: 3, p: sg2, a: sg2 });
    withA(clamp(sg), () => {
      ctx.save(); xform(W / 2, 620, lerp(.8, 1, clamp(sg)));
      const r = 46, gw = r * 4.4; brandGroup(W / 2 - gw / 2, 620, r, 1); ctx.restore();
    });
    T('SK Mahbub', W / 2, 745 + (1 - sg2) * 16, { size: 54, w: 800, c: C.ink, al: 'center', ls: -1, a: sg2 });
    T(ROLE, W / 2, 795 + (1 - sg2) * 16, { size: 26, w: 600, c: C.deep, al: 'center', a: sg2 });
  } else {
    const L1 = [['Do your ', C.ink], ['Google Ads', C.ink]], L2 = [['conversions match', C.ink]], L3 = [['your ', C.ink], ['qualified &', C.head]], L4 = [['booked leads', C.head], ['?', C.ink]];
    [L1, L2, L3, L4].forEach((ln, i) => {
      const a = i < 2 ? a1 : a2;
      runs(ln.map(([s, c]) => ({ s, size: 84, w: 800, c })), W / 2, 440 + i * 104 + (1 - a) * 20, { al: 'center', a, ls: -2 });
    });
    line(W / 2 - 60, 860, W / 2 + 60, 860, { c: C.acc, lw: 3, p: sg2, a: sg2 });
    withA(clamp(sg), () => {
      ctx.save(); xform(W / 2, 1000, lerp(.8, 1, clamp(sg)));
      const r = 62, gw = r * 4.4; brandGroup(W / 2 - gw / 2, 1000, r, 1); ctx.restore();
    });
    T('SK Mahbub', W / 2, 1170 + (1 - sg2) * 16, { size: 68, w: 800, c: C.ink, al: 'center', ls: -1.5, a: sg2 });
    T('Paid Ads, Web Analytics &', W / 2, 1236 + (1 - sg2) * 16, { size: 36, w: 600, c: C.deep, al: 'center', a: sg2 });
    T('Conversion Tracking Consultant', W / 2, 1284 + (1 - sg2) * 16, { size: 36, w: 600, c: C.deep, al: 'center', a: sg2 });
  }
}
function overlay(t) {
  const tagA = P(t, t2(.8), .6) * (1 - P(t, t2(54.6), .5));
  chip('ILLUSTRATIVE SCENARIO', W / 2, V ? 196 : 124, { size: V ? 15 : 13, al: 'center', fill: '#fff', stroke: C.line, c: C.mut, ls: 2, a: tagA, dot: true });
}

// ---------------- frame ----------------
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  const cam = camAt(t);
  background(t, cam);
  ctx.save(); applyCam(cam);
  scene1(t, 1 - P(t, O2 - .35, .9, E.io));
  if (t > O2 - .4 && t < O3 + 1.2) scene2(t, P(t, O2 - .2, .9, E.io) * (1 - P(t, O3 - .2, .9, E.io)));
  if (t > O3 - .2) scene3(t, P(t, O3 - .2, .6));
  ctx.restore();
  overlay(t);
  drawCursor(t, cam);
  captions(t);
  watermark(t);
  progress(t);
}
