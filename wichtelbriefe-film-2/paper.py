"""Papier-Grundbausteine: gerissene Kanten, Schatten, Zweiton-Falz, Glow, Kritzel."""
import math
import cairo
import numpy as np

# ---------------------------------------------------------------- Farben
CREAM = (0.965, 0.918, 0.815)
CREAM2 = (0.915, 0.855, 0.740)
CREAM3 = (0.840, 0.770, 0.650)
WHITE = (0.990, 0.975, 0.945)
WHITE2 = (0.900, 0.895, 0.880)
RED = (0.780, 0.215, 0.190)
RED_D = (0.610, 0.145, 0.145)
RED_L = (0.890, 0.345, 0.290)
GREEN = (0.180, 0.420, 0.300)
GREEN_D = (0.115, 0.310, 0.225)
GREEN_L = (0.300, 0.545, 0.400)
PINK = (0.960, 0.765, 0.760)
PINK_D = (0.900, 0.640, 0.650)
BLUE = (0.690, 0.810, 0.915)
BLUE_D = (0.560, 0.690, 0.820)
BLUE_L = (0.790, 0.880, 0.955)
MINT = (0.740, 0.890, 0.800)
YELLOW = (0.985, 0.875, 0.520)
YELLOW_D = (0.930, 0.740, 0.330)
LILAC = (0.820, 0.760, 0.905)
WOOD = (0.835, 0.640, 0.440)
WOOD_D = (0.720, 0.520, 0.340)
WOOD_L = (0.890, 0.720, 0.530)
SKIN = (0.985, 0.830, 0.710)
SKIN_D = (0.930, 0.715, 0.590)
HAIR = (0.540, 0.330, 0.200)
HAIR_D = (0.430, 0.250, 0.150)
INK = (0.330, 0.170, 0.150)
GOLD = (0.960, 0.780, 0.330)
GOLD_D = (0.850, 0.600, 0.200)
BROWN = (0.420, 0.270, 0.190)
WARM = (1.00, 0.70, 0.36)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def darker(c, f=0.78):
    return (c[0] * f, c[1] * f, c[2] * f)


# ---------------------------------------------------------------- Zeit-Helfer
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lin(t, t0, t1):
    if t1 == t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease(t, t0, t1):
    x = lin(t, t0, t1)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def spring(x):
    if x <= 0:
        return 0.0
    return 1 - math.exp(-5.5 * x) * math.cos(8.5 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def twos(t, fps=12.0):
    """Stop-Motion-Zeit: Figuren bewegen sich auf 'Zweiern'."""
    return math.floor(t * fps) / fps


# ---------------------------------------------------------------- Geometrie
def ellipse_pts(cx, cy, rx, ry, n=None, rot=0.0, a0=0.0, a1=2 * math.pi):
    if n is None:
        n = int(max(14, min(90, (rx + ry) * 0.9)))
    a = np.linspace(a0, a1, n, endpoint=(a1 - a0) < 2 * math.pi - 1e-6)
    x = rx * np.cos(a)
    y = ry * np.sin(a)
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        x, y = x * c - y * s, x * s + y * c
    return np.column_stack([x + cx, y + cy])


def rect_pts(x, y, w, h):
    return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], float)


def rot_pts(pts, ang, cx=0.0, cy=0.0):
    P = np.asarray(pts, float) - (cx, cy)
    c, s = math.cos(ang), math.sin(ang)
    return np.column_stack([P[:, 0] * c - P[:, 1] * s, P[:, 0] * s + P[:, 1] * c]) + (cx, cy)


def tr_pts(pts, dx, dy, sx=1.0, sy=1.0):
    P = np.asarray(pts, float)
    return np.column_stack([P[:, 0] * sx + dx, P[:, 1] * sy + dy])


def star_pts(cx, cy, r1, r2, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts)


_noise_cache = {}


def _noise_params(seed):
    seed = int(seed)
    if seed not in _noise_cache:
        r = np.random.RandomState(seed % (2 ** 31))
        _noise_cache[seed] = (r.uniform(0, 6.283, 4), r.uniform(0.8, 1.25, 4))
    return _noise_cache[seed]


