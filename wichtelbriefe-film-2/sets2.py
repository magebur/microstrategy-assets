"""Kulissen: Wohnzimmer (Wand-, Möbel-, Vordergrundebene), Wichtelstube, Außenwelt im Fenster."""
import math
import cairo
import numpy as np
from paper import *
from engine import catmull, soft, soft2, emboss, heart_pts, sprig_pts, draw_snowflake
from chars2 import CAT, CAT_D, CAT_CREAM, paw_seal

FLOOR = 1050.0
KF = 0.75
KID = (270.0, 560.0, 300.0)
GD = (640.0, 690.0, 970.0)          # Wichteltür x0, x1, oben
WIN = (1450.0, 1950.0, 230.0, 770.0)
FIRE = (2250.0, 2750.0)
SOFA = (2950.0, 3600.0)
TREE_X = 3950.0
BASKET = (1960.0, 2220.0)
NIGHT = (0.47, 0.53, 0.72)
DAWN = (0.98, 0.90, 0.86)


def fy(z):
    return FLOOR + KF * z


def light_col(L):
    return mix(NIGHT, DAWN, L)


# ------------------------------------------------------------------ Außenwelt
def outside(ctx, t, L, storm, camx):
    x0, x1, y0, y1 = WIN
    off = (camx - 1700) * 0.25
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    top = mix((0.17, 0.21, 0.32), (0.55, 0.62, 0.82), L)
    bot = mix((0.30, 0.35, 0.48), (1.0, 0.80, 0.62), L)
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.fill()
    if L > 0.05:
        glow(ctx, 1700 - off * 0.5, 700, 260, (1.0, 0.75, 0.45), 0.5 * L, op=cairo.OPERATOR_OVER)
    ctx.save()
    ctx.translate(off, 0)
    for j, (yb, col) in enumerate(((640, (0.70, 0.75, 0.86)), (690, (0.84, 0.87, 0.94)))):
        pts = [(x0 - 300, y1 + 50)] + [(x, yb - 30 * math.sin(x * 0.01 + j * 2)) for x in np.linspace(x0 - 300, x1 + 300, 30)] + [(x1 + 300, y1 + 50)]
        soft(ctx, pts, mix(col, (1.0, 0.92, 0.86), L * 0.6), seed=8000 + j, u=2, n=3, shadow=1.2)
    for i, (fx, fh) in enumerate(((1400, 220), (1520, 150), (1760, 260), (1900, 180), (2020, 230))):
        _fir(ctx, fx, 700 + (i % 2) * 15, fh, 8010 + i * 9, mix((0.10, 0.26, 0.20), GREEN, L * 0.7))
    ctx.restore()
    # Schnee
    r = np.random.RandomState(31)
    n = 70 if storm < 0.1 else 140
    for i in range(n):
        sx = r.uniform(0, 1)
        sy = r.uniform(0, 1)
        sp = r.uniform(0.6, 1.4)
        size = r.uniform(4, 9)
        drift = 140 * storm
        y = y0 + ((sy * (y1 - y0) + t * (40 + 160 * storm) * sp) % (y1 - y0 + 40)) - 20
        x = x0 + ((sx * (x1 - x0) + t * drift * sp + math.sin(t + i) * 10) % (x1 - x0))
        dot(ctx, x, y, size * 0.5, WHITE, 0.9)
    ctx.restore()


def _fir(ctx, x, y, h, seed, col, col2=None, u=1.5):
    col2 = col2 or darker(col, 0.8)
    for i in range(4):
        k = i / 4
        w = h * (0.42 - 0.07 * k) * (1 - k * 0.5)
        top = y - h * (0.3 + 0.7 * (i + 1) / 4)
        bot = y - h * (0.1 + 0.62 * i / 4)
        soft2(ctx, [(x, top), (x + w * 0.5, (top + bot) / 2), (x + w, bot), (x, bot + h * 0.03), (x - w, bot), (x - w * 0.5, (top + bot) / 2)],
              col, col2, (x, top - 10), (x + w * 0.1, bot + 10), seed=seed + i, u=u, n=4)
        soft(ctx, [(x, top), (x + w * 0.35, top + (bot - top) * 0.35), (x, top + (bot - top) * 0.28), (x - w * 0.35, top + (bot - top) * 0.35)],
             WHITE, seed=seed + 20 + i, u=u, n=3, shadow=0.3)


