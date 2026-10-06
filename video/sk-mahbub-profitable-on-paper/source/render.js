// SK Mahbub — "Profitable on paper" — frame renderer (canvas 2D, deterministic per t)
const C = {
  bg: '#F4F9F8', card: '#FFFFFF', acc: '#19C3B1', deep: '#0B7A70', head: '#0D9689',
  ink: '#0A1A1D', mut: '#4A5C5F', line: '#E1EBE9', soft: '#E6F7F5', faint: '#A3B3B5', gray: '#EEF2F2'
};
let cv, ctx, W, H, V;
const O2 = 31.552, O3 = 87.168, END = O3 + 38.635 + 3.4;
const t2 = x => O2 + x, t3 = x => O3 + x;

function init(vertical) {
  V = vertical; W = V ? 1080 : 1920; H = V ? 1920 : 1080;
  cv = document.getElementById('c'); cv.width = W; cv.height = H;
  ctx = cv.getContext('2d');
}

// ---------- math / easing ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, p) => a + (b - a) * p;
const E = {
  out: p => 1 - Math.pow(1 - p, 3),
  out5: p => 1 - Math.pow(1 - p, 5),
  io: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
  back: p => { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  lin: p => p
};
function P(t, a, d = .6, e = E.out) { if (t <= a) return 0; if (t >= a + d) return 1; return e((t - a) / d); }
const win = (t, a, b, fi = .5, fo = .5) => P(t, a, fi) * (1 - P(t, b, fo));
const fmt = n => Math.round(n).toLocaleString('en-US');
function keyed(t, keys) { // [[t,v],...]
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
    const [a, va] = keys[i - 1], [b, vb] = keys[i]; return lerp(va, vb, E.io((t - a) / (b - a)));
  }
  return keys[keys.length - 1][1];
}

