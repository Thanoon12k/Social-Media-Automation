// Renders ad.html frame-by-frame with headless Chromium, then encodes an MP4 with ffmpeg.
// Usage: node render.mjs [ffmpegPath]
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const ffmpeg = process.argv[2] || 'ffmpeg';
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.join(dir, 'ad.html'));
await page.evaluate(async () => { await document.fonts.load("700 100px PlexDigits"); await document.fonts.ready; });
const dur = await page.evaluate(() => window.DURATION);

const enc = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart',
  path.join(dir, 'ad.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });

const total = Math.round(dur * FPS);
for (let f = 0; f < total; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
}
enc.stdin.end();
await new Promise(r => enc.on('close', r));
await browser.close();
console.log('wrote ad.mp4');
