"""Figuren: Papierwichtel und Papierkind."""
import math
import numpy as np
from paper import *


# ====================================================================== Wichtel
def flame(ctx, x, y, size, t, seed=0):
    """Kerzenflamme (emissiv, nach der Nachttönung zeichnen)."""
    fl = 1 + 0.12 * math.sin(t * 23 + seed) + 0.08 * math.sin(t * 37 + 2 * seed)
    sw = 0.25 * math.sin(t * 11 + seed)
    h = 9 * size * fl
    w = 3.2 * size
    pts = [(x, y - h)]
    for a in np.linspace(0, math.pi, 12):
        pts.append((x + sw * size + w * math.cos(a), y - w * 0.2 * math.sin(a) + 0.0))
    pts = np.array([(x + sw * size * 2.0, y - h)] + [(x + w * math.cos(a), y + w * 0.6 * math.sin(a)) for a in np.linspace(0, math.pi, 14)])
    path(ctx, pts)
    ctx.set_source_rgb(1.0, 0.72, 0.30)
    ctx.fill()
    pts2 = np.array([(x + sw * size * 1.6, y - h * 0.62)] + [(x + w * 0.55 * math.cos(a), y + w * 0.45 * math.sin(a)) for a in np.linspace(0, math.pi, 10)])
    path(ctx, pts2)
    ctx.set_source_rgb(1.0, 0.95, 0.72)
    ctx.fill()
    return fl


def quill(ctx, hx, hy, ang=-0.9, u=0.35):
    """Schreibfeder, Spitze bei (hx,hy)."""
    L = 26
    pts = []
    n = 14
    for i in range(n + 1):
        k = i / n
        w = math.sin(k * math.pi) ** 0.8 * 4.2 * (1 - 0.3 * k)
        pts.append((k * L, -w))
    for i in range(n, -1, -1):
        k = i / n
        w = math.sin(k * math.pi) ** 0.8 * 3.0 * (1 - 0.3 * k)
        pts.append((k * L, w))
    P = rot_pts(np.array(pts) + (3, 0), ang) + (hx, hy)
    piece2(ctx, P, WHITE, WHITE2, (hx, hy), (hx + math.cos(ang) * 30, hy + math.sin(ang) * 30), seed=91, u=u, shadow=0.6)
    line(ctx, [(hx, hy), (hx + math.cos(ang) * 31, hy + math.sin(ang) * 31)], CREAM3, 0.6)
    dot(ctx, hx, hy, 0.7, INK)


def candle(ctx, x, y, s=1.0, u=0.35):
    """Kerze auf Untersetzer, Fußpunkt (x,y). Gibt Dochtposition zurück."""
    piece(ctx, ellipse_pts(x, y - 1 * s, 7 * s, 2.2 * s, n=20), RED_D, seed=31, u=u, shadow=0.6)
    piece(ctx, ellipse_pts(x, y - 2 * s, 6 * s, 1.7 * s, n=20), RED, seed=32, u=u, shadow=0)
    body = rect_pts(x - 2.6 * s, y - 15 * s, 5.2 * s, 13 * s)
    piece2(ctx, body, CREAM, CREAM2, (x + 0.6 * s, y), (x + 0.6 * s, y - 20), seed=33, u=u, shadow=0.4)
    # Wachstropfen
    piece(ctx, ellipse_pts(x - 1.2 * s, y - 13.5 * s, 1.3 * s, 2.3 * s, n=10), WHITE, seed=34, u=u * 0.6, shadow=0, amp=0.2)
    line(ctx, [(x, y - 15 * s), (x + 0.2 * s, y - 17 * s)], INK, 0.6 * s)
    return (x + 0.2 * s, y - 17.2 * s)


def mini_letter(ctx, x, y, w, h, col=CREAM, seal=RED, u=0.35, seed=5, tilt=0.0, seal_star=False):
    """Gefalteter Brief (Vorderseite mit Umschlag-Falz und Siegel), Mittelpunkt unten (x,y)."""
    pts = rect_pts(-w / 2, -h, w, h)
    pts = rot_pts(pts, tilt) + (x, y)
    piece(ctx, pts, col, seed=seed, u=u, shadow=0.8)
    # Umschlag-Klappe: V-Falz
    c, s_ = math.cos(tilt), math.sin(tilt)

    def T(px, py):
        return (x + px * c - py * s_, y + px * s_ + py * c)
    fl = np.array([T(-w / 2, -h), T(w / 2, -h), T(0, -h * 0.42)])
    piece(ctx, fl, darker(col, 0.92), seed=seed + 1, u=u, shadow=0.25, amp=0.2)
    sx, sy = T(0, -h * 0.45)
    if seal_star:
        piece(ctx, star_pts(sx, sy, h * 0.24, h * 0.11), seal, seed=seed + 2, u=u * 0.6, shadow=0.3, amp=0.15)
    else:
        piece(ctx, ellipse_pts(sx, sy, h * 0.14, h * 0.14, n=14), seal, seed=seed + 2, u=u * 0.6, shadow=0.3, amp=0.25)


