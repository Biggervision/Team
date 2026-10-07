// Renders the canvas animation to video (or stills) with headless Chromium.
//   node render.cjs video  <h|v> <out.mp4> [--caps] [--from s] [--to s]
//   node render.cjs stills <h|v> <outDir> t1 t2 ... [--caps]
// Needs NODE_PATH pointing at a global playwright install.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const ROOT = __dirname;
const FPS = 30;
const DURATION = 71.5;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  const args = process.argv.slice(2);
  const [mode, orient, out] = args;
  const caps = args.includes('--caps');
  const opt = k => { const i = args.indexOf(k); return i > -1 ? parseFloat(args[i + 1]) : null; };
  const vert = orient === 'v';
  const [w, h] = vert ? [1080, 1920] : [1920, 1080];

  const srv = await serve();
  const url = `http://127.0.0.1:${srv.address().port}/src/index.html?v=${vert ? 1 : 0}&caps=${caps ? 1 : 0}`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(url);
  await page.waitForFunction('window.READY === true', null, { timeout: 30000 });

  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    const times = args.slice(3).filter(a => !a.startsWith('--')).map(Number);
    for (const t of times) {
      const d = await page.evaluate(t => window.still(t), t);
      fs.writeFileSync(path.join(out, `${vert ? 'v' : 'h'}_${t.toFixed(2)}.png`), Buffer.from(d.split(',')[1], 'base64'));
    }
  } else {
    const from = opt('--from') ?? 0, to = opt('--to') ?? DURATION;
    const n0 = Math.round(from * FPS), n1 = Math.round(to * FPS);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = n0; f < n1; f++) {
      const d = await page.evaluate(t => window.frame(t), f / FPS);
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 150 === 0) console.log(`${orient} frame ${f}/${n1} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
  srv.close();
})().catch(e => { console.error(e); process.exit(1); });
