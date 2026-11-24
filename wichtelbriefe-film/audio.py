"""Komplett synthetisierter Ton: Filmmusik (Klavier, Glockenspiel, Streicher) und Geräusche."""
import math
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
import wave

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.RandomState(1)

mus = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype='band', fs=SR, output='sos')
    return sosfilt(sos, x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0:
        return
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    buf[i:j, 0] += s * l * 1.414
    buf[i:j, 1] += s * r * 1.414


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ Instrumente
def piano(m, dur=2.5, vel=0.6):
    f = hz(m)
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, 9):
        fh = f * h * math.sqrt(1 + 0.0004 * h * h)
        if fh > 16000:
            break
        dec = 1.2 + 0.9 * h + f / 600
        out += (1.0 / h ** 1.25) * np.sin(2 * math.pi * fh * t + h) * np.exp(-t * dec)
    att = np.minimum(1, t / 0.004)
    rel = np.minimum(1, (dur - t) / 0.08)
    hammer = bp(rng.randn(n), 1500, 5000) * np.exp(-t * 90) * 0.05
    return (out * att * rel + hammer) * vel * 0.32


def glock(m, dur=2.0, vel=0.5):
    f = hz(m)
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, dec in ((1.0, 1.0, 2.2), (2.756, 0.35, 6), (5.404, 0.18, 12), (8.933, 0.08, 20)):
        if f * ratio < 18000:
            out += amp * np.sin(2 * math.pi * f * ratio * t) * np.exp(-t * dec)
    att = np.minimum(1, t / 0.0015)
    return out * att * vel * 0.25


def strings(freqs, dur, env_fn, t0, vel=0.18):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0.0, 0.0055):
            vib = 1 + 0.0035 * np.sin(2 * math.pi * 5.2 * t + rng.uniform(0, 6))
            ph = 2 * math.pi * np.cumsum(f * (1 + det) * vib) / SR
            sig = np.zeros(n)
            for h in range(1, 12):
                if f * h > 9000:
                    break
                sig += np.sin(h * ph) / h
            out += sig
    out = lp(out, 2600)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.8)
    tt = t0 + t
    out *= env * env_fn(tt)
    return out * vel / max(1, len(freqs))


# ------------------------------------------------------------------ Musik
CH = {
    'F': [53, 57, 60], 'Dm': [50, 53, 57], 'Bb': [46, 50, 53], 'C': [48, 52, 55], 'Am': [45, 48, 52],
    'Gm': [43, 46, 50], 'Csus': [48, 53, 55],
}
prog = []
cyc = ['F', 'Dm', 'Bb', 'C']
t = 0.0
i = 0
while t < 54:
    prog.append((t, cyc[i % 4]))
    t += 3.0
    i += 1
prog = [(a, c) for (a, c) in prog if a < 54]
prog += [(54.0, 'Csus'), (55.5, 'C'), (56.0, 'F')]


def intensity(t):
    t = np.asarray(t, float)
    v = 0.28 + 0 * t
    for (a, b, c, d, lvl) in ((18.6, 19.6, 21.5, 22.6, 0.85), (25.9, 26.3, 27.8, 28.6, 0.75),
                              (31.9, 32.3, 34.2, 35.0, 0.85), (35.0, 35.5, 40.0, 40.6, 0.6),
                              (44.8, 45.8, 48.4, 50.0, 1.05), (54.5, 55.0, 56.0, 56.5, 0.7),
                              (56.0, 56.6, 59.0, 60.0, 0.9)):
        k = np.clip((t - a) / (b - a), 0, 1) * np.clip((d - t) / (d - c), 0, 1)
        v = np.maximum(v, 0.28 + (lvl - 0.28) * k)
    v *= np.clip((60.0 - t) / 0.8, 0, 1)
    v *= np.clip(t / 1.0, 0.3, 1)
    return v


def chord_at(t):
    c = prog[0][1]
    for a, cc in prog:
        if t >= a:
            c = cc
    return c


