"""Builds the soundtrack for ad.mp4: Iraqi-Arabic voiceover (edge-tts), synthesized
sound effects synced to the animation cues in cues.json, and an arranged music bed
(build-up, drop before the price reveal, impact on the slam). Then muxes with the video.
Usage: python3 make_audio.py [ffmpegPath]   (needs: pip install edge-tts)"""
import json, math, os, random, struct, subprocess, sys, wave

FF = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
DIR = os.path.dirname(os.path.abspath(__file__))
VOICE = 'ar-IQ-BasselNeural'
SR = 44100
TAU = 2 * math.pi
p = lambda *a: os.path.join(DIR, *a)
cues = json.load(open(p('cues.json')))
A = lambda name: sorted(cues['anim'].get(name, []))
DUR = cues['duration']
N = int((DUR + .6) * SR)
rnd = random.Random(3)
sfx, music, vo = [0.0] * N, [0.0] * N, [0.0] * N

def add(buf, sig, t, g=1.0):
    o = int(t * SR)
    for i, v in enumerate(sig):
        if 0 <= o + i < N: buf[o + i] += v * g

def tone(f0, f1, length, decay, amp=.5, harm=()):
    n = int(length * SR); ph = 0; out = []
    for i in range(n):
        x = i / n; f = f0 + (f1 - f0) * x; ph += TAU * f / SR
        s = math.sin(ph) + sum(h[1] * math.sin(ph * h[0]) for h in harm)
        out.append(s * amp * min(1, i / 60) * math.exp(-i / (decay * SR)))
    return out

def noise(length, lp0, lp1, shape, amp):
    n = int(length * SR); lp = 0; out = []
    for i in range(n):
        x = i / n; k = lp0 + (lp1 - lp0) * x
        lp += k * (rnd.uniform(-1, 1) - lp); out.append(lp * shape(x) * amp)
    return out

bell = lambda x: math.sin(math.pi * x) ** 2
pop     = lambda: tone(950, 380, .12, .03, .5)
tick    = lambda f=1800: tone(f, f, .04, .008, .25)
whoosh  = lambda L=.55: noise(L, .01, .3, bell, 2.0)
bigwhoosh = lambda: [a + b for a, b in zip(noise(.9, .005, .25, bell, 2.6), tone(70, 40, .9, .5, .5))]
swish   = lambda: noise(.22, .6, .9, lambda x: math.sin(math.pi * x), .5)
thud    = lambda: [a + b for a, b in zip(tone(120, 45, .5, .12, .9), noise(.5, .15, .02, lambda x: math.exp(-x * 8), 1.2))]
notif   = lambda: tone(1320, 1320, .1, .06, .3) + tone(1760, 1760, .25, .08, .3)
ding    = lambda f=1318: tone(f, f, 1.2, .35, .28, ((1.5, .5), (2, .3), (3, .1)))
boing   = lambda: tone(300, 700, .35, .2, .35)
sweepup = lambda L: tone(300, 1400, L, 9, .12, ((2, .3),))
click   = lambda: tone(2400, 1200, .03, .006, .6) + [0.0] * int(.02 * SR) + tone(1600, 900, .03, .006, .4)
shimmer = lambda: [sum(v) for v in zip(*[[0.0] * int(k * .06 * SR) + tone(f, f, .9, .25, .12) + [0.0] * int((6 - k) * .06 * SR)
                                          for k, f in enumerate([1568, 1760, 2093, 2349, 2637, 3136])])]
def riser(L):
    return [a + b for a, b in zip(noise(L, .005, .5, lambda x: x ** 2.5, 2.2), tone(200, 1600, L, 99, .1))]
def boom():
    b = tone(90, 30, 1.6, .5, 1.1)
    c = noise(1.6, .6, .05, lambda x: math.exp(-x * 5), 1.0)
    return [x + y for x, y in zip(b, c)]
def counter(t0, L):  # accelerating-then-slowing ticks like a counter
    t, k = 0.0, 0
    while t < L:
        add(sfx, tick(1500 + 600 * t / L), t0 + t, .7)
        k += 1; t += .035 + .12 * (t / L) ** 2

# ---- sound effects from animation cues
scenes = A('sc-a') + A('sc-b') + A('sc-c') + A('sc-d')
starts = sorted(s for s, _ in scenes)
wipes = [s for s, _ in A('wipe')]
for s in starts[1:]:
    if not any(abs(s - w) < .05 for w in wipes): add(sfx, whoosh(), s - .3, .9)
for w in wipes: add(sfx, bigwhoosh(), w - .35, 1.0)
for t, _ in A('wordIn'): add(sfx, tick(2200), t + .05, .35)
for t, _ in A('pop'): add(sfx, pop(), t + .05, .7)
for t, _ in A('chip'): add(sfx, notif(), t + .1, .8)
for t, d in A('cnt'): counter(t, d * .85)
for t, _ in A('strike'): add(sfx, swish(), t, 1.2)
for t, _ in A('stamp'): add(sfx, thud(), t + .25, 1.0)
for t, _ in A('sweep'): add(sfx, swish(), t, .7)
for t, _ in A('wig'): add(sfx, boing(), t, .8)
for t, _ in A('flip'): add(sfx, noise(.3, .05, .4, bell, 1.2), t, .8)
for t, _ in A('check'): add(sfx, ding(2093), t + .1, .5)
for t, _ in A('heart')[::2]: add(sfx, tone(600, 1200, .1, .04, .3), t + .1, .6)
for t, _ in A('grow'): add(sfx, tick(900 + 120 * (t % 1) * 10 % 700), t, .6)
for t, d in A('draw'): add(sfx, sweepup(d), t, 1.0)
for t, _ in A('cur'): add(sfx, whoosh(.35), t, .5)
for t, _ in A('press'): add(sfx, click(), t + .12, 1.0)
for t, _ in A('pulse')[:1]: add(sfx, tone(220, 220, .3, .1, .2), t, .5)
slam = A('slam')[0][0]
add(sfx, riser(1.2), slam - 1.15, .9)
add(sfx, boom(), slam + .08, 1.1)
add(sfx, shimmer(), slam + .15, 1.0)
add(sfx, ding(1568), A('press')[0][0] + .2, .8)

