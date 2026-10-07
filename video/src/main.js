// Frame compositor. window.frame(t) draws master time t and returns a JPEG data URL.
const params = new URLSearchParams(location.search);
V = params.get('v') === '1';
W = V ? 1080 : 1920;
H = V ? 1920 : 1080;
const CAPS = params.get('caps') === '1';

const cv = document.getElementById('c');
cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas');
layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');

const FADE = 0.45; // cross-dissolve half-width between scenes

function drawCaption(c, t) {
  const cue = CAPTIONS.find(([a, b]) => t >= a && t < b);
  if (!cue) return;
  const [a, b, s] = cue;
  const k = Math.min(clamp((t - a) / 0.15), clamp((b - t) / 0.15));
  const lines = s.split('\n');
  const size = 40, lh = 52;
  const w = Math.max(...lines.map(l => measure(c, l, size, 600))) + 64;
  const h = lines.length * lh + 30;
  const cy = 1440;
  c.save(); c.globalAlpha = k;
  rr(c, W / 2 - w / 2, cy - h / 2, w, h, 22);
  c.fillStyle = 'rgba(14,26,43,0.84)'; c.fill();
  lines.forEach((l, i) => txt(c, l, W / 2, cy - h / 2 + 15 + lh / 2 + i * lh, size, 600, '#fff', 'center'));
  c.restore();
}

function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  background(ctx, t);
  for (const [name, s, e] of SCENES) {
    if (t < s - FADE || t > e + FADE) continue;
    const first = s === 0, last = e >= DURATION;
    const ain = first ? 1 : clamp((t - (s - FADE)) / (2 * FADE));
    const aout = last ? 1 : clamp(((e + FADE) - t) / (2 * FADE));
    const a = Math.min(ain, aout);
    if (a <= 0) continue;
    lctx.setTransform(1, 0, 0, 1, 0, 0);
    lctx.globalAlpha = 1;
    lctx.clearRect(0, 0, W, H);
    SCENE_FN[name](lctx, t);
    ctx.save();
    ctx.globalAlpha = eio(a);
    // gentle depth on the dissolve: incoming scenes settle from slightly larger
    const sc = ain < 1 ? lerp(1.025, 1, eio(ain)) : aout < 1 ? lerp(0.985, 1, eio(aout)) : 1;
    if (sc !== 1) zoomAt(ctx, W / 2, H / 2, sc);
    ctx.drawImage(layer, 0, 0);
    ctx.restore();
  }
  if (CAPS) drawCaption(ctx, t);
}

window.frame = (t, q = 0.93) => { render(t); return cv.toDataURL('image/jpeg', q); };
window.still = (t) => { render(t); return cv.toDataURL('image/png'); };

(async () => {
  IMG.portrait = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = '../assets/portrait.jpg'; });
  await Promise.all(['400', '500', '600', '650', '700'].map(w => document.fonts.load(`${w} 40px Inter`)));
  render(0);
  window.READY = true;
})();
