"""Wichtel (Krepppapier-Mütze, gerissener Faserbart, Knopfaugen) und Papierkatze (Akkordeon-Segmente)."""
import math
import cairo
import numpy as np
from paper import *
from engine import catmull, soft, soft2, emboss, heart_pts

CAT = (0.930, 0.620, 0.345)
CAT_D = (0.845, 0.505, 0.265)
CAT_DD = (0.720, 0.400, 0.200)
CAT_CREAM = (0.985, 0.915, 0.800)
LEG = (0.300, 0.230, 0.200)
BOOT = (0.450, 0.290, 0.200)


def ik(a, b, L1, L2, bend=1.0):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return a
    d2 = min(d, L1 + L2 - 1e-3)
    x = (L1 * L1 - L2 * L2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, L1 * L1 - x * x))
    ux, uy = dx / d, dy / d
    return (ax + ux * x - uy * h * bend, ay + uy * x + ux * h * bend)


def limb(ctx, a, b, L1, L2, w, col, bend=1.0, w2=None):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d > (L1 + L2) * 0.995:
        f = (L1 + L2) * 0.995 / d
        b = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
    k = ik(a, b, L1, L2, bend)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    # weicher Schatten
    ctx.save()
    ctx.translate(0.5, 0.8)
    line(ctx, [a, k, b], (0.15, 0.08, 0.05), w, alpha=0.18)
    ctx.restore()
    line(ctx, [a, k, b], darker(col, 0.82), w + 0.7)
    line(ctx, [a, k, b], col, w)
    return k


def T(m, p):
    return m.transform_point(*p)


# ====================================================================== Wichtel
def gp(**kw):
    P = dict(crouch=0.0, tilt=0.0, bob=0.0, footB=(-4, 0), footF=(4, 0), handB=None, handF=None, eyes='open',
             look=0.0, sway=0.0, pack=False, squash=0.0, item=None, item_back=None, liftB=0, liftF=0)
    P.update(kw)
    return P


def _g(kw, **base):
    base.update(kw)
    return gp(**base)


def pose_walk(ph, speed=1.0, **kw):
    s = math.sin(ph)
    c = math.cos(ph)
    st = 6.5 * speed
    return _g(kw, footB=(-st * s, -max(0, c) * 3.5), footF=(st * s, -max(0, -c) * 3.5), bob=abs(s) * 1.6,
              handB=(-6 + 4 * s, -10), handF=(7 - 4 * s, -10), tilt=0.05, sway=0.25 * s)


def pose_sneak(ph, **kw):
    s = math.sin(ph)
    c = math.cos(ph)
    return _g(kw, crouch=0.45, footB=(-8 * s - 2, -max(0, c) * 5), footF=(8 * s + 2, -max(0, -c) * 5), bob=abs(s) * 2.0,
              handB=(4, -24), handF=(10, -22), tilt=0.16, sway=0.3 * s)


def pose_run(ph, **kw):
    s = math.sin(ph)
    c = math.cos(ph)
    return _g(kw, crouch=0.2, footB=(-11 * s - 2, -max(0, c) * 7), footF=(11 * s + 2, -max(0, -c) * 7),
              bob=abs(s) * 3.5 + 2, handB=(-9 * s + 2, -14 + 3 * c), handF=(9 * s + 4, -14 - 3 * c), tilt=0.28,
              sway=-0.6 + 0.3 * s)


def pose_climb(ph, **kw):
    s = math.sin(ph)
    return _g(kw, crouch=0.25, footB=(-3, -4 + 6 * s), footF=(5, -4 - 6 * s), handB=(4, -50 - 8 * s), handF=(10, -50 + 8 * s),
              tilt=0.08, sway=0.2 * s)


def pose_freeze(**kw):
    return _g(kw, footB=(-7, 0), footF=(8, -6), handB=(-14, -26), handF=(15, -27), eyes='wide', tilt=-0.04)


def pose_pull(k, **kw):
    return _g(kw, crouch=0.35, footB=(-9, 0), footF=(6, 0), handB=(13 - 4 * k, -14), handF=(16 - 4 * k, -13), tilt=-0.18 * k - 0.05,
              **kw)


