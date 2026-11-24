"""Zeitleiste und Einstellungen des Films 'Wichtelbriefe' (60 s)."""
import math
import cairo
import numpy as np
from paper import *
from characters import *
from sets import *
from inserts import insert, endcard, paper_star

DUR = 60.0
_tex = None
_post = {}


def tex():
    global _tex
    if _tex is None:
        _tex = paper_texture()
    return _tex


def cam(ctx, W, cx, cy, z, H=None):
    S = W / 1920.0
    H = H or W * 9 / 16
    ctx.translate(W / 2, H / 2)
    ctx.scale(S * z, S * z)
    ctx.translate(-cx, -cy)


def camk(t, keys):
    """Kamerapfad aus Keyframes [(t, cx, cy, z)], weich interpoliert."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            k = ease(t, a[0], b[0])
            return tuple(lerp(a[i], b[i], k) for i in range(1, 4))
    return keys[-1][1:]


# ---------------------------------------------------------------- Kalender-/Licht-Zustand
def montage_q(t):
    return (t - 35.0) / 0.27 - 0.35


def dayf_at(t):
    if t < 15.1:
        return 0.0
    if t < 25.15:
        return smooth(lin(t, 15.1, 15.45))
    if t < 31.15:
        return 1 + smooth(lin(t, 25.15, 25.45))
    if t < 35.0:
        return 2 + smooth(lin(t, 31.15, 31.45))
    if t < 44.15:
        q = montage_q(t)
        if q <= 0:
            return 3.0
        fq = math.floor(q)
        return min(23.0, 3 + fq + smooth(clamp((q - fq) * 2.5)))
    return 23 + smooth(lin(t, 44.15, 44.5))


def stack_at(t):
    if t < 22.6:
        return 0, 0
    if t < 28.6:
        return 1, 1
    if t < 35.0:
        return (2 if t < 35.0 and t < 31.6 else 3), 1
    if t < 40.6:
        d = dayf_at(t)
        n = int(math.floor(d - 0.3))
        pop = clamp((d - 0.3 - n) * 2) if n > 3 else 1
        return max(3, n), pop
    if t < 48.4:
        return 23, 1
    return 24, 1


def L_at(t):
    if t < 14.8:
        return 0.0
    if t < 22.6:
        return smooth(lin(t, 14.8, 15.4))
    if t < 25.0:
        return 0.0
    if t < 28.6:
        return smooth(lin(t, 25.0, 25.4))
    if t < 31.0:
        return 0.0
    if t < 35.0:
        return smooth(lin(t, 31.0, 31.4))
    if t < 40.6:
        return 0.5 - 0.5 * math.cos(2 * math.pi * (t - 35.0) / 0.27)
    if t < 44.05:
        return 0.0
    return smooth(lin(t, 44.05, 44.45))


def base_state(t):
    n, pop = stack_at(t)
    st = {'L': L_at(t), 'dayf': dayf_at(t), 'stack': n, 'stack_pop': pop, 'actors': [], 'emissive': [],
          'floor_items': [], 'bed': 'sleep', 'door': 0.0, 'door_lit': 0.0}
    if 12.0 <= t < 22.6:
        st['flour'] = 1.0
    if 22.6 <= t < 35.0:
        st['cookie'] = 1
        st['cookie_print'] = 1.0 if t > 23.55 else 0.0
    if t >= 29.5 and t < 40.6:
        st['sock'] = smooth(lin(t, 29.5, 29.9))
        st['sock_t'] = t - 29.5
    return st


def add_candle(st, x, z, t, s=1.0):
    def draw(ctx):
        candle(ctx, x, fy(z), s)

    def em(ctx):
        wx, wy = x + 0.2 * s, fy(z) - 17.2 * s
        fl = 1 + 0.08 * math.sin(t * 17) + 0.05 * math.sin(t * 29)
        glow(ctx, wx, wy - 4, 200 * fl, (1.0, 0.62, 0.30), 0.30)
        glow(ctx, wx, wy - 4, 60, (1.0, 0.80, 0.50), 0.28)
        flame(ctx, wx, wy, 0.85 * s, t)
    st['floor_items'].append(draw)
    st['emissive'].append(em)


def floor_quad(pts3):
    return np.array([(x, fy(z) - h) for (x, z, h) in pts3])


def folding_sheet(ctx, t, x0, x1, z0, z1, scrib, tw, tf1, tf2, col, back, seal=RED, crooked=0.0, wr=None,
                  stroke=(INK, 0.45), seed=0):
    """Blatt auf dem Boden, wird beschrieben (tw) und zweimal gefaltet (tf1, tf2).
    Gibt aktuelle Stiftspitze (Welt) oder None zurück."""
    xm = (x0 + x1) / 2
    zm = (z0 + z1) / 2
    tip = None
    u = 0.35 if wr is None else wr

    def draw_scr(clip_x1=None, alpha=1.0, prog=1.0):
        pts = []
        for s in scrib:
            pts.append(np.column_stack([x0 + s[:, 0], fy(z0 + s[:, 1])]))
        if clip_x1 is not None:
            ctx.save()
            ctx.rectangle(x0 - 5, 0, clip_x1 - x0 + 5, 3000)
            ctx.clip()
        tp = draw_scribbles(ctx, pts, stroke[0], stroke[1], prog, alpha)
        if clip_x1 is not None:
            ctx.restore()
        return tp

    th1 = ease(t, *tf1) * math.pi
    th2 = ease(t, *tf2) * math.pi
    if t < tf1[0]:
        piece(ctx, floor_quad([(x0, z0, 0), (x1, z0, 0), (x1, z1, 0), (x0, z1, 0)]), col, seed=seed, u=u, shadow=0.4)
        tip = draw_scr(prog=lin(t, *tw))
    elif t < tf1[1] or th2 <= 0:
        piece(ctx, floor_quad([(x0, z0, 0), (xm, z0, 0), (xm, z1, 0), (x0, z1, 0)]), col, seed=seed, u=u, shadow=0.4)
        draw_scr(clip_x1=xm)
        wh = x1 - xm
        c, s = math.cos(th1), math.sin(th1)
        cr = crooked * s
        if th1 < math.pi * 0.999:
            fl = floor_quad([(xm, z0, 0), (xm, z1, 0), (xm + wh * c, z1 + cr * 8, wh * s), (xm + wh * c, z0 + cr * 3, wh * s)])
            if c > 0:
                piece(ctx, fl, col, seed=seed + 1, u=u, shadow=0.5)
                ctx.save()
                path(ctx, fl)
                ctx.clip()
                ctx.restore()
            else:
                piece(ctx, fl, back, seed=seed + 1, u=u, shadow=0.5)
        else:
            piece(ctx, floor_quad([(x0 + crooked * 3, z0 + crooked * 3, 0.3), (xm, z0, 0.3), (xm, z1, 0.3), (x0 + crooked * 5, z1 + crooked * 8, 0.3)]),
                  back, seed=seed + 1, u=u, shadow=0.5)
    else:
        # zweiter Falz (hintere Hälfte nach vorn)
        dh = z1 - zm
        c, s = math.cos(th2), math.sin(th2)
        piece(ctx, floor_quad([(x0, z0, 0), (xm, z0, 0), (xm, zm, 0), (x0, zm, 0)]), back, seed=seed + 2, u=u, shadow=0.4)
        if th2 < math.pi * 0.999:
            cr = crooked * s
            fl = floor_quad([(x0, zm, 0), (xm, zm, 0), (xm + cr * 4, zm + dh * c, dh * s), (x0 + cr * 6, zm + dh * c, dh * s)])
            piece(ctx, fl, back if c > 0 else darker(back, 0.94), seed=seed + 3, u=u, shadow=0.5)
        else:
            fl = floor_quad([(x0 + crooked * 6, z0 + crooked * 2, 0.3), (xm + crooked * 4, z0 - crooked * 1, 0.3), (xm, zm, 0.3), (x0, zm, 0.3)])
            piece(ctx, fl, darker(back, 0.94), seed=seed + 3, u=u, shadow=0.5)
            if seal is not None:
                cx, cy = (x0 + xm) / 2, fy((z0 + zm) / 2)
                ctx.save()
                ctx.translate(cx, cy)
                ctx.scale(1, KF)
                dot(ctx, 0, 0, (xm - x0) * 0.13, seal)
                ctx.restore()
    return tip


def gnome_hand_local(gx, gy, s, facing, hx, hy):
    return ((hx - gx) / (facing * s), (hy - gy) / s)


# ================================================================ Einstellungen
def shot_exterior(ctx, t, W, H):
    cx, cy, z = camk(t, [(0.0, 960, 540, 1.0), (3.4, 1172, 628, 2.35)])
    cam(ctx, W, cx, cy, z)
    exterior(ctx, t)
    texture(ctx, tex(), 1.6)
    exterior_emissive(ctx, t)
    snow(ctx, t, cx - 1100 / z, cy - 700 / z, cx + 1100 / z, cy + 700 / z, 70, 11, 1.4 / z ** 0.3, 1.2)
    snow(ctx, t * 1.3, cx - 1000 / z, cy - 650 / z, cx + 1000 / z, cy + 650 / z, 22, 12, 3.0 / z ** 0.5, 2.0)


def shot_push(ctx, t, W, H):
    cx, cy, z = camk(t, [(3.0, 1290, 760, 0.76), (5.2, 1520, 960, 1.9)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['door_lit'] = 0.55 + 0.1 * math.sin(t * 5)
    room(ctx, t, st, tex())


def shot_door(ctx, t, W, H):
    cx, cy, z = camk(t, [(5.2, 1592, 1006, 5.6), (7.8, 1640, 1018, 6.0)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    o = ease(t, 5.3, 5.85)
    st['door'] = o
    st['door_lit'] = 0.7 + 0.3 * o
    tt = twos(t)
    if tt >= 5.8:
        if tt < 6.35:
            k = ease(tt, 5.8, 6.3)
            gx, gz, ph, look = lerp(1568, 1586, k), 0.0, None, 0.0
            sq = 0.06
        else:
            k = lin(tt, 6.35, 7.6)
            gx, gz = lerp(1586, 1690, ease(tt, 6.35, 7.6)), lerp(0, 16, k)
            ph = (tt - 6.35) * 11
            look = 0.0
            sq = 0.06 * (1 - k)
        gy = fy(gz)

        def actor(c, gx=gx, gy=gy, ph=ph, sq=sq, tt=tt):
            if tt < 6.35:
                c.save()
                arch = np.vstack([[(DOOR_X0, FLOOR)], ellipse_pts((DOOR_X0 + DOOR_X1) / 2, DOOR_TOP + 23, 23, 23, a0=math.pi, a1=2 * math.pi, n=24), [(DOOR_X1, FLOOR)]])
                path(c, arch)
                c.clip()
            hx, hy = gnome(c, gx, gy, 0.92, 1, ph, hand=(15, -30), sway=math.sin(tt * 6) * 0.4, squash=sq, t=tt,
                           blink=(5.95 < tt < 6.05))
            wick = candle(c, hx + 1, hy + 4, 0.75)
            if tt < 6.35:
                c.restore()
            st['emissive'].append(lambda c2, w=wick: (glow(c2, w[0], w[1] - 4, 190, (1.0, 0.62, 0.30), 0.30),
                                                     glow(c2, w[0], w[1] - 4, 50, (1.0, 0.8, 0.5), 0.3),
                                                     flame(c2, w[0], w[1], 0.65, t)))
        st['actors'].append(actor)
    room(ctx, t, st, tex())


SCRIB_G = scribble_pts(4, 5, 24, 4, 4.4, seed=41, h=1.25)
SCRIB_BIG = scribble_pts(8, 8, 96, 6, 6.5, seed=43, h=2.6)
SCRIB_KID = scribble_pts(6, 8, 58, 4, 9, seed=44, h=4.2)


def shot_write(ctx, t, W, H):
    cx, cy, z = camk(t, [(7.8, 1656, 1030, 7.2), (12.0, 1654, 1026, 7.8)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['door'] = 1.0
    st['door_lit'] = 1.0
    tt = twos(t)
    add_candle(st, 1622, 10, t)
    gx, gz, s, fc = 1692, 18, 0.92, -1
    gy = fy(gz)
    sheet = dict(x0=1638, x1=1670, z0=4, z1=28)
    state = {}

    def sheet_draw(c):
        if tt < 11.25:
            tip = folding_sheet(c, tt, sheet['x0'], sheet['x1'], sheet['z0'], sheet['z1'], SCRIB_G, (8.0, 10.0),
                                (10.1, 10.65), (10.7, 11.2), CREAM, CREAM2, seed=600)
            state['tip'] = tip
        else:
            k = ease(tt, 11.25, 11.75)
            x = lerp(1646, 1652, k)
            hh = lerp(9, 11, k)
            ww = lerp(16, 17, k)
            hop = math.sin(k * math.pi) * 6
            c.save()
            c.translate(x, fy(lerp(16, 1, k)) - hop)
            c.scale(1, lerp(0.55, 1.0, k))
            mini_letter(c, 0, 0, ww, hh, CREAM, seed=610)
            c.restore()
    st['floor_items'].append(sheet_draw)

    def actor(c):
        sit = 1.0 if tt < 11.2 else 1 - lin(tt, 11.2, 11.4)
        hand = None
        tip = state.get('tip')
        cheer = smooth(lin(tt, 11.75, 11.95)) * (0.7 + 0.3 * math.sin(tt * 20))
        if tt < 10.05 and tt > 7.95 and tip is not None:
            hand = gnome_hand_local(gx, gy, s, fc, tip[0] + 0.5, tip[1] - 1.0)
        elif 10.05 <= tt < 11.2:
            # Faltbewegung: Hand führt die Klappe
            k = (tt - 10.05) / 1.15
            hand = (24 - 10 * math.sin(k * math.pi * 2), -10 - 8 * abs(math.sin(k * math.pi * 2)))
        elif 11.2 <= tt < 11.75:
            hand = (30, -18)
        hx, hy = gnome(c, gx, gy, s, fc, None, sit=sit, hand=hand, t=tt, cheer=cheer, look=-0.5 if tt < 10 else 0.0,
                       blink=(9.0 < tt < 9.1), sway=math.sin(tt * 3) * 0.3, squash=-0.06 * cheer)
        if tt < 10.05:
            quill(c, hx, hy, ang=-1.0 + 0.15 * math.sin(tt * 25))
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_flour(ctx, t, W, H):
    tt = twos(t)
    k = lin(tt, 12.1, 13.9)
    gx = lerp(1930, 2300, k)
    cx, cy, z = camk(t, [(12.0, 2010, 715, 5.2), (14.6, 2250, 712, 5.4)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['flour'] = clamp((gx - 1950) / (22 * 17))

    def actor(c):
        ph = None if tt > 13.9 else tt * 15
        cheer = smooth(lin(tt, 14.0, 14.15)) * (0.6 + 0.4 * math.sin(tt * 22))
        hop = abs(math.sin((tt - 14.0) * 10)) * 4 if tt > 14.0 else 0
        gnome(c, gx, 755 - hop, 0.9, 1, ph, item='flour', t=tt, cheer=cheer, blink=tt > 14.2 and tt < 14.3,
              sway=math.sin(tt * 8) * 0.6)
        # Mehlwölkchen
        r = np.random.RandomState(int(tt * 12))
        for i in range(5):
            if tt < 13.95:
                dot(c, gx - 8 + r.uniform(-8, 8), 752 - r.uniform(0, 10), r.uniform(1, 3), WHITE, 0.8)
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_calendar(ctx, t, W, H, t0, t1, door_xy=(2120, 345), z0=2.7, z1=3.0):
    cx, cy, z = camk(t, [(t0, door_xy[0], door_xy[1], z0), (t1, door_xy[0] + 10, door_xy[1] - 5, z1)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    room(ctx, t, st, tex())


def shot_morning1(ctx, t, W, H):
    cx, cy, z = camk(t, [(15.8, 1000, 820, 1.05), (16.6, 1050, 840, 1.1), (18.2, 1480, 930, 1.75)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    tt = twos(t)
    st['bed'] = 'sleep' if tt < 16.15 else 'empty'
    letter_taken = tt >= 18.0

    if not letter_taken:
        st['floor_items'].append(lambda c: mini_letter(c, 1652, fy(1), 17, 11, CREAM, seed=610))
    if tt >= 16.15:
        def actor(c):
            if tt < 16.6:
                k = lin(tt, 16.15, 16.6)
                x = lerp(430, 600, k)
                y = lerp(900, fy(60), k) - math.sin(k * math.pi) * 90
                child(c, x, y, 0.95, 1, 'jump', joy=0.55, mouth_o=0.6, t=tt)
            elif tt < 17.65:
                k = lin(tt, 16.6, 17.65)
                x = lerp(600, 1505, k)
                child(c, x, fy(60), 0.95, 1, 'run', phase=tt * 15, joy=0.5, t=tt, look=(1, 0))
            else:
                k = smooth(lin(tt, 17.65, 18.0))
                hand = (lerp(60, 140, k), lerp(-60, -40, k))
                hx, hy = child(c, 1505, fy(60), 0.95, 1, 'sit', hand=hand, joy=0.55, t=tt, look=(1, 0.8))
                if letter_taken:
                    mini_letter(c, hx, hy + 5, 17, 11, CREAM, seed=610)
        st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_cookie(ctx, t, W, H):
    cx, cy, z = camk(t, [(22.6, 2170, 728, 4.4), (24.9, 2180, 728, 4.7)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    tt = twos(t)

    def actor(c):
        if tt < 23.1:
            gx = lerp(2080, 2150, lin(tt, 22.6, 23.1))
            ph = tt * 14
            hand = None
        elif tt < 23.85:
            gx = 2150
            ph = None
            k = math.sin(lin(tt, 23.15, 23.75) * math.pi)
            hand = (lerp(13, 38, k), lerp(-15, -27, k))
        else:
            gx = 2150 if tt < 24.45 else lerp(2150, 2060, lin(tt, 24.45, 24.9))
            ph = None if tt < 24.45 else tt * 16
            hand = None
        fc = 1 if tt < 24.45 else -1
        cheer = smooth(lin(tt, 23.9, 24.05)) * (1 - lin(tt, 24.35, 24.45)) * (0.6 + 0.4 * math.sin(tt * 22))
        gnome(c, gx, 755, 0.9, fc, ph, hand=hand, t=tt, cheer=cheer, sway=math.sin(tt * 7) * 0.5, blink=24.0 < tt < 24.1)
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_sock(ctx, t, W, H):
    cx, cy, z = camk(t, [(28.6, 1190, 650, 5.4), (30.9, 1215, 652, 5.8)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    tt = twos(t)

    def actor(c):
        if tt < 29.2:
            gx = lerp(1110, 1214, lin(tt, 28.6, 29.2))
            ph = tt * 14
            hand = (12, -30)
        elif tt < 29.95:
            gx = 1214
            ph = None
            k = smooth(lin(tt, 29.2, 29.45)) * (1 - smooth(lin(tt, 29.8, 29.95)))
            hand = (lerp(12, 30, k), lerp(-30, -66, k))
        else:
            gx, ph, hand = 1214, None, None
        cheer = smooth(lin(tt, 30.05, 30.2)) * (0.6 + 0.4 * math.sin(tt * 22))
        hx, hy = gnome(c, gx, 712, 0.9, 1, ph, hand=hand, t=tt, cheer=cheer, sway=math.sin(tt * 6) * 0.5,
                       blink=30.3 < tt < 30.4, look=0.6 if tt > 29.9 else 0)
        if tt < 29.5:
            # zusammengeknüllte Socke in der Hand
            c.save()
            c.translate(hx, hy)
            c.scale(0.35, 0.35)
            piece(c, np.array([(-11, -14), (11, -14), (12, 20), (26, 30), (18, 40), (-4, 36), (-12, 24)]),
                  (0.93, 0.80, 0.78), seed=1001, u=0.8)
            c.restore()
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_montage(ctx, t, W, H):
    cx, cy, z = camk(t, [(35.0, 2120, 470, 1.5), (40.6, 2115, 470, 1.65)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    L = st['L']
    if L < 0.4:
        p = (t - 35.0) / 0.27
        k = (p + 0.5) % 1.0
        cyc = int(p + 0.5)
        dirn = 1 if cyc % 2 == 0 else -1
        gx = lerp(1880, 2400, k) if dirn > 0 else lerp(2400, 1880, k)
        st['actors'].append(lambda c: (gnome(c, gx, 755, 0.9, dirn, t * 24, t=t, sway=0.5),
                                       mini_letter(c, gx + dirn * 14, 735, 16, 10, CREAM, seed=630)))
    room(ctx, t, st, tex())


def shot_bigletter(ctx, t, W, H):
    cx, cy, z = camk(t, [(40.6, 1668, 1018, 4.1), (44.0, 1672, 1016, 4.4)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['door'] = 1.0
    st['door_lit'] = 1.0
    tt = twos(t)
    add_candle(st, 1620, 8, t)
    state = {}
    x0, x1, z0, z1 = 1640, 1760, 4, 52
    GOLDP = (0.98, 0.90, 0.66)

    def sheet_draw(c):
        if tt < 42.75:
            folding_sheet(c, tt, x0, x1, z0, z1, SCRIB_BIG, (40.0, 40.1), (41.2, 41.95), (42.05, 42.7), GOLDP,
                          (0.95, 0.84, 0.55), seal=GOLD_D, seed=640, stroke=(INK, 0.7))
        else:
            k = ease(tt, 42.75, 43.25)
            hop = math.sin(k * math.pi) * 10
            c.save()
            c.translate(lerp(1670, 1686, k), fy(lerp(16, 1, k)) - hop)
            c.scale(1, lerp(0.6, 1.0, k))
            mini_letter(c, 0, 0, 58, 38, GOLDP, seal=GOLD_D, seed=650, seal_star=True)
            c.restore()
            if k >= 1:
                st['emissive'].append(lambda c2: glow(c2, 1686, fy(1) - 20, 60, (1.0, 0.85, 0.5), 0.18 + 0.06 * math.sin(t * 4)))
    st['floor_items'].append(sheet_draw)

    def actor(c):
        # Wichtel schiebt die Klappen um
        if tt < 41.2:
            gx = lerp(1790, 1772, lin(tt, 40.6, 41.2))
            ph = tt * 10 if tt < 41.1 else None
            hand = None
            fc = -1
        elif tt < 41.95:
            k = ease(tt, 41.2, 41.95)
            gx = lerp(1772, 1712, k)
            ph = tt * 9
            hand = (18, -36 + 10 * math.sin(k * 3))
            fc = -1
        elif tt < 42.7:
            k = ease(tt, 41.95, 42.7)
            gx = lerp(1712, 1735, k)
            ph = tt * 9 if k < 0.95 else None
            hand = (16, -30)
            fc = -1
        else:
            gx, ph, hand, fc = 1735, None, None, -1
        cheer = smooth(lin(tt, 43.3, 43.45)) * (0.6 + 0.4 * math.sin(tt * 20))
        gnome(c, gx, fy(26) if tt < 42.7 else fy(20), 0.92, fc, ph, hand=hand, t=tt, cheer=cheer, sway=math.sin(tt * 5) * 0.5,
              blink=43.6 < tt < 43.7, squash=0.05 * math.sin(tt * 18) if 41.2 < tt < 42.7 else 0)
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_star_room(ctx, t, W, H):
    cx, cy, z = camk(t, [(48.4, 1250, 720, 0.98), (50.2, 1250, 700, 1.08)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['bed'] = 'empty'
    tt = twos(t)
    sx, sy = 1250, 650 + math.sin(t * 1.6) * 12

    def actor(c):
        j = abs(math.sin((tt - 48.4) * 5.5))
        child(c, 1250, fy(110), 1.0, 1, 'jump', joy=1.0, jump=j * 0.8, t=tt, look=(0, -1), mouth_o=0.6)
        paper_star(c, sx, sy, 62, 1.0, math.sin(t * 1.2) * 0.1, 1.0)
        line(c, [(sx, sy - 62), (sx, -100)], (0.95, 0.85, 0.6), 1.5, alpha=0.6)
    st['actors'].append(actor)

    def em(c):
        pul = 1 + 0.05 * math.sin(t * 5)
        glow(c, sx, sy, 900 * pul, (1.0, 0.68, 0.34), 0.30)
        glow(c, sx, sy, 170, (1.0, 0.92, 0.65), 0.45)
        paper_star(c, sx, sy, 62, 1.0, math.sin(t * 1.2) * 0.1, 1.0)
        glow(c, sx, sy, 40, (1.0, 0.97, 0.85), 0.4)
    st['emissive'].append(em)
    st['L'] = 0.9
    room(ctx, t, st, tex())


def shot_reply(ctx, t, W, H):
    cx, cy, z = camk(t, [(50.2, 1500, 935, 2.5), (54.6, 1520, 950, 2.65), (56.0, 1586, 1008, 4.4)])
    cam(ctx, W, cx, cy, z)
    st = base_state(t)
    st['bed'] = 'empty'
    st['L'] = 0.78
    st['door_lit'] = 1.35 * smooth(lin(t, 54.65, 55.05))
    tt = twos(t)
    state = {}
    x0, x1, z0, z1 = 1468, 1536, 34, 76
    # Kind sitzt links vom Blatt

    def sheet_draw(c):
        if tt < 53.05:
            tip = folding_sheet(c, tt, x0, x1, z0, z1, SCRIB_KID, (50.4, 51.8), (51.9, 52.45), (52.5, 53.0), WHITE, (0.95, 0.93, 0.9),
                                seal=RED_L, crooked=1.0, seed=660, stroke=(RED, 2.2), wr=0.8)
            state['tip'] = tip
            state['pk'] = None
        else:
            # zerknittertes Päckchen gleitet unter die Tür
            k = ease(tt, 53.05, 54.25)
            w = (x1 - x0) / 2
            d = (z1 - z0) / 2
            cxp = lerp(x0 + w / 2, (DOOR_X0 + DOOR_X1) / 2, k)
            zc = lerp(z0 + d / 2, -d / 2 - 2, k)
            c.save()
            c.rectangle(0, FLOOR, 4000, 1000)
            c.clip()
            q = floor_quad([(cxp - w / 2 + 2, zc - d / 2, 0.3), (cxp + w / 2, zc - d / 2 + 1, 0.3), (cxp + w / 2 - 1, zc + d / 2, 0.3),
                            (cxp - w / 2 - 1, zc + d / 2 - 2, 0.3)])
            piece(c, q, (0.92, 0.90, 0.87), seed=670, u=0.8, shadow=0.5)
            c.save()
            c.translate(cxp, fy(zc))
            c.scale(1, KF)
            dot(c, 0, 0, 4, RED_L)
            c.restore()
            line(c, [(cxp - w / 2 + 3, fy(zc - 3)), (cxp + w / 2 - 4, fy(zc + 4))], (0.8, 0.78, 0.74), 0.8)
            c.restore()
            state['pk'] = (cxp + w / 2 - 6, fy(zc + d / 2))
    st['floor_items'].append(sheet_draw)

    def actor(c):
        tip = state.get('tip')
        hand = None
        if 50.4 <= tt < 51.8 and tip is not None:
            hand = ((tip[0] - 1395) / 0.95, (tip[1] - fy(70)) / 0.95)
        elif 51.8 <= tt < 53.05:
            k = (tt - 51.8) / 1.25
            hand = (95 + 25 * math.sin(k * math.pi * 2), -30 - 15 * abs(math.sin(k * math.pi * 2)))
        elif 53.05 <= tt < 54.3 and state.get('pk') is not None:
            px, py = state['pk']
            hand = (min(150, (px - 1395) / 0.95), (py - fy(70)) / 0.95 - 4)
        elif tt >= 54.3:
            k = smooth(lin(tt, 54.3, 54.6))
            hand = (lerp(150, 110, k), lerp(-12, -60, k))
        joy = 0.6 if tt < 54.65 else 1.0
        mo = 0.8 * clamp(1 - (tt - 54.7) * 1.5) if tt > 54.65 else 0
        hx, hy = child(c, 1395, fy(70), 0.95, 1, 'sit', hand=hand, joy=joy, t=tt, look=(1, 0.9), mouth_o=mo,
                       blink=52.0 < tt < 52.1)
        if hand is not None and 50.4 <= tt < 51.85:
            # Wachsmalstift
            c.save()
            c.translate(hx, hy)
            c.rotate(-0.6)
            piece(c, rect_pts(-3, -26, 6, 24), RED, seed=680, u=0.6, shadow=0.4)
            c.restore()
    st['actors'].append(actor)
    room(ctx, t, st, tex())


def shot_insert(kind, t0, dur, j0, j1, t_open):
    def fn(ctx, t, W, H):
        ctx.scale(W / 1920.0, W / 1920.0)
        insert(ctx, t - t0, kind, dur, j0, j1, tex(), t_open)
    return fn


def shot_end(ctx, t, W, H):
    ctx.scale(W / 1920.0, W / 1920.0)
    endcard(ctx, t - 56.0, tex())


SHOTS = [
    (0.0, 3.4, shot_exterior),
    (3.0, 5.2, shot_push),
    (5.2, 7.8, shot_door),
    (7.8, 12.0, shot_write),
    (12.0, 14.6, shot_flour),
    (14.6, 15.8, lambda c, t, W, H: shot_calendar(c, t, W, H, 14.6, 15.8, (2117, 345), 2.5, 2.9)),
    (15.8, 18.2, shot_morning1),
    (18.2, 22.6, shot_insert('dog', 18.2, 4.4, 0.3, 0.55, (0.35, 1.15))),
    (22.6, 24.9, shot_cookie),
    (24.9, 25.6, lambda c, t, W, H: shot_calendar(c, t, W, H, 24.9, 25.6, (2060, 270), 3.0, 3.3)),
    (25.6, 28.6, shot_insert('tooth', 25.6, 3.0, 0.55, 0.74, (0.25, 0.9))),
    (28.6, 30.9, shot_sock),
    (30.9, 31.6, lambda c, t, W, H: shot_calendar(c, t, W, H, 30.9, 31.6, (2160, 420), 3.0, 3.3)),
    (31.6, 35.0, shot_insert('drawing', 31.6, 3.4, 0.74, 0.92, (0.25, 0.9))),
    (35.0, 40.6, shot_montage),
    (40.6, 44.0, shot_bigletter),
    (44.0, 44.6, lambda c, t, W, H: shot_calendar(c, t, W, H, 44.0, 44.6, (2150, 330), 2.8, 3.2)),
    (44.6, 48.4, shot_insert('star', 44.6, 3.8, 0.92, 1.0, (0.2, 0.9))),
    (48.4, 50.2, shot_star_room),
    (50.2, 56.0, shot_reply),
    (55.6, 60.0, shot_end),
]
XFADE = {(0, 1): (3.0, 3.4), (19, 20): (55.6, 56.0)}


def draw_shot(fn, t, W, H):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(*CREAM)
    ctx.paint()
    ctx.save()
    fn(ctx, t, W, H)
    ctx.restore()
    surf.flush()
    arr = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W, :3]
    return arr[:, :, ::-1].astype(np.float32)


def post(W, H):
    if (W, H) not in _post:
        r = np.random.RandomState(3)
        g = r.randn(H // 2 + 1, W // 2 + 1).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)[:H, :W]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx / W - 0.5) ** 2 * 1.2 + (yy / H - 0.5) ** 2 * 1.6)
        vig = 1 - 0.32 * np.clip(d * 2.2, 0, 1) ** 1.6
        _post[(W, H)] = ((1 + 0.018 * g) * vig)[:, :, None].astype(np.float32)
    return _post[(W, H)]


def render_frame(t, W, H):
    act = [i for i, (a, b, f) in enumerate(SHOTS) if a <= t < b]
    if not act:
        act = [len(SHOTS) - 1]
    if len(act) >= 2 and tuple(act[:2]) in XFADE:
        i, j = act[:2]
        x0, x1 = XFADE[(i, j)]
        k = smooth(lin(t, x0, x1))
        A = draw_shot(SHOTS[i][2], t, W, H)
        B = draw_shot(SHOTS[j][2], t, W, H)
        img = A * (1 - k) + B * k
    else:
        img = draw_shot(SHOTS[act[-1]][2], t, W, H)
    # Abblende ganz am Ende
    img *= post(W, H)
    if t > 59.6:
        img *= 1 - 0.0 * lin(t, 59.6, 60)
    if t < 0.4:
        img *= smooth(lin(t, 0.0, 0.4))
    return np.clip(img, 0, 255).astype(np.uint8)