# ------------------------------------------------------------------ Wand-Ebene
def wall_layer(ctx, t, st):
    L = st['L']
    ctx.rectangle(-400, -400, 5200, FLOOR + 400)
    ctx.set_source_rgb(*CREAM)
    ctx.fill()
    pw = 120
    x = -400
    i = 0
    while x < 4800:
        ctx.rectangle(x, -400, pw, FLOOR + 400)
        ctx.set_source_rgb(*(CREAM if i % 2 == 0 else mix(CREAM, CREAM2, 0.55)))
        ctx.fill()
        line(ctx, [(x, -400), (x, FLOOR)], darker(CREAM2, 0.92), 1.0, alpha=0.55, cap=0)
        x += pw
        i += 1
    # geprägte Sterne + Karos auf der Tapete
    r = np.random.RandomState(9)
    for k in range(int(5200 / 140) * 7):
        gx = -380 + (k % 38) * 140 + ((k // 38) % 2) * 70
        gy = -300 + (k // 38) * 190
        if gy > 900:
            continue
        col = CREAM if (int((gx + 400) / pw) % 2 == 0) else mix(CREAM, CREAM2, 0.55)
        if (k // 38) % 2:
            emboss(ctx, star_pts(gx, gy, 16, 7, 5, rot=-math.pi / 2), col, u=1.0, depth=1.2)
        else:
            emboss(ctx, rot_pts(rect_pts(gx - 8, gy - 8, 16, 16), math.pi / 4, gx, gy), col, u=1.0, depth=1.0, raised=False)
    # Fußleiste mit geprägtem Tannenzweig
    piece(ctx, np.array([(-400, 990), (4800, 990), (4800, FLOOR), (-400, FLOOR)]), GREEN, seed=8100, u=2, shadow=0.8, amp=0.15)
    piece(ctx, np.array([(-400, 984), (4800, 984), (4800, 996), (-400, 996)]), GREEN_L, seed=8101, u=2, shadow=0.4, amp=0.1)
    for k in range(40):
        for p in sprig_pts(-380 + k * 130, 1022, 70, 0.0):
            emboss(ctx, p, GREEN, u=0.8, depth=1.0)
    floor_(ctx, t, st)
    kid_door(ctx, t, st)
    gnome_door(ctx, t, st)
    calendar(ctx, t, st)
    window(ctx, t, st)


def floor_(ctx, t, st):
    ctx.rectangle(-400, FLOOR, 5200, 700)
    ctx.set_source_rgb(*WOOD)
    ctx.fill()
    y = FLOOR
    i = 0
    while y < 1800:
        hh = 24 + i * 9
        piece(ctx, rect_pts(-400, y, 5200, hh), WOOD_L if i % 2 == 0 else mix(WOOD_L, WOOD, 0.55), seed=8110 + i, u=2, shadow=0.35, amp=0.12)
        y += hh
        i += 1
    # Teppich mit Falzmuster (Rauten-Knicke + Prägesterne)
    x0, x1, z0, z1 = 1760, 3350, 18, 150
    q = np.array([(x0 + 30, fy(z0)), (x1 - 30, fy(z0)), (x1 + 20, fy(z1)), (x0 - 20, fy(z1))])
    p = piece(ctx, catmull(q, 3), RED, seed=8120, u=2, shadow=1.0, amp=0.1)
    ctx.save()
    path(ctx, p)
    ctx.clip()
    n = 22
    for i in range(n):
        for j in range(4):
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            za = z0 + (z1 - z0) * j / 4
            zb = z0 + (z1 - z0) * (j + 1) / 4
            xm, zm = (xa + xb) / 2, (za + zb) / 2
            dia = np.array([(xm, fy(za)), (xb, fy(zm)), (xm, fy(zb)), (xa, fy(zm))])
            path(ctx, np.array([(xa, fy(za)), (xm, fy(za)), (xa, fy(zm))]))
            ctx.set_source_rgba(*RED_D, 0.5)
            ctx.fill()
            path(ctx, np.array([(xb, fy(zb)), (xm, fy(zb)), (xb, fy(zm))]))
            ctx.set_source_rgba(*RED_L, 0.45)
            ctx.fill()
            path(ctx, dia)
            ctx.set_source_rgba(*darker(RED, 0.7), 0.5)
            ctx.set_line_width(1.0)
            ctx.stroke()
    ctx.restore()
    piece(ctx, np.array([(x0 + 10, fy(z0) - 2), (x1 - 10, fy(z0) - 2), (x1 + 5, fy(z0 + 8)), (x0 - 5, fy(z0 + 8))]), GOLD_D, seed=8121, u=2, shadow=0.2, amp=0.1)
    piece(ctx, np.array([(x0 - 20, fy(z1 - 8)), (x1 + 20, fy(z1 - 8)), (x1 + 24, fy(z1)), (x0 - 24, fy(z1))]), GOLD_D, seed=8122, u=2, shadow=0.2, amp=0.1)


def kid_door(ctx, t, st):
    x0, x1, top = KID
    piece2(ctx, np.array([(x0 - 26, FLOOR), (x0 - 26, top - 26), (x1 + 26, top - 26), (x1 + 26, FLOOR)]), WHITE, WHITE2,
           ((x0 + x1) / 2, top - 100), ((x0 + x1) / 2, FLOOR + 100), seed=8200, u=2, shadow=1.4, amp=0.12)
    o = st.get('kid_open', 0.0)
    lit = st.get('kid_light', 0.0)
    path(ctx, rect_pts(x0, top, x1 - x0, FLOOR - top))
    ctx.set_source_rgb(*mix((0.25, 0.2, 0.2), (0.98, 0.85, 0.62), lit))
    ctx.fill()
    ang = o * 1.2
    cw = math.cos(ang)
    leaf = np.array([(x0, top), (x0 + (x1 - x0) * cw, top - 20 * math.sin(ang)), (x0 + (x1 - x0) * cw, FLOOR + 22 * math.sin(ang)), (x0, FLOOR)])
    p = piece(ctx, leaf, mix(CREAM, PINK, 0.3), seed=8201, u=2, shadow=1.0, amp=0.1)
    if cw > 0.3:
        for (a, b, c, d) in ((0.12, 0.08, 0.76, 0.36), (0.12, 0.52, 0.76, 0.40)):
            pr = np.array([(x0 + (x1 - x0) * a * cw, top + (FLOOR - top) * b), (x0 + (x1 - x0) * (a + c) * cw, top + (FLOOR - top) * b),
                           (x0 + (x1 - x0) * (a + c) * cw, top + (FLOOR - top) * (b + d)), (x0 + (x1 - x0) * a * cw, top + (FLOOR - top) * (b + d))])
            emboss(ctx, pr, mix(CREAM, PINK, 0.3), u=2, depth=1.2)
        dot(ctx, x0 + (x1 - x0) * 0.88 * cw, 700, 11, GOLD)
        # Herz-Schild
        emboss(ctx, heart_pts(x0 + (x1 - x0) * 0.5 * cw, 410, 30), RED_L, u=1.5)


def gnome_door(ctx, t, st):
    x0, x1, top = GD
    w = x1 - x0
    o = st.get('gdoor', 0.0)
    inner = st.get('gdoor_lit', 0.6)
    fr = np.vstack([[(x0 - 8, FLOOR)], ellipse_pts((x0 + x1) / 2, top + w / 2, w / 2 + 8, w / 2 + 8, a0=math.pi, a1=2 * math.pi, n=26), [(x1 + 8, FLOOR)]])
    piece2(ctx, fr, CREAM, CREAM3, ((x0 + x1) / 2, top - 20), ((x0 + x1) / 2, FLOOR), seed=8300, u=0.6, shadow=1.0, amp=0.1)
    arch = np.vstack([[(x0, FLOOR)], ellipse_pts((x0 + x1) / 2, top + w / 2, w / 2, w / 2, a0=math.pi, a1=2 * math.pi, n=26), [(x1, FLOOR)]])
    path(ctx, arch)
    g = cairo.RadialGradient((x0 + x1) / 2, FLOOR - 25, 2, (x0 + x1) / 2, FLOOR - 25, 70)
    g.add_color_stop_rgb(0, *mix((0.3, 0.18, 0.12), (1.0, 0.82, 0.5), inner))
    g.add_color_stop_rgb(1, *mix((0.2, 0.12, 0.08), (0.7, 0.38, 0.18), inner))
    ctx.set_source(g)
    ctx.fill()
    ang = o * 1.75
    cw = math.cos(ang)
    leaf = arch.copy()
    leaf[:, 0] = x0 + (leaf[:, 0] - x0) * cw
    if o < 0.999:
        col = RED if cw > 0 else RED_D
        piece(ctx, leaf, col, seed=8301, u=0.6, shadow=0.6, amp=0.1)
        if cw > 0.2:
            for k in (0.33, 0.66):
                line(ctx, [(x0 + w * k * cw, top + 10), (x0 + w * k * cw, FLOOR - 2)], RED_D, 0.7)
            dot(ctx, x0 + w * 0.2 * cw, top + 48, 2.2, GOLD)
            # Schlüsselloch
            kx, ky = x0 + w * 0.72 * cw, top + 46
            ctx.save()
            ctx.translate(kx, ky)
            ctx.scale(max(cw, 0.01), 1)
            ki = np.vstack([ellipse_pts(0, -2, 3.0, 3.0, n=18), np.array([(1.6, 0), (2.4, 6), (-2.4, 6), (-1.6, 0)])])
            path(ctx, catmull(np.array([(0, -5), (2.6, -3.8), (2.4, -0.5), (2.6, 6), (-2.6, 6), (-2.4, -0.5), (-2.6, -3.8)]), 4))
            ctx.set_source_rgb(*mix((0.18, 0.10, 0.07), (1.0, 0.78, 0.45), inner * 0.9))
            ctx.fill()
            ctx.restore()
    st['_gd_arch'] = arch


def calendar(ctx, t, st):
    x0, y0 = 800, 230
    u = 1.6
    line(ctx, [(x0 + 30, y0 + 4), (x0 + 210, 175), (x0 + 390, y0 + 4)], INK, 1.6)
    dot(ctx, x0 + 210, 175, 4, GOLD_D)
    piece2(ctx, rect_pts(x0, y0, 420, 320), RED, RED_D, (x0 + 210, y0 - 10), (x0 + 210, y0 + 400), seed=8400, u=u, shadow=1.6, amp=0.1)
    piece(ctx, rect_pts(x0 + 8, y0 + 8, 404, 304), GREEN, seed=8401, u=u, shadow=0.3, amp=0.1)
    order = [7, 19, 2, 13, 22, 10, 16, 4, 11, 24, 1, 20, 9, 14, 21, 5, 17, 3, 12, 23, 8, 15, 6, 18]
    for idx, n in enumerate(order):
        c, r = idx % 6, idx // 6
        dx, dy = x0 + 20 + c * 65, y0 + 20 + r * 74
        w, h = 56, 64
        piece(ctx, rect_pts(dx, dy, w, h), (0.25, 0.14, 0.12), seed=8410 + n, u=0.5, shadow=0, amp=0.1)
        if n < 24:
            cx, cy = dx + w / 2, dy + h / 2
            emboss(ctx, star_pts(cx, cy, 13, 6), YELLOW if n % 2 else PINK, u=0.8)
            ww = w * math.cos(1.9)
            piece(ctx, np.array([(dx, dy), (dx + ww, dy - 3), (dx + ww, dy + h + 3), (dx, dy + h)]), darker(CREAM, 0.82), seed=8440 + n, u=0.5, shadow=0.5, amp=0.1)
        else:
            piece(ctx, rect_pts(dx, dy, w, h), GOLD, seed=8470, u=0.5, shadow=0.6, amp=0.1)
            emboss(ctx, star_pts(dx + w / 2, dy + 20, 10, 4.5), GOLD, u=0.6)
            ctx.save()
            ctx.select_font_face("Kurale", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(30)
            e = ctx.text_extents("24")
            ctx.move_to(dx + w / 2 - e.x_advance / 2, dy + h - 10)
            ctx.text_path("24")
            ctx.set_source_rgb(*RED_D)
            ctx.fill_preserve()
            ctx.set_line_width(0.8)
            ctx.stroke()
            ctx.restore()
            st['_cal24'] = (dx + w / 2, dy + h / 2)


def window(ctx, t, st):
    x0, x1, y0, y1 = WIN
    L = st['L']
    storm = st.get('storm', 0.0)
    outside(ctx, t, L, storm, st.get('camx', 1700))
    # Fensterrahmen
    for p in (rect_pts(x0 - 20, y0 - 20, x1 - x0 + 40, 24), rect_pts(x0 - 20, y1 - 4, x1 - x0 + 40, 24),
              rect_pts(x0 - 20, y0 - 20, 24, y1 - y0 + 40), rect_pts(x1 - 4, y0 - 20, 24, y1 - y0 + 40)):
        piece(ctx, p, WHITE, seed=int(p[0, 0] + p[0, 1]) + 8500, u=2, shadow=1.4, amp=0.1)
    # Flügel (aufgedrückt durch die Böe)
    o = st.get('win_open', 0.0)
    rattle = st.get('rattle', 0.0)
    mid = (x0 + x1) / 2
    for side in (-1, 1):
        hinge = x0 if side < 0 else x1
        a = o * (1.25 + 0.12 * math.sin(t * 17 + side) * rattle)
        cw = math.cos(a)
        wx = (mid - hinge) * cw
        wing = np.array([(hinge, y0), (hinge + wx, y0 - 18 * math.sin(a)), (hinge + wx, y1 + 18 * math.sin(a)), (hinge, y1)])
        if abs(wx) > 2:
            # Glas (leicht milchig) + Sprossen
            path(ctx, wing)
            ctx.set_source_rgba(0.85, 0.9, 1.0, 0.10 + 0.15 * (1 - cw))
            ctx.fill()
            fr = WHITE if cw > 0.4 else WHITE2
            for (ax, ay, bx, by) in ((0, 0, 1, 0), (0, 1, 1, 1), (1, 0, 1, 1), (0, 0.5, 1, 0.5)):
                pA = (hinge + wx * ax, lerp(y0 - 18 * math.sin(a) * ax, y1 + 18 * math.sin(a) * ax, ay))
                pB = (hinge + wx * bx, lerp(y0 - 18 * math.sin(a) * bx, y1 + 18 * math.sin(a) * bx, by))
                line(ctx, [pA, pB], darker(fr, 0.85), 15, cap=0)
                line(ctx, [pA, pB], fr, 12, cap=0)
    # Fensterbank
    piece2(ctx, np.array([(x0 - 30, y1 + 4), (x1 + 30, y1 + 4), (x1 + 44, y1 + 30), (x0 - 44, y1 + 30)]), WHITE, WHITE2,
           (x0, y1 + 16), (x1, y1 + 16), seed=8520, u=2, shadow=1.6, amp=0.1)
    # Vorhänge (flattern im Sturm)
    flap = st.get('curtain', 0.0)
    for side in (-1, 1):
        cx = x0 - 45 if side < 0 else x1 + 45
        for f in range(5):
            w = 24
            xa = cx + side * (f - 2.5) * w * 0.9
            col = PINK if f % 2 == 0 else PINK_D
            pts = []
            for k in np.linspace(0, 1, 9):
                yy = lerp(190, 820, k)
                bil = flap * (k ** 1.3) * (60 * math.sin(t * 9 + f * 0.7 + k * 3) + 120 * side * -1 * 0) + flap * k ** 1.5 * 150 * (-side) * 0.0
                sway = flap * k ** 1.4 * (70 * math.sin(t * 8.5 + f * 0.6 + k * 4) - 160 * side)
                pts.append((xa - w / 2 + sway, yy))
            for k in np.linspace(1, 0, 9):
                yy = lerp(190, 820, k)
                sway = flap * k ** 1.4 * (70 * math.sin(t * 8.5 + f * 0.6 + k * 4 + 0.4) - 160 * side)
                pts.append((xa + w / 2 + sway, yy))
            piece(ctx, np.array(pts), col, seed=8530 + f + (side + 1) * 10, u=2, shadow=0.9, amp=0.15, alpha=0.96)
    piece(ctx, rect_pts(1340, 175, 720, 18), WOOD_D, seed=8550, u=2, shadow=1.4, amp=0.1)
    dot(ctx, 1340, 184, 14, GOLD_D)
    dot(ctx, 2060, 184, 14, GOLD_D)


# ------------------------------------------------------------------ Möbel-Ebene
def fireplace(ctx, t, st):
    x0, x1 = FIRE
    u = 2
    soft2(ctx, [(x0 + 30, -400), (x1 - 30, -400), (x1 - 30, 600), (x0 + 30, 600)], mix(CREAM, CREAM2, 0.6), CREAM2,
          ((x0 + x1) / 2, -400), ((x0 + x1) / 2, 700), seed=8600, u=u, n=2)
    for r in range(18):
        for c in range(8):
            bx = x0 + 40 + c * 56 + (r % 2) * 28
            by = -390 + r * 54
            if bx + 50 < x1 - 30 and by < 580:
                emboss(ctx, rect_pts(bx, by, 50, 46), mix(CREAM, CREAM2, 0.6), u=1.0, depth=0.9, raised=False)
    soft2(ctx, [(x0 + 20, 620), (x1 - 20, 620), (x1 - 20, FLOOR), (x0 + 20, FLOOR)], RED, RED_D, ((x0 + x1) / 2, 500), ((x0 + x1) / 2, 1100),
          seed=8601, u=u, n=2)
    for p in sprig_pts(x0 + 40, 700, 110, 0.0) + sprig_pts(x1 - 40, 700, 110, math.pi):
        emboss(ctx, p, RED, u=0.8)
    op = np.vstack([[(x0 + 130, FLOOR)], ellipse_pts((x0 + x1) / 2, 830, 120, 90, a0=math.pi, a1=2 * math.pi, n=30), [(x1 - 130, FLOOR)]])
    path(ctx, op)
    g = cairo.LinearGradient(0, 760, 0, FLOOR)
    g.add_color_stop_rgb(0, 0.12, 0.07, 0.06)
    g.add_color_stop_rgb(1, 0.30, 0.12, 0.06)
    ctx.set_source(g)
    ctx.fill()
    # Holzscheite + Glut
    for i, (lx, ly, lw, la) in enumerate(((2440, 1018, 120, 0.12), (2540, 1022, 110, -0.15), (2490, 1000, 100, 0.03))):
        ctx.save()
        ctx.translate(lx, ly)
        ctx.rotate(la)
        soft(ctx, [(-lw / 2, -11), (lw / 2, -11), (lw / 2 + 4, 0), (lw / 2, 11), (-lw / 2, 11), (-lw / 2 - 4, 0)], (0.35, 0.20, 0.13), seed=8610 + i, u=1, n=3)
        dot(ctx, lw / 2, 0, 9, (0.55, 0.38, 0.25))
        ctx.restore()
    r = np.random.RandomState(4)
    for i in range(26):
        ex = r.uniform(2400, 2600)
        ey = r.uniform(1018, 1045)
        fl = 0.5 + 0.5 * math.sin(t * r.uniform(3, 7) + i)
        col = mix((0.55, 0.12, 0.05), (1.0, 0.55, 0.15), fl)
        piece(ctx, star_pts(ex, ey, r.uniform(6, 12), r.uniform(3, 5), 3, rot=r.uniform(0, 6)), col, seed=8620 + i, u=0.6, shadow=0.2, amp=0.15)
    # Kaminsims mit Strümpfen
    soft2(ctx, [(x0 - 10, 590), (x1 + 10, 590), (x1 + 16, 622), (x0 - 16, 622)], WOOD_L, WOOD, (x0, 606), (x1, 606), seed=8630, u=u, n=2)
    for i, sx in enumerate((x0 + 90, x1 - 90)):
        sw = math.sin(t * 1.4 + i) * 0.03 + st.get('curtain', 0) * 0.1 * math.sin(t * 7 + i)
        ctx.save()
        ctx.translate(sx, 618)
        ctx.rotate(sw)
        sk = [(-20, 0), (20, 0), (22, 90), (48, 108), (44, 132), (10, 132), (-18, 112)]
        soft2(ctx, sk, RED_L if i else GREEN_L, RED if i else GREEN, (0, -10), (8, 140), seed=8640 + i, u=1.2, n=4)
        piece(ctx, rect_pts(-24, -4, 48, 22), WHITE, seed=8645 + i, u=1.2, shadow=0.5, amp=0.6)
        emboss(ctx, star_pts(4, 64, 12, 5), RED_L if i else GREEN_L, u=0.7)
        ctx.restore()
    # Kerzen auf dem Sims
    for cx in (2420, 2580):
        piece(ctx, rect_pts(cx - 7, 548, 14, 42), CREAM, seed=8650 + cx, u=1, shadow=0.6, amp=0.1)
    st.setdefault('_mantel_candles', [(2420, 546), (2580, 546)])


def basket(ctx, t, st, front=False):
    x0, x1 = BASKET
    cx = (x0 + x1) / 2
    z = 40
    if not front:
        soft2(ctx, [(x0, fy(z) - 30), (cx, fy(z) - 44), (x1, fy(z) - 30), (x1, fy(z) + 8), (x0, fy(z) + 8)], WOOD_L, WOOD, (cx, 900), (cx, 1200),
              seed=8700, u=2, n=4)
        piece(ctx, ellipse_pts(cx, fy(z) - 26, (x1 - x0) / 2 - 12, 16, n=40), mix(RED_L, PINK, 0.4), seed=8701, u=2, shadow=0.4, amp=0.1)
    else:
        p = soft2(ctx, [(x0 - 6, fy(z) - 26), (x1 + 6, fy(z) - 26), (x1 - 4, fy(z) + 20), (x0 + 4, fy(z) + 20)], WOOD, WOOD_D,
                  (cx, 900), (cx, 1300), seed=8702, u=2, n=3)
        ctx.save()
        path(ctx, p)
        ctx.clip()
        for i in range(14):
            xx = x0 + i * 20
            line(ctx, [(xx, fy(z) - 30), (xx + 10, fy(z) + 24)], WOOD_L, 4, alpha=0.6)
        ctx.restore()


def sofa_back(ctx, t, st):
    x0, x1 = SOFA
    u = 2
    soft2(ctx, [(x0 + 40, 820), (x0 + 50, 600), (x0 + 120, 560), (x1 - 120, 560), (x1 - 50, 600), (x1 - 40, 820)], RED_L, RED,
          ((x0 + x1) / 2, 500), ((x0 + x1) / 2, 900), seed=8800, u=u, n=4)
    for k in range(3):
        cx = x0 + 150 + k * 175
        soft2(ctx, [(cx - 80, 815), (cx - 78, 640), (cx, 625), (cx + 78, 640), (cx + 80, 815)], RED_L, RED, (cx, 600), (cx, 900), seed=8801 + k, u=u, n=4)
        for p in sprig_pts(cx - 40, 720, 80, -0.2):
            emboss(ctx, p, RED_L, u=0.8)
    # Kissen
    soft2(ctx, [(x0 + 90, 790), (x0 + 110, 700), (x0 + 220, 690), (x0 + 230, 790)], GOLD, GOLD_D, (x0 + 160, 650), (x0 + 160, 820), seed=8810, u=u, n=4)
    emboss(ctx, star_pts(x0 + 165, 742, 24, 10), GOLD, u=1)
    # Sitzfläche
    soft2(ctx, [(x0, 800), (x1, 800), (x1 + 10, 870), (x0 - 10, 870)], RED, RED_D, (x0, 835), (x1, 835), seed=8811, u=u, n=3)
    # Schatten unter dem Sofa
    ctx.rectangle(x0 + 20, 870, x1 - x0 - 40, FLOOR - 870 + 20)
    g = cairo.LinearGradient(0, 870, 0, FLOOR + 20)
    g.add_color_stop_rgba(0, 0.08, 0.04, 0.03, 0.75)
    g.add_color_stop_rgba(1, 0.08, 0.04, 0.03, 0.35)
    ctx.set_source(g)
    ctx.fill()
    for lx in (x0 + 60, x1 - 60):
        soft(ctx, [(lx - 10, 870), (lx + 10, 870), (lx + 6, FLOOR - 4), (lx - 6, FLOOR - 4)], WOOD_D, seed=8820 + lx, u=1, n=2)


def sofa_front(ctx, t, st):
    x0, x1 = SOFA
    u = 2
    for side in (-1, 1):
        ax = x0 - 10 if side < 0 else x1 + 10
        soft2(ctx, [(ax - 50, 900), (ax - 52, 700), (ax - 40, 670), (ax + 40, 670), (ax + 52, 700), (ax + 50, 900)], RED_L, RED,
              (ax, 640), (ax, 920), seed=8830 + side, u=u, n=4)
        soft(ctx, [(ax - 10, 900), (ax + 10, 900), (ax + 6, FLOOR + 30), (ax - 6, FLOOR + 30)], WOOD_D, seed=8835 + side, u=1, n=2)
    # Volant / Saum mit Bogenkante
    pts = [(x0 - 5, 862), (x1 + 5, 862)]
    for k in np.linspace(x1 + 5, x0 - 5, 26):
        pts.append((k, 905 + 8 * math.sin((k - x0) / 25)))
    soft(ctx, pts, RED_D, seed=8840, u=u, n=2)


def tree(ctx, t, st):
    cx = TREE_X
    u = 2
    swing = st.get('swing', 0.2)
    # Topf
    soft2(ctx, [(cx - 75, 960), (cx + 75, 960), (cx + 60, FLOOR), (cx - 60, FLOOR)], RED, RED_D, (cx, 940), (cx, 1080), seed=8900, u=u, n=3)
    for p in sprig_pts(cx - 40, 1005, 80, 0):
        emboss(ctx, p, RED, u=0.8)
    soft(ctx, [(cx - 12, 900), (cx + 12, 900), (cx + 12, 962), (cx - 12, 962)], WOOD_D, seed=8901, u=1, n=2)
    tiers = 7
    for i in range(tiers):
        k = i / (tiers - 1)
        w = 70 + 170 * k
        top = 80 + 125 * i - 70
        bot = 80 + 125 * i + 120
        pts = [(cx, top), (cx + w * 0.45, (top + bot) / 2 - 10), (cx + w, bot), (cx + w * 0.55, bot - 14), (cx + w * 0.2, bot + 4), (cx, bot - 10),
               (cx - w * 0.2, bot + 4), (cx - w * 0.55, bot - 14), (cx - w, bot), (cx - w * 0.45, (top + bot) / 2 - 10)]
        soft2(ctx, pts, GREEN_L, GREEN, (cx + 4, top - 20), (cx + 18, bot + 30), seed=8910 + i, u=u, n=4)
        for p in sprig_pts(cx - w * 0.6, bot - 30, w * 0.4, -0.3):
            emboss(ctx, p, GREEN_L, u=0.6, depth=0.8)
    # Lametta-Girlanden
    for i, (ya, wa) in enumerate(((230, 90), (420, 150), (600, 200), (790, 240))):
        pts = []
        for k in np.linspace(-1, 1, 30):
            pts.append((cx + k * wa, ya + 45 * (1 - k * k) + 3 * math.sin(t * 5 + k * 6 + i) * swing))
        col = GOLD if i % 2 == 0 else (0.85, 0.88, 0.92)
        line(ctx, pts, darker(col, 0.8), 6)
        line(ctx, pts, col, 4)
        for j in range(0, 30, 2):
            px, py = pts[j]
            sx = 2 * math.sin(t * 7 + j + i) * (0.4 + swing)
            line(ctx, [(px, py), (px + sx, py + 18 + (j % 3) * 5)], col, 1.4, alpha=0.9)
    # gefaltete Kugeln
    orn = [(-50, 300, RED), (55, 360, GOLD), (-100, 520, GREEN_L), (90, 500, RED), (0, 450, WHITE), (-150, 700, GOLD), (140, 680, RED_L),
           (-40, 640, RED), (60, 820, GOLD), (-170, 880, RED), (180, 860, GREEN_L), (-80, 920, WHITE)]
    for i, (dx, dy, col) in enumerate(orn):
        a = swing * 0.35 * math.sin(t * 3.1 + i * 1.7)
        ox, oy = cx + dx, dy
        L = 26
        bx, by = ox + math.sin(a) * L, oy + math.cos(a) * L
        line(ctx, [(ox, oy), (bx, by)], GOLD_D, 1.2)
        folded_ball(ctx, bx, by + 22, 22, col, a, seed=8950 + i)
    # Stern oben
    piece2(ctx, star_pts(cx, 18, 52, 22), GOLD, GOLD_D, (cx, -40), (cx, 80), seed=8990, u=1, shadow=1.0, amp=0.1)


def folded_ball(ctx, x, y, r, col, rot, seed):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    p = piece(ctx, ellipse_pts(0, 0, r, r, n=30), col, seed=seed, u=0.6, shadow=0.9, amp=0.08)
    ctx.save()
    path(ctx, p)
    ctx.clip()
    for i in range(6):
        xa = -r + i * r / 3
        ctx.rectangle(xa, -r, r / 3, 2 * r)
        ctx.set_source_rgba(*(darker(col, 0.82) if i % 2 else mix(col, (1, 1, 1), 0.18)), 0.8)
        ctx.fill()
    for i in range(1, 6):
        xa = -r + i * r / 3
        line(ctx, [(xa * 0.6, -r), (xa, 0), (xa * 0.6, r)], darker(col, 0.7), 0.6, alpha=0.6)
    ctx.restore()
    piece(ctx, rect_pts(-5, -r - 5, 10, 7), GOLD_D, seed=seed + 50, u=0.4, shadow=0.3, amp=0.05)
    ctx.restore()


def furniture_layer(ctx, t, st):
    fireplace(ctx, t, st)
    sofa_back(ctx, t, st)
    tree(ctx, t, st)
    basket(ctx, t, st, front=False)


# ------------------------------------------------------------------ Vordergrund (Parallax)
def foreground_props(ctx, t, st):
    """Geschenke, Stuhlbein, Pflanze – große, dunkle Papierschichten nah an der Kamera."""
    for i, (x, kind) in enumerate(((620, 'gift'), (1250, 'leg'), (1850, 'gift2'), (2650, 'gift2'), (3350, 'gift'), (4150, 'leg'))):
        y = FLOOR + 175
        if kind == 'gift':
            soft2(ctx, [(x - 90, y), (x - 90, y - 130), (x + 90, y - 130), (x + 90, y)], GREEN, GREEN_D, (x, y - 200), (x, y + 50), seed=9000 + i, u=2, n=2)
            piece(ctx, rect_pts(x - 14, y - 130, 28, 130), GOLD, seed=9010 + i, u=2, shadow=0.4, amp=0.1)
            soft(ctx, [(x, y - 130), (x - 50, y - 175), (x - 40, y - 135)], GOLD_D, seed=9020 + i, u=2, n=3)
            soft(ctx, [(x, y - 130), (x + 50, y - 175), (x + 40, y - 135)], GOLD, seed=9030 + i, u=2, n=3)
        elif kind == 'gift2':
            soft2(ctx, [(x - 70, y), (x - 70, y - 100), (x + 70, y - 100), (x + 70, y)], RED, RED_D, (x, y - 200), (x, y + 50), seed=9040 + i, u=2, n=2)
            piece(ctx, rect_pts(x - 70, y - 62, 140, 22), WHITE, seed=9050 + i, u=2, shadow=0.4, amp=0.1)
        elif kind == 'leg':
            soft2(ctx, [(x - 15, -300), (x + 15, -300), (x + 12, y), (x - 12, y)], WOOD, WOOD_D, (x, -300), (x, y), seed=9060 + i, u=2, n=2)
        else:
            soft2(ctx, [(x - 70, y), (x - 80, y - 110), (x + 80, y - 110), (x + 70, y)], RED_L, RED, (x, y - 200), (x, y + 50), seed=9070 + i, u=2, n=2)
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.33 + 0.05 * math.sin(t * 2 + k)
                ctx.save()
                ctx.translate(x, y - 110)
                ctx.rotate(a)
                soft2(ctx, [(0, -10), (120, -24), (190, 0), (120, 22), (0, 10)], GREEN_L, GREEN, (0, 0), (200, 0), seed=9080 + k, u=2, n=4)
                ctx.restore()


# ------------------------------------------------------------------ Wichtelstube
def gnome_room(ctx, t, st):
    """Stube hinter der Fußleiste (eigene Koordinaten, Boden y=300)."""
    u = 0.6
    ctx.rectangle(-400, -400, 1200, 800)
    ctx.set_source_rgb(0.86, 0.66, 0.44)
    ctx.fill()
    x = -400
    i = 0
    while x < 800:
        ctx.rectangle(x, -400, 40, 700)
        ctx.set_source_rgb(*((0.86, 0.66, 0.44) if i % 2 == 0 else (0.80, 0.60, 0.39)))
        ctx.fill()
        x += 40
        i += 1
    for k in range(60):
        gx = -380 + (k % 15) * 55 + ((k // 15) % 2) * 27
        gy = -60 + (k // 15) * 75
        emboss(ctx, star_pts(gx, gy, 6, 2.6), (0.86, 0.66, 0.44) if (k % 2) else (0.80, 0.60, 0.39), u=0.5, depth=1)
    # Holzboden + Gewölbe-Rand
    soft2(ctx, [(-400, 300), (800, 300), (800, 500), (-400, 500)], WOOD, WOOD_D, (0, 250), (0, 500), seed=9100, u=1, n=2)
    for i in range(10):
        line(ctx, [(-400, 300 + i * 12 + i * i), (800, 300 + i * 12 + i * i)], WOOD_D, 1, alpha=0.5)
    # Regal mit Spulen und Büchlein
    soft2(ctx, [(30, 120), (240, 120), (240, 128), (30, 128)], WOOD_L, WOOD, (100, 100), (100, 140), seed=9110, u=u, n=2)
    for i, (bx, bw, bh, col) in enumerate(((40, 10, 28, RED), (52, 8, 24, GREEN), (62, 11, 30, GOLD_D), (76, 9, 22, BLUE_D))):
        soft(ctx, [(bx, 120), (bx + bw, 120), (bx + bw, 120 - bh), (bx, 120 - bh)], col, seed=9111 + i, u=u, n=2, shadow=0.5)
    for i, sx in enumerate((120, 150, 180)):
        soft2(ctx, [(sx - 9, 120), (sx + 9, 120), (sx + 7, 98), (sx - 7, 98)], WOOD_L, WOOD, (sx, 90), (sx, 125), seed=9120 + i, u=u, n=2)
        piece(ctx, rect_pts(sx - 6, 102, 12, 14), [RED, GREEN_L, WHITE][i], seed=9125 + i, u=u, shadow=0.3, amp=0.1)
    dot(ctx, 215, 112, 8, GOLD)
    # Bildchen: Herz
    piece(ctx, rect_pts(-150, 40, 60, 70), WOOD_L, seed=9130, u=u, shadow=1, amp=0.1)
    piece(ctx, rect_pts(-143, 47, 46, 56), CREAM, seed=9131, u=u, shadow=0.3, amp=0.1)
    emboss(ctx, heart_pts(-120, 72, 16), RED_L, u=0.5)
    # Pult (schräg) + Hocker
    soft2(ctx, [(150, 300), (156, 246), (162, 246), (158, 300)], WOOD_D, darker(WOOD_D, 0.85), (156, 230), (156, 320), seed=9140, u=u, n=2)
    soft2(ctx, [(232, 300), (229, 244), (235, 244), (240, 300)], WOOD_D, darker(WOOD_D, 0.85), (232, 230), (232, 320), seed=9141, u=u, n=2)
    soft2(ctx, [(140, 242), (246, 234), (248, 244), (142, 252)], WOOD_L, WOOD, (190, 220), (190, 260), seed=9142, u=u, n=2)
    soft2(ctx, [(262, 300), (264, 270), (290, 270), (292, 300)], RED, RED_D, (276, 260), (276, 310), seed=9143, u=u, n=2)
    # Tintenfass
    soft(ctx, [(146, 244), (147, 234), (157, 234), (158, 243)], (0.2, 0.2, 0.3), seed=9150, u=u, n=2, shadow=0.6)
    piece(ctx, rect_pts(149, 231, 6, 4), GOLD_D, seed=9151, u=u, shadow=0.2, amp=0.05)


def kid_feet(ctx, x, y, k, t):
    """Pantoffeln des Kindes in der Tür (Schritte)."""
    for i, dx in enumerate((-40, 40)):
        lift = max(0, math.sin(t * 7 + i * math.pi)) * 10 * k
        soft2(ctx, [(x + dx - 50, y), (x + dx - 46, y - 32 - lift), (x + dx + 40, y - 36 - lift), (x + dx + 60, y - 14 - lift), (x + dx + 50, y)],
              RED, RED_D, (x + dx, y - 60), (x + dx, y + 10), seed=9200 + i, u=2, n=4)
        piece(ctx, ellipse_pts(x + dx + 20, y - 30 - lift, 16, 8), WHITE, seed=9210 + i, u=2, shadow=0.4, amp=0.6)