// ---------- primitives ----------
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function card(x, y, w, h, o = {}) {
  const { r = 22, a = 1, fill = C.card, stroke = C.line, sw = 1.5, sh = 1, dashed = false } = o;
  if (a <= 0.001) return;
  ctx.save(); ctx.globalAlpha *= a;
  if (sh > 0) {
    ctx.shadowColor = `rgba(10,26,29,${0.07 * sh})`; ctx.shadowBlur = 44; ctx.shadowOffsetY = 14;
    rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill();
    ctx.shadowColor = `rgba(10,26,29,${0.04 * sh})`; ctx.shadowBlur = 6; ctx.shadowOffsetY = 2;
    ctx.fill(); ctx.shadowColor = 'transparent';
  } else if (fill) { rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) {
    rr(x + sw / 2, y + sw / 2, w - sw, h - sw, r); ctx.strokeStyle = stroke; ctx.lineWidth = sw;
    if (dashed) ctx.setLineDash([10, 8]); ctx.stroke(); ctx.setLineDash([]);
  }
  ctx.restore();
}
function font(size, w) { return `${w} ${size}px Inter`; }
function T(s, x, y, o = {}) {
  const { size = 32, w = 500, c = C.ink, al = 'left', bl = 'alphabetic', ls = 0, a = 1 } = o;
  if (a <= 0.001) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.font = font(size, w); ctx.fillStyle = c;
  ctx.textAlign = al; ctx.textBaseline = bl; ctx.letterSpacing = ls + 'px'; ctx.fillText(s, x, y); ctx.restore();
}
function M(s, size, w, ls = 0) { ctx.save(); ctx.font = font(size, w); ctx.letterSpacing = ls + 'px'; const m = ctx.measureText(s).width; ctx.restore(); return m; }
// runs: [{s, size, w, c}] drawn on one baseline, aligned
function runs(list, x, y, o = {}) {
  const { al = 'center', a = 1, ls = 0 } = o;
  const widths = list.map(r => M(r.s, r.size, r.w, r.ls ?? ls));
  const tot = widths.reduce((p, q) => p + q, 0);
  let cx = al === 'center' ? x - tot / 2 : al === 'right' ? x - tot : x;
  list.forEach((r, i) => { T(r.s, cx, y, { size: r.size, w: r.w, c: r.c, a: a * (r.a ?? 1), ls: r.ls ?? ls }); cx += widths[i]; });
  return tot;
}
function check(x, y, s, c = C.deep, lw = 3) {
  ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * .45, y); ctx.lineTo(x - s * .1, y + s * .35); ctx.lineTo(x + s * .5, y - s * .35); ctx.stroke(); ctx.restore();
}
function chip(text, x, y, o = {}) { // x,y = left, vertical center
  const { size = 16, w = 700, fill = C.soft, c = C.deep, a = 1, pad = 14, h = size * 2.1, ls = 1, stroke = null, dot = false, tick = false, al = 'left' } = o;
  const extra = (dot ? size * .9 : 0) + (tick ? size * 1.15 : 0);
  const tw = M(text, size, w, ls) + pad * 2 + extra;
  if (a * ctx.globalAlpha <= 0.001) return tw;
  const lx = al === 'right' ? x - tw : al === 'center' ? x - tw / 2 : x;
  ctx.save(); ctx.globalAlpha *= a;
  rr(lx, y - h / 2, tw, h, h / 2); if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.5; ctx.stroke(); }
  let tx = lx + pad;
  if (dot) { ctx.beginPath(); ctx.arc(tx + size * .3, y, size * .28, 0, 7); ctx.fillStyle = c; ctx.fill(); tx += size * 1.25; }
  if (tick) { check(tx + size * .4, y, size * .7, c, Math.max(2, size / 7)); tx += size * 1.15; }
  ctx.restore();
  T(text, tx, y + size * .36, { size, w, c, a, ls });
  return tw;
}
function line(x1, y1, x2, y2, o = {}) {
  const { c = C.acc, lw = 3, a = 1, dash = null, p = 1 } = o;
  if (a <= 0.001 || p <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = c; ctx.lineWidth = lw; ctx.lineCap = 'round';
  if (dash) ctx.setLineDash(dash);
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(lerp(x1, x2, p), lerp(y1, y2, p)); ctx.stroke(); ctx.restore();
}
// pulses travelling from p0 to p1 along a segment, continuous
function pulses(x1, y1, x2, y2, t, o = {}) {
  const { a = 1, n = 3, period = 1.4, r = 6, stop = 1, c = C.acc } = o;
  if (a <= 0.001) return;
  for (let i = 0; i < n; i++) {
    let ph = ((t / period) + i / n) % 1;
    const p = ph * stop;
    const fade = Math.min(1, ph * 6) * (stop < 1 ? (1 - Math.pow(ph, 3)) : Math.min(1, (1 - ph) * 6));
    const x = lerp(x1, x2, p), y = lerp(y1, y2, p);
    ctx.save(); ctx.globalAlpha *= a * fade;
    ctx.beginPath(); ctx.arc(x, y, r * 2.2, 0, 7); ctx.fillStyle = 'rgba(25,195,177,0.18)'; ctx.fill();
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = c; ctx.fill(); ctx.restore();
  }
}
function withA(a, fn) { if (a <= 0.001) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
function xform(cx, cy, s, dx = 0, dy = 0) { ctx.translate(cx + dx, cy + dy); ctx.scale(s, s); ctx.translate(-cx, -cy); }

// ---------- canvas: background + grid ----------
function background(t) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const ga = keyed(t, [[0, .05], [9, .05], [11, .085], [t3(34.4), .085], [t3(35.6), .045]]);
  const g = 60;
  ctx.save(); ctx.lineWidth = 1;
  for (let x = (W % g) / 2; x <= W; x += g) {
    const major = Math.round((x - (W % g) / 2) / g) % 4 === 0;
    ctx.strokeStyle = `rgba(74,92,95,${major ? ga * 1.5 : ga})`;
    ctx.beginPath(); ctx.moveTo(Math.round(x) + .5, 0); ctx.lineTo(Math.round(x) + .5, H); ctx.stroke();
  }
  for (let y = (H % g) / 2; y <= H; y += g) {
    const major = Math.round((y - (H % g) / 2) / g) % 4 === 0;
    ctx.strokeStyle = `rgba(74,92,95,${major ? ga * 1.5 : ga})`;
    ctx.beginPath(); ctx.moveTo(0, Math.round(y) + .5); ctx.lineTo(W, Math.round(y) + .5); ctx.stroke();
  }
  ctx.restore();
  // soft center light so the grid recedes at the edges (restrained)
  const rg = ctx.createRadialGradient(W / 2, H * .45, 0, W / 2, H * .45, Math.max(W, H) * .75);
  rg.addColorStop(0, 'rgba(255,255,255,0.35)'); rg.addColorStop(.6, 'rgba(244,249,248,0)'); rg.addColorStop(1, 'rgba(232,242,240,0.55)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}

// ---------- brand signature (persistent ownership mark) ----------
function monogram(x, y, r, a = 1) {
  withA(a, () => {
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = C.deep; ctx.fill();
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = C.acc; ctx.lineWidth = r * .12; ctx.stroke();
    T('SK', x, y + r * .02, { size: r * .78, w: 800, c: '#fff', al: 'center', bl: 'middle', ls: -.5 });
  });
}
function watermark(t) {
  const a = P(t, 0.3, .8) * (1 - P(t, t3(36.2), .6));
  if (a <= 0) return;
  if (!V) {
    monogram(86, 74, 22, a);
    T('SK Mahbub', 122, 70, { size: 21, w: 750, c: C.ink, a });
    T('Web Analytics & Conversion Tracking Consultant', 122, 94, { size: 15, w: 500, c: C.mut, a });
  } else {
    const tw = Math.max(M('SK Mahbub', 27, 750), M('Web Analytics & Conversion Tracking Consultant', 19, 500));
    const x0 = (W - (tw + 70)) / 2;
    monogram(x0 + 26, 118, 26, a);
    T('SK Mahbub', x0 + 66, 112, { size: 27, w: 750, c: C.ink, a });
    T('Web Analytics & Conversion Tracking Consultant', x0 + 66, 141, { size: 19, w: 500, c: C.mut, a });
  }
}
function progress(t) {
  if (V) return;
  const a = P(t, .3, .8) * (1 - P(t, t3(34.6), .6));
  if (a <= 0) return;
  const segs = [[0, O2, '01  THE HOOK'], [O2, O3, '02  THE REALITY'], [O3, t3(34.8), '03  THE INSIGHT']];
  const x0 = W - 64 - 3 * 64 - 2 * 8;
  let cur = 0;
  segs.forEach((s, i) => {
    const x = x0 + i * 72, p = clamp((t - s[0]) / (s[1] - s[0]));
    if (t >= s[0]) cur = i;
    withA(a, () => {
      rr(x, 66, 64, 4, 2); ctx.fillStyle = C.line; ctx.fill();
      if (p > 0) { rr(x, 66, 64 * p, 4, 2); ctx.fillStyle = C.acc; ctx.fill(); }
    });
  });
  T(segs[cur][2], W - 64, 98, { size: 14, w: 650, c: C.mut, al: 'right', ls: 2, a });
}

// ---------- captions ----------
const CAPS = [
  [0.0, 2.35, 'Your Google Ads can look *profitable*'],
  [2.42, 6.35, 'while your business is *actually losing money.*'],
  [6.7, 10.2, 'And this happens more often than you think.'],
  [10.54, 14.7, 'Because when you look at your *Google Ads dashboard,*'],
  [14.8, 19.2, 'you see *clicks,* *calls,* *forms* and *conversions.*'],
  [19.6, 24.2, 'But there\'s one thing Google Ads *doesn\'t really know:*'],
  [24.5, 30.6, 'How many of those leads actually became *paying customers?*'],
  [t2(0), t2(3.5), 'Let\'s say your agency shows you *two campaigns.*'],
  [t2(3.66), t2(7.25), 'Campaign A is generating leads at *$60.*'],
  [t2(7.5), t2(12.1), 'Campaign B is generating leads at *$120.*'],
  [t2(12.38), t2(16.45), 'So naturally, you\'d think *Campaign A is the winner.*'],
  [t2(16.78), t2(18.4), 'But here\'s the *problem.*'],
  [t2(18.5), t2(24.95), 'If those $60 leads only give you *2 qualified leads* out of *20,*'],
  [t2(25.14), t2(30.2), 'you\'re paying *$600* for each qualified lead.'],
  [t2(30.44), t2(38.55), 'While the $120 leads might give you *6 qualified leads* from the same *20 leads.*'],
  [t2(38.82), t2(43.3), 'Now your cost per qualified lead is only *$400.*'],
  [t2(43.54), t2(48.95), 'So the campaign with the *higher CPL*'],
  [t2(49.0), t2(54.3), 'is actually generating *better-quality leads* at a *lower cost.*'],
  [t3(0.94), t3(4.95), 'That\'s why I don\'t judge Google Ads by *CPL alone.*'],
  [t3(5.14), t3(11.7), 'I want to know how many leads actually become *qualified,* *booked opportunities* — and eventually, *revenue.*'],
  [t3(11.94), t3(17.95), 'Your Google Ads data needs to connect with your *CRM* and your *actual sales outcomes.*'],
  [t3(18.22), t3(21.85), 'Because until you make that connection,'],
  [t3(22.0), t3(26.9), 'a "profitable" Google Ads campaign may only be *profitable on paper.*'],
  [t3(27.12), t3(34.5), 'So compare your *Google Ads conversions* with your *qualified and booked leads* this month.'],
  [t3(34.8), t3(37.6), 'Do they tell the *same story?*'],
];
function captions(t) {
  for (const [s, e, txt] of CAPS) {
    if (t < s - .02 || t > e + .35) continue;
    const a = P(t, s, .3) * (1 - P(t, e, .3));
    if (a <= 0) continue;
    const dy = (1 - P(t, s, .45, E.out5)) * 14;
    drawCaption(txt, a, dy);
  }
}
function drawCaption(txt, a, dy) {
  const size = V ? 46 : 40, maxW = V ? 900 : 1480, lh = size * 1.3;
  const words = [];
  txt.split(/(\*[^*]+\*)/).filter(Boolean).forEach(seg => {
    const hl = seg.startsWith('*');
    seg.replace(/\*/g, '').split(' ').filter(Boolean).forEach(w => words.push({ w, hl }));
  });
  const sp = M(' ', size, 600);
  const wid = x => M(x.w, size, x.hl ? 800 : 560);
  const lines = []; let cur = [], cw = 0;
  for (const x of words) {
    const ww = wid(x);
    if (cur.length && cw + sp + ww > maxW) { lines.push([cur, cw]); cur = []; cw = 0; }
    cw += (cur.length ? sp : 0) + ww; cur.push(x);
  }
  if (cur.length) lines.push([cur, cw]);
  const bw = Math.max(...lines.map(l => l[1])) + (V ? 64 : 72), bh = lines.length * lh + (V ? 40 : 34);
  const cy = (V ? 1530 : 968) + dy;
  const bx = W / 2 - bw / 2, by = cy - bh / 2;
  withA(a, () => {
    card(bx, by, bw, bh, { r: 20, fill: 'rgba(255,255,255,0.94)', stroke: 'rgba(225,235,233,0.9)', sh: .7 });
    lines.forEach(([ws, lw], i) => {
      let x = W / 2 - lw / 2; const y = by + (V ? 20 : 17) + lh * i + lh * .5 + size * .35;
      ws.forEach((q, j) => {
        T(q.w, x, y, { size, w: q.hl ? 800 : 560, c: q.hl ? C.deep : C.ink });
        x += wid(q) + (j < ws.length - 1 ? sp : 0);
      });
    });
  });
}

// =====================================================================
// SCENE 1 — THE HOOK
// =====================================================================
const S1 = {
  metrics: [['CLICKS', 4812], ['CALLS', 126], ['FORMS', 214], ['CONVERSIONS', 340]],
  hl: [15.12, 16.02, 16.82, 17.56],
};
function chartData(i, n) { const x = i / (n - 1); return .22 + .58 * x + .06 * Math.sin(i * 1.7) + .035 * Math.sin(i * 3.3 + 1); }

function scene1(t, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const out = 1 - alpha;
  if (V) ctx.translate(0, -out * 70); else ctx.translate(-out * 110, 0);

  const D = V ? { x: 70, y: 240, w: 940, h: 1050 } : { x: 250, y: 150, w: 1420, h: 690 };
  const N = V
    ? [{ x: 190, y: 300, w: 700, h: 180 }, { x: 190, y: 640, w: 700, h: 180 }, { x: 190, y: 980, w: 700, h: 180 }]
    : [{ x: 160, y: 400, w: 380, h: 170 }, { x: 770, y: 400, w: 380, h: 170 }, { x: 1380, y: 400, w: 380, h: 170 }];

  const morph = P(t, 19.7, 1.1, E.io);
  const contentA = 1 - P(t, 19.6, .45);
  const appear = P(t, 0.05, .9, E.out5);

  // ---- dashboard (morphs into the "Google Ads" node) ----
  {
    const zoom = 1 + .035 * P(t, 10.6, 3.6, E.io) * (1 - morph);
    const R = {
      x: lerp(D.x, N[0].x, morph), y: lerp(D.y, N[0].y, morph),
      w: lerp(D.w, N[0].w, morph), h: lerp(D.h, N[0].h, morph)
    };
    ctx.save();
    xform(D.x + D.w / 2, D.y + D.h * (V ? .3 : .35), zoom * lerp(.97, 1, appear), 0, (1 - appear) * 30);
    ctx.globalAlpha *= appear;
    card(R.x, R.y, R.w, R.h, { r: lerp(26, 22, morph) });
    if (contentA > 0) withA(contentA, () => dashContent(t, D));
    ctx.restore();
  }

  // ---- business result card (the contradiction) ----
  const la = win(t, 4.35, 9.7, .6, .6);
  if (la > 0) {
    const B = V ? { x: 420, y: 1110, w: 590, h: 230 } : { x: 1390, y: 610, w: 430, h: 215 };
    const dy = (1 - P(t, 4.35, .7, E.out5)) * 24;
    withA(la, () => {
      card(B.x, B.y + dy, B.w, B.h, { r: 22, sh: 1.5 });
      T('ACTUAL BUSINESS RESULT', B.x + 32, B.y + dy + 50, { size: V ? 17 : 15, w: 700, c: C.mut, ls: 1.6 });
      T('−$3,240', B.x + 32, B.y + dy + (V ? 140 : 130), { size: V ? 74 : 64, w: 800, c: C.ink, ls: -1.5 });
      T('net, after sales & fulfilment', B.x + 32, B.y + dy + (V ? 188 : 175), { size: V ? 21 : 18, w: 500, c: C.mut });
      // down arrow, charcoal (no extra colors)
      const ax = B.x + B.w - 60, ay = B.y + dy + (V ? 108 : 100);
      ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath(); ctx.moveTo(ax, ay - 22); ctx.lineTo(ax, ay + 20); ctx.moveTo(ax - 14, ay + 6); ctx.lineTo(ax, ay + 20); ctx.lineTo(ax + 14, ay + 6); ctx.stroke(); ctx.restore();
    });
  }

  // ---- flow: Google Ads -> Leads -> ??? ----
  const na = P(t, 20.4, .5);
  if (na > 0) {
    nodeLabel(N[0], 'SOURCE', 'Google Ads', '4,812 clicks', na);
    const bA = P(t, 20.9, .6, E.out5);
    if (bA > 0) {
      withA(bA, () => {
        ctx.save(); xform(N[1].x + N[1].w / 2, N[1].y + N[1].h / 2, lerp(.94, 1, bA)); card(N[1].x, N[1].y, N[1].w, N[1].h); ctx.restore();
        nodeLabel(N[1], 'CAPTURED', 'Leads', fmt(340 * P(t, 21.1, 1.0)) + ' leads', 1);
      });
    }
    const cA = P(t, 22.5, .7);
    if (cA > 0) {
      withA(cA, () => {
        card(N[2].x, N[2].y, N[2].w, N[2].h, { fill: 'rgba(255,255,255,0.45)', stroke: C.faint, dashed: true, sh: 0, sw: 2 });
        const pulse = 1 + .03 * Math.sin((t - 28.3) * 4) * win(t, 28.3, 31, .3, .5);
        ctx.save(); xform(N[2].x + N[2].w / 2, N[2].y + N[2].h / 2, pulse);
        nodeLabel(N[2], 'BUSINESS OUTCOME', 'Paying customers', '???', 1, true);
        ctx.restore();
      });
    }
    // connectors
    const [a0, a1] = edge(N[0], N[1]), [b0, b1] = edge(N[1], N[2]);
    line(a0.x, a0.y, a1.x, a1.y, { p: P(t, 21.1, .7, E.io), lw: 3 });
    pulses(a0.x, a0.y, a1.x, a1.y, t, { a: P(t, 21.9, .5), period: 1.3 });
    const dp = P(t, 22.6, .8, E.io);
    // dashed line with a visible gap (the missing connection)
    const g1 = .42, g2 = .64;
    if (dp > 0) {
      line(b0.x, b0.y, lerp(b0.x, b1.x, Math.min(dp, g1)), lerp(b0.y, b1.y, Math.min(dp, g1)), { c: C.acc, lw: 3, dash: [2, 9] });
      if (dp > g2) line(lerp(b0.x, b1.x, g2), lerp(b0.y, b1.y, g2), lerp(b0.x, b1.x, dp), lerp(b0.y, b1.y, dp), { c: C.faint, lw: 3, dash: [2, 9] });
    }
    pulses(b0.x, b0.y, b1.x, b1.y, t, { a: P(t, 24.6, .5), stop: g1, period: 1.3 });
    // gap marker
    const gm = P(t, 26.9, .5, E.back);
    if (gm > 0) {
      const gx = lerp(b0.x, b1.x, (g1 + g2) / 2), gy = lerp(b0.y, b1.y, (g1 + g2) / 2);
      withA(gm, () => {
        ctx.save(); xform(gx, gy, gm);
        if (V) chip('NO DATA', gx + 26, gy, { size: 17, fill: '#fff', stroke: C.faint, c: C.ink, ls: 1.5 });
        else chip('NO DATA', gx, gy - 46, { size: 15, fill: '#fff', stroke: C.faint, c: C.ink, ls: 1.5, al: 'center' });
        ctx.beginPath(); ctx.arc(gx, gy, 9, 0, 7); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 2; ctx.stroke();
        ctx.restore();
      });
    }
    // the question
    const q1 = P(t, 28.5, .7, E.out5), q2 = P(t, 29.3, .7, E.out5);
    const qy = V ? 1295 : 250;
    T('The platform sees the lead.', W / 2, qy + (1 - q1) * 16, { size: V ? 44 : 46, w: 650, c: C.deep, al: 'center', a: q1 });
    T('Does it see the business result?', W / 2, qy + (V ? 64 : 66) + (1 - q2) * 16, { size: V ? 46 : 50, w: 800, c: C.ink, al: 'center', a: q2, ls: -.5 });
  }
  ctx.restore();
}
function edge(A, B) { // connector points between two node rects (horizontal in L, vertical in V)
  if (V) return [{ x: A.x + A.w / 2, y: A.y + A.h + 6 }, { x: B.x + B.w / 2, y: B.y - 6 }];
  return [{ x: A.x + A.w + 6, y: A.y + A.h / 2 }, { x: B.x - 6, y: B.y + B.h / 2 }];
}
function nodeLabel(N, k, title, val, a, ghost = false) {
  const s = V ? 1.12 : 1;
  T(k, N.x + 30, N.y + 44 * s, { size: 14 * s, w: 700, c: ghost ? C.faint : C.mut, ls: 1.8, a });
  T(title, N.x + 30, N.y + 92 * s, { size: 32 * s, w: 750, c: ghost ? C.mut : C.ink, a, ls: -.5 });
  T(val, N.x + 30, N.y + 134 * s, { size: 22 * s, w: ghost ? 800 : 600, c: ghost ? C.mut : C.deep, a, ls: ghost ? 4 : 0 });
}
function dashContent(t, D) {
  const pad = V ? 34 : 40;
  // header
  const hx = D.x + pad, hy = D.y + (V ? 58 : 56);
  rr(hx, hy - 22, 44, 44, 12); ctx.fillStyle = C.soft; ctx.fill();
  [[8, 18], [18, 26], [28, 34]].forEach(([dx, hh]) => { rr(hx + dx, hy + 14 - hh * .7, 7, hh * .7, 2); ctx.fillStyle = C.acc; ctx.fill(); });
  T('Google Ads', hx + 60, hy + 2, { size: V ? 28 : 26, w: 750, c: C.ink });
  T('Campaign overview', hx + 60, hy + 26, { size: V ? 18 : 16, w: 500, c: C.mut });
  const stA = P(t, 1.6, .5, E.back);
  let rx = D.x + D.w - pad;
  withA(stA, () => { rx -= chip('PROFITABLE', rx, hy, { size: V ? 17 : 15, al: 'right', dot: true, ls: 1.5 }) + 12; });
  if (!V) {
    withA(stA, () => { rx -= chip('ROAS 4.2×', rx, hy, { size: 15, al: 'right', fill: null, stroke: C.acc, c: C.deep, ls: .5 }) + 12; });
    chip('Last 30 days', rx, hy, { size: 15, al: 'right', fill: null, stroke: C.line, c: C.mut, w: 600, ls: .2 });
  }

  // metric tiles
  const cols = V ? 2 : 4, gap = V ? 22 : 22;
  const mw = (D.w - pad * 2 - gap * (cols - 1)) / cols, mh = V ? 210 : 170;
  const my0 = D.y + (V ? 120 : 112);
  S1.metrics.forEach(([k, v], i) => {
    const cx = D.x + pad + (i % cols) * (mw + gap), cy = my0 + Math.floor(i / cols) * (mh + gap);
    const ap = P(t, .45 + i * .14, .6, E.out5);
    const hl = P(t, S1.hl[i] - .05, .35, E.out);
    const lift = hl * 6;
    withA(ap, () => {
      ctx.save(); ctx.translate(0, (1 - ap) * 20 - lift);
      card(cx, cy, mw, mh, { r: 18, sh: .35 + hl * .8, stroke: hl > 0 ? `rgba(25,195,177,${.25 + hl * .75})` : C.line, sw: 1.5 + hl * 1.5 });
      T(k, cx + 26, cy + (V ? 46 : 40), { size: V ? 17 : 14, w: 700, c: hl > .5 ? C.deep : C.mut, ls: 1.6 });
      const val = v * P(t, .6 + i * .14, 1.6, E.out);
      T(fmt(val), cx + 24, cy + (V ? 128 : 104), { size: V ? 66 : 50, w: 800, c: C.ink, ls: -1.5 });
      chip('▲ ' + [18, 12, 22, 16][i] + '%', cx + 26, cy + mh - (V ? 38 : 32), { size: V ? 16 : 13, h: V ? 30 : 26, pad: 10, ls: .3 });
      // sparkline
      const sx = cx + mw - (V ? 150 : 120), sy = cy + mh - (V ? 40 : 34), sw = V ? 120 : 92, sh = V ? 60 : 46;
      ctx.beginPath();
      for (let j = 0; j < 12; j++) { const px = sx + sw * j / 11, py = sy - sh * chartData(j + i * 3, 12) * .9; j ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
      ctx.strokeStyle = C.acc; ctx.lineWidth = 2.5; ctx.lineJoin = 'round'; ctx.stroke();
      if (hl > 0) { check(cx + mw - 34, cy + (V ? 40 : 34), 16, C.deep, 3); }
      ctx.restore();
    });
  });

  // conversions chart
  const cy0 = my0 + (V ? 2 * (mh + gap) + 18 : mh + 34), chh = D.y + D.h - cy0 - pad;
  const cx0 = D.x + pad, cw = D.w - pad * 2;
  const ca = P(t, 1.0, .6);
  withA(ca, () => {
    T('Conversions', cx0, cy0 + 22, { size: V ? 20 : 17, w: 650, c: C.ink });
    T('Daily · last 30 days', cx0 + (V ? 136 : 116), cy0 + 22, { size: V ? 18 : 15, w: 500, c: C.faint });
    const gy0 = cy0 + 50, gh = chh - 60;
    for (let k = 0; k <= 3; k++) line(cx0, gy0 + gh * k / 3, cx0 + cw, gy0 + gh * k / 3, { c: C.line, lw: 1 });
    const n = 30, prog = P(t, 1.1, 2.6, E.io);
    const pts = []; for (let i = 0; i < n; i++) pts.push([cx0 + cw * i / (n - 1), gy0 + gh - gh * chartData(i, n) * .95]);
    ctx.save(); ctx.beginPath(); ctx.rect(cx0 - 10, gy0 - 10, (cw + 20) * prog, gh + 20); ctx.clip();
    ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]));
    ctx.lineTo(cx0 + cw, gy0 + gh); ctx.lineTo(cx0, gy0 + gh); ctx.closePath();
    const gr = ctx.createLinearGradient(0, gy0, 0, gy0 + gh); gr.addColorStop(0, 'rgba(25,195,177,0.18)'); gr.addColorStop(1, 'rgba(25,195,177,0.0)');
    ctx.fillStyle = gr; ctx.fill();
    ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]));
    ctx.strokeStyle = C.acc; ctx.lineWidth = 3.5; ctx.lineJoin = 'round'; ctx.stroke();
    ctx.restore();
    if (prog >= 1) {
      const lp = pts[n - 1];
      const bl = .5 + .5 * Math.sin(t * 3);
      ctx.beginPath(); ctx.arc(lp[0], lp[1], 7 + bl * 4, 0, 7); ctx.fillStyle = 'rgba(25,195,177,0.18)'; ctx.fill();
      ctx.beginPath(); ctx.arc(lp[0], lp[1], 6, 0, 7); ctx.fillStyle = C.acc; ctx.fill();
    }
  });
}

