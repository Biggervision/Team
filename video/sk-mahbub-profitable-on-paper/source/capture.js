// usage: node capture.js <v|l> <mode:stills|video> <start> <end> <out> [times...]
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [ori, mode, s, e, out, ...times] = process.argv.slice(2);
  const vert = ori === 'v', W = vert ? 1080 : 1920, H = vert ? 1920 : 1080;
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-gpu-vsync'] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto('file://' + path.resolve(__dirname, 'index.html'));
  await page.evaluate(async v => { await document.fonts.load('700 20px Inter'); await document.fonts.load('400 20px Inter'); await document.getElementById('me').decode(); init(v); }, vert);
  if (mode === 'stills') {
    for (const t of times) {
      const b64 = await page.evaluate(t => { renderFrame(+t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t);
      require('fs').writeFileSync(`${out}_${ori}_${t}.png`, Buffer.from(b64, 'base64'));
    }
  } else {
    const fps = 30, f0 = Math.round(+s * fps), f1 = Math.round(+e * fps);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '30', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = f0; f < f1; f++) {
      const b64 = await page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.97).split(',')[1]; }, f / fps);
      if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 300 === 0) console.error(ori, out, f, '/', f1);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
