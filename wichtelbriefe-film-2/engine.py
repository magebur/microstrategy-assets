"""Schattenkasten-Compositing: Papierebenen mit weichen (geblurrten) Schlagschatten,
weltfester Papierstruktur pro Ebene, Kamera mit Parallax."""
import math
import cairo
import numpy as np
from scipy.ndimage import gaussian_filter
from paper import *

_tex = {}


def textures():
    if 'p' not in _tex:
        _tex['p'] = crumple_texture()
    return _tex['p']


def crumple_texture(size=1024, seed=11):
    """Papierfasern + leichte Knitterfacetten + Prägespuren, nahtlos kachelbar."""
    r = np.random.RandomState(seed)
    fx = np.fft.fftfreq(size)[:, None]
    fy_ = np.fft.fftfreq(size)[None, :]
    f = np.sqrt(fx ** 2 + fy_ ** 2) + 1e-4
    base = np.real(np.fft.ifft2(np.fft.fft2(r.randn(size, size)) / f ** 1.15))
    base = (base - base.mean()) / base.std()
    fib = np.zeros((size, size))
    for ang in r.uniform(0, np.pi, 7):
        k = np.cos(ang) * fx + np.sin(ang) * fy_
        kp = -np.sin(ang) * fx + np.cos(ang) * fy_
        filt = np.exp(-(k / 0.0035) ** 2) * np.exp(-(kp / 0.28) ** 2)
        fib += np.real(np.fft.ifft2(np.fft.fft2(r.randn(size, size)) * filt))
    fib = (fib - fib.mean()) / fib.std()
    # Knitter: periodisches Voronoi-Facettenmuster mit Lichtrichtung
    n = 26
    pts = r.uniform(0, size, (n, 2))
    shade = r.uniform(-1, 1, n)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    best = np.full((size, size), 1e9, np.float32)
    second = np.full((size, size), 1e9, np.float32)
    val = np.zeros((size, size), np.float32)
    for i in range(n):
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                d = (xx - pts[i, 0] - ox) ** 2 + (yy - pts[i, 1] - oy) ** 2
                m = d < best
                second = np.where(m, best, np.minimum(second, d))
                val = np.where(m, shade[i], val)
                best = np.where(m, d, best)
    edge = np.sqrt(second) - np.sqrt(best)
    crease = np.exp(-edge / 1.6)
    fine = r.randn(size, size)
    v = (0.955 - 0.018 * base - 0.016 * np.clip(fib, -3, 3) - 0.007 * fine
         - 0.012 * val - 0.035 * crease)
    v = np.clip(v, 0.82, 1.0)
    img = (v * 255).astype(np.uint8)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, size, size)
    buf = np.ndarray((size, surf.get_stride() // 4, 4), np.uint8, surf.get_data())
    for c in range(3):
        buf[:, :size, c] = img
    buf[:, :size, 3] = 255
    surf.mark_dirty()
    return surf


def cam_matrix(W, H, cx, cy, z, k=1.0, rot=0.0):
    S = W / 1920.0
    m = cairo.Matrix()
    m.translate(W / 2, H / 2)
    if rot:
        m.rotate(rot)
    m.scale(S * z * k, S * z * k)
    m.translate(-cx, -cy)
    return m


def screen_matrix(W):
    S = W / 1920.0
    return cairo.Matrix(xx=S, yy=S)


class Layer:
    def __init__(self, fn, mat, shadow=None, tex=2.0, tex_alpha=1.0):
        self.fn = fn
        self.mat = mat
        self.shadow = shadow      # (dx, dy, blur, alpha) in Basis-Pixeln (1920er Raster)
        self.tex = tex
        self.tex_alpha = tex_alpha


def _shadow(octx, surf, W, H, sh):
    dx, dy, blur, alpha = sh
    S = W / 1920.0
    f = max(1, int(round(4 * S)))
    a = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W, 3]
    h2, w2 = H // f, W // f
    small = a[:h2 * f, :w2 * f].reshape(h2, f, w2, f).mean(axis=(1, 3))
    sig = blur * S / f
    if sig > 0.3:
        small = gaussian_filter(small, sig, mode='constant')
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_A8, w2)
    arr = np.zeros((h2, stride), np.uint8)
    arr[:, :w2] = np.clip(small, 0, 255).astype(np.uint8)
    ms = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_A8, w2, h2, stride)
    octx.save()
    octx.translate(dx * S, dy * S)
    octx.scale(f, f)
    octx.set_source_rgba(0.16, 0.09, 0.07, alpha)
    pat = cairo.SurfacePattern(ms)
    pat.set_filter(cairo.FILTER_BILINEAR)
    octx.mask(pat)
    octx.restore()
    del arr


def compose(W, H, layers, bg=(0.2, 0.2, 0.25)):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    octx = cairo.Context(out)
    octx.set_source_rgb(*bg)
    octx.paint()
    tex = textures()
    for L in layers:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        c.set_matrix(L.mat)
        L.fn(c)
        surf.flush()
        if L.shadow is not None:
            _shadow(octx, surf, W, H, L.shadow)
        octx.set_source_surface(surf)
        octx.paint()
        if L.tex:
            pat = cairo.SurfacePattern(tex)
            pat.set_extend(cairo.EXTEND_REPEAT)
            pat.set_filter(cairo.FILTER_GOOD)
            inv = cairo.Matrix(*L.mat)
            inv.invert()
            pm = inv.multiply(cairo.Matrix(xx=L.tex, yy=L.tex))
            pat.set_matrix(pm)
            octx.save()
            octx.set_operator(cairo.OPERATOR_MULTIPLY)
            octx.set_source(pat)
            octx.mask_surface(surf)
            octx.restore()
        surf.finish()
    return out, octx


