// Renders index.html frame-by-frame with headless Chromium and pipes into ffmpeg.
// usage: node render.mjs [out.mp4] [--preview t1,t2,...]
import { createRequire } from 'module';
import { spawn, execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
const args = process.argv.slice(2);
const previewIdx = args.indexOf('--preview');
const ffmpeg = process.env.FFMPEG || 'ffmpeg';

const browser = await pw.chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(dir, 'index.html'));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);

if (previewIdx >= 0) {
  const times = args[previewIdx + 1].split(',').map(Number);
  for (const t of times) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(dir, `preview_${t}.png`) });
  }
  await browser.close();
  process.exit(0);
}

const out = args[0] || path.join(dir, 'thahabi-intro.mp4');
const dur = await page.evaluate(() => window.DUR);
const frames = Math.round(dur * FPS);
const audio = path.join(dir, 'music.wav');
const ff = spawn(ffmpeg, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-i', audio, '-map', '0:v', '-map', '1:a',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  '-c:a', 'aac', '-b:a', '192k', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.seek(t), i / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stderr.write(`frame ${i}/${frames}\n`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log('done ->', out);
