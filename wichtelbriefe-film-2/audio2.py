"""Soundtrack 'Die Mission': Klavier, Glockenspiel, Pizzicato-Streicher + Geräusche, komplett synthetisiert."""
import math
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.RandomState(7)
mus = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or len(sig) == 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    l = math.cos((pan + 1) * math.pi / 4) * 1.414
    r = math.sin((pan + 1) * math.pi / 4) * 1.414
    buf[i:j, 0] += s * l
    buf[i:j, 1] += s * r


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tvec(d):
    return np.arange(int(SR * d)) / SR


# ------------------------------------------------------------------ Instrumente
def piano(m, dur=2.0, vel=0.6):
    f = hz(m)
    t = tvec(dur)
    out = np.zeros(len(t))
    for h in range(1, 9):
        fh = f * h * math.sqrt(1 + 0.0004 * h * h)
        if fh > 15000:
            break
        out += (1.0 / h ** 1.25) * np.sin(2 * math.pi * fh * t + h) * np.exp(-t * (1.3 + 0.9 * h + f / 600))
    att = np.minimum(1, t / 0.004)
    rel = np.minimum(1, (dur - t) / 0.08)
    ham = bp(rng.randn(len(t)), 1500, 5000) * np.exp(-t * 90) * 0.05
    return (out * att * rel + ham) * vel * 0.3


def glock(m, dur=1.8, vel=0.5):
    f = hz(m)
    t = tvec(dur)
    out = np.zeros(len(t))
    for ratio, amp, dec in ((1.0, 1.0, 2.4), (2.756, 0.35, 6), (5.404, 0.16, 12), (8.933, 0.07, 20)):
        if f * ratio < 18000:
            out += amp * np.sin(2 * math.pi * f * ratio * t) * np.exp(-t * dec)
    return out * np.minimum(1, t / 0.0015) * vel * 0.24


def pizz(m, vel=0.6, dur=0.7):
    """Pizzicato-Streicher via Karplus-Strong."""
    f = hz(m)
    n = int(SR * dur)
    L = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, L)
    buf = lp(buf, min(6000, f * 8))
    out = np.zeros(n)
    idx = 0
    damp = 0.4985 if f < 300 else 0.497
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % L
        buf[idx] = damp * (buf[idx] + buf[nxt])
        idx = nxt
    t = np.arange(n) / SR
    body = lp(out, 2500) * np.exp(-t * 5.5)
    return body * vel * 0.9 * np.minimum(1, t / 0.002)


def pad(freqs, dur, env, vel=0.15):
    t = tvec(dur)
    out = np.zeros(len(t))
    for f in freqs:
        for det in (-0.006, 0.0, 0.0055):
            vib = 1 + 0.0035 * np.sin(2 * math.pi * 5.1 * t + rng.uniform(0, 6))
            ph = 2 * math.pi * np.cumsum(f * (1 + det) * vib) / SR
            for h in range(1, 10):
                if f * h > 8000:
                    break
                out += np.sin(h * ph) / h
    out = lp(out, 2200)
    return out * env(t) * vel / max(1, len(freqs))


_pizz_cache = {}


def pz(m, vel):
    if m not in _pizz_cache:
        _pizz_cache[m] = pizz(m, 1.0)
    return _pizz_cache[m] * vel


# ------------------------------------------------------------------ Musik
Dm = [50, 53, 57]
F = [53, 57, 60]
Bb = [46, 50, 53]
C = [48, 52, 55]
A = [45, 49, 52]
Gm = [43, 46, 50]

# 0–8: geheimnisvoll (d-Moll): tiefe Klaviertöne, einzelne Glockenspiel-Töne
for i, (tt, m) in enumerate(((0.2, 38), (2.6, 41), (5.0, 36), (7.0, 38))):
    add(mus, tt, piano(m, 3.0, 0.5), 1.0, -0.2)
for tt, m in ((0.9, 81), (1.7, 77), (2.5, 74), (3.4, 81), (4.4, 84), (5.4, 79), (6.3, 77), (6.8, 81)):
    add(mus, tt, glock(m, 2.0, 0.35), 1.0, 0.4)
add(mus, 0.0, pad([hz(50), hz(57), hz(62)], 8.5, lambda t: np.minimum(1, t / 2) * np.clip((8.5 - t) / 1.5, 0, 1), 0.10))