BEAT = 0.75
# Klavier: Bass + gebrochene Akkorde in Achteln
for k, (a, c) in enumerate(prog):
    end = prog[k + 1][0] if k + 1 < len(prog) else 60.0
    notes = CH[c]
    root = notes[0]
    while root > 45:
        root -= 12
    add(mus, a, piano(root, min(4, end - a + 1.5), 0.55), 1.0, -0.2)
    pat = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 12, notes[0] + 24, notes[2] + 12, notes[1] + 12, notes[2] + 12]
    tt = a
    j = 0
    while tt < end - 0.01 and tt < 59.2:
        iv = float(intensity(tt))
        vel = 0.30 + 0.25 * iv
        add(mus, tt, piano(pat[j % 8], 1.8, vel), 1.0, 0.15 * ((j % 2) * 2 - 1))
        tt += BEAT / 2
        j += 1
    if c == 'F' and a >= 56:
        for m in (65, 69, 72, 77):
            add(mus, a + 0.02 * (m - 65), piano(m, 4.0, 0.45), 1.0, 0.1)

# Streicher
for k, (a, c) in enumerate(prog):
    end = prog[k + 1][0] if k + 1 < len(prog) else 60.0
    notes = CH[c]
    fr = [hz(notes[0] - 12), hz(notes[0]), hz(notes[1] + 12), hz(notes[2] + 12)]
    s = strings(fr, end - a + 0.9, lambda x: intensity(x) ** 1.6, a, vel=0.5)
    add(mus, a, s, 1.0, 0.0)

# Glockenspiel-Melodie (Motiv, wiederholt mit Variation)
SCALE = [65, 67, 69, 70, 72, 74, 76, 77, 79, 81]
motif = [(0.0, 0), (0.75, 2), (1.5, 1), (2.25, 4)]
r = np.random.RandomState(8)
for k, (a, c) in enumerate(prog[:-1]):
    if a < 3.0:
        continue
    notes = [n + 24 for n in CH[c]]
    if 35.0 <= a < 40.6:
        continue
    for j, (dt, deg) in enumerate(motif):
        if a + dt >= 59:
            break
        if j in (1, 3) and (r.rand() < 0.3):
            m = SCALE[min(len(SCALE) - 1, max(0, SCALE.index(min(SCALE, key=lambda s: abs(s - notes[0]))) + deg))]
        else:
            m = notes[(deg + k) % 3]
            while m < 72:
                m += 12
            while m > 86:
                m -= 12
        iv = float(intensity(a + dt))
        add(mus, a + dt, glock(m, 2.0, 0.35 + 0.35 * iv), 1.0, 0.3)

# Montage: schnelle Glockenspiel-Arpeggien, ein Ton pro Tag
for d in range(4, 24):
    td = 35.0 + (d - 3 + 0.35 - 0.0) * 0.27 + 0.05
    c = chord_at(td)
    notes = [n + 24 for n in CH[c]]
    m = notes[d % 3] + (12 if d % 6 >= 3 else 0)
    add(mus, td, glock(m, 1.2, 0.55), 1.0, 0.4 * math.sin(d))
    add(mus, td + 0.135, glock(m + 7 if m + 7 < 96 else m - 5, 1.0, 0.3), 1.0, -0.3)

# Funkeln bei Pop-ups und Stern
for t0, n in ((18.85, 6), (26.1, 6), (32.1, 7), (45.1, 10), (45.6, 12), (57.7, 8)):
    for i in range(n):
        m = [84, 88, 91, 93, 96, 91, 88, 93, 96, 98, 100, 96][i % 12]
        add(mus, t0 + i * 0.07, glock(m, 1.4, 0.32), 1.0, math.sin(i * 1.3) * 0.6)

# ------------------------------------------------------------------ Geräusche
def noise(d):
    return rng.randn(int(SR * d))


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))


def rustle(d, amp=0.3, lo=1800, hi=9000, density=60):
    n = int(SR * d)
    x = bp(rng.randn(n), lo, hi)
    # Knistern: zufällige Impulse
    cr = np.zeros(n)
    k = int(density * d)
    idx = rng.randint(0, n, k)
    cr[idx] = rng.uniform(0.5, 1.5, k)
    cr = np.convolve(cr, np.exp(-np.arange(int(SR * 0.004)) / (SR * 0.0008)), 'same')
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    mod = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * rng.uniform(3, 7) * t + rng.uniform(0, 6)))
    return (x * 0.6 * mod + bp(cr * rng.randn(n), 2000, 10000) * 2.0) * env * amp