def gnome(ctx, x, y, P, s=1.0, facing=1, t=0.0, u=0.3):
    ctx.save()
    ctx.translate(x, y)
    # Kontaktschatten
    ctx.save()
    ctx.scale(1, 0.22)
    dot(ctx, 0, 0, 14 * s, (0.12, 0.06, 0.04), 0.22)
    ctx.restore()
    ctx.scale(s * facing, s * (1 - P['squash']))
    hip_y = -16 * (1 - 0.35 * P['crouch']) - P['bob']
    m = cairo.Matrix()
    m.translate(0, hip_y)
    m.rotate(P['tilt'])
    shB = T(m, (-6, -21))
    shF = T(m, (6, -21))
    hB = P['handB'] or (-8, -9 + hip_y + 16)
    hF = P['handF'] or (9, -9 + hip_y + 16)
    # hinteres Bein + Arm
    hipB = (-3.5, hip_y)
    hipF = (3.5, hip_y)
    limb(ctx, hipB, P['footB'], 8.5, 8.5, 5.6, darker(LEG, 0.85), bend=-1)
    _boot(ctx, P['footB'], darker(BOOT, 0.85), u)
    hB = _reach(shB, hB, 14)
    limb(ctx, shB, hB, 7, 7, 4.6, darker(GREEN_D, 0.85), bend=1)
    dot(ctx, hB[0], hB[1], 2.9, SKIN_D)
    if P['item_back']:
        P['item_back'](ctx, hB)
    # Körper (gekippt um die Hüfte)
    ctx.save()
    ctx.transform(m)
    if P['pack']:
        ctx.save()
        ctx.translate(-12, -12)
        ctx.rotate(-0.12)
        piece(ctx, rect_pts(-7, -10, 14, 19), CREAM, seed=7001, u=u, shadow=0.9, amp=0.2)
        piece(ctx, np.array([(-7, -10), (7, -10), (0, -3)]), CREAM2, seed=7002, u=u, shadow=0.3, amp=0.1)
        dot(ctx, 0, -3.5, 2.0, RED)
        ctx.restore()
    tun = [(-10, 3), (-11, -8), (-8, -20), (0, -24), (8, -20), (11, -8), (10, 3), (0, 5)]
    soft2(ctx, tun, GREEN_L, GREEN, (1.2, 8), (0.5, -30), seed=7010, u=u)
    piece(ctx, rect_pts(-10.6, -3.2, 21.2, 3.6), RED_D, seed=7011, u=u, shadow=0.3, amp=0.1)
    piece(ctx, rect_pts(1.2, -3.6, 4.2, 4.4), GOLD, seed=7012, u=u * 0.5, shadow=0.3, amp=0.1)
    if P['pack']:
        line(ctx, [(-6, -21), (2, -12), (5, -3)], RED_D, 1.6)
    # Gesichtshaut
    piece(ctx, ellipse_pts(1, -31, 9.5, 6.5, n=30), SKIN, seed=7013, u=u, shadow=0.2, amp=0.1)
    # Bart: gerissenes Papier mit Fasern
    br = [(-10.5, -30), (-11.5, -22), (-8.5, -12), (-4, -5), (0, -2), (4, -5), (8.5, -12), (11.5, -22), (10.5, -30), (5, -28.5), (0, -29.5), (-5, -28.5)]
    bp = catmull(br, 8)
    p = piece2(ctx, bp, WHITE, WHITE2, (3.0, -35), (1.0, 0), seed=7014, u=u, amp=1.25, shadow=0.8)
    rs = np.random.RandomState(5)
    for i in range(0, len(p), 3):
        px, py = p[i]
        if py > -24:
            ang = math.atan2(py + 16, px) + rs.uniform(-0.5, 0.5)
            L = rs.uniform(0.8, 2.2)
            line(ctx, [(px, py), (px + math.cos(ang) * L, py + math.sin(ang) * L)], (0.86, 0.85, 0.83), 0.22, alpha=0.9)
    # Nase
    lk = P['look']
    piece(ctx, ellipse_pts(3.2 + lk, -27.5, 5.3, 4.8, n=24), (0.96, 0.64, 0.58), seed=7015, u=u, shadow=0.8, amp=0.1)
    dot(ctx, 1.8 + lk, -29.0, 1.4, (1, 0.86, 0.82), 0.85)
    # Seidenpapier-Wangen
    for (cx, cy) in ((-6.8 + lk, -27.8), (11.4 + lk, -27.8)):
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1, 0.78)
        path(ctx, deckle(ellipse_pts(0, 0, 3.8, 3.8, n=18), 7016 + int(cx), u * 0.6, 0.4))
        ctx.set_source_rgba(0.98, 0.55, 0.62, 0.55)
        ctx.fill()
        ctx.restore()
    # Knopfaugen
    ey = -33.2
    for ex in (-3.4 + lk, 6.6 + lk):
        e = P['eyes']
        if e == 'shut':
            arc_stroke(ctx, ex, ey + 0.6, 2.6, 0.15 * math.pi, 0.85 * math.pi, INK, 0.8)
        elif e == 'squint':
            arc_stroke(ctx, ex, ey + 1.8, 2.6, 1.15 * math.pi, 1.85 * math.pi, INK, 0.9)
        else:
            r = 3.0 if e == 'open' else 3.7
            dot(ctx, ex + 0.3, ey + 0.5, r, (0.1, 0.05, 0.04), 0.35)
            dot(ctx, ex, ey, r, (0.10, 0.07, 0.07))
            ctx.new_path()
            ctx.arc(ex, ey, r - 0.25, 0, 2 * math.pi)
            ctx.set_source_rgba(0.45, 0.38, 0.38, 0.8)
            ctx.set_line_width(0.4)
            ctx.stroke()
            dot(ctx, ex - r * 0.35, ey - r * 0.38, r * 0.36, WHITE)
            dot(ctx, ex + r * 0.38, ey + r * 0.35, r * 0.14, WHITE, 0.8)
    # Krepppapier-Mütze
    sw = P['sway'] * 6
    hat = [(-12.8, -34.6), (-10.2, -48), (-7.6, -60), (-9 + sw * 0.6, -68), (-15 + sw, -73), (-9 + sw, -66.5), (-1, -55),
           (6, -45), (12.8, -34.6), (6, -36.4), (0, -37.2), (-6, -36.4)]
    hp = catmull(hat, 7)
    ph = piece2(ctx, hp, RED_L, RED, (0.5, -37), (-11 + sw, -72), seed=7020, u=u, amp=0.15)
    ctx.save()
    path(ctx, ph)
    ctx.clip()
    tip = (-13 + sw, -71.5)
    for i in range(22):
        bx = -13 + i * 26 / 21
        pts = []
        for k in np.linspace(0, 1, 14):
            px = lerp(bx, tip[0], k) + 0.25 * math.sin(k * 20 + i)
            py = lerp(-36.5, tip[1], k)
            pts.append((px, py))
        line(ctx, pts, (0.45, 0.06, 0.06) if i % 2 else (1, 0.75, 0.7), 0.28, alpha=0.35 if i % 2 else 0.25)
    ctx.restore()
    # Krempe als gestauchtes Krepp-Band
    rim = [(-13.2, -35.2), (0, -38.2), (13.2, -35.2), (13, -32.8), (0, -35.6), (-13, -32.8)]
    soft(ctx, rim, RED_D, seed=7021, u=u, shadow=0.6, n=5)
    ctx.restore()
    # vorderes Bein + Arm
    limb(ctx, hipF, P['footF'], 8.5, 8.5, 5.6, LEG, bend=-1)
    _boot(ctx, P['footF'], BOOT, u)
    hF = _reach(shF, hF, 14)
    if P['item']:
        P['item'](ctx, hF, 'under')
    limb(ctx, shF, hF, 7, 7, 4.6, GREEN_D, bend=1)
    dot(ctx, hF[0], hF[1], 3.0, SKIN)
    if P['item']:
        P['item'](ctx, hF, 'over')
    ctx.restore()
    # Weltposition der Hände
    def W(p):
        return (x + facing * s * p[0], y + s * (1 - P['squash']) * p[1])
    return W(hF), W(hB)