# 8–12 und 22.5–25: Schleich-Motiv (Pizzicato)
sneak = [50, 53, 57, 55, 53, 52, 50, 45]
for (t0, t1) in ((7.8, 10.6), (22.5, 24.4)):
    tt = t0
    k = 0
    while tt < t1:
        add(mus, tt, pz(sneak[k % 8] + (12 if k % 16 >= 8 else 0), 0.42), 1.0, 0.2 if k % 2 else -0.2)
        if k % 4 == 0:
            add(mus, tt, pz(38, 0.35), 1.0, -0.3)
        tt += 0.32
        k += 1

# 10.6–18: Sturm – Tremolo-Fläche (verminderter Akkord)
add(mus, 10.55, pad([hz(45), hz(48), hz(51), hz(54)], 7.8, lambda t: np.minimum(1, t / 0.6) * np.clip((7.8 - t) / 2.0, 0, 1)
                    * (0.75 + 0.25 * np.sin(2 * np.pi * 9 * t)), 0.17), 1.0, 0.0)
for tt, m in ((10.6, 86), (12.6, 84), (14.6, 81), (16.6, 79)):
    add(mus, tt, glock(m, 2.0, 0.3), 1.0, -0.4)

# 18–22.5: Katze erwacht – tiefer Cluster, ein 'Ping' beim Augenöffnen
add(mus, 18.0, piano(38, 4.0, 0.45), 1.0, -0.2)
add(mus, 18.0, piano(39, 4.0, 0.25), 1.0, 0.2)
add(mus, 19.0, glock(89, 2.5, 0.5), 1.0, 0.3)
add(mus, 19.65, glock(88, 2.5, 0.35), 1.0, 0.3)
add(mus, 20.8, piano(41, 2.5, 0.4), 1.0, -0.2)

# 25–34.8: Verfolgung – schnell und verspielt (Pizzicato + Klavier-Ostinato), 160 BPM
beat = 60 / 160
prog = [Dm, Dm, Bb, C, F, F, Gm, A]
tt = 24.9
k = 0
while tt < 34.75:
    ch = prog[(k // 8) % len(prog)]
    step = k % 8
    note = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[2] + 12][step]
    v = 0.85 + 0.35 * min(1, (tt - 24.9) / 8)
    add(mus, tt, piano(note, 0.6, 0.42 * v), 1.0, 0.25)
    if step % 2 == 0:
        add(mus, tt, pz(ch[0] - (12 if step == 0 else 0), 0.65 * v), 1.0, -0.3)
    if step in (3, 7):
        add(mus, tt, pz(ch[2] + 12, 0.5 * v), 1.0, 0.35)
    if step == 6 and (k // 8) % 2 == 1:
        add(mus, tt, glock(note + 24, 1.2, 0.35 * v), 1.0, 0.5)
    tt += beat / 2
    k += 1
# 34.8–36.4: Stille (nur ein langer, tiefer Atem)
# 36.4–42: Gleitflug – leichtes Glockenspiel/Klavier in F-Dur
for i, tt in enumerate(np.arange(36.45, 42.0, 0.45)):
    ch = [F, C, Bb, F][int((tt - 36.45) / 1.8) % 4]
    add(mus, tt, glock(ch[i % 3] + 24 + (12 if i % 6 == 5 else 0), 1.6, 0.32), 1.0, 0.4 * math.sin(i))
    if i % 2 == 0:
        add(mus, tt, piano(ch[0], 1.6, 0.35), 1.0, -0.2)
add(mus, 36.4, pad([hz(53), hz(60), hz(65)], 6.0, lambda t: np.minimum(1, t / 1.5) * np.clip((6 - t) / 1.2, 0, 1), 0.10))
add(mus, 38.9, pad([hz(56), hz(59), hz(62)], 1.6, lambda t: np.sin(np.pi * np.clip(t / 1.6, 0, 1)), 0.10))
# 42–47: Eile – leises Pizzicato-Ticken, Stopp bei den Schritten
for i, tt in enumerate(np.arange(42.6, 44.3, 0.21)):
    add(mus, tt, pz([57, 60, 62, 60][i % 4], 0.35), 1.0, 0.3 if i % 2 else -0.3)
for i, tt in enumerate(np.arange(45.3, 46.9, 0.16)):
    add(mus, tt, pz([62, 64, 65, 67, 69, 70, 72, 74, 76, 77][min(i, 9)], 0.4), 1.0, 0.2)
add(mus, 47.05, glock(84, 2.0, 0.4), 1.0, 0.2)
add(mus, 47.6, pad([hz(53), hz(57), hz(60)], 3.0, lambda t: np.minimum(1, t / 1.5) * np.clip((3 - t) / 0.5, 0, 1), 0.08))
# 50–56: Pop-up – warm anschwellend (F-Dur)
swell = lambda t: np.minimum(1, (t / 1.3) ** 1.5) * np.clip((6.2 - t) / 1.2, 0, 1)
add(mus, 50.0, pad([hz(41), hz(53), hz(57), hz(60), hz(65)], 6.2, swell, 0.16), 1.0, 0.0)
for i, (tt, ch) in enumerate(((50.0, F), (51.2, F), (52.4, Bb), (53.6, C), (54.8, F))):
    for j, m in enumerate([ch[0] - 12, ch[0], ch[1], ch[2], ch[1] + 12, ch[2] + 12]):
        add(mus, tt + j * 0.13, piano(m, 2.5, 0.45 if i else 0.3), 1.0, -0.3 + 0.12 * j)
for i in range(9):
    add(mus, 51.15 + i * 0.07, glock([84, 88, 91, 96, 93, 91, 96, 100, 96][i], 1.6, 0.4), 1.0, math.sin(i) * 0.6)
for tt, m in ((52.4, 81), (52.9, 84), (53.6, 86), (54.2, 84), (54.8, 89)):
    add(mus, tt, glock(m, 2.0, 0.4), 1.0, 0.3)
# 56–60: Pointe + Schluss
for i, (tt, m) in enumerate(((56.2, 57), (56.45, 55), (56.7, 53))):
    add(mus, tt, pz(m, 0.6), 1.0, 0.2)
add(mus, 57.0, pad([hz(53), hz(57), hz(60), hz(65)], 3.0, lambda t: np.minimum(1, t / 0.8) * np.clip((3 - t) / 1.0, 0, 1), 0.18))
for j, m in enumerate([41, 53, 57, 60, 65, 69]):
    add(mus, 57.9 + j * 0.06, piano(m, 2.2, 0.45), 1.0, -0.3 + 0.12 * j)
for i in range(7):
    add(mus, 58.0 + i * 0.08, glock([84, 88, 91, 96, 100, 96, 101][i], 1.5, 0.4), 1.0, math.sin(i * 1.3) * 0.6)
add(mus, 59.3, pz(53, 0.7), 1.0, 0.0)
add(mus, 59.3, pz(41, 0.6), 1.0, 0.0)


# ------------------------------------------------------------------ Geräusche
def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))