# ---- music: 120 bpm, four-chord loop, arranged around the cues
bpm = 120; beat = 60 / bpm; bar = 4 * beat
roots = [220.0, 174.6, 261.6, 196.0]          # Am F C G
triads = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
full_from = starts[3] if len(starts) > 3 else 6
drop = (slam - 1.2, slam + .05)
outro = starts[-1]
def level(t):  # arrangement: intro sparse, full after the "solution", drop before slam
    if drop[0] <= t < drop[1]: return 0.0
    return 1.0
def drums_on(t): return not (drop[0] <= t < drop[1])
nb = int(DUR / beat) + 1
kick = tone(150, 45, .3, .08, .9)
clap = noise(.18, .5, .3, lambda x: math.exp(-x * 9), .7)
hat = noise(.05, .95, .95, lambda x: math.exp(-x * 25), .25)
for k in range(nb):
    t = k * beat
    if not drums_on(t) or t > DUR - .3: continue
    add(music, kick, t, 1.0)
    if t >= full_from:
        if k % 2 == 1: add(music, clap, t, .9)
        add(music, hat, t + beat / 2, 1)
        add(music, hat, t, .5)
    elif t >= starts[1] and k % 2 == 1:
        add(music, hat, t + beat / 2, .8)
for b in range(int(DUR / bar) + 1):
    t0 = b * bar; ch = triads[b % 4]; r = roots[b % 4] / 2
    s0 = int(t0 * SR); n = int(bar * SR)
    for i in range(n):
        j = s0 + i
        if j >= N: break
        t = i / SR; tt = t0 + t
        lv = level(tt)
        if lv == 0: continue
        a = min(1, t / .15) * min(1, (bar - t) / .15)
        pad = sum(math.sin(TAU * f * tt) + .25 * math.sin(TAU * 2 * f * tt) for f in ch) * .03
        e8 = (t % (beat / 2)) / (beat / 2)                     # 8th-note bass pluck
        bass = (math.sin(TAU * r * tt) + .3 * math.sin(TAU * 2 * r * tt)) * math.exp(-e8 * 3) * (.16 if tt >= full_from else .08)
        arp = 0
        if tt >= full_from:                                      # 16th arpeggio in full section
            step = int(t / (beat / 4)); f = ch[step % 3] * 2; e16 = (t % (beat / 4)) / (beat / 4)
            arp = math.sin(TAU * f * tt) * math.exp(-e16 * 5) * .035
        music[j] += (pad + bass + arp) * a * lv
# final sting chord
for f in (440, 554.4, 659.3, 880):
    add(music, tone(f, f, 2.2, .8, .06, ((2, .2),)), outro + 1.9, 1)

# ---- voiceover
lines = [l.strip() for l in open(p('voice.txt'), encoding='utf-8') if l.strip()]
os.makedirs(p('build'), exist_ok=True)
for i, (line, t0) in enumerate(zip(lines, cues['voice'])):
    mp3, wav = p('build', f'vo{i}.mp3'), p('build', f'vo{i}.wav')
    subprocess.run(['edge-tts', '-v', VOICE, '--rate=+12%', '-t', line, '--write-media', mp3], check=True, capture_output=True)
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', mp3, '-af',
        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
        'highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,equalizer=f=3000:t=q:w=1:g=3',
        '-ar', str(SR), '-ac', '1', wav], check=True)
    w = wave.open(wav); raw = w.readframes(w.getnframes())
    add(vo, [v / 32768 for (v,) in struct.iter_unpack('<h', raw)], t0, 1.0)

# ---- mix: duck music under voice, soft-clip, fade out
lvl = 0.0; out = bytearray()
for i in range(N):
    lvl = max(abs(vo[i]), lvl * (1 - 1 / (SR * .3)))
    duck = 1 - .6 * min(1, lvl * 4)
    fade = min(1, (N - i) / (SR * .8))
    s = (vo[i] * 1.1 + sfx[i] * .5 + music[i] * .85 * duck) * fade
    s = math.tanh(s * 1.1)
    out += struct.pack('<h', int(s * 30000))
w = wave.open(p('build', 'mix.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(out)); w.close()

subprocess.run([FF, '-loglevel', 'error', '-y', '-i', p('video_silent.mp4'), '-i', p('build', 'mix.wav'),
    '-af', 'aecho=0.8:0.5:40:0.12,loudnorm=I=-14:TP=-1', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
    '-shortest', '-movflags', '+faststart', p('ad.mp4')], check=True)
print('wrote ad.mp4')
