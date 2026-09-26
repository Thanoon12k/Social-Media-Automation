"""Builds the soundtrack for ad.mp4: Iraqi-Arabic voiceover (edge-tts), synthesized
sound effects synced to cues.json, and a light music bed; then muxes with the video.
Usage: python3 make_audio.py [ffmpegPath]   (needs: pip install edge-tts)"""
import json, math, os, random, struct, subprocess, sys, wave

FF = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
DIR = os.path.dirname(os.path.abspath(__file__))
VOICE = 'ar-IQ-BasselNeural'
SR = 44100
p = lambda *a: os.path.join(DIR, *a)
cues = json.load(open(p('cues.json')))
N = int((cues['duration'] + 0.5) * SR)
mix = [0.0] * N
rnd = random.Random(3)

def add(sig, t, gain=1.0):
    o = int(t * SR)
    for i, v in enumerate(sig):
        if 0 <= o + i < N: mix[o + i] += v * gain

def env(n, a, d):  # attack/decay envelope in samples
    return [min(1, i / max(1, a)) * math.exp(-i / max(1, d)) for i in range(n)]

def pop():
    n = int(.12 * SR); e = env(n, 60, SR * .03)
    return [math.sin(2 * math.pi * (900 - 500 * i / n) * i / SR) * e[i] * .5 for i in range(n)]

def whoosh(length=.5):
    n = int(length * SR); out = []; lp = 0
    for i in range(n):
        x = i / n; a = math.sin(math.pi * x) ** 2
        k = .02 + .25 * x  # sweeping low-pass
        lp += k * (rnd.uniform(-1, 1) - lp); out.append(lp * a * 1.6)
    return out

def ding():
    n = int(1.2 * SR); e = env(n, 40, SR * .35)
    return [(math.sin(2*math.pi*1318*i/SR) + .5*math.sin(2*math.pi*1976*i/SR) + .3*math.sin(2*math.pi*2637*i/SR)) * e[i] * .3 for i in range(n)]

def swish():
    n = int(.25 * SR); out = []; hp = 0; prev = 0
    for i in range(n):
        s = rnd.uniform(-1, 1); hp = .9 * (hp + s - prev); prev = s
        out.append(hp * math.sin(math.pi * i / n) * .35)
    return out

def tick(f):
    n = int(.06 * SR); e = env(n, 20, SR * .015)
    return [math.sin(2 * math.pi * f * i / SR) * e[i] * .25 for i in range(n)]

# music bed: 100 bpm, soft pad chords + kick + shaker
bpm = 100; beat = 60 / bpm
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
bar = beat * 4; music = [0.0] * N
for b in range(int(cues['duration'] / bar) + 1):
    ch = chords[b % 4]; s0 = int(b * bar * SR); n = int(bar * SR)
    for i in range(n):
        if s0 + i >= N: break
        t = i / SR; a = min(1, t / .3) * min(1, (bar - t) / .3)
        music[s0 + i] += sum(math.sin(2 * math.pi * f * t) + .3 * math.sin(4 * math.pi * f * t) for f in ch) * a * .035
for k in range(int(cues['duration'] / beat) + 1):
    s0 = int(k * beat * SR)
    for i in range(int(.25 * SR)):
        if s0 + i >= N: break
        t = i / SR; music[s0 + i] += math.sin(2 * math.pi * (50 + 90 * math.exp(-t * 30)) * t) * math.exp(-t * 14) * .28
    for off in (.5,):
        s1 = int((k + off) * beat * SR)
        for i in range(int(.05 * SR)):
            if s1 + i < N: music[s1 + i] += rnd.uniform(-1, 1) * math.exp(-i / (SR * .01)) * .05

# voiceover
vo = [0.0] * N
lines = [l.strip() for l in open(p('voice.txt'), encoding='utf-8') if l.strip()]
os.makedirs(p('build'), exist_ok=True)
for i, (line, t0) in enumerate(zip(lines, cues['voice'])):
    mp3, wav = p('build', f'vo{i}.mp3'), p('build', f'vo{i}.wav')
    subprocess.run(['edge-tts', '-v', VOICE, '--rate=+12%', '-t', line, '--write-media', mp3], check=True, capture_output=True)
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', mp3, '-af',
        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
        '-ar', str(SR), '-ac', '1', wav], check=True)
    w = wave.open(wav); raw = w.readframes(w.getnframes())
    o = int(t0 * SR)
    for j, (v,) in enumerate(struct.iter_unpack('<h', raw)):
        if o + j < N: vo[o + j] += v / 32768

# sfx
for t in cues['scene'][1:]: add(whoosh(), t - .25, .9)
for t in cues['pop']: add(pop(), t + .05, .8)
for t in cues['strike']: add(swish(), t, 1)
for j, t in enumerate(sorted(cues['grow'])): add(tick(700 + 60 * j), t + .1, .8)
add(ding(), cues['voice'][4] + .5, .9)  # price reveal
add(ding(), cues['scene'][-1] + .6, .6)   # CTA

# duck music under voice, then mix
win = int(.05 * SR); lvl = 0.0; out = bytearray()
for i in range(N):
    lvl = max(abs(vo[i]), lvl * (1 - 1 / (SR * .25)))
    duck = 1 - .55 * min(1, lvl * 4)
    fade = min(1, (N - i) / (SR * .6))
    s = (vo[i] * 1.0 + mix[i] * .55 + music[i] * duck) * fade
    out += struct.pack('<h', int(max(-1, min(1, s * .9)) * 32767))
w = wave.open(p('build', 'mix.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(out)); w.close()

subprocess.run([FF, '-loglevel', 'error', '-y', '-i', p('video_silent.mp4'), '-i', p('build', 'mix.wav'),
    '-af', 'loudnorm=I=-14:TP=-1', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
    '-movflags', '+faststart', p('ad.mp4')], check=True)
print('wrote ad.mp4')