def gnome(ctx, x, y, s=0.95, facing=1, phase=None, sit=0.0, hand=None, item=None, sway=0.0,
          blink=False, bob=0.0, hand_back=None, t=0.0, squash=0.0, look=0.0, cheer=0.0):
    """Papierwichtel. (x,y) = Fußpunkt. Gibt Weltposition der Hand (vorn) zurück."""
    u = 0.35
    ctx.save()
    ctx.translate(x, y)
    # Bodenschatten
    ctx.save()
    ctx.scale(1, 0.22)
    dot(ctx, 0, 0, 15 * s, (0.15, 0.08, 0.05), 0.22)
    ctx.restore()
    ctx.scale(s * facing, s * (1 - squash))
    fl = fr = 0.0
    ll = lr = 0.0
    if phase is not None:
        fl = math.sin(phase) * 5.5
        fr = -fl
        ll = max(0.0, math.cos(phase)) * 3.0
        lr = max(0.0, -math.cos(phase)) * 3.0
        bob = abs(math.sin(phase)) * 1.8 + bob
    dy = -bob + sit * 6.0
    lean = (0.06 if phase is not None else 0.0) + cheer * -0.05
    # hinterer Arm
    sh_b = (-9, -27 + dy)
    hb = hand_back if hand_back is not None else (-13 - fl * 0.4, -15 + dy)
    if cheer > 0:
        hb = (lerp(hb[0], -16, cheer), lerp(hb[1], -44 + dy, cheer))
    line(ctx, [sh_b, hb], darker(GREEN_D, 0.85), 5.2)
    dot(ctx, hb[0], hb[1], 2.7, SKIN_D)
    # Füße
    if sit > 0.5:
        piece(ctx, ellipse_pts(10, -3, 7, 3.6, n=16), BROWN, seed=11, u=u, shadow=0.5)
        piece(ctx, ellipse_pts(17, -2.5, 7, 3.6, n=16), darker(BROWN, 0.9), seed=12, u=u, shadow=0.5)
    else:
        piece(ctx, ellipse_pts(-5 + fl, -3 - ll, 7, 3.6, n=16), darker(BROWN, 0.88), seed=11, u=u, shadow=0.5)
        piece(ctx, ellipse_pts(6 + fr, -3 - lr, 7, 3.6, n=16), BROWN, seed=12, u=u, shadow=0.5)
    ctx.save()
    ctx.translate(0, dy)
    ctx.rotate(lean)
    # Kittel
    tun = np.array([(-13, -5), (13, -5), (9.5, -31), (-9.5, -31)])
    piece2(ctx, tun, GREEN_L, GREEN, (1.5, 0), (0.5, -40), seed=13, u=u)
    line(ctx, [(-12, -12), (12, -12)], darker(RED_D, 0.9), 2.2, cap=0)
    dot(ctx, 3.5, -12, 1.4, GOLD)
    # Bart
    br = np.array([(-11.5, -41), (11.5, -41), (11, -31), (7, -22), (2, -15.5), (-1, -15), (-6, -21), (-10.5, -30)])
    piece2(ctx, br, WHITE, WHITE2, (2.5, -45), (1.0, -14), seed=14, u=u, amp=1.1)
    # Gesicht: Nase und Augen
    piece(ctx, ellipse_pts(3.5 + look, -41, 5.6, 5.0, n=18), (0.95, 0.62, 0.58), seed=15, u=u, shadow=0.7)
    dot(ctx, 2.0 + look, -42.5, 1.4, (1, 0.85, 0.82), 0.8)
    if blink:
        line(ctx, [(-3.2 + look, -46), (-0.8 + look, -46)], INK, 0.9)
        line(ctx, [(6.2 + look, -46), (8.6 + look, -46)], INK, 0.9)
    else:
        dot(ctx, -2.0 + look, -46.2, 1.35, INK)
        dot(ctx, 7.4 + look, -46.2, 1.35, INK)
    if cheer > 0.3:
        # lachende Augenbögen
        pass
    # Mütze (Kegel mit Falz)
    tipx = -15 + sway * 6
    hat = np.array([(-13.5, -44), (-11, -55), (-8.5, -64), (tipx + 2, -76), (tipx, -81), (tipx + 6, -77),
                    (3, -64), (8, -55), (13.5, -44)])
    piece2(ctx, hat, RED_L, RED, (0.5, -44), (tipx + 3, -79), seed=16, u=u)
    piece(ctx, ellipse_pts(tipx, -81, 3.3, 3.3, n=14), WHITE, seed=17, u=u, amp=0.9, shadow=0.5)
    ctx.restore()
    # vorderer Arm
    sh = (9 + lean * 30, -27 + dy)
    hf = hand if hand is not None else (13 + fl * 0.4, -15 + dy)
    if cheer > 0:
        hf = (lerp(hf[0], 17, cheer), lerp(hf[1], -46 + dy, cheer))
    if item == 'flour':
        # Mehlsäckchen über der Schulter
        sk = ellipse_pts(-4, -34 + dy, 9, 8, n=18)
        piece2(ctx, sk, CREAM, CREAM2, (-4, -44 + dy), (-4, -24 + dy), seed=18, u=u, amp=0.9)
        line(ctx, [(-1, -41 + dy), (3, -44 + dy)], RED_D, 1.4)
    line(ctx, [sh, hf], GREEN_D, 5.2)
    dot(ctx, hf[0], hf[1], 2.8, SKIN)
    ctx.restore()
    wx = x + facing * s * hf[0]
    wy = y + s * (1 - squash) * hf[1]
    return wx, wy