def deckle(pts, seed=0, u=1.0, amp=0.55, seg=3.5):
    """Weiche, gerissene Papierkante: Kante unterteilen und entlang der Normale verschieben.
    Rauschen hängt nur von der Bogenlänge ab -> kein Flackern zwischen Frames."""
    P = np.asarray(pts, float)
    Q = np.vstack([P, P[:1]])
    D = np.diff(Q, axis=0)
    L = np.hypot(D[:, 0], D[:, 1])
    segl = seg * u
    out = []
    s0 = 0.0
    for i in range(len(L)):
        n = max(1, int(L[i] / segl))
        t = np.arange(n) / n
        p = Q[i] + D[i] * t[:, None]
        nl = np.array([-D[i, 1], D[i, 0]]) / max(L[i], 1e-9)
        s = (s0 + t * L[i]) / u
        out.append((p, nl, s))
        s0 += L[i]
    ph, fr = _noise_params(seed)
    res = []
    for p, nl, s in out:
        nz = (np.sin(s * 0.21 * fr[0] + ph[0]) * 0.55 + np.sin(s * 0.63 * fr[1] + ph[1]) * 0.3
              + np.sin(s * 1.7 * fr[2] + ph[2]) * 0.22 + np.sin(s * 3.9 * fr[3] + ph[3]) * 0.1)
        res.append(p + nl[None, :] * (nz * amp * u)[:, None])
    return np.vstack(res)


def path(ctx, pts):
    ctx.new_path()
    it = iter(pts)
    x, y = next(it)
    ctx.move_to(x, y)
    for x, y in it:
        ctx.line_to(x, y)
    ctx.close_path()


def piece(ctx, pts, col, seed=0, u=1.0, shadow=1.0, outline=True, amp=0.55, alpha=1.0, edge=0.78):
    """Ein Stück Papier: weicher Schatten, Fläche, leicht dunklere Kante."""
    p = deckle(pts, seed, u, amp) if amp > 0 else np.asarray(pts, float)
    if shadow > 0:
        for k, a in ((1.0, 0.10), (0.55, 0.12)):
            ctx.save()
            ctx.translate(1.6 * u * shadow * k, 2.4 * u * shadow * k)
            path(ctx, p)
            ctx.set_source_rgba(0.22, 0.13, 0.10, a * alpha)
            ctx.fill()
            ctx.restore()
    path(ctx, p)
    ctx.set_source_rgba(col[0], col[1], col[2], alpha)
    if outline:
        ctx.fill_preserve()
        e = darker(col, edge)
        ctx.set_source_rgba(e[0], e[1], e[2], 0.85 * alpha)
        ctx.set_line_width(0.75 * u)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.fill()
    return p


def piece2(ctx, pts, col_a, col_b, p0, p1, seed=0, u=1.0, shadow=1.0, amp=0.55, alpha=1.0, crease=True):
    """Zweiton-Papier mit scharfer Falzkante entlang p0->p1 (links col_a, rechts col_b)."""
    p = deckle(pts, seed, u, amp) if amp > 0 else np.asarray(pts, float)
    if shadow > 0:
        for k, a in ((1.0, 0.10), (0.55, 0.12)):
            ctx.save()
            ctx.translate(1.6 * u * shadow * k, 2.4 * u * shadow * k)
            path(ctx, p)
            ctx.set_source_rgba(0.22, 0.13, 0.10, a * alpha)
            ctx.fill()
            ctx.restore()
    path(ctx, p)
    ctx.set_source_rgba(col_b[0], col_b[1], col_b[2], alpha)
    ctx.fill()
    # Halbebene links der Falzlinie
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1
    dx, dy = dx / ln, dy / ln
    nx, ny = dy, -dx
    big = 1e4
    hp = np.array([[p0[0] - dx * big, p0[1] - dy * big], [p0[0] + dx * big, p0[1] + dy * big],
                   [p0[0] + dx * big + nx * big, p0[1] + dy * big + ny * big],
                   [p0[0] - dx * big + nx * big, p0[1] - dy * big + ny * big]])
    ctx.save()
    path(ctx, p)
    ctx.clip()
    path(ctx, hp)
    ctx.set_source_rgba(col_a[0], col_a[1], col_a[2], alpha)
    ctx.fill()
    if crease:
        ctx.move_to(p0[0] - dx * big, p0[1] - dy * big)
        ctx.line_to(p0[0] + dx * big, p0[1] + dy * big)
        e = darker(col_b, 0.85)
        ctx.set_source_rgba(e[0], e[1], e[2], 0.5 * alpha)
        ctx.set_line_width(0.45 * u)
        ctx.stroke()
    ctx.restore()
    path(ctx, p)
    e = darker(col_b, 0.78)
    ctx.set_source_rgba(e[0], e[1], e[2], 0.85 * alpha)
    ctx.set_line_width(0.75 * u)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    return p