// =====================================================================
// SCENE 2 — THE TWIST
// =====================================================================
const CA = { name: 'CAMPAIGN A', cpl: 60, spend: '$1,200', q: 2, cpq: 600 };
const CB = { name: 'CAMPAIGN B', cpl: 120, spend: '$2,400', q: 6, cpq: 400 };

function campState(t, isB) {
  const s = {};
  s.a = P(t, t2(isB ? 1.0 : .55), .8, E.out5);
  s.cpl = isB ? P(t, t2(9.7), 1.0) : P(t, t2(4.9), .9);
  const elevA = P(t, t2(12.7), .6) * (1 - P(t, t2(16.85), .5));
  const winB = P(t, t2(41.9), .6, E.out5);
  s.elev = isB ? winB : elevA;
  const pause = P(t, t2(16.8), .35) * (1 - P(t, t2(18.3), .4));
  s.pause = pause;
  let dim = 0;
  if (isB) { dim = Math.max(elevA * .5, win(t, t2(18.6), t2(30.4), .5, .5) * .45); }
  else { dim = Math.max(win(t, t2(30.5), t2(41.9), .5, .3) * .4, winB * .5); }
  s.dim = dim;
  s.badge = isB ? winB : P(t, t2(14.2), .5, E.back) * (1 - P(t, t2(16.85), .4));
  s.badgeText = isB ? 'LOWER COST / QUALIFIED LEAD' : 'LOWER CPL';
  s.dots = isB ? P(t, t2(31.2), 1.0, E.lin) : P(t, t2(19.5), 1.0, E.lin);
  s.qT = isB ? t2(34.6) : t2(22.1);
  s.lbl20 = isB ? P(t, t2(31.2), .5) : P(t, t2(19.5), .5);
  s.lblQ = isB ? P(t, t2(34.8), .5, E.back) : P(t, t2(22.3), .5, E.back);
  s.calc = isB ? P(t, t2(39.2), .6) : P(t, t2(25.3), .6);
  s.res = isB ? P(t, t2(41.2), 1.0) : P(t, t2(26.2), .9);
  s.resPop = isB ? Math.sin(clamp((t - t2(41.94)) / .5) * Math.PI) : 0;
  s.loser = isB ? 0 : winB;
  s.exit = P(t, t2(43.3), .8, E.io);
  return s;
}

