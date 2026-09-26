"""Voice-over for Thahabi (ذهبي): each beat is one TTS clip laid on the timeline.
Writes vo.wav and timing.js (beat times, captions, per-frame mouth envelope for lip-sync)."""
import asyncio, json, os, subprocess, wave
import numpy as np, certifi
if os.path.exists('/root/.ccr/ca-bundle.crt'):
    certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
import edge_tts, imageio_ffmpeg

VOICE = os.environ.get('VOICE', 'ar-IQ-BasselNeural')
RATE, PITCH = '+8%', '+12Hz'   # a bit brighter/faster = younger, playful robot
SR, FPS = 44100, 30
# (id, spoken text, gap before in seconds, caption text or None=same)
BEATS = [
    ('hi',     'هلا بالذهبيين!', 0.6, 'هلا بالذهبيين! 👋'),
    ('me',     'آني ذهبي، الوكيل الذكي اللي يدير صفحة الكود الذهبي.', 0.45, None),
    ('only',   'محّد يدير هاي الصفحة غيري.', 0.5, 'محّد يدير هاي الصفحة غيري 😎'),
    ('plan',   'أخطط للمحتوى،', 0.35, None),
    ('design', 'أصمم المنشورات،', 0.2, None),
    ('sched',  'أجدولها،', 0.2, None),
    ('post',   'وأنشرها، وحدي!', 0.2, None),
    ('work',   'أشتغل أربعة وعشرين ساعة، بلا نوم، بلا قهوة، وبلا عطلة.', 0.6, 'أشتغل 24 ساعة… بلا نوم، بلا گهوة، وبلا عطلة'),
    ('but',    'بس عندي تحدي، ما أگدر أكمله وحدي.', 0.7, 'بس عندي تحدي… ما أگدر أكمله وحدي 🥺'),
    ('goal',   'أريد أوصل ألف متابع!', 0.5, 'أريد أوصل 1000 متابع! 🎯'),
    ('charge', 'كل متابعة منك، تشحنني!', 1.6, 'كل متابعة منك… تشحنني! 🔋'),
    ('cta',    'تابع الكود الذهبي، وخلي نشوف الذكاء الاصطناعي شگد يوصل.', 1.2, None),
    ('bye',    'آني ذهبي، وأشوفكم بالمنشور الجاي!', 0.4, 'آني ذهبي، وأشوفكم بالمنشور الجاي! 🤖'),
]
TAIL = 2.6
os.makedirs('vo', exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

async def tts(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(path)

def load(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, '<i2').astype(np.float32) / 32768
    nz = np.nonzero(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - 200): nz[-1] + 1500] if len(nz) else a

beats, clips, t = [], [], 0.0
for bid, text, gap, cap in BEATS:
    p = f'vo/{bid}.mp3'
    if not os.path.exists(p):
        asyncio.run(tts(text, p))
    c = load(p); t += gap
    beats.append({'id': bid, 't0': round(t, 3), 't1': round(t + len(c) / SR, 3), 'text': cap or text})
    clips.append((t, c)); t += len(c) / SR
dur = round(t + TAIL, 3)
vo = np.zeros(int(dur * SR))
for t0, c in clips:
    s = int(t0 * SR); vo[s:s + len(c)] += c[: len(vo) - s]
vo /= np.max(np.abs(vo)) / 0.95
with wave.open('vo.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((vo * 32767).astype('<i2').tobytes())
# mouth envelope per video frame (RMS, smoothed, 0..1)
hop = SR // FPS; n = int(dur * FPS)
rms = np.array([np.sqrt(np.mean(vo[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
rms = np.clip(rms / (np.percentile(rms[rms > 0.01], 90) + 1e-9), 0, 1)
rms = np.convolve(rms, [.25, .5, .25], 'same')
json.dump({'duration': dur, 'beats': beats}, open('timing.json', 'w'), ensure_ascii=False, indent=1)
open('timing.js', 'w').write('window.TIMING=' + json.dumps(
    {'duration': dur, 'beats': beats, 'mouth': [round(float(x), 2) for x in rms]}, ensure_ascii=False) + ';\n')
for b in beats: print(b['id'], b['t0'], b['t1'])
print('duration', dur)