def _reach(a, b, L):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d <= L * 0.995:
        return b
    f = L * 0.995 / d
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def _boot(ctx, f, col, u):
    piece(ctx, catmull([(f[0] - 4.5, f[1] - 0.2), (f[0] - 3.5, f[1] - 4.2), (f[0] + 2, f[1] - 4.4), (f[0] + 6.8, f[1] - 2.6),
                        (f[0] + 7.4, f[1] - 4.6), (f[0] + 7.6, f[1] - 1.0), (f[0] + 4, f[1] + 0.4)], 5), col, seed=7030 + int(col[0] * 100),
          u=u, shadow=0.6, amp=0.1)


# ====================================================================== Brief / Papierflieger
def letter_flat(ctx, x, y, w, h, rot=0.0, col=CREAM, seal=RED, flap=True, scribble=True, u=0.4, seed=7100, bend=0.0,
                singe=0.0, t=0.0):
    """Gefalteter Brief (Umschlag) mit Siegel; bend wölbt ihn (Segeln)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    pts = []
    for k in np.linspace(0, 1, 8):
        pts.append((-w / 2 + w * k, -h / 2 + math.sin(k * math.pi) * bend * h))
    for k in np.linspace(1, 0, 8):
        pts.append((-w / 2 + w * k, h / 2 + math.sin(k * math.pi) * bend * h * 0.6))
    p = piece(ctx, np.array(pts), col, seed=seed, u=u, shadow=1.0, amp=0.2)
    if flap:
        line(ctx, [(-w / 2, -h / 2 + 0.5), (0, h * 0.08 + bend * h * 0.8), (w / 2, -h / 2 + 0.5)], darker(col, 0.85), 0.6 * u / 0.4)
    if seal is not None:
        dot(ctx, 0, h * 0.1 + bend * h * 0.8, min(w, h) * 0.14, seal)
    if singe > 0:
        ctx.save()
        path(ctx, p)
        ctx.clip()
        _singe(ctx, w / 2, h / 2, singe, t, u)
        ctx.restore()
    ctx.restore()


def _singe(ctx, cx, cy, k, t, u):
    """Angesengte, glimmende Ecke."""
    ctx.save()
    pts = deckle(ellipse_pts(cx, cy, 6 * u / 0.4, 5 * u / 0.4, n=16), 7150, u, 1.2)
    path(ctx, pts)
    ctx.set_source_rgba(0.18, 0.10, 0.06, 0.85 * min(1, k * 2))
    ctx.fill()
    path(ctx, pts)
    glo = max(0.0, 1 - abs(k - 0.35) * 2.2) * (0.7 + 0.3 * math.sin(t * 40))
    ctx.set_source_rgba(1.0, 0.55, 0.15, glo)
    ctx.set_line_width(1.3 * u / 0.4)
    ctx.stroke()
    ctx.restore()


def plane(ctx, x, y, s=1.0, rot=0.0, facing=-1, singe=0.0, t=0.0, roll=0.0):
    """Papierflieger aus dem Brief (Seitenansicht, gefaltete Flügel)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s * facing, s)
    u = 0.4
    wing_up = 1 - 0.25 * roll
    body = np.array([(26, 0), (-22, -3), (-22, 5)])
    wing = np.array([(26, -0.5), (-22, -3.5), (-18, -14 * wing_up), (2, -6 * wing_up)])
    wing2 = np.array([(26, 0.2), (-22, -2.5), (-26, -8 * wing_up)])
    piece(ctx, wing2, darker(CREAM, 0.86), seed=7201, u=u, shadow=0.6, amp=0.1)
    piece(ctx, body, CREAM2, seed=7202, u=u, shadow=0.8, amp=0.1)
    wp = piece(ctx, wing, CREAM, seed=7203, u=u, shadow=0.7, amp=0.1)
    line(ctx, [(26, -0.5), (-22, -3.5)], CREAM3, 0.5)
    # Schnörkel auf dem Flügel (Brieftext)
    for k in range(3):
        line(ctx, [(-14 + k * 2, -7 - k * 1.8), (-4 + k * 2, -6 - k * 1.2), (6, -4.5 - k * 0.6)], INK, 0.35, alpha=0.5)
    dot(ctx, -6, 1.2, 1.6, RED)
    if singe > 0:
        ctx.save()
        path(ctx, wp)
        ctx.clip()
        _singe(ctx, -20, -10, singe, t, u)
        ctx.restore()
    ctx.restore()