function drawCampaign(t, B, d, s) {
  const a = s.a * (1 - s.exit);
  if (a <= 0) return;
  ctx.save();
  const sc = (1 + .025 * s.elev) * (1 - .015 * s.pause) * (1 - .04 * s.exit) * lerp(.97, 1, s.a);
  xform(B.x + B.w / 2, B.y + B.h / 2, sc, 0, (1 - s.a) * 40);
  ctx.globalAlpha *= a * (1 - s.dim);
  card(B.x, B.y, B.w, B.h, { r: 26, sh: 1 + s.elev, stroke: s.elev > 0 ? `rgba(25,195,177,${.3 + .7 * s.elev})` : C.line, sw: 1.5 + 1.5 * s.elev });
  const u = V ? 1 : 1, px = B.x + (V ? 40 : 46), pr = B.x + B.w - (V ? 40 : 46);
  // header
  const hy = B.y + (V ? 52 : 58);
  T(d.name, px, hy + 6, { size: V ? 20 : 18, w: 750, c: C.mut, ls: 2.4 });
  if (s.badge > 0) withA(s.badge, () => { ctx.save(); xform(pr, hy, lerp(.85, 1, s.badge)); chip(s.badgeText, pr, hy, { size: V ? 16 : 14, al: 'right', tick: true, fill: C.acc, c: '#fff', ls: 1.2 }); ctx.restore(); });

  // CPL
  const cplY = B.y + (V ? 150 : 205);
  if (!V) T('COST PER LEAD', px, B.y + 116, { size: 14, w: 700, c: C.faint, ls: 1.6 });
  const cplVal = s.cpl > 0 ? '$' + fmt(d.cpl * s.cpl) : '$ —';
  const cplSize = V ? 96 : 104;
  const cplC = s.loser > 0 ? C.mut : C.ink;
  T(cplVal, px, cplY, { size: cplSize, w: 800, c: cplC, ls: -3 });
  T('CPL', px + M(cplVal, cplSize, 800, -3) + 14, cplY, { size: V ? 34 : 34, w: 700, c: C.mut, ls: 1 });
  if (V) T('COST PER LEAD', pr, cplY - 8, { size: 15, w: 700, c: C.faint, ls: 1.6, al: 'right' });

  line(px, B.y + (V ? 182 : 248), pr, B.y + (V ? 182 : 248), { c: C.line, lw: 1.5 });

  // leads -> qualified
  const ly = B.y + (V ? 232 : 300);
  T('20 leads', px, ly, { size: V ? 26 : 24, w: 650, c: C.ink, a: s.lbl20 });
  if (s.lblQ > 0) {
    runs([{ s: String(d.q), size: V ? 56 : 46, w: 800, c: C.head }, { s: '  QUALIFIED', size: V ? 20 : 18, w: 750, c: C.deep, ls: 1.8 }], pr, ly + (V ? 8 : 6), { al: 'right', a: s.lblQ });
  }
  const dr = V ? 19 : 18, dsp = V ? 56 : 58, dy0 = B.y + (V ? 280 : 350);
  for (let i = 0; i < 20; i++) {
    const row = Math.floor(i / 10), col = i % 10;
    const cx = px + dr + col * dsp, cy = dy0 + row * (V ? 50 : 54);
    const ap = clamp((s.dots * 20 - i) * 1.0);
    if (ap <= 0) continue;
    const qIdx = d.q === 2 ? [3, 14] : [1, 4, 8, 11, 15, 18];
    const qi = qIdx.indexOf(i);
    const q = qi >= 0 ? P(t, s.qT + qi * .13, .4, E.back) : 0;
    ctx.save(); ctx.globalAlpha *= ap;
    ctx.beginPath(); ctx.arc(cx, cy, dr * lerp(.6, 1, ap) * (1 + .12 * Math.sin(clamp(q) * Math.PI)), 0, 7);
    ctx.fillStyle = q > 0 ? `rgba(25,195,177,${clamp(q)})` : C.gray; ctx.fill();
    if (q <= 0) { ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke(); }
    if (q > .3) check(cx, cy, dr * .9, '#fff', 3);
    ctx.restore();
  }

  line(px, B.y + (V ? 372 : 476), pr, B.y + (V ? 372 : 476), { c: C.line, lw: 1.5, a: s.calc });
  // calc
  const cy1 = B.y + (V ? 425 : 530);
  if (s.calc > 0) {
    runs([
      { s: d.spend, size: V ? 28 : 26, w: 750, c: C.ink }, { s: ' ad spend  ', size: V ? 24 : 22, w: 500, c: C.mut },
      { s: '÷  ', size: V ? 28 : 26, w: 600, c: C.deep }, { s: String(d.q), size: V ? 28 : 26, w: 800, c: C.deep }, { s: ' qualified', size: V ? 24 : 22, w: 500, c: C.mut },
    ], px, cy1 + (1 - s.calc) * 10, { al: 'left', a: s.calc });
  }
  if (s.res > 0) {
    const isWin = d.cpq === 400 && t > t2(41.9);
    const rc = s.loser > 0 ? C.mut : (isWin ? C.head : C.ink);
    const rs = (V ? 76 : 70) * (1 + .08 * s.resPop);
    const rv = '$' + fmt(d.cpq * s.res);
    const ry = B.y + (V ? 522 : 630);
    T('=', px, ry - (V ? 14 : 12), { size: V ? 40 : 36, w: 600, c: C.faint, a: s.res });
    T(rv, px + (V ? 40 : 38), ry, { size: rs, w: 800, c: rc, ls: -2.5, a: s.res });
    T('/ qualified lead', px + (V ? 52 : 50) + M(rv, rs, 800, -2.5), ry, { size: V ? 26 : 24, w: 650, c: s.loser > 0 ? C.faint : C.deep, a: s.res });
  }
  ctx.restore();
}

