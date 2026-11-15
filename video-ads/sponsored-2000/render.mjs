// Renders ad.html frame-by-frame with headless Chromium, then encodes an MP4 with ffmpeg.
// Usage: node render.mjs [ffmpegPath]   then: python3 make_audio.py [ffmpegPath]
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
// Export timing cues so make_audio.py can sync sound effects to the animation.
const cues = await page.evaluate(() => {
  const c = { duration: window.DURATION, voice: window.VO_START, anim: {} };
  for (const a of document.getAnimations()) {
    const t = a.effect.getTiming();
    if (t.iterations === Infinity) continue;
    (c.anim[a.animationName] ||= []).push([t.delay / 1000, t.duration / 1000]);
  }
  return c;
});
(await import('node:fs')).writeFileSync(path.join(dir, 'cues.json'), JSON.stringify(cues, null, 1));

const enc = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart',
  path.join(dir, 'video_silent.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });

const total = Math.round(dur * FPS);
for (let f = 0; f < total; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
}
enc.stdin.end();
await new Promise(r => enc.on('close', r));
await browser.close();
console.log('wrote video_silent.mp4 + cues.json');