def fold(amp=0.5):
    sw = rustle(0.35, amp * 0.8, 1200, 7000, 30)
    n = int(SR * 0.06)
    click = bp(rng.randn(n), 2500, 9000) * env_ad(n, 0.001, 0.008) * amp * 1.4
    out = np.zeros(len(sw) + n)
    out[: len(sw)] += sw
    out[int(SR * 0.3): int(SR * 0.3) + n] += click
    return out


def step(amp=0.25, f=170, soft=True):
    n = int(SR * 0.09)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * t * (1 - 0.3 * t / 0.09)) * np.exp(-t * 55)
    tick = bp(rng.randn(n), 1500, 6000) * np.exp(-t * 160) * 0.35
    return (body + tick) * amp


def scratch(d, amp=0.22, lo=2500, hi=7500, rate=9.0):
    n = int(SR * d)
    t = np.arange(n) / SR
    x = bp(rng.randn(n), lo, hi, 3)
    stroke = np.abs(np.sin(2 * np.pi * rate * t + 2 * np.sin(2 * np.pi * 1.3 * t))) ** 1.5
    gaps = (np.sin(2 * np.pi * 0.9 * t + 1) > -0.7).astype(float)
    gaps = lp(gaps, 30)
    grain = 1 + 0.6 * (rng.rand(n) > 0.995)
    return x * stroke * gaps * grain * amp * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.05)


def giggle(f0=820, n_syl=5, amp=0.25, spacing=0.11, formants=((800, 1.0), (2600, 0.5), (3600, 0.25))):
    """Kichern ohne Worte: kurze, stimmhafte 'hi'-Silben mit fallender Tonhöhe."""
    total = int(SR * (n_syl * spacing + 0.2))
    out = np.zeros(total)
    for i in range(n_syl):
        d = spacing * 0.7
        n = int(SR * d)
        t = np.arange(n) / SR
        f = f0 * (1.08 - 0.05 * i) * (1 + 0.06 * np.sin(np.pi * t / d))
        ph = 2 * np.pi * np.cumsum(f) / SR
        src = np.zeros(n)
        for h in range(1, 14):
            src += np.sin(h * ph) / h ** 0.9
        v = np.zeros(n)
        for fc, a in formants:
            v += bp(src, fc * 0.85, fc * 1.15) * a
        br = bp(rng.randn(n), 3000, 8000) * 0.12
        env = np.sin(np.pi * t / d) ** 1.5
        s = (v + br) * env
        i0 = int(SR * i * spacing * (1 + 0.1 * rng.rand()))
        out[i0:i0 + n] += s
    return out / (np.abs(out).max() + 1e-9) * amp


def creak(d=0.35, amp=0.12, f0=900):
    n = int(SR * d)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.4 * t / d) * (1 + 0.05 * np.sin(2 * np.pi * 37 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    pulses = (np.sin(ph) > 0.9).astype(float)
    s = bp(pulses + 0.2 * np.sin(ph), 600, 4000)
    return s * np.sin(np.pi * t / d) * amp


def whoosh(d, amp=0.2, f0=600, f1=3000):
    n = int(SR * d)
    x = rng.randn(n)
    out = np.zeros(n)
    seg = 2048
    for i in range(0, n, seg):
        k = i / n
        fc = f0 + (f1 - f0) * math.sin(k * math.pi)
        out[i:i + seg] = bp(x[i:i + seg + 512], fc * 0.7, fc * 1.4)[: len(out[i:i + seg])]
    t = np.arange(n) / SR
    return lp(out, 6000) * np.sin(np.pi * t / d) ** 2 * amp


def thump(amp=0.4, f=90):
    n = int(SR * 0.25)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t * (1 - 0.4 * t / 0.25)) * np.exp(-t * 22) + bp(rng.randn(n), 200, 1200) * np.exp(-t * 60) * 0.3) * amp


