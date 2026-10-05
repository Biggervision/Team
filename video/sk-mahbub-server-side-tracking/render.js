// Usage: node render.js stills out_dir t1 t2 ...   |   node render.js video f0 f1 out.mp4
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const TL = JSON.parse(fs.readFileSync(path.join(__dirname, 'timeline.json'), 'utf8'));
if (process.env.LAND) TL.land = true;
if (process.env.LIGHT) TL.light = true;

(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: TL.land ? { width: 1920, height: 1080 } : { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
  await page.addInitScript(`window.TIMELINE=${JSON.stringify(TL)};`);
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => window.assetsReady);
  await page.evaluate(() => document.fonts.load('900 40px Inter'));
  if (mode === 'stills') {
    const [dir, ...ts] = args; fs.mkdirSync(dir, { recursive: true });
    for (const t of ts) {
      const b = await page.evaluate(tt => window.grab(tt, 'image/jpeg', .85), parseFloat(t));
      fs.writeFileSync(path.join(dir, `f_${parseFloat(t).toFixed(2)}.jpg`), Buffer.from(b, 'base64'));
    }
  } else {
    const [f0, f1, out] = args; const fps = TL.fps;
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-tune', 'animation', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = +f0; f < +f1; f++) {
      const b = await page.evaluate(tt => window.grab(tt), f / fps);
      if (!ff.stdin.write(Buffer.from(b, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 150 === 0) console.log(out, f, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