# ====================================================================== Katze
def cp(**kw):
    C = dict(mode='stand', ph=0.0, stretch=1.0, eyeF=1.0, eyeB=1.0, pupil=0.7, ears=0.0, tail_ph=0.0, tail_curl=0.15,
             paw=0.0, breath=0.0, look=(0.0, 0.0), head_rot=0.0, lid=0.0, squash=0.0, mouth=0.0, arch=0.0)
    C.update(kw)
    return C


def cat(ctx, x, y, C, s=1.0, facing=1, t=0.0):
    u = 1.0
    ctx.save()
    ctx.translate(x, y)
    mode = C['mode']
    ctx.save()
    ctx.scale(1, 0.18)
    dot(ctx, 0, 0, 150 * s, (0.12, 0.06, 0.04), 0.2 if mode != 'climb' else 0.0)
    ctx.restore()
    ctx.scale(s * facing, s * (1 - C['squash']))
    ph = C['ph']
    br = 1 + 0.035 * C['breath']
    legs = []
    head_tilt = C['head_rot']
    if mode == 'sleep':
        Hp, Sp, th = (-95, -36 * br), (55, -38 * br), 66 * br
        head = (112, -44)
        head_tilt += 0.12
        tail = dict(pts=[(-118, -30), (-138, -14), (-118, -4), (-70, -3), (-20, -3), (25, -5), (55, -9)], wave=3.0)
        paws = [(118, -8), (140, -7)]
    elif mode == 'offended':
        Hp, Sp, th = (-12, -50), (14, -120), 80
        head = (36, -166)
        head_tilt += -0.25
        tail = dict(pts=[(-60, -14), (-30, -4), (10, -3), (50, -5), (78, -14), (88, -30)], wave=5.0)
        paws = [(30, -6), (52, -6)]
    else:
        st = C['stretch']
        if mode == 'run':
            st = 1.0 + 0.28 * math.sin(ph)
        L = 150 * st
        Hp = (-L / 2, -82)
        Sp = (L / 2, -86)
        th = 58 / max(0.8, st) ** 0.5
        if mode == 'run':
            Hp = (Hp[0], Hp[1] - 10 * max(0, math.sin(ph + 1.2)))
            Sp = (Sp[0], Sp[1] - 12 * max(0, math.sin(ph + 0.3)))
        head = (Sp[0] + 52, Sp[1] - 26)
        tail = dict(base=(Hp[0] - 22, Hp[1] - 6), ang=math.pi * 0.85, curl=C['tail_curl'], n=9, wave=0.22)
        paws = None
        # Beine
        if mode == 'run':
            for (root, phase, near, front) in ((Hp, ph + 0.4, False, False), (Sp, ph + 2.2, False, True),
                                               (Hp, ph, True, False), (Sp, ph + 1.8, True, True)):
                sx = math.sin(phase)
                fx = root[0] + 45 * sx * (1 if front else -1) * 0.9 + (12 if front else -8)
                fy_ = -max(0, math.cos(phase)) * 22
                legs.append((root, (fx, fy_), near, front))
        elif mode == 'climb':
            for (root, phase, near, front) in ((Hp, ph + 0.8, False, False), (Sp, ph + 2.6, False, True),
                                               (Hp, ph, True, False), (Sp, ph + 1.8, True, True)):
                sx = math.sin(phase)
                fx = root[0] + 30 * sx + (20 if front else -10)
                legs.append((root, (fx, root[1] + 66), near, front))
        else:
            for (root, phase, near, front) in ((Hp, ph + math.pi, False, False), (Sp, ph, False, True),
                                               (Hp, ph, True, False), (Sp, ph + math.pi, True, True)):
                sx = math.sin(phase)
                fx = root[0] + 16 * sx + (8 if front else -6)
                fy_ = -max(0, math.cos(phase)) * 10 * (1 if C['ph'] else 0)
                legs.append((root, (fx, fy_), near, front))
    # ferne Beine
    for root, foot, near, front in legs:
        if not near:
            _cat_leg(ctx, root, foot, th, CAT_DD, front, u)
    # Schwanz
    if 'pts' not in tail:
        _tail(ctx, tail, C['tail_ph'], u)
    if mode == 'offended':
        soft2(ctx, [(-75, -4), (-80, -45), (-55, -85), (-10, -92), (25, -70), (30, -20), (10, -2)], CAT, CAT_D, (-20, -110), (-25, 10),
              seed=7390, u=u, n=6)
    # Körper: Akkordeon-Segmente
    _cat_body(ctx, Hp, Sp, th, u, mode, C['arch'])
    if 'pts' in tail:
        _tail_pts(ctx, tail, C['tail_ph'])
    if paws:
        for i, (px, py) in enumerate(paws):
            soft(ctx, [(px - 15, py), (px - 12, py - 11), (px + 6, py - 12), (px + 16, py - 4), (px + 10, py + 2)], CAT_CREAM if i else darker(CAT_CREAM, 0.94),
                 seed=7300 + i, u=u, n=5)
    # nahe Beine
    for root, foot, near, front in legs:
        if near:
            if front and C['paw'] > 0:
                k = C['paw']
                tgt = (lerp(foot[0], root[0] + 120, k), lerp(foot[1], root[1] - 10, k))
                _cat_leg(ctx, root, tgt, th, CAT, True, u, claws=k > 0.5)
            else:
                _cat_leg(ctx, root, foot, th, CAT, front, u)
    # Kopf
    _cat_head(ctx, head, C, head_tilt, u, mode, t)
    ctx.restore()