function scene2(t, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const inP = P(t, O2 - .2, 1.0, E.io);
  if (V) ctx.translate(0, (1 - inP) * 60); else ctx.translate((1 - inP) * 90, 0);
  ctx.translate(0, 0);
  const A = V ? { x: 60, y: 235, w: 960, h: 560 } : { x: 150, y: 160, w: 740, h: 690 };
  const B = V ? { x: 60, y: 825, w: 960, h: 560 } : { x: 1030, y: 160, w: 740, h: 690 };

  // illustrative scenario tag
  const tagA = P(t, t2(.8), .6) * (1 - P(t, t2(54.6), .5));
  chip('ILLUSTRATIVE SCENARIO', W / 2, V ? 196 : 118, { size: V ? 15 : 13, al: 'center', fill: '#fff', stroke: C.line, c: C.mut, ls: 2, a: tagA, dot: true });

  const sa = campState(t, false), sb = campState(t, true);
  // draw the dominant one last
  if (t > t2(41.9)) { drawCampaign(t, A, CA, sa); drawCampaign(t, B, CB, sb); }
  else { drawCampaign(t, B, CB, sb); drawCampaign(t, A, CA, sa); }
  // VS marker
  const vsA = Math.min(sa.a, sb.a) * (1 - sa.exit);
  if (vsA > 0) {
    const vx = V ? W / 2 : W / 2, vy = V ? 810 : 505;
    withA(vsA, () => { ctx.beginPath(); ctx.arc(vx, vy, 30, 0, 7); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke(); });
    T('VS', vx, vy + 1, { size: 15, w: 800, c: C.mut, al: 'center', bl: 'middle', ls: 1.5, a: vsA });
  }

  // ---- final payoff ----
  const fa = P(t, t2(43.9), .8, E.out5);
  if (fa > 0) {
    const FA = V ? { x: 80, y: 255, w: 920, h: 360 } : { x: 330, y: 165, w: 590, h: 400 };
    const FB = V ? { x: 80, y: 645, w: 920, h: 360 } : { x: 1000, y: 165, w: 590, h: 400 };
    finalCard(t, FA, CA, P(t, t2(44.0), .8, E.out5), false);
    finalCard(t, FB, CB, P(t, t2(44.45), .8, E.out5), true);
    const ma = P(t, t2(47.7), .8, E.out5);
    if (ma > 0) {
      if (!V) {
        runs([{ s: 'HIGHER CPL', size: 78, w: 800, c: C.ink }, { s: '  ≠  ', size: 92, w: 700, c: C.head }, { s: 'WORSE PERFORMANCE', size: 78, w: 800, c: C.ink }], W / 2, 720 + (1 - ma) * 24, { al: 'center', a: ma, ls: -1.5 });
        T('Illustrative scenario · same 20 leads per campaign', W / 2, 790, { size: 18, w: 500, c: C.faint, al: 'center', a: P(t, t2(49), .6) });
      } else {
        T('HIGHER CPL', W / 2, 1125 + (1 - ma) * 24, { size: 92, w: 800, c: C.ink, al: 'center', a: ma, ls: -2 });
        T('≠', W / 2, 1238 + (1 - ma) * 24, { size: 110, w: 700, c: C.head, al: 'center', a: P(t, t2(48.1), .6, E.out5) });
        T('WORSE PERFORMANCE', W / 2, 1345 + (1 - ma) * 24, { size: 76, w: 800, c: C.ink, al: 'center', a: P(t, t2(48.4), .7, E.out5), ls: -2 });
        T('Illustrative scenario · same 20 leads per campaign', W / 2, 1405, { size: 22, w: 500, c: C.faint, al: 'center', a: P(t, t2(49), .6) });
      }
    }
  }
  ctx.restore();
}
function finalCard(t, B, d, a, win) {
  if (a <= 0) return;
  const glow = win ? P(t, t2(50.6), .6) : 0;
  const pop = win ? Math.sin(clamp((t - t2(53.3)) / .5) * Math.PI) : 0;
  ctx.save(); xform(B.x + B.w / 2, B.y + B.h / 2, lerp(.95, 1, a) * (win ? 1.02 : 1), 0, (1 - a) * 30); ctx.globalAlpha *= a;
  card(B.x, B.y, B.w, B.h, { r: 26, sh: win ? 1.6 : .8, stroke: win ? `rgba(25,195,177,${.5 + .5 * glow})` : C.line, sw: win ? 3 : 1.5 });
  const px = B.x + (V ? 44 : 44);
  T(d.name, px, B.y + 64, { size: V ? 20 : 18, w: 750, c: C.mut, ls: 2.4 });
  T('$' + d.cpl + ' CPL', B.x + B.w - 44, B.y + 64, { size: V ? 28 : 24, w: 700, c: win ? C.ink : C.mut, al: 'right' });
  line(px, B.y + 96, B.x + B.w - 44, B.y + 96, { c: C.line, lw: 1.5 });
  T('COST PER QUALIFIED LEAD', px, B.y + 146, { size: V ? 17 : 15, w: 700, c: C.faint, ls: 1.6 });
  const v = '$' + fmt(d.cpq * P(t, t2(win ? 44.6 : 44.2), .9));
  const vs = (V ? 130 : 120) * (1 + .06 * pop);
  T(v, px - 4, B.y + (V ? 280 : 290), { size: vs, w: 800, c: win ? C.head : C.mut, ls: -4 });
  if (V) T('/ qualified lead', px + M(v, vs, 800, -4) + 14, B.y + 280, { size: 28, w: 650, c: win ? C.deep : C.faint });
  else T('/ qualified lead', px, B.y + 345, { size: 24, w: 650, c: win ? C.deep : C.faint });
  T(d.q + ' of 20 leads qualified', B.x + B.w - 44, B.y + (V ? 330 : 345), { size: V ? 22 : 20, w: 600, c: win ? C.deep : C.faint, al: 'right' });
  if (win) chip('BETTER', B.x + B.w - 44, B.y + (V ? 190 : 200), { size: V ? 16 : 14, al: 'right', tick: true, fill: C.acc, c: '#fff', ls: 1.4, a: P(t, t2(45.2), .5, E.back) });
  ctx.restore();
}