def dot(ctx, x, y, r, col, alpha=1.0):
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgba(col[0], col[1], col[2], alpha)
    ctx.fill()


def line(ctx, pts, col, w, alpha=1.0, cap=cairo.LINE_CAP_ROUND):
    if len(pts) < 2:
        return
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgba(col[0], col[1], col[2], alpha)
    ctx.set_line_width(w)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def glow(ctx, x, y, r, col, a, op=cairo.OPERATOR_ADD):
    if a <= 0.001:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    for o in (0.0, 0.15, 0.35, 0.6, 1.0):
        k = (1 - o) ** 2.2
        g.add_color_stop_rgba(o, col[0], col[1], col[2], a * k)
    ctx.save()
    ctx.set_operator(op)
    ctx.set_source(g)
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def arc_stroke(ctx, cx, cy, r, a0, a1, col, w):
    ctx.new_path()
    ctx.arc(cx, cy, r, a0, a1)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def scribble_pts(x0, y0, width, rows, row_gap, seed, h=1.0, sy=1.0):
    """Handschrift-Schnörkel ohne lesbaren Text: Schleifen (Zykloiden) mit Wortlücken."""
    r = np.random.RandomState(seed)
    strokes = []
    for row in range(rows):
        x = x0 + (r.uniform(0, 0.15) * width if row else 0.12 * width)
        end = x0 + width * (r.uniform(0.6, 0.85) if row == rows - 1 else r.uniform(0.9, 1.0))
        y = y0 + row * row_gap
        while x < end - h * 2:
            wl = min(r.uniform(3, 7) * h * 1.4, end - x)
            n = max(6, int(wl / h * 6))
            th = np.linspace(0, wl / h * 2.2, n)
            amp = h * r.uniform(0.7, 1.0)
            xs = x + th / (wl / h * 2.2) * wl - 0.45 * h * np.sin(th)
            ys = y - amp * (0.55 + 0.45 * np.cos(th * 0.5 + r.uniform(0, 3))) * np.abs(np.sin(th * 0.5)) * 1.3
            ys = y + (ys - y) * sy
            strokes.append(np.column_stack([xs, ys]))
            x += wl + h * r.uniform(1.2, 2.0)
    return strokes


def draw_scribbles(ctx, strokes, col, w, progress=1.0, alpha=1.0):
    """Zeichnet Kritzel bis 'progress' (0..1) und gibt die aktuelle Stiftspitze zurück."""
    total = sum(len(s) for s in strokes)
    lim = progress * total
    cnt = 0
    tip = None
    for s in strokes:
        if cnt >= lim:
            break
        k = int(min(len(s), lim - cnt))
        if k >= 2:
            line(ctx, s[:k], col, w, alpha)
            tip = s[k - 1]
        cnt += len(s)
    return tip


def paper_texture(size=1024, seed=7):
    """Nahtlos kachelbare Papierfaser-Textur (Werte ~0.86..1.0)."""
    r = np.random.RandomState(seed)
    fx = np.fft.fftfreq(size)[:, None]
    fy = np.fft.fftfreq(size)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2) + 1e-4
    spec = np.fft.fft2(r.randn(size, size)) / f ** 1.1
    base = np.real(np.fft.ifft2(spec))
    base = (base - base.mean()) / base.std()
    # Fasern: anisotropes Rauschen in zwei Richtungen
    fib = np.zeros((size, size))
    for ang in r.uniform(0, np.pi, 6):
        k = np.cos(ang) * fx + np.sin(ang) * fy
        kp = -np.sin(ang) * fx + np.cos(ang) * fy
        filt = np.exp(-(k / 0.004) ** 2) * np.exp(-(kp / 0.25) ** 2)
        fib += np.real(np.fft.ifft2(np.fft.fft2(r.randn(size, size)) * filt))
    fib = (fib - fib.mean()) / fib.std()
    fine = r.randn(size, size)
    v = 0.955 - 0.022 * base - 0.018 * np.clip(fib, -3, 3) - 0.008 * fine
    v = np.clip(v, 0.82, 1.0)
    img = (v * 255).astype(np.uint8)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, size, size)
    buf = np.ndarray((size, surf.get_stride() // 4, 4), np.uint8, surf.get_data())
    buf[:, :size, 0] = img
    buf[:, :size, 1] = img
    buf[:, :size, 2] = img
    buf[:, :size, 3] = 255
    surf.mark_dirty()
    return surf