def warm_on(amp=0.35):
    n = int(SR * 2.5)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f, a in ((174.6, 1.0), (261.6, 0.6), (349.2, 0.5), (523.3, 0.25)):
        s += a * np.sin(2 * np.pi * f * t)
    env = np.minimum(1, t / 0.35) * np.exp(-np.maximum(0, t - 0.35) * 1.3)
    return lp(s, 1200) * env * amp


# Atmosphäre: Wind draußen, leiser Raumton
n = int(SR * 3.6)
wind = lp(rng.randn(n), 500) * 0.9
wt = np.arange(n) / SR
wind *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * wt)) * np.minimum(1, wt / 0.8) * np.clip((3.6 - wt) / 0.6, 0, 1)
add(sfx, 0.0, wind, 0.22, 0.0)
room = lp(rng.randn(N), 250) * 0.025
add(sfx, 0.0, room, 1.0)

# Szenen-Geräusche
add(sfx, 5.3, creak(0.45, 0.10), 1.0, 0.1)
for i, tt in enumerate(np.arange(6.4, 7.6, 0.285)):
    add(sfx, tt, step(0.16, 210 + 15 * (i % 2)), 1.0, 0.05 + 0.02 * i)
add(sfx, 7.85, rustle(0.4, 0.18), 1.0, 0.0)
add(sfx, 8.0, scratch(2.0, 0.20), 1.0, -0.05)
add(sfx, 10.1, fold(0.45), 1.0, 0.0)
add(sfx, 10.7, fold(0.45), 1.0, 0.05)
add(sfx, 11.25, rustle(0.5, 0.18), 1.0, -0.1)
add(sfx, 11.8, giggle(900, 5, 0.22), 1.0, 0.1)
for i, tt in enumerate(np.arange(12.12, 13.9, 0.21)):
    add(sfx, tt, step(0.15, 230 + 20 * (i % 2)), 1.0, -0.5 + 0.06 * i)
    add(sfx, tt + 0.02, bp(noise(0.12), 1500, 6000) * env_ad(int(SR * 0.12), 0.005, 0.04), 0.05, -0.5 + 0.06 * i)
add(sfx, 14.05, giggle(950, 6, 0.24, 0.1), 1.0, 0.4)
add(sfx, 15.1, fold(0.35)[: int(SR * 0.4)], 1.0, 0.3)
add(sfx, 16.15, rustle(0.4, 0.25, 600, 5000), 1.0, -0.6)
add(sfx, 16.6, thump(0.45), 1.0, -0.5)
for i, tt in enumerate(np.arange(16.78, 17.65, 0.21)):
    add(sfx, tt, step(0.32, 110 + 10 * (i % 2)), 1.0, -0.5 + 0.12 * i)
add(sfx, 17.9, rustle(0.4, 0.22), 1.0, 0.3)
for (ti, t0o, t1o) in ((18.2, 0.35, 1.15), (25.6, 0.25, 0.9), (31.6, 0.25, 0.9), (44.6, 0.2, 0.9)):
    add(sfx, ti + 0.05, rustle(0.3, 0.15), 1.0, -0.2)
    add(sfx, ti + t0o, rustle(t1o - t0o, 0.32, 1500, 9000, 120), 1.0, -0.2)
    add(sfx, ti + t0o + (t1o - t0o) * 0.36 + 0.1, whoosh(0.4, 0.14, 800, 2500), 1.0, -0.2)
for tt, f0 in ((19.9, 520), (27.0, 540), (32.8, 560), (46.9, 560), (49.0, 580), (55.15, 540)):
    add(sfx, tt, giggle(f0, 4, 0.20, 0.14, ((700, 1.0), (1800, 0.6), (2800, 0.3))), 1.0, 0.35)
# Nacht 2
for i, tt in enumerate(list(np.arange(22.62, 23.1, 0.22)) + list(np.arange(24.47, 24.9, 0.19))):
    add(sfx, tt, step(0.13, 240), 1.0, 0.1)
add(sfx, 23.4, bp(noise(0.25), 800, 5000) * env_ad(int(SR * 0.25), 0.01, 0.07), 0.22, 0.15)
add(sfx, 23.95, giggle(980, 5, 0.22), 1.0, 0.1)
add(sfx, 25.15, fold(0.35)[: int(SR * 0.4)], 1.0, -0.2)
# Nacht 3
for i, tt in enumerate(np.arange(28.62, 29.2, 0.22)):
    add(sfx, tt, step(0.13, 250), 1.0, -0.1)
