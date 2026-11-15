"""Iraqi-Arabic voice-over: generates clips (edge-tts, ar-IQ voice), fits the scene
timeline around them, and writes vo.wav + timing.json (used by index.html & music.py)."""
import asyncio, json, os, subprocess, wave
import numpy as np, certifi
certifi.where = lambda: os.environ.get('SSL_CERT_FILE', '/root/.ccr/ca-bundle.crt') if os.path.exists('/root/.ccr/ca-bundle.crt') else certifi.core.where()
import edge_tts, imageio_ffmpeg

VOICE = os.environ.get('VOICE', 'ar-IQ-BasselNeural')
RATE = '+10%'
SR = 44100
TARGET = 60.0
# base scene timeline (seconds in the original 40s animation)
BASE = [('s1', 0, 3.3), ('s2', 3.3, 6.4), ('s3', 6.4, 11.6), ('s4', 11.6, 20.4),
        ('s5', 20.4, 22.0), ('s6', 22.0, 27.4), ('s7', 27.4, 32.6), ('s8', 32.6, 40.0)]
# (base offset inside scene, text). Clips land on these animation beats.
SCRIPT = {
    's1': [(0.05, 'عندك موقع؟'), (1.1, 'بوت؟'), (2.15, 'ولّا بس فكرة براسك؟')],
    's2': [(0.15, 'إحنا بكولدن كود، نحوّل فكرتك لكود حقيقي يشتغل.')],
    's3': [(0.3, 'بس اكتبلنا فكرتك، وإحنا نرتّبلك كلشي.'),
           (3.4, 'نحلل الفكرة، نصمم الواجهة، ونبرمج ونطلق.')],
    's4': [(0.2, 'نكتب الكود سطر بسطر، ونبنيلك واجهة فخمة، سريعة، وتشتغل على كل الأجهزة.'),
           (5.6, 'تصميم، برمجة، اختبار، وإطلاق. كلها بمكان واحد.')],
    's5': [(0.05, 'كود ذهبي!')],
    's6': [(0.2, 'نبني، نختبر، ونطلق مشروعك أونلاين، بدون وجع راس.')],
    's7': [(0.1, 'وصار حقيقي!'), (1.0, 'الطلبات تجي، والزباين مبسوطين، والتقييم خمس نجوم.')],
    's8': [(0.3, 'كولدن كود. نبرمج أفكارك بلمسة ذهبية.'), (3.6, 'تابعنا هسه، ودزلنا فكرتك!')],
}
GAP = 0.25
os.makedirs('vo', exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

async def tts(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)

def load(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, '<i2').astype(np.float32) / 32768
    nz = np.nonzero(np.abs(a) > 0.01)[0]  # trim silence
    return a[max(0, nz[0] - 200): nz[-1] + 2000] if len(nz) else a

clips = {}
for sid, items in SCRIPT.items():
    for i, (_, text) in enumerate(items):
        p = f'vo/{sid}_{i}.mp3'
        if not os.path.exists(p):
            asyncio.run(tts(text, p))
        clips[(sid, i)] = load(p)

# stretch factor per scene so every clip fits before the next beat
scenes, t = [], 0.0
for sid, a, b in BASE:
    L = b - a; items = SCRIPT[sid]; k = 1.0
    for i, (o, _) in enumerate(items):
        nxt = items[i + 1][0] if i + 1 < len(items) else L
        tail = 2.2 if sid == 's8' and i + 1 == len(items) else GAP
        k = max(k, (len(clips[(sid, i)]) / SR + tail) / (nxt - o))
    scenes.append([sid, a, b, k])
total = sum((b - a) * k for _, a, b, k in scenes)
if total < TARGET:  # spread spare time over the longer, visual scenes
    spare = TARGET - total; w = {'s4': 3, 's3': 1, 's6': 1, 's7': 1, 's8': 1}
    ws = sum(w.values())
    for s in scenes:
        if s[0] in w: s[3] += spare * w[s[0]] / ws / (s[2] - s[1])
timing, t = [], 0.0
for sid, a, b, k in scenes:
    timing.append({'id': sid, 'a': a, 'b': b, 'na': round(t, 4), 'nb': round(t + (b - a) * k, 4)}); t += (b - a) * k
dur = t
json.dump({'duration': round(dur, 3), 'scenes': timing}, open('timing.json', 'w'), ensure_ascii=False, indent=1)

vo = np.zeros(int(dur * SR) + SR)
captions = []
for sc in timing:
    k = (sc['nb'] - sc['na']) / (sc['b'] - sc['a'])
    for i, (o, text) in enumerate(SCRIPT[sc['id']]):
        c = clips[(sc['id'], i)]; st = sc['na'] + o * k; s = int(st * SR)
        vo[s:s + len(c)] += c[: len(vo) - s]
        captions.append({'t0': round(st, 3), 't1': round(st + len(c) / SR + .15, 3), 'text': text})
vo = vo[: int(dur * SR)]
vo /= np.max(np.abs(vo)) / 0.95
with wave.open('vo.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((vo * 32767).astype('<i2').tobytes())
for sc in timing: print(sc)
print('duration', round(dur, 2))
open('timing.js', 'w').write('window.TIMING=' + json.dumps({'duration': round(dur, 3), 'scenes': timing, 'captions': captions}, ensure_ascii=False) + ';\n')