def rustle(d, amp=0.3, lo=1800, hi=9000, density=60):
    n = int(SR * d)
    x = bp(rng.randn(n), lo, hi)
    cr = np.zeros(n)
    k = max(1, int(density * d))
    cr[rng.randint(0, n, k)] = rng.uniform(0.5, 1.5, k)
    cr = np.convolve(cr, np.exp(-np.arange(int(SR * 0.004)) / (SR * 0.0008)), 'same')
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    mod = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * rng.uniform(3, 7) * t + rng.uniform(0, 6)))
    return (x * 0.6 * mod + bp(cr * rng.randn(n), 2000, 10000) * 2.0) * env * amp


def fold(amp=0.45):
    sw = rustle(0.32, amp * 0.8, 1200, 7000, 30)
    n = int(SR * 0.06)
    click = bp(rng.randn(n), 2500, 9000) * env_ad(n, 0.001, 0.008) * amp * 1.4
    out = np.zeros(len(sw) + n)
    out[: len(sw)] += sw
    out[int(SR * 0.27): int(SR * 0.27) + n] += click
    return out


def step(amp=0.2, f=200):
    t = tvec(0.09)
    return (np.sin(2 * np.pi * f * t * (1 - 0.3 * t / 0.09)) * np.exp(-t * 55) + bp(rng.randn(len(t)), 1500, 6000) * np.exp(-t * 160) * 0.35) * amp


def heavy_step(amp=0.5):
    t = tvec(0.3)
    return lp(np.sin(2 * np.pi * 70 * t) * np.exp(-t * 18) + rng.randn(len(t)) * np.exp(-t * 40) * 0.4, 400) * amp


def scratch(d, amp=0.2, lo=2500, hi=7500, rate=9.0):
    t = tvec(d)
    x = bp(rng.randn(len(t)), lo, hi, 3)
    stroke = np.abs(np.sin(2 * np.pi * rate * t + 2 * np.sin(2 * np.pi * 1.3 * t))) ** 1.5
    return x * stroke * amp * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.05)


