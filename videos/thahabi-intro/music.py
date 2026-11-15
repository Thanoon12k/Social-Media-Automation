"""Soundtrack for the Thahabi intro: beat + SFX synced to timing.json, voice mixed on top
with the music ducked under it."""
import numpy as np, wave, json, os

TM = json.load(open('timing.json'))
SR = 44100
DUR = TM['duration']
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
BT = {b['id']: b for b in TM['beats']}
def W(bid, word, n=0):
    ws = [w for w in BT[bid]['words'] if word in w[0]]
    return ws[min(n, len(ws) - 1)][1]
SC = {'me': BT['me']['t0'] - .3, 'only': BT['only']['t0'] - .3, 'tasks': BT['plan']['t0'] - .3,
      'work': BT['work']['t0'] - .3, 'but': BT['but']['t0'] - .3, 'goal': BT['goal']['t0'] - .3,
      'charge': BT['charge']['t0'] - .3, 'end': BT['cta']['t0'] - .3}

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= max(i, 0): return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def lp(x, k):  # one-pole low-pass, k in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc); y[i] = acc
    return y

def note(f): return 440 * 2 ** ((f - 69) / 12)

# ---- drums ----
def kick():
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 1.1
def hat():
    n = int(.06 * SR); return np.diff(rng.standard_normal(n + 1)) * env(n, .001, .015) * .25
def clap():
    n = int(.25 * SR); x = rng.standard_normal(n)
    return (x - lp(x, .15)) * env(n, .002, .06) * .5
def impact():
    n = int(2.5 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 80 * np.exp(-t * 8)) / SR) * np.exp(-t * 1.6)
    x = rng.standard_normal(n); noise = lp(x, .05) * np.exp(-t * 3) * 1.5
    return (boom * 1.3 + noise)
def whoosh(d=.6, up=True):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); sh = np.sin(np.pi * t / d) ** 2
    k = np.linspace(.02, .35, n) if up else np.linspace(.35, .02, n)
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc += k[i] * (x[i] - acc); y[i] = acc
    return y * sh * .9
def riser(d):
    n = int(d * SR); t = np.arange(n) / SR
    f = 200 * (8 ** (t / d))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .15 + whoosh(d) * .8) * (t / d) ** 2
def click():
    n = int(.03 * SR); x = rng.standard_normal(n)
    return (x - lp(x, .3)) * env(n, .0005, .004) * .35
def bell(f, d=1.2, g=.3):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * m * t) * a for m, a in [(1, 1), (2.01, .4), (3.02, .2), (4.2, .1)])
    return s * env(n, .002, d / 3.5) * g

# ---- music ----
BPM = 100; B = 60 / BPM
# Am - F - C - G  (root midi)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]
def pad(chord, d):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in chord:
        for det in (-.12, .12):
            f = note(m + 12) * (1 + det / 100)
            s += np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * f * t)
    s = lp(s, .04)
    a = np.minimum(1, t / .4) * np.minimum(1, (d - t) / .4)
    return s * a * .05
def bass(m, d):
    n = int(d * SR); t = np.arange(n) / SR
    f = note(m - 12)
    s = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)
    return s * env(n, .005, d * .6) * .35
def arp(chord, t0, bars_len, g=.08):
    step = B / 2; k = 0; tt = t0
    seq = chord + [chord[1] + 12, chord[0] + 12]
    while tt < t0 + bars_len - 1e-6:
        f = note(seq[k % len(seq)] + 12)
        n = int(step * SR * .9); t = np.arange(n) / SR
        add(np.sin(2 * np.pi * f * t) * env(n, .003, .12) * g, tt, pan=.3 if k % 2 else -.3)
        k += 1; tt += step


def blip(f, d=.12, g=.2):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t * (1 + .5 * np.exp(-t * 40))) * env(n, .001, d / 3) * g

bar = 4 * B
def section(t0, t1, drums=True, arps=True, pads=True, prog_=prog):
    t = t0; ci = 0
    while t < t1 - .05:
        root, ch = prog_[ci % 4]; d = min(bar, t1 - t)
        if pads: add(pad(ch, d + .3), t)
        if drums:
            for b in range(4):
                if t + b * B < t1: add(bass(root, B * .9), t + b * B, .9)
        if arps: arp(ch, t, d)
        t += bar; ci += 1
    if drums:
        tt, beat = t0, 0
        while tt < t1 - .05:
            if beat % 4 in (0, 2): add(kick(), tt, .9)
            if beat % 4 in (1, 3): add(clap(), tt, .55)
            add(hat(), tt + B / 2, .8, pan=.2); add(hat(), tt, .35, pan=-.2)
            tt += B; beat += 1

section(0, SC['me'], drums=False, arps=True)
section(SC['me'], SC['but'])
section(SC['but'], SC['goal'], drums=False, arps=False, prog_=[(57, [57, 60, 64]), (53, [53, 57, 60])] * 2)
section(SC['goal'], DUR - 1.5)

# ---- SFX ----
add(whoosh(.6), 0.0, .8); add(kick(), .6, 1.0); add(impact() * .35, .6, .8)          # drop + land
add(bell(note(81), 1.0, .2), BT['hi']['t0']); add(bell(note(88), 1.0, .14), BT['hi']['t0'] + .1)
for k, t in SC.items(): add(whoosh(.5), t - .25, .6)
add(bell(note(84), 1.2, .22), W('me', 'ذهبي'))
for i in range(3): add(blip(note(84 + i * 3)), W('me', 'الكود') + i * .15)
add(riser(.5), W('only', 'غيري') - .5, .6); add(bell(note(91), 1.2, .2), W('only', 'غيري'))
for i, b in enumerate(['plan', 'design', 'sched', 'post']): add(bell(note(76 + i * 3), .7, .18), BT[b]['t0'])
add(impact() * .7, W('post', 'وحدي') - .08, .9); add(clap(), W('post', 'وحدي'), .9)
add(impact() * .5, SC['work'] + .1, .7)
for w in ('نوم', 'قهوة', 'عطلة'):
    add(blip(note(79)), W('work', w) - .1); add(whoosh(.25, False), W('work', w) + .35, .7)
# sad: low tone
add(bell(note(57), 2.0, .2), BT['but']['t0']); add(bell(note(60), 2.0, .15), W('but', 'ما'))
# counter ticks + success
c0, c1 = W('goal', 'ألف') - .1, W('goal', 'متابع') + .9
x = c0
while x < c1:
    add(click(), x, 1.0); x += .045 + .05 * (1 - (x - c0) / (c1 - c0))
add(riser(c1 - c0), c0, .6)
add(impact() * .6, c1, .8)
for i, n_ in enumerate((84, 88, 91, 96)): add(bell(note(n_), 1.4, .2), c1 + i * .06)
# battery charge blips
s0, s1 = BT['charge']['t0'] + .2, SC['end'] - .4
for i in range(5): add(blip(note(72 + i * 4), .18, .25), s0 + (s1 - s0) * i / 5)
add(bell(note(96), 1.2, .2), s1)
# follow tap
tap = BT['bye']['t0'] + 1.3
add(click() * 3, tap, 1.0); add(bell(note(88), 1.5, .25), tap + .05); add(bell(note(93), 1.5, .18), tap + .12)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / .89
with wave.open('vo.wav') as w:
    vo = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
e = np.abs(vo); win = int(.25 * SR)
e = np.convolve(e, np.ones(win) / win, 'same'); e = np.minimum(1, e / (e.max() * .25))
mix = mix * .6 * (1 - .6 * e)[:, None] + vo[:, None]
fade = np.ones(N); fo = int(1.5 * SR); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / .95
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('music.wav written')