// =====================================================================
// SCENE 3 — THE INSIGHT
// =====================================================================
const FLOW = [
  ['GOOGLE ADS', 'Clicks & conversions', 5.3], ['LEAD', 'Call or form', 6.5], ['QUALIFIED', 'Right fit', 7.7],
  ['BOOKED', 'Sales call booked', 8.55], ['REVENUE', 'Closed deal', 10.8]];
const LINKS = ['Tracking', 'CRM', 'Sales', 'Attribution'];

function flowRects() {
  if (V) return FLOW.map((f, i) => ({ x: 230, y: 250 + i * 218, w: 660, h: 150 }));
  return FLOW.map((f, i) => ({ x: 150 + i * 340, y: 360, w: 260, h: 160 }));
}
function scene3(t, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const lt = t - O3;

  // --- a) CPL alone ---
  const ca = P(lt, .95, .7, E.out5) * (1 - P(lt, 5.0, .6));
  if (ca > 0) {
    const w = V ? 600 : 520, h = V ? 280 : 240, x = W / 2 - w / 2, y = (V ? 720 : 400) - h / 2 + (1 - P(lt, .95, .7, E.out5)) * 30 - P(lt, 5.0, .6) * 30;
    withA(ca, () => {
      card(x, y, w, h, { r: 28, sh: 1.2 });
      T('COST PER LEAD', W / 2, y + 62, { size: V ? 18 : 15, w: 700, c: C.faint, ls: 2, al: 'center' });
      runs([{ s: '$60', size: V ? 120 : 104, w: 800, c: C.ink, ls: -3 }, { s: ' CPL', size: V ? 44 : 38, w: 700, c: C.mut }], W / 2, y + (V ? 200 : 175), { al: 'center' });
      const al = P(lt, 4.1, .5, E.back);
      chip('ONLY ONE METRIC', W / 2, y + h + 46, { size: V ? 18 : 15, al: 'center', fill: '#fff', stroke: C.faint, c: C.ink, ls: 1.6, a: al });
    });
  }

  // --- b) full funnel ---
  const fa = P(lt, 5.2, .5) * (1 - P(lt, 11.9, .6));
  if (fa > 0) withA(fa, () => {
    const R = flowRects();
    R.forEach((r, i) => {
      const ap = P(lt, FLOW[i][2], .6, E.out5);
      if (ap <= 0) return;
      const biz = i >= 2;
      withA(ap, () => {
        ctx.save(); xform(r.x + r.w / 2, r.y + r.h / 2, lerp(.92, 1, ap), V ? 0 : 0, (1 - ap) * 18);
        const final = i === 4;
        card(r.x, r.y, r.w, r.h, { r: 20, sh: final ? 1.4 : 1, stroke: final ? C.acc : C.line, sw: final ? 2.5 : 1.5 });
        const s = V ? 1.08 : 1;
        T('0' + (i + 1), r.x + 26, r.y + 42 * s, { size: 15 * s, w: 750, c: C.acc, ls: 1.5 });
        T(FLOW[i][0], r.x + 26, r.y + 92 * s, { size: (V ? 34 : 28) , w: 800, c: final ? C.head : C.ink, ls: .5 });
        T(FLOW[i][1], r.x + 26, r.y + 128 * s, { size: 17 * s, w: 500, c: C.mut });
        if (i === 4) {
          const ix = r.x + r.w - 46, iy = r.y + 46 * s; // revenue glyph
          ctx.beginPath(); ctx.arc(ix, iy, 18, 0, 7); ctx.fillStyle = C.soft; ctx.fill();
          T('$', ix, iy + 1, { size: 20, w: 800, c: C.deep, al: 'center', bl: 'middle' });
        }
        ctx.restore();
      });
      if (i > 0) {
        const [p0, p1] = edge(R[i - 1], r);
        line(p0.x, p0.y, p1.x, p1.y, { p: P(lt, FLOW[i][2] - .25, .45, E.io), lw: 3 });
        pulses(p0.x, p0.y, p1.x, p1.y, t, { a: P(lt, FLOW[i][2] + .2, .4), n: 2, period: 1.1, r: 5 });
        const la = P(lt, FLOW[i][2] + .1, .5);
        if (!V) chip(LINKS[i - 1], (p0.x + p1.x) / 2, r.y - 34, { size: 13, al: 'center', fill: '#fff', stroke: C.line, c: C.deep, w: 650, ls: .8, a: la });
        else chip(LINKS[i - 1], p0.x + 26, (p0.y + p1.y) / 2, { size: 16, fill: '#fff', stroke: C.line, c: C.deep, w: 650, ls: .8, a: la });
      }
    });
    // brackets
    const b1 = P(lt, 9.4, .6), b2 = P(lt, 10.9, .6);
    if (!V) {
      const by = R[0].y + R[0].h + 46;
      bracketH(R[0].x, R[1].x + R[1].w, by, 'WHAT GOOGLE ADS SEES', C.mut, b1);
      bracketH(R[2].x, R[4].x + R[4].w, by, 'WHAT YOUR BUSINESS NEEDS TO SEE', C.deep, b2);
    } else {
      bracketV(R[0].y, R[1].y + R[1].h, 160, 'GOOGLE ADS SEES', C.mut, b1);
      bracketV(R[2].y, R[4].y + R[4].h, 160, 'YOUR BUSINESS NEEDS', C.deep, b2);
    }
  });

  // --- c) CRM connection ---
  const ra = P(lt, 12.2, .8, E.out5) * (1 - P(lt, 21.4, .6));
  if (ra > 0) withA(ra, () => crmScene(t, lt));

  // --- d) PROFITABLE? -> split ---
  const pa = P(lt, 21.95, .6, E.out5) * (1 - P(lt, 34.4, .6));
  if (pa > 0) withA(pa, () => profitScene(t, lt));

  // --- f) CTA ---
  const qa = P(lt, 34.85, .8, E.out5);
  if (qa > 0) withA(qa, () => ctaScene(t, lt));
  ctx.restore();
}
function bracketH(x1, x2, y, label, c, a) {
  if (a <= 0) return;
  withA(a, () => {
    ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = 2; ctx.globalAlpha *= .7;
    ctx.beginPath(); ctx.moveTo(x1, y - 12); ctx.lineTo(x1, y); ctx.lineTo(x2, y); ctx.lineTo(x2, y - 12); ctx.stroke(); ctx.restore();
    T(label, (x1 + x2) / 2, y + 40, { size: 16, w: 750, c, al: 'center', ls: 2 });
  });
}
function bracketV(y1, y2, x, label, c, a) {
  if (a <= 0) return;
  withA(a, () => {
    ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = 2; ctx.globalAlpha *= .7;
    ctx.beginPath(); ctx.moveTo(x + 14, y1); ctx.lineTo(x, y1); ctx.lineTo(x, y2); ctx.lineTo(x + 14, y2); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.translate(x - 22, (y1 + y2) / 2); ctx.rotate(-Math.PI / 2);
    T(label, 0, 0, { size: 17, w: 750, c, al: 'center', ls: 2 }); ctx.restore();
  });
}