def giggle(f0=900, n_syl=5, amp=0.22, spacing=0.1):
    total = int(SR * (n_syl * spacing + 0.2))
    out = np.zeros(total)
    for i in range(n_syl):
        d = spacing * 0.7
        t = tvec(d)
        f = f0 * (1.08 - 0.05 * i) * (1 + 0.06 * np.sin(np.pi * t / d))
        ph = 2 * np.pi * np.cumsum(f) / SR
        src = sum(np.sin(h * ph) / h ** 0.9 for h in range(1, 14))
        v = bp(src, 680, 920) + 0.5 * bp(src, 2200, 3000) + 0.25 * bp(src, 3300, 4000)
        s = (v + bp(rng.randn(len(t)), 3000, 8000) * 0.12) * np.sin(np.pi * t / d) ** 1.5
        i0 = int(SR * i * spacing * (1 + 0.1 * rng.rand()))
        out[i0:i0 + len(t)] += s
    return out / (np.abs(out).max() + 1e-9) * amp


def creak(d=0.4, amp=0.1, f0=900):
    t = tvec(d)
    f = f0 * (1 + 0.4 * t / d) * (1 + 0.05 * np.sin(2 * np.pi * 37 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = bp((np.sin(ph) > 0.9).astype(float) + 0.2 * np.sin(ph), 500, 4000)
    return s * np.sin(np.pi * t / d) * amp


def whoosh(d, amp=0.2, f0=600, f1=3000):
    n = int(SR * d)
    x = rng.randn(n + 4096)
    out = np.zeros(n)
    seg = 2048
    for i in range(0, n, seg):
        fc = f0 + (f1 - f0) * math.sin(i / n * math.pi)
        out[i:i + seg] = bp(x[i:i + seg + 512], fc * 0.7, fc * 1.4)[: len(out[i:i + seg])]
    t = np.arange(n) / SR
    return lp(out, 6000) * np.sin(np.pi * t / d) ** 2 * amp


def wind(d, amp=0.4):
    """Heulender Wind: Rauschen durch wandernde, resonante Bandpässe."""
    n = int(SR * d)
    x = rng.randn(n)
    t = np.arange(n) / SR
    out = np.zeros(n)
    seg = 4096
    for k, (base, sw, a) in enumerate(((420, 260, 1.0), (760, 300, 0.6), (1300, 400, 0.3))):
        for i in range(0, n, seg):
            fc = base + sw * math.sin(2 * math.pi * (0.23 + 0.1 * k) * i / SR + k)
            out[i:i + seg] += a * bp(x[i:i + seg + 1024], fc * 0.93, fc * 1.07, 2)[: len(out[i:i + seg])]
    out += lp(x, 300) * 0.8
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * t) ** 2
    return out * gust * amp


def knock(amp=0.4, f=520):
    t = tvec(0.18)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 40) + np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t * 70) * 0.5
            + bp(rng.randn(len(t)), 1500, 6000) * np.exp(-t * 200) * 0.6) * amp


def purr(d, amp=0.35, rate=26):
    t = tvec(d)
    pulses = np.maximum(0, np.sin(2 * np.pi * rate * t)) ** 3
    breath = 0.55 + 0.45 * np.sin(2 * np.pi * 0.45 * t) ** 2
    s = lp(rng.randn(len(t)), 380) * pulses * 1.6 + np.sin(2 * np.pi * 52 * t) * pulses * 0.6
    return s * breath * amp * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.3)


def hiss(d=0.5, amp=0.5):
    t = tvec(d)
    s = hp(rng.randn(len(t)), 1800) * (1 + 0.3 * np.sin(2 * np.pi * 31 * t))
    return lp(s, 9000) * np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - 0.2) * 5) * amp


def crackle(d, amp=0.25, dens=30):
    n = int(SR * d)
    out = lp(rng.randn(n), 200) * 0.3
    k = int(dens * d)
    for i in rng.randint(0, n - 2000, k):
        m = rng.randint(150, 900)
        out[i:i + m] += bp(rng.randn(m), 900, 6000) * np.exp(-np.arange(m) / (m / 5)) * rng.uniform(0.4, 1.4)
    return out * amp


def mrrp(amp=0.3):
    t = tvec(0.45)
    f = 220 * (1 + 0.25 * np.sin(np.pi * t / 0.45)) * (1 - 0.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(h * ph) / h for h in range(1, 12))
    s = bp(src, 300, 1200) + 0.4 * bp(src, 1800, 2600)
    am = 0.6 + 0.4 * np.maximum(0, np.sin(2 * np.pi * 22 * t))
    return s * am * np.sin(np.pi * t / 0.45) * amp