add(sfx, 29.45, rustle(0.45, 0.18, 800, 5000), 1.0, 0.1)
add(sfx, 30.1, giggle(940, 6, 0.24, 0.1), 1.0, 0.05)
add(sfx, 31.15, fold(0.35)[: int(SR * 0.4)], 1.0, 0.25)
# Montage: Türchen-Klicks
for d in range(4, 24):
    td = 35.0 + (d - 3 + 0.35) * 0.27 - 0.27 + 0.27
    n = int(SR * 0.05)
    add(sfx, td, bp(noise(0.05), 2500, 9000) * env_ad(n, 0.001, 0.006), 0.35, 0.3 * math.sin(d))
# Nacht 24
for i, tt in enumerate(np.arange(40.65, 41.1, 0.28)):
    add(sfx, tt, step(0.14, 220), 1.0, 0.2)
add(sfx, 41.2, fold(0.6), 1.0, 0.1)
add(sfx, 41.25, rustle(0.7, 0.2, 900, 6000), 1.0, 0.1)
add(sfx, 42.05, fold(0.6), 1.0, 0.0)
add(sfx, 42.1, rustle(0.6, 0.2, 900, 6000), 1.0, 0.0)
add(sfx, 42.75, rustle(0.5, 0.2), 1.0, 0.1)
add(sfx, 43.35, giggle(900, 6, 0.24, 0.1), 1.0, 0.2)
add(sfx, 44.15, fold(0.4)[: int(SR * 0.4)], 1.0, 0.1)
add(sfx, 45.5, whoosh(1.2, 0.18, 500, 3500), 1.0, -0.3)
# Antwortbrief
add(sfx, 50.4, scratch(1.4, 0.24, 700, 3500, 5.0), 1.0, 0.0)
add(sfx, 51.9, fold(0.5), 1.0, 0.05)
add(sfx, 52.5, fold(0.5), 1.0, 0.05)
add(sfx, 52.7, rustle(0.4, 0.2, 800, 5000, 150), 1.0, 0.05)
add(sfx, 53.05, rustle(1.2, 0.18, 600, 4000, 20), 1.0, 0.15)
add(sfx, 54.65, warm_on(0.35), 1.0, 0.2)
add(sfx, 54.9, giggle(1000, 4, 0.13), 1.0, 0.3)
# Endcard: Briefe fliegen ein
for i in range(17):
    tc = 56.0 + 0.12 + i * 0.055
    add(sfx, tc + 0.1, whoosh(0.5, 0.05, 900, 3000), 1.0, -0.8 + 0.1 * i)
    add(sfx, tc + 0.7, bp(noise(0.05), 2500, 9000) * env_ad(int(SR * 0.05), 0.001, 0.007), 0.18, -0.8 + 0.1 * i)

# ------------------------------------------------------------------ Mischung
def reverb(x, secs=2.2, wet=0.25, seed=3):
    r = np.random.RandomState(seed)
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = r.randn(n) * np.exp(-t * 6.9 / secs)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    out = np.zeros_like(x)
    for c in range(2):
        out[:, c] = fftconvolve(x[:, c], ir * (1 if c == 0 else 1), 'full')[: len(x)]
    return x * (1 - wet) + out * wet * 2.5


mus_r = reverb(mus, 2.6, 0.32)
sfx_r = reverb(sfx, 0.9, 0.15, seed=4)
mix_ = mus_r * 0.9 + sfx_r * 1.0
mix_ = hp(mix_.T, 30).T
peak = np.abs(mix_).max()
mix_ = np.tanh(mix_ / peak * 1.3) / math.tanh(1.3) * 0.89
fade = np.clip((DUR - np.arange(N) / SR) / 0.6, 0, 1)
mix_ *= fade[:, None]


def write(fn):
    data = (mix_ * 32767).astype('<i2')
    with wave.open(fn, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == '__main__':
    import sys
    write(sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav')
    print('ok')