def _cat_leg(ctx, root, foot, th, col, front, u, claws=False):
    r = (root[0], root[1] + th * 0.15)
    k = limb(ctx, r, foot, 46, 42, 19, col, bend=(1 if front else -1))
    soft(ctx, [(foot[0] - 12, foot[1] + 1), (foot[0] - 10, foot[1] - 9), (foot[0] + 8, foot[1] - 10), (foot[0] + 15, foot[1] - 3),
               (foot[0] + 10, foot[1] + 2)], CAT_CREAM if col == CAT else darker(CAT_CREAM, 0.9), seed=7310, u=u, n=5, shadow=0.5)
    if claws:
        for i in range(3):
            cx = foot[0] + 12
            cy = foot[1] - 8 + i * 4
            piece(ctx, np.array([(cx, cy), (cx + 8, cy + 1), (cx, cy + 2.2)]), WHITE, seed=7320 + i, u=0.4, shadow=0.3, amp=0.05)


def _tail(ctx, tl, tph, u):
    bx, by = tl['base']
    ang = tl['ang']
    pts = [(bx, by)]
    for i in range(tl['n']):
        ang += tl['curl'] + tl['wave'] * math.sin(tph + i * 0.7)
        bx += math.cos(ang) * 15
        by += math.sin(ang) * 15
        pts.append((bx, by))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(len(pts) - 1):
        w = 17 - i * 0.9
        col = CAT if i % 2 == 0 else CAT_D
        if i == len(pts) - 2:
            col = CAT_CREAM
        ctx.save()
        ctx.translate(1.2, 2)
        line(ctx, [pts[i], pts[i + 1]], (0.15, 0.08, 0.05), w, alpha=0.15)
        ctx.restore()
        line(ctx, [pts[i], pts[i + 1]], darker(col, 0.85), w + 1)
        line(ctx, [pts[i], pts[i + 1]], col, w)