add(sfx, 0.0, lp(rng.randn(N), 220) * 0.03, 1.0)                        # Raumton
add(sfx, 0.0, wind(9.0, 0.07) * np.minimum(1, tvec(9.0) / 1.5) * np.clip((9 - tvec(9.0)) / 2, 0, 1), 1.0, 0.5)
# Banner falten
for tt in (1.0, 18.85, 51.85):
    add(sfx, tt, fold(0.32), 1.0, 0.0)
for tt in (4.68, 22.13, 55.13):
    add(sfx, tt, fold(0.26)[::-1].copy(), 1.0, 0.0)
# Stube
add(sfx, 2.05, scratch(1.2, 0.2), 1.0, 0.2)
add(sfx, 3.4, fold(0.4), 1.0, 0.1)
add(sfx, 4.0, fold(0.4), 1.0, 0.1)
add(sfx, 4.75, rustle(0.5, 0.2), 1.0, 0.2)
add(sfx, 5.15, step(0.25, 180), 1.0, 0.1)
for tt in np.arange(5.62, 6.2, 0.35):
    add(sfx, tt, step(0.12, 220), 1.0, -0.2)
# Tür + Schleichen
add(sfx, 7.15, creak(0.45, 0.10), 1.0, -0.3)
for i, tt in enumerate(np.arange(7.55, 10.6, 0.42)):
    add(sfx, tt, step(0.13, 230 + 20 * (i % 2)), 1.0, -0.3 + 0.03 * i)
# Sturm
add(sfx, 10.55, wind(8.0, 0.32) * np.minimum(1, tvec(8.0) / 0.3) * np.clip((8.0 - tvec(8.0)) / 2.5, 0, 1), 1.0, 0.1)
add(sfx, 10.6, knock(0.7, 380), 1.0, -0.1)
add(sfx, 10.63, knock(0.6, 460), 1.0, 0.2)
for tt in sorted(rng.uniform(10.9, 16.5, 22)):
    add(sfx, tt, knock(rng.uniform(0.2, 0.45), rng.uniform(420, 620)), 1.0, rng.uniform(-0.3, 0.3))
add(sfx, 12.55, rustle(0.4, 0.4, 1000, 8000, 140), 1.0, 0.0)
add(sfx, 12.6, rustle(5.2, 0.22, 1200, 7000, 25) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 4 * tvec(5.2)))), 1.0, 0.2)
for i, tt in enumerate(np.arange(13.45, 14.6, 0.18)):
    add(sfx, tt, step(0.14, 250), 1.0, 0.1)
add(sfx, 17.8, rustle(0.25, 0.25, 1500, 7000, 80), 1.0, 0.2)
# Katze
add(sfx, 18.0, purr(6.3, 0.55), 1.0, 0.25)
for i, tt in enumerate(np.arange(22.55, 23.85, 0.4)):
    add(sfx, tt, step(0.1, 240), 1.0, -0.1)
add(sfx, 24.0, rustle(0.45, 0.22, 1500, 7000, 60), 1.0, 0.1)
add(sfx, 24.38, hiss(0.6, 0.45), 1.0, 0.25)
add(sfx, 24.45, whoosh(0.3, 0.22, 700, 2500), 1.0, 0.2)
# Verfolgung
for i, tt in enumerate(np.arange(24.6, 28.85, 0.165)):
    add(sfx, tt, step(0.14, 240 + 30 * (i % 2)), 1.0, -0.2 + 0.4 * ((tt - 24.6) / 4.3))
for i, tt in enumerate(np.arange(25.25, 28.9, 0.42)):
    add(sfx, tt, heavy_step(0.18) * (0.5 if 27.4 < tt < 29 else 1), 1.0, -0.2)
    add(sfx, tt + 0.09, heavy_step(0.14), 1.0, -0.2)
for tt in np.arange(28.95, 32.0, 0.26):
    add(sfx, tt, scratch(0.12, 0.16, 1200, 4500, 30), 1.0, 0.1)
add(sfx, 28.9, rustle(5.5, 0.14, 2500, 10000, 50), 1.0, 0.3)                 # Lametta
for tt in sorted(rng.uniform(29.0, 35.0, 12)):
    add(sfx, tt, glock(int(rng.choice([93, 96, 98, 100])), 0.6, 0.18), 1.0, rng.uniform(-0.4, 0.6))
