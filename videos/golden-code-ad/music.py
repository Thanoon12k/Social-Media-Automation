"""Generates music.wav: a synthesized beat + SFX synced to the ad timeline (40s)."""
import numpy as np, wave

SR = 44100
DUR = 40.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
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

bar = 4 * B
t = 0.0; ci = 0
while t < DUR - .5:
    root, ch = prog[ci % 4]
    add(pad(ch, bar + .3), t)
    if t >= 3.3 - 1e-6 and not (20.0 <= t < 22.0):
        for b in range(4):
            add(bass(root, B * .9), t + b * B, .9)
    if 11.6 <= t < 20.0 or 22.0 <= t < 38.0:
        arp(ch, t, bar)
    t += bar; ci += 1

# drums: groove from 3.3 to 38, break during 19.4-22.0 (riser + impact)
tt = 3.3
beat = 0
while tt < 38.0:
    if not (19.0 <= tt < 22.0):
        if beat % 4 in (0, 2) or (tt > 22 and beat % 8 == 7): add(kick(), tt, .9)
        if beat % 4 in (1, 3): add(clap(), tt, .6)
        add(hat(), tt + B / 2, .8, pan=.2)
        if tt > 11.6: add(hat(), tt, .4, pan=-.2)
    tt += B; beat += 1

# ---- SFX synced to visuals ----
for s in (0.0, 1.05, 2.1):
    add(kick(), s, .8); add(bell(note(81 + [0, 3, 7][[0.0, 1.05, 2.1].index(s)]), 1.0, .18), s)
for s in (3.3, 6.4, 11.6, 22.0, 27.4):
    add(whoosh(.55), s - .3, .7)
# typing in prompt (6.9-8.6) and code editor (12.1-16.8)
for a, b, rate in ((6.9, 8.6, 18), (12.1, 16.8, 22)):
    x = a
    while x < b:
        add(click(), x, .8 + rng.random() * .4, pan=rng.random() - .5); x += 1 / rate * (0.6 + rng.random() * .8)
add(whoosh(.4, False), 8.85, .8)          # send
add(bell(note(76), .8, .2), 9.5)           # reply bubble
for i in range(3): add(bell(note(72 + i * 4), .5, .12), 10.0 + i * .22)
add(riser(1.4), 19.0, 1.0)
add(impact(), 20.4, 1.0)                    # gold flash
add(clap(), 20.75, .8)
add(bell(note(84), 1.8, .3), 25.1); add(bell(note(88), 1.8, .2), 25.1)   # build done
for s in (28.4, 29.3, 30.2): add(bell(note(90), .5, .2), s); add(bell(note(95), .5, .12), s + .08)
add(impact() * .6, 32.6, .8)                # end card
add(bell(note(81), 3.0, .25), 32.8); add(bell(note(88), 3.0, .18), 32.8); add(bell(note(93), 3.0, .12), 33.0)

mix = np.stack([L, R], 1)
fade = np.ones(N); fo = int(2.0 * SR); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / .89
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('music.wav written')