def _tail_pts(ctx, tl, tph):
    P = np.array(tl['pts'], float)
    n = len(P)
    for i in range(n):
        k = i / (n - 1)
        P[i, 1] += -abs(math.sin(tph)) * tl['wave'] * k ** 2 * 2
        P[i, 0] += math.sin(tph) * tl['wave'] * k ** 2
    pts = catmull(P, 4, closed=False)
    for i in range(len(pts) - 1):
        w = 17 - 7 * i / len(pts)
        col = CAT if (i // 3) % 2 == 0 else CAT_D
        if i > len(pts) - 4:
            col = CAT_CREAM
        line(ctx, [pts[i], pts[i + 1]], darker(col, 0.85), w + 1)
        line(ctx, [pts[i], pts[i + 1]], col, w)


def _cat_body(ctx, Hp, Sp, th, u, mode, arch):
    n = 7
    hx, hy = Hp
    sx, sy = Sp
    mx, my = (hx + sx) / 2, (hy + sy) / 2 - arch
    L = math.hypot(sx - hx, sy - hy)
    seg = L / (n - 1)
    # Unterbauch (Falzinnenseite sichtbar bei Dehnung)
    belly = []
    for k in np.linspace(0, 1, 12):
        x = (1 - k) ** 2 * hx + 2 * (1 - k) * k * mx + k * k * sx
        y = (1 - k) ** 2 * hy + 2 * (1 - k) * k * my + k * k * sy
        belly.append((x, y))
    ang = math.atan2(sy - hy, sx - hx)
    nx, ny = -math.sin(ang), math.cos(ang)
    top = [(x - nx * th * 0.42, y - ny * th * 0.42) for x, y in belly]
    bot = [(x + nx * th * 0.5, y + ny * th * 0.5) for x, y in belly[::-1]]
    piece(ctx, catmull(top + bot, 4), CAT_DD, seed=7400, u=u, shadow=1.0, amp=0.2)
    for i in range(n):
        k = i / (n - 1)
        x = (1 - k) ** 2 * hx + 2 * (1 - k) * k * mx + k * k * sx
        y = (1 - k) ** 2 * hy + 2 * (1 - k) * k * my + k * k * sy
        h = th * (0.86 + 0.18 * math.sin(math.pi * k)) * (1.08 if i in (0, n - 1) else 1)
        w = max(seg * 1.05, th * 0.42)
        if i in (0, n - 1):
            w = th * 0.9
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang)
        r = min(w, h) * 0.45
        pts = [(-w / 2, -h / 2 + r), (-w / 2 + r * 0.3, -h / 2), (w / 2 - r * 0.3, -h / 2), (w / 2, -h / 2 + r),
               (w / 2, h / 2 - r), (w / 2 - r * 0.3, h / 2), (-w / 2 + r * 0.3, h / 2), (-w / 2, h / 2 - r)]
        col = CAT if i % 2 == 0 else CAT_D
        p = piece(ctx, catmull(pts, 5), col, seed=7410 + i, u=u, shadow=0.7, amp=0.15)
        # Bauchstreifen creme
        ctx.save()
        path(ctx, p)
        ctx.clip()
        ctx.rectangle(-w, h * 0.22, 2 * w, h)
        ctx.set_source_rgba(*CAT_CREAM, 0.9)
        ctx.fill()
        # Tigerstreifen
        line(ctx, [(-w * 0.15, -h / 2), (w * 0.05, -h * 0.18)], CAT_DD, 4.5, alpha=0.8)
        ctx.restore()
        # Falzkante
        line(ctx, [(-w / 2, -h / 2 + 3), (-w / 2, h / 2 - 3)], darker(col, 0.75), 1.0, alpha=0.6)
        ctx.restore()