for tt in (32.4, 32.95, 33.5, 34.05):
    add(sfx, tt, fold(0.42), 1.0, 0.3)
add(sfx, 34.5, hiss(0.5, 0.35), 1.0, -0.1)
# Sprung + Zeitlupe
add(sfx, 34.8, lp(whoosh(1.7, 0.35, 150, 700), 1500), 1.0, -0.2)
# Gleitflug + Kamin
add(sfx, 36.4, whoosh(5.6, 0.10, 500, 1800), 1.0, -0.3)
add(sfx, 36.5, crackle(5.0, 0.20) * np.sin(np.pi * np.clip(tvec(5.0) / 5.0, 0, 1)) ** 2, 1.0, 0.1)
add(sfx, 39.05, hp(rng.randn(int(SR * 0.6)), 3000) * env_ad(int(SR * 0.6), 0.02, 0.18) * 0.18, 1.0, 0.1)   # Ansengen
# Landung, Entfalten, Schritte
add(sfx, 42.0, rustle(0.6, 0.3, 800, 6000, 40), 1.0, -0.2)
for tt in np.arange(42.7, 44.3, 0.27):
    add(sfx, tt, fold(0.3), 1.0, -0.2)
for i, tt in enumerate(np.arange(44.3, 48.2, 0.58)):
    add(sfx, tt, heavy_step(0.30 + 0.06 * i), 1.0, -0.5)
add(sfx, 45.2, rustle(0.25, 0.2), 1.0, -0.3)
for tt in np.arange(45.3, 46.3, 0.13):
    add(sfx, tt, step(0.12, 260), 1.0, 0.0)
add(sfx, 45.85, creak(0.25, 0.06, 1100), 1.0, 0.1)
t_click = tvec(0.05)
add(sfx, 47.0, bp(rng.randn(len(t_click)), 2000, 8000) * env_ad(len(t_click), 0.001, 0.006) * 0.5, 1.0, 0.1)
add(sfx, 47.02, knock(0.15, 900), 1.0, 0.1)
add(sfx, 48.0, creak(1.2, 0.07, 500), 1.0, -0.6)
for tt in np.arange(48.8, 50.0, 0.4):
    add(sfx, tt, lp(rustle(0.25, 0.25, 300, 2500, 10), 2500), 1.0, -0.5)
# Pop-up
add(sfx, 50.3, rustle(0.7, 0.32, 1500, 9000, 110), 1.0, -0.2)
add(sfx, 50.65, whoosh(0.4, 0.12, 800, 2500), 1.0, -0.2)
add(sfx, 51.5, giggle(520, 4, 0.18, 0.14), 1.0, 0.3)
add(sfx, 53.5, rustle(0.4, 0.2), 1.0, 0.0)
add(sfx, 53.9, giggle(560, 3, 0.15, 0.16), 1.0, 0.0)
add(sfx, 55.35, giggle(1000, 4, 0.13, 0.09), 1.0, -0.2)
# Pointe
add(sfx, 56.3, mrrp(0.28), 1.0, 0.2)
add(sfx, 57.0, whoosh(0.9, 0.14, 700, 3000), 1.0, 0.4)
add(sfx, 57.0, rustle(0.8, 0.18), 1.0, 0.4)


def reverb(x, secs=2.2, wet=0.25, seed=3):
    r = np.random.RandomState(seed)
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = lp(r.randn(n) * np.exp(-t * 6.9 / secs), 5000)
    ir /= np.sqrt((ir ** 2).sum())
    out = np.zeros_like(x)
    for c in range(2):
        out[:, c] = fftconvolve(x[:, c], ir, 'full')[: len(x)]
    return x * (1 - wet) + out * wet * 2.5


mix_ = reverb(mus, 2.4, 0.3) * 0.95 + reverb(sfx, 0.8, 0.14, 4) * 1.0
mix_ = hp(mix_.T, 30).T
mix_ = np.tanh(mix_ / np.abs(mix_).max() * 1.3) / math.tanh(1.3) * 0.89
mix_ *= np.clip((DUR - np.arange(N) / SR) / 0.5, 0, 1)[:, None]

if __name__ == '__main__':
    import sys
    data = (mix_ * 32767).astype('<i2')
    with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav', 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    for s in range(0, 60, 4):
        seg = mix_[s * SR:(s + 4) * SR]
        print(s, round(float(np.sqrt((seg ** 2).mean())), 3))