def tint_all(octx, col):
    octx.save()
    octx.identity_matrix()
    octx.set_operator(cairo.OPERATOR_MULTIPLY)
    octx.set_source_rgb(*col)
    octx.paint()
    octx.restore()


def to_array(surf, W, H):
    surf.flush()
    arr = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W, :3]
    return arr[:, :, ::-1].astype(np.float32)


# ------------------------------------------------------------------ Form-Helfer
def catmull(pts, n=8, closed=True):
    """Weiche Kurve durch Stützpunkte (Catmull-Rom) -> dichtes Polygon."""
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P[-1:], P, P[:2]])
    else:
        P = np.vstack([P[:1], P, P[-1:]])
    out = []
    ts = np.linspace(0, 1, n, endpoint=False)
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in ts:
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(P[-2])
    return np.array(out)


def rounded(pts, r):
    """Polygon mit sauber abgerundeten Ecken (Radius r, begrenzt durch Kantenlänge)."""
    P = np.asarray(pts, float)
    n = len(P)
    out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        v1 = a - b
        v2 = c - b
        l1, l2 = np.hypot(*v1), np.hypot(*v2)
        if l1 < 1e-6 or l2 < 1e-6:
            out.append(b)
            continue
        rr = min(r, l1 * 0.45, l2 * 0.45)
        p1 = b + v1 / l1 * rr
        p2 = b + v2 / l2 * rr
        for k in np.linspace(0, 1, 5):
            out.append((1 - k) ** 2 * p1 + 2 * (1 - k) * k * b + k * k * p2)
    return np.array(out)


def _shape(pts, n):
    if n <= 3:
        P = np.asarray(pts, float)
        span = max(np.ptp(P[:, 0]), np.ptp(P[:, 1]))
        return rounded(P, max(1.0, span * 0.03 * n))
    return catmull(pts, n)


def soft(ctx, pts, col, seed=0, u=1.0, shadow=1.0, n=8, amp=0.18, alpha=1.0, edge=0.8):
    """Weich gerundetes, sauber geschnittenes Papierstück (n<=3: eckig mit runden Ecken)."""
    return piece(ctx, _shape(pts, n), col, seed=seed, u=u, shadow=shadow, amp=amp, alpha=alpha, edge=edge)


def soft2(ctx, pts, a, b, p0, p1, seed=0, u=1.0, shadow=1.0, n=8, amp=0.18, alpha=1.0):
    return piece2(ctx, _shape(pts, n), a, b, p0, p1, seed=seed, u=u, shadow=shadow, amp=amp, alpha=alpha)


def emboss(ctx, pts, col, u=1.0, depth=1.0, raised=True, alpha=1.0):
    """Präge-/Stanzmotiv: Licht oben links, Schatten unten rechts, kaum Farbänderung."""
    s = 1 if raised else -1
    hl = mix(col, (1, 1, 1), 0.45)
    sh = darker(col, 0.72)
    for (o, c, a) in ((-0.9, hl, 0.75), (0.9, sh, 0.55)):
        ctx.save()
        ctx.translate(o * s * u * depth, o * s * u * depth)
        path(ctx, pts)
        ctx.set_source_rgba(*c, a * alpha)
        ctx.fill()
        ctx.restore()
    path(ctx, pts)
    ctx.set_source_rgba(*mix(col, (1, 1, 1), 0.04 if raised else 0), alpha)
    ctx.fill()


def heart_pts(cx, cy, s, n=36):
    return np.array([(cx + s * 16 * math.sin(a) ** 3 / 16, cy - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16)
                     for a in np.linspace(0, 2 * math.pi, n, endpoint=False)])


def sprig_pts(x, y, L, ang=0.0):
    """Tannenzweig-Motiv als Liste von Nadelpolygonen."""
    out = []
    c, s = math.cos(ang), math.sin(ang)

    def T(px, py):
        return (x + px * c - py * s, y + px * s + py * c)
    out.append(np.array([T(0, -0.6), T(L, -0.3), T(L, 0.3), T(0, 0.6)]))
    for k in range(1, 7):
        px = L * k / 7.5
        for sg in (-1, 1):
            out.append(np.array([T(px, 0), T(px + L * 0.16, sg * L * 0.13), T(px + L * 0.2, sg * L * 0.11), T(px + L * 0.06, 0)]))
    return out


def snowflake_pts(r, holes=True):
    """Gestanzte Papierschneeflocke: Sechsstern mit runden Löchern (Even-Odd)."""
    outer = []
    for i in range(12):
        a = i * math.pi / 6 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.52
        outer.append((rr * math.cos(a), rr * math.sin(a)))
    return catmull(outer, 4)


def draw_snowflake(ctx, x, y, r, rot, alpha=1.0, col=WHITE):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    p = snowflake_pts(r)
    ctx.save()
    ctx.translate(r * 0.12, r * 0.18)
    path(ctx, p)
    ctx.set_source_rgba(0.15, 0.15, 0.25, 0.18 * alpha)
    ctx.fill()
    ctx.restore()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    path(ctx, p)
    ctx.new_sub_path()
    ctx.arc(0, 0, r * 0.16, 0, 2 * math.pi)
    for i in range(6):
        a = i * math.pi / 3 - math.pi / 2
        ctx.new_sub_path()
        ctx.arc(math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, r * 0.09, 0, 2 * math.pi)
    ctx.set_source_rgba(*col, alpha)
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.restore()