def _cat_eye(ctx, x, y, w, h, open_, pupil, lid, look, closed_curve=True):
    if open_ < 0.08:
        if closed_curve:
            arc_stroke(ctx, x, y - h * 0.4, w * 0.55, 0.2 * math.pi, 0.8 * math.pi, INK, 2.4)
        return
    hh = h * open_
    pts = [(-w / 2, 0), (-w * 0.25, -hh * 0.55), (w * 0.15, -hh * 0.6), (w / 2, -hh * 0.15), (w * 0.35, hh * 0.4),
           (-w * 0.05, hh * 0.55), (-w * 0.35, hh * 0.35)]
    P = catmull(pts, 6) + (x, y)
    path(ctx, P)
    ctx.set_source_rgb(0.82, 0.86, 0.34)
    ctx.fill()
    ctx.save()
    path(ctx, P)
    ctx.clip()
    dot(ctx, x - w * 0.1, y + hh * 0.2, w * 0.5, (0.65, 0.74, 0.22), 0.6)
    pw = w * (0.05 + 0.3 * pupil)
    ctx.save()
    ctx.translate(x + look[0] * w * 0.15, y + look[1] * h * 0.1)
    ctx.scale(pw / (h * 0.5), 1)
    dot(ctx, 0, 0, h * 0.5, (0.08, 0.05, 0.05))
    ctx.restore()
    dot(ctx, x + w * 0.08, y - hh * 0.25, w * 0.08, WHITE, 0.9)
    if lid > 0:
        ctx.rectangle(x - w, y - h, 2 * w, h * (0.4 + lid * 0.6) + (-0.35 * h))
        ctx.set_source_rgb(*CAT)
        ctx.fill()
        line(ctx, [(x - w * 0.6, y - h * 0.35 + lid * h * 0.6 - 0.2 * h), (x + w * 0.6, y - h * 0.35 + lid * h * 0.6 - 0.2 * h)], INK, 2.0)
    ctx.restore()
    path(ctx, P)
    ctx.set_source_rgba(*INK, 0.9)
    ctx.set_line_width(1.8)
    ctx.stroke()