# ====================================================================== Kind
def child_head(ctx, cx, cy, r, joy=0.3, blink=False, look=(0.0, 0.0), gap=False, u=1.2, seed=200, sleep=False,
               mouth_o=0.0, tilt=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(tilt)
    # Haare hinten
    piece(ctx, ellipse_pts(0, -0.06 * r, r * 1.1, r * 1.02), HAIR_D, seed=seed, u=u, amp=0.9)
    # Ohren
    piece(ctx, ellipse_pts(-r * 0.98, 0.08 * r, r * 0.17, r * 0.21), SKIN_D, seed=seed + 1, u=u * 0.6)
    piece(ctx, ellipse_pts(r * 0.98, 0.08 * r, r * 0.17, r * 0.21), SKIN_D, seed=seed + 2, u=u * 0.6)
    # Gesicht (Zweiton)
    face = ellipse_pts(0, 0.04 * r, r * 0.96, r * 0.93)
    piece2(ctx, face, SKIN, mix(SKIN, SKIN_D, 0.55), (r * 0.42, -r), (r * 0.30, r), seed=seed + 3, u=u)
    # Pony
    pts = []
    for a in np.linspace(math.pi * 1.04, math.pi * 1.96, 22):
        pts.append((math.cos(a) * r * 1.03, math.sin(a) * r * 1.0 - 0.04 * r))
    teeth = 6
    xs = np.linspace(r * 0.93, -r * 0.93, teeth * 2 + 1)
    for i, xx in enumerate(xs):
        yy = -0.28 * r if i % 2 == 0 else -0.44 * r
        yy += -0.12 * r * (abs(xx) / r) ** 2
        pts.append((xx, yy))
    piece2(ctx, np.array(pts), HAIR, HAIR_D, (r * 0.35, -1.2 * r), (r * 0.15, 0), seed=seed + 4, u=u, amp=0.6)
    # Haarbüschel
    tuft = np.array([(-0.1 * r, -1.0 * r), (0.05 * r, -1.28 * r), (0.2 * r, -1.22 * r), (0.12 * r, -0.98 * r)])
    piece(ctx, tuft, HAIR, seed=seed + 5, u=u * 0.6, shadow=0.4)
    lx, ly = look[0] * r * 0.08, look[1] * r * 0.06
    ey = -0.05 * r
    ex = 0.34 * r
    # Wangen
    ca = 0.22 + 0.55 * joy
    for sx in (-1, 1):
        ctx.save()
        ctx.translate(sx * 0.55 * r, 0.24 * r)
        ctx.scale(1, 0.62)
        dot(ctx, 0, 0, 0.17 * r, (0.97, 0.55, 0.55), ca)
        ctx.restore()
    # Augen
    if sleep:
        for sx in (-1, 1):
            arc_stroke(ctx, sx * ex, ey, 0.1 * r, 0.15 * math.pi, 0.85 * math.pi, INK, 0.045 * r)
    elif blink:
        for sx in (-1, 1):
            line(ctx, [(sx * ex - 0.1 * r + lx, ey + ly), (sx * ex + 0.1 * r + lx, ey + ly)], INK, 0.045 * r)
    elif joy > 0.78:
        for sx in (-1, 1):
            arc_stroke(ctx, sx * ex + lx * 0.4, ey + 0.05 * r, 0.12 * r, 1.1 * math.pi, 1.9 * math.pi, INK, 0.055 * r)
    else:
        er = r * (0.085 + 0.03 * clamp((joy - 0.3) * 2))
        for sx in (-1, 1):
            dot(ctx, sx * ex + lx, ey + ly, er, INK)
            dot(ctx, sx * ex + lx - er * 0.35, ey + ly - er * 0.4, er * 0.33, WHITE)
    # Mund
    my = 0.36 * r
    if sleep:
        arc_stroke(ctx, 0, my - 0.06 * r, 0.08 * r, 0.2 * math.pi, 0.8 * math.pi, INK, 0.035 * r)
    elif joy < 0.55 and mouth_o < 0.3:
        w = 0.12 + 0.28 * joy
        arc_stroke(ctx, 0, my - 0.22 * r * (w / 0.27), r * w, 0.25 * math.pi, 0.75 * math.pi, INK, 0.045 * r)
    else:
        k = clamp(max((joy - 0.5) * 2.2, mouth_o))
        mw = r * (0.22 + 0.16 * k)
        mh = r * (0.12 + 0.2 * k)
        pts = [(-mw, my - 0.02 * r), (mw, my - 0.02 * r)]
        for a in np.linspace(0, math.pi, 16):
            pts.append((mw * math.cos(a), my - 0.02 * r + mh * math.sin(a)))
        P = np.array(pts[1:])
        path(ctx, P)
        ctx.set_source_rgb(0.55, 0.16, 0.18)
        ctx.fill()
        ctx.save()
        path(ctx, P)
        ctx.clip()
        dot(ctx, 0, my + mh * 1.05, mw * 0.62, (0.93, 0.50, 0.52))
        # Zähne oben
        ctx.rectangle(-mw, my - 0.03 * r, 2 * mw, mh * 0.32)
        ctx.set_source_rgb(*WHITE)
        ctx.fill()
        if gap:
            ctx.rectangle(-mw * 0.18 + mw * 0.15, my - 0.03 * r, mw * 0.3, mh * 0.34)
            ctx.set_source_rgb(0.45, 0.12, 0.14)
            ctx.fill()
        ctx.restore()
        path(ctx, P)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(0.035 * r)
        ctx.stroke()
    ctx.restore()


def pajama_dots(ctx, poly, seed, r=4.5, n=14):
    ctx.save()
    path(ctx, poly)
    ctx.clip()
    rs = np.random.RandomState(seed)
    xs, ys = poly[:, 0], poly[:, 1]
    for i in range(n):
        x = rs.uniform(xs.min(), xs.max())
        y = rs.uniform(ys.min(), ys.max())
        dot(ctx, x, y, r, WHITE, 0.85)
    ctx.restore()


def child(ctx, x, y, s=1.0, facing=1, pose='stand', phase=0.0, joy=0.4, blink=False, look=(0.6, 0.3),
          hand=None, hand2=None, jump=0.0, gap=False, holding=None, t=0.0, mouth_o=0.0):
    """Papierkind (ca. 330 Einheiten groß). Gibt Weltposition der vorderen Hand zurück."""
    u = 1.2
    ctx.save()
    ctx.translate(x, y)
    ctx.save()
    ctx.scale(1, 0.2)
    dot(ctx, 0, 0, 62 * s * (1 - 0.3 * jump), (0.15, 0.08, 0.05), 0.2)
    ctx.restore()
    ctx.scale(s * facing, s)
    ctx.translate(0, -jump * 70)
    hand_out = None
    if pose in ('stand', 'run', 'jump'):
        sw = math.sin(phase) if pose == 'run' else 0.0
        bob = abs(math.cos(phase)) * 10 if pose == 'run' else 0.0
        ctx.translate(0, -bob)
        # Beine
        for side, k in ((-1, -sw), (1, sw)):
            ctx.save()
            ctx.translate(side * 17, -100)
            ctx.rotate(k * 0.5)
            leg = np.array([(-14, 0), (14, 0), (12, 92), (-12, 92)])
            piece(ctx, leg, BLUE_D if side < 0 else BLUE, seed=210 + side, u=u)
            piece(ctx, ellipse_pts(6, 96, 20, 9), RED_D if side < 0 else RED, seed=212 + side, u=u)
            ctx.restore()
        # hinterer Arm
        a_back = (-0.2 + sw * 0.8) if pose != 'jump' else -2.6
        if pose == 'stand' and hand2 is None:
            a_back = 0.15
        ctx.save()
        ctx.translate(-36, -200)
        ctx.rotate(a_back)
        arm = np.array([(-11, 0), (11, 0), (9, 84), (-9, 84)])
        piece(ctx, arm, BLUE_D, seed=215, u=u)
        piece(ctx, ellipse_pts(0, 90, 12, 12), SKIN_D, seed=216, u=u * 0.6)
        ctx.restore()
        # Rumpf
        tor = np.array([(-50, -92), (50, -92), (40, -214), (-40, -214)])
        piece2(ctx, tor, BLUE_L, BLUE, (10, -80), (8, -230), seed=217, u=u)
        pajama_dots(ctx, tor, 3)
        line(ctx, [(-50, -96), (50, -96)], BLUE_D, 4)
        # vorderer Arm
        a_f = (0.2 - sw * 0.8) if pose != 'jump' else 2.6
        if pose == 'stand':
            a_f = -0.15
        ctx.save()
        ctx.translate(36, -200)
        if hand is not None:
            a_f = math.atan2(-(hand[0] - 36), hand[1] + 200)
        ctx.rotate(a_f)
        arm = np.array([(-11, 0), (11, 0), (9, 84), (-9, 84)])
        piece(ctx, arm, BLUE_L, seed=218, u=u)
        piece(ctx, ellipse_pts(0, 90, 12.5, 12.5), SKIN, seed=219, u=u * 0.6)
        ctx.restore()
        hx = 36 - math.sin(a_f) * 90
        hy = -200 + math.cos(a_f) * 90 - bob
        hand_out = (hx, hy)
        child_head(ctx, 0, -266, 58, joy, blink, look, gap, u=u * 0.9, mouth_o=mouth_o,
                   tilt=0.04 * sw)
    elif pose == 'sit':
        # Kind kniet / sitzt auf dem Boden, Blick nach rechts
        thigh = np.array([(-30, -58), (62, -52), (70, -10), (-36, -8)])
        piece(ctx, thigh, BLUE_D, seed=230, u=u)
        piece(ctx, ellipse_pts(80, -10, 22, 10), RED_D, seed=231, u=u)
        thigh2 = np.array([(-22, -50), (74, -44), (84, -6), (-26, -4)])
        piece(ctx, thigh2, BLUE, seed=232, u=u)
        piece(ctx, ellipse_pts(96, -8, 22, 10), RED, seed=233, u=u)
        # hinterer Arm
        h2 = hand2 if hand2 is not None else (40, -70)
        _limb(ctx, (-20, -150), h2, BLUE_D, SKIN_D, 234, u)
        tor = np.array([(-46, -46), (40, -46), (34, -166), (-36, -166)])
        piece2(ctx, tor, BLUE_L, BLUE, (6, -40), (4, -180), seed=235, u=u)
        pajama_dots(ctx, tor, 5)
        h1 = hand if hand is not None else (60, -60)
        hand_out = h1
        child_head(ctx, 4, -218, 58, joy, blink, look, gap, u=u * 0.9, mouth_o=mouth_o, tilt=0.12)
        _limb(ctx, (22, -150), h1, BLUE_L, SKIN, 236, u)
    ctx.restore()
    if hand_out is None:
        return None
    return (x + facing * s * hand_out[0], y + s * (hand_out[1] - jump * 70))


def _limb(ctx, a, b, col, hcol, seed, u):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ctx.save()
    ctx.translate(*a)
    ctx.rotate(ang)
    arm = np.array([(0, -11), (L, -9), (L, 9), (0, 11)])
    piece(ctx, arm, col, seed=seed, u=u)
    piece(ctx, ellipse_pts(L + 4, 0, 12.5, 12.5), hcol, seed=seed + 1, u=u * 0.6)
    ctx.restore()