const CRM_ROWS = [
  ['Jordan Carter', [['NEW', 0], ['QUALIFIED', 14.4]], '—'],
  ['Maria Lopez', [['QUALIFIED', 0], ['BOOKED', 15.3]], '$4,800'],
  ['Alex Patel', [['UNQUALIFIED', 0]], '—'],
  ['Ryan Kim', [['BOOKED', 0], ['WON', 16.5]], '$6,200'],
  ['Sam Rivera', [['NEW', 0]], '—'],
];
function statusChip(s, x, y, a, size) {
  const st = {
    NEW: { fill: C.gray, c: C.mut }, UNQUALIFIED: { fill: C.gray, c: C.faint },
    QUALIFIED: { fill: '#fff', c: C.deep, stroke: C.acc }, BOOKED: { fill: C.soft, c: C.deep }, WON: { fill: C.acc, c: '#fff' }
  }[s];
  chip(s, x, y, { size, fill: st.fill, c: st.c, stroke: st.stroke || null, ls: 1.2, a, tick: s === 'WON' || s === 'QUALIFIED' || s === 'BOOKED', w: 700 });
}
function crmScene(t, lt) {
  const G = V ? { x: 190, y: 250, w: 700, h: 140 } : { x: 80, y: 395, w: 320, h: 150 };
  const CR = V ? { x: 60, y: 470, w: 960, h: 640 } : { x: 500, y: 190, w: 920, h: 620 };
  const RV = V ? { x: 190, y: 1190, w: 700, h: 140 } : { x: 1520, y: 395, w: 320, h: 150 };
  const ga = P(lt, 12.2, .6, E.out5), cra = P(lt, 13.6, .7, E.out5), rva = P(lt, 16.6, .6, E.out5);
  const s = V ? 1.05 : 1;
  const node = (R, k, title, val, a, hl) => withA(a, () => {
    ctx.save(); xform(R.x + R.w / 2, R.y + R.h / 2, lerp(.94, 1, a));
    card(R.x, R.y, R.w, R.h, { r: 20, stroke: hl ? C.acc : C.line, sw: hl ? 2.5 : 1.5, sh: hl ? 1.4 : 1 });
    T(k, R.x + 28, R.y + 42 * s, { size: 14 * s, w: 750, c: C.mut, ls: 1.8 });
    T(title, R.x + 28, R.y + 88 * s, { size: 30 * s, w: 800, c: hl ? C.head : C.ink });
    T(val, R.x + 28, R.y + 124 * s, { size: 20 * s, w: 650, c: C.deep });
    ctx.restore();
  });
  node(G, 'SOURCE', 'Google Ads', '340 conversions', ga, false);
  // connectors
  const strong = P(lt, 18.5, .8);
  const [g0, g1] = V ? [{ x: W / 2, y: G.y + G.h + 6 }, { x: W / 2, y: CR.y - 6 }] : [{ x: G.x + G.w + 6, y: G.y + G.h / 2 }, { x: CR.x - 6, y: G.y + G.h / 2 }];
  const [r0, r1] = V ? [{ x: W / 2, y: CR.y + CR.h + 6 }, { x: W / 2, y: RV.y - 6 }] : [{ x: CR.x + CR.w + 6, y: RV.y + RV.h / 2 }, { x: RV.x - 6, y: RV.y + RV.h / 2 }];
  line(g0.x, g0.y, g1.x, g1.y, { p: P(lt, 13.2, .5, E.io), lw: 3 + strong * 2 });
  pulses(g0.x, g0.y, g1.x, g1.y, t, { a: P(lt, 13.6, .4), n: 2, period: .9, r: 5 + strong * 2 });
  line(r0.x, r0.y, r1.x, r1.y, { p: P(lt, 16.3, .5, E.io), lw: 3 + strong * 2 });
  pulses(r0.x, r0.y, r1.x, r1.y, t, { a: P(lt, 16.7, .4), n: 2, period: .9, r: 5 + strong * 2 });

  withA(cra, () => {
    ctx.save(); xform(CR.x + CR.w / 2, CR.y + CR.h / 2, lerp(.96, 1, cra), 0, (1 - cra) * 24);
    card(CR.x, CR.y, CR.w, CR.h, { r: 26, sh: 1.3 });
    const px = CR.x + (V ? 36 : 40), pr = CR.x + CR.w - (V ? 36 : 40);
    chip('CRM', px, CR.y + 52, { size: V ? 17 : 15, fill: C.deep, c: '#fff', ls: 1.6 });
    T('Pipeline · this month', px + (V ? 90 : 80), CR.y + 60, { size: V ? 24 : 22, w: 700, c: C.ink });
    T('Lead source: Google Ads', pr, CR.y + 60, { size: V ? 18 : 16, w: 500, c: C.mut, al: 'right' });
    const hy = CR.y + 116;
    const cols = V ? [px, px + 360, pr] : [px, px + 300, px + 520, pr];
    const heads = V ? ['LEAD', 'STATUS', 'VALUE'] : ['LEAD', 'SOURCE', 'STATUS', 'VALUE'];
    heads.forEach((h, i) => T(h, cols[i], hy, { size: V ? 15 : 13, w: 700, c: C.faint, ls: 1.8, al: i === heads.length - 1 ? 'right' : 'left' }));
    line(px, hy + 18, pr, hy + 18, { c: C.line, lw: 1.5 });
    const rh = V ? 86 : 78;
    CRM_ROWS.forEach((row, i) => {
      const ra = P(lt, 13.9 + i * .16, .5, E.out5);
      if (ra <= 0) return;
      const y = hy + 30 + i * rh + rh / 2;
      withA(ra, () => {
        ctx.save(); ctx.translate((1 - ra) * 30, 0);
        // highlight on status change
        let cur = row[1][0][0], chT = -1;
        row[1].forEach(([st, at]) => { if (lt >= at) { cur = st; chT = at; } });
        const flash = chT > 0 ? win(lt, chT, chT + 1.2, .2, .8) : 0;
        if (flash > 0) { rr(px - 14, y - rh / 2 + 6, pr - px + 28, rh - 12, 12); ctx.fillStyle = `rgba(25,195,177,${.08 * flash})`; ctx.fill(); }
        ctx.beginPath(); ctx.arc(px + 20, y, 20, 0, 7); ctx.fillStyle = C.gray; ctx.fill();
        T(row[0].split(' ').map(q => q[0]).join(''), px + 20, y + 1, { size: 14, w: 700, c: C.mut, al: 'center', bl: 'middle' });
        T(row[0], px + 54, y + 8, { size: V ? 23 : 21, w: 600, c: C.ink });
        if (!V) T('Google Ads', cols[1], y + 7, { size: 18, w: 500, c: C.mut });
        const sp = chT > 0 ? P(lt, chT, .35, E.back) : 1;
        ctx.save(); xform(cols[V ? 1 : 2], y, lerp(.85, 1, sp)); statusChip(cur, cols[V ? 1 : 2], y, 1, V ? 15 : 13); ctx.restore();
        const showVal = row[2] !== '—' && (row[1].length < 2 || lt >= row[1][row[1].length - 1][1] || row[0] === 'Maria Lopez');
        T(showVal ? row[2] : '—', pr, y + 8, { size: V ? 24 : 21, w: 700, c: showVal ? C.ink : C.faint, al: 'right' });
        if (i < CRM_ROWS.length - 1) line(px, y + rh / 2, pr, y + rh / 2, { c: C.line, lw: 1 });
        ctx.restore();
      });
    });
    // funnel summary bar
    const fy = CR.y + CR.h - (V ? 70 : 64);
    const sa = P(lt, 16.8, .6);
    withA(sa, () => {
      rr(px - 6, fy - 30, pr - px + 12, 62, 14); ctx.fillStyle = C.bg; ctx.fill();
      runs([{ s: 'Revenue attributed to Google Ads  ', size: V ? 20 : 19, w: 600, c: C.mut }, { s: '$' + fmt(11000 * P(lt, 16.9, 1.0)), size: V ? 28 : 26, w: 800, c: C.head }], px + 14, fy + 9, { al: 'left' });
    });
    ctx.restore();
  });
  node(RV, 'SALES OUTCOME', 'Revenue', '$' + fmt(11000 * P(lt, 16.9, 1.0)) + ' closed', rva, true);
  // connection label
  const cl = P(lt, 18.4, .6) * (1 - P(lt, 21.2, .4));
  if (!V) chip('THE CONNECTION MOST REPORTS MISS', W / 2, 870 - 25, { size: 14, al: 'center', fill: C.deep, c: '#fff', ls: 1.8, a: cl * 0 });
}
function profitScene(t, lt) {
  const big = P(lt, 21.95, .7, E.out5), shrink = P(lt, 24.9, .9, E.io);
  // PROFITABLE?
  const y0 = V ? 760 : 470, y1 = V ? 330 : 205;
  const sz = lerp(V ? 120 : 150, V ? 64 : 56, shrink);
  const fadeTitle = 1 - P(lt, 26.0, .6);
  runs([{ s: 'PROFITABLE', size: sz, w: 800, c: C.head }, { s: '?', size: sz, w: 800, c: C.ink }], W / 2, lerp(y0, y1, shrink) + (1 - big) * 30, { al: 'center', a: big * fadeTitle, ls: -sz * .02 });
  if (shrink <= 0) return;
  const split = P(lt, 25.2, .9, E.io);
  const L = V ? { x: 90, y: 250, w: 900, h: 470 } : { x: 220, y: 230, w: 620, h: 560 };
  const R = V ? { x: 90, y: 900, w: 900, h: 470 } : { x: 1080, y: 230, w: 620, h: 560 };
  const off = (1 - split) * (V ? 220 : 260);
  const drawSide = (B, dir, title, rows, biz) => {
    ctx.save();
    if (V) ctx.translate(0, dir * -off); else ctx.translate(dir * -off, 0);
    ctx.globalAlpha *= split;
    card(B.x, B.y, B.w, B.h, { r: 26, sh: 1.2, stroke: biz ? C.acc : C.line, sw: biz ? 2.5 : 1.5 });
    const px = B.x + 44;
    T(biz ? 'WHAT THE BUSINESS NEEDS' : 'WHAT THE PLATFORM SEES', px, B.y + 56, { size: V ? 16 : 14, w: 700, c: C.faint, ls: 1.8 });
    T(title, px, B.y + (V ? 116 : 112), { size: V ? 50 : 44, w: 800, c: biz ? C.head : C.ink, ls: -1 });
    const rh = V ? 92 : 112, ry0 = B.y + (V ? 160 : 170);
    rows.forEach(([k, v, hlAt], i) => {
      const a = P(lt, 25.7 + i * .2 + (biz ? .3 : 0), .5, E.out5);
      const y = ry0 + i * rh;
      const hl = win(lt, hlAt, 34.0, .4, .4);
      withA(a, () => {
        if (hl > 0) { rr(px - 16, y + 8, B.w - 56, rh - 16, 14); ctx.fillStyle = `rgba(25,195,177,${.1 * hl})`; ctx.fill(); }
        T(k, px, y + rh / 2 + 10, { size: V ? 30 : 28, w: 600, c: C.ink });
        if (!biz) {
          T(v, B.x + B.w - 96, y + rh / 2 + 12, { size: V ? 38 : 36, w: 800, c: C.ink, al: 'right' });
          ctx.beginPath(); ctx.arc(B.x + B.w - 62, y + rh / 2, 16, 0, 7); ctx.fillStyle = C.soft; ctx.fill();
          check(B.x + B.w - 62, y + rh / 2, 13, C.deep, 3);
        } else {
          const bx = B.x + B.w - 150, bw = 102, bh = V ? 56 : 58;
          const qp = 1 + .05 * Math.sin(lt * 5) * hl;
          ctx.save(); xform(bx + bw / 2, y + rh / 2, qp);
          card(bx, y + rh / 2 - bh / 2, bw, bh, { r: 14, fill: 'rgba(255,255,255,.6)', stroke: C.faint, dashed: true, sh: 0, sw: 2 });
          T('?', bx + bw / 2, y + rh / 2 + 1, { size: V ? 36 : 34, w: 800, c: C.mut, al: 'center', bl: 'middle' });
          ctx.restore();
        }
        if (i < rows.length - 1) line(px, y + rh, B.x + B.w - 44, y + rh, { c: C.line, lw: 1 });
      });
    });
    ctx.restore();
  };
  drawSide(L, 1, 'Platform metrics', [['Clicks', '4,812', 99], ['Conversions', '340', 29.1], ['Cost per lead', '$60', 99]], false);
  drawSide(R, -1, 'Business results', [['Qualified leads', '', 30.7], ['Booked leads', '', 31.9], ['Revenue', '', 99]], true);
  // ≠
  const ne = P(lt, 26.05, .5, E.back);
  if (ne > 0) {
    const nx = W / 2, ny = V ? 810 : 510;
    withA(ne, () => {
      ctx.save(); xform(nx, ny, ne);
      ctx.beginPath(); ctx.arc(nx, ny, V ? 66 : 70, 0, 7); ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(10,26,29,.10)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 8; ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.strokeStyle = C.acc; ctx.lineWidth = 3; ctx.stroke();
      T('≠', nx, ny + 4, { size: V ? 84 : 88, w: 700, c: C.head, al: 'center', bl: 'middle' });
      ctx.restore();
    });
  }
  // "this month" chip
  const tm = P(lt, 32.9, .5, E.back);
  if (!V) chip('THIS MONTH', W / 2, 160, { size: 14, al: 'center', fill: C.deep, c: '#fff', ls: 2, a: tm, dot: false });
  else chip('THIS MONTH', W / 2, 205, { size: 16, al: 'center', fill: C.deep, c: '#fff', ls: 2, a: tm });
}
function ctaScene(t, lt) {
  const a1 = P(lt, 34.85, .8, E.out5), a2 = P(lt, 35.4, .8, E.out5), sg = P(lt, 36.7, 1.0, E.out5);
  if (!V) {
    runs([{ s: 'Do your ', size: 70, w: 750, c: C.ink }, { s: 'Google Ads conversions', size: 70, w: 800, c: C.ink }], W / 2, 380 + (1 - a1) * 20, { al: 'center', a: a1, ls: -1.5 });
    runs([{ s: 'match your ', size: 70, w: 750, c: C.ink }, { s: 'qualified & booked leads', size: 70, w: 800, c: C.head }, { s: '?', size: 70, w: 800, c: C.ink }], W / 2, 470 + (1 - a2) * 20, { al: 'center', a: a2, ls: -1.5 });
    withA(sg, () => {
      line(W / 2 - 60, 580, W / 2 + 60, 580, { c: C.acc, lw: 3, p: sg });
      const nw = M('SK Mahbub', 50, 800, -1);
      monogram(W / 2 - nw / 2 - 44, 652, 28, 1);
      T('SK Mahbub', W / 2 - nw / 2 + 0, 670, { size: 50, w: 800, c: C.ink, ls: -1 });
      T('Web Analytics & Conversion Tracking Consultant', W / 2, 722, { size: 26, w: 600, c: C.deep, al: 'center' });
    });
  } else {
    const L1 = [['Do your ', C.ink], ['Google Ads', C.ink]], L2 = [['conversions match', C.ink]], L3 = [['your ', C.ink], ['qualified &', C.head]], L4 = [['booked leads', C.head], ['?', C.ink]];
    [L1, L2, L3, L4].forEach((ln, i) => {
      const a = i < 2 ? a1 : a2;
      runs(ln.map(([s, c]) => ({ s, size: 84, w: 800, c })), W / 2, 520 + i * 104 + (1 - a) * 20, { al: 'center', a, ls: -2 });
    });
    withA(sg, () => {
      line(W / 2 - 60, 1000, W / 2 + 60, 1000, { c: C.acc, lw: 3, p: sg });
      monogram(W / 2, 1100, 44, 1);
      T('SK Mahbub', W / 2, 1220, { size: 64, w: 800, c: C.ink, al: 'center', ls: -1.5 });
      T('Web Analytics & Conversion', W / 2, 1282, { size: 34, w: 600, c: C.deep, al: 'center' });
      T('Tracking Consultant', W / 2, 1326, { size: 34, w: 600, c: C.deep, al: 'center' });
    });
  }
}

// =====================================================================
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  background(t);
  const s1a = 1 - P(t, O2 - .35, .9, E.io);
  scene1(t, s1a);
  if (t > O2 - .4 && t < O3 + 1.2) {
    const a = P(t, O2 - .2, .9, E.io) * (1 - P(t, O3 - .2, .9, E.io));
    scene2(t, a);
  }
  if (t > O3 - .2) scene3(t, P(t, O3 - .2, .6));
  captions(t);
  watermark(t);
  progress(t);
}