def _cat_head(ctx, head, C, tilt, u, mode, t):
    ctx.save()
    ctx.translate(*head)
    ctx.rotate(tilt)
    ears = C['ears']
    # hinteres Ohr
    for (bx0, bx1, tipx, tipy, col, sd, side) in ((-34, -8, -30, -82, CAT_D, 7500, -1), (8, 34, 30, -84, CAT, 7502, 1)):
        ctx.save()
        ctx.translate((bx0 + bx1) / 2, -36)
        ctx.rotate(-ears * (1.0 if side < 0 else 1.2))
        ctx.translate(-(bx0 + bx1) / 2, 36)
        e = [(bx0, -30), (tipx - 3, tipy + 6), (tipx, tipy), (tipx + 4, tipy + 7), (bx1, -36)]
        soft(ctx, e, col, seed=sd, u=u, n=5)
        inner = [(bx0 + 6, -34), (tipx - 1, tipy + 14), (tipx + 2, tipy + 13), (bx1 - 6, -37)]
        soft(ctx, inner, PINK, seed=sd + 1, u=u, n=4, shadow=0.2)
        ctx.restore()
    hd = [(-42, -20), (-30, -40), (0, -46), (30, -40), (46, -16), (50, 10), (34, 32), (0, 38), (-32, 32), (-48, 8)]
    soft2(ctx, hd, CAT, CAT_D, (12, -60), (18, 50), seed=7510, u=u, n=7)
    for i, dx in enumerate((-10, 2, 14)):
        line(ctx, [(dx - 4, -44), (dx, -30)], CAT_DD, 4.0, alpha=0.8)
    # Schnauze
    piece(ctx, ellipse_pts(24, 14, 24, 17, n=30), CAT_CREAM, seed=7511, u=u, shadow=0.5, amp=0.15)
    soft(ctx, [(30, 3), (42, 2), (37, 10)], (0.95, 0.55, 0.58), seed=7512, u=u, n=4, shadow=0.4)
    if C['mouth'] > 0.1:
        m = C['mouth']
        soft(ctx, [(22, 18), (44, 18), (38, 18 + 14 * m), (26, 18 + 14 * m)], (0.55, 0.15, 0.18), seed=7513, u=u, n=4, shadow=0)
        for fx in (26, 40):
            piece(ctx, np.array([(fx - 2, 18), (fx + 2, 18), (fx, 24)]), WHITE, seed=7514 + fx, u=0.4, shadow=0, amp=0.05)
    else:
        line(ctx, [(37, 10), (37, 16), (32, 19)], INK, 1.6)
        line(ctx, [(37, 16), (42, 19)], INK, 1.6)
    # Augen
    lk = C['look']
    _cat_eye(ctx, -6, -6, 26, 18, C['eyeB'], C['pupil'], C['lid'], lk)
    _cat_eye(ctx, 24, -7, 24, 17, C['eyeF'], C['pupil'], C['lid'], lk)
    # Schnurrhaare aus Papierstreifen
    tw = math.sin(t * 3) * 0.04
    for i, (ex, ey) in enumerate(((98, 0), (102, 14), (96, 28))):
        a = (34, 14)
        pts = np.array([(a[0], a[1] - 0.9), (ex, ey - 0.9 + tw * 30 * (i - 1)), (ex, ey + 0.9 + tw * 30 * (i - 1)), (a[0], a[1] + 0.9)])
        piece(ctx, pts, CAT_CREAM, seed=7520 + i, u=0.4, shadow=0.6, amp=0.05)
    for i, (ex, ey) in enumerate(((-30, 4), (-28, 18))):
        a = (10, 14)
        pts = np.array([(a[0], a[1] - 0.8), (ex, ey - 0.8), (ex, ey + 0.8), (a[0], a[1] + 0.8)])
        piece(ctx, pts, darker(CAT_CREAM, 0.92), seed=7530 + i, u=0.4, shadow=0.4, amp=0.05)
    ctx.restore()


def paw_seal(ctx, x, y, r, col=RED):
    dot(ctx, x, y + r * 0.25, r * 0.48, col)
    for (dx, dy) in ((-0.5, -0.32), (-0.18, -0.6), (0.18, -0.6), (0.5, -0.32)):
        dot(ctx, x + dx * r, y + dy * r, r * 0.2, col)
