"""Kulissen: Papierhaus außen, Zimmer innen (Fenster, Bett, Tisch, Adventskalender, Wichteltür)."""
import math
import cairo
import numpy as np
from paper import *
from characters import *

FLOOR = 1050.0
KF = 0.75          # Bodenverkürzung: y = FLOOR + KF*z
DOOR_X0, DOOR_X1 = 1560.0, 1606.0
DOOR_TOP = 976.0
NIGHT = (0.44, 0.51, 0.71)
DAYC = (1.0, 0.985, 0.955)


def fy(z):
    return FLOOR + KF * z


# ---------------------------------------------------------------- Schnee
def snow(ctx, t, x0, y0, x1, y1, n, seed, size=1.0, speed=1.0, alpha=1.0):
    r = np.random.RandomState(seed)
    xs = r.uniform(0, 1, n)
    ys = r.uniform(0, 1, n)
    sp = r.uniform(0.6, 1.4, n)
    sz = r.uniform(0.6, 1.3, n)
    ph = r.uniform(0, 6.28, n)
    H = y1 - y0
    W = x1 - x0
    for i in range(n):
        y = y0 + ((ys[i] * H + t * 38 * speed * sp[i]) % (H + 20)) - 10
        x = x0 + (xs[i] * W + math.sin(t * 0.9 * sp[i] + ph[i]) * 12 * size) % W
        rr = 3.2 * size * sz[i]
        dot(ctx, x + rr * 0.35, y + rr * 0.5, rr, (0.2, 0.2, 0.3), 0.12 * alpha)
        dot(ctx, x, y, rr, WHITE, 0.92 * alpha)


def tint(ctx, L, extra=None):
    c = mix(NIGHT, DAYC, L)
    if extra is not None:
        c = extra
    ctx.save()
    ctx.identity_matrix()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_rgb(*c)
    ctx.paint()
    ctx.restore()


def texture(ctx, tex, scale=2.2, alpha=1.0):
    pat = cairo.SurfacePattern(tex)
    pat.set_extend(cairo.EXTEND_REPEAT)
    pat.set_filter(cairo.FILTER_GOOD)
    pat.set_matrix(cairo.Matrix(xx=scale, yy=scale))
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source(pat)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def fir(ctx, x, y, h, seed, cols=(GREEN_L, GREEN), u=2.0, snowcap=False):
    """Papiertanne aus gestapelten, gefalzten Dreiecken."""
    tiers = 4
    for i in range(tiers):
        k = i / tiers
        w = h * (0.55 - 0.1 * k) * (1 - k * 0.55)
        top = y - h * (0.35 + 0.65 * (i + 1) / tiers) - h * 0.05
        bot = y - h * (0.12 + 0.62 * i / tiers)
        tri = np.array([(x, top), (x + w, bot), (x - w, bot)])
        piece2(ctx, tri, cols[0], cols[1], (x, top), (x + w * 0.1, bot), seed=seed + i, u=u)
        if snowcap:
            cap = np.array([(x, top), (x + w * 0.35, top + (bot - top) * 0.35), (x + w * 0.1, top + (bot - top) * 0.3),
                            (x - w * 0.15, top + (bot - top) * 0.38), (x - w * 0.35, top + (bot - top) * 0.35)])
            piece(ctx, cap, WHITE, seed=seed + 10 + i, u=u, shadow=0.3)
    piece(ctx, rect_pts(x - h * 0.05, y - h * 0.13, h * 0.1, h * 0.13), WOOD_D, seed=seed + 20, u=u)


# ====================================================================== Außen
def exterior(ctx, t, glow_amt=1.0):
    u = 2.0
    g = cairo.LinearGradient(0, 0, 0, 900)
    g.add_color_stop_rgb(0, 0.16, 0.20, 0.31)
    g.add_color_stop_rgb(1, 0.33, 0.39, 0.52)
    ctx.set_source(g)
    ctx.rectangle(-400, -400, 2800, 1900)
    ctx.fill()
    # Sterne
    r = np.random.RandomState(4)
    for i in range(40):
        x, y = r.uniform(-200, 2100), r.uniform(-100, 520)
        s = r.uniform(3, 7)
        tw = 0.6 + 0.4 * math.sin(t * 2.0 + i)
        piece(ctx, star_pts(x, y, s, s * 0.42, 4), (0.97, 0.92, 0.75), seed=500 + i, u=0.5, shadow=0, amp=0.2,
              alpha=tw, outline=False)
    # Mond
    piece2(ctx, ellipse_pts(1620, 190, 70, 70), (0.98, 0.95, 0.83), (0.92, 0.88, 0.74), (1650, 100), (1600, 280), seed=520, u=u)
    for (dx, dy, rr) in ((-20, -15, 11), (18, 22, 8), (25, -25, 6)):
        dot(ctx, 1620 + dx, 190 + dy, rr, (0.88, 0.84, 0.70), 0.7)
    # Hügel
    for j, (yb, col, sd) in enumerate(((760, (0.74, 0.79, 0.88), 530), (820, (0.84, 0.88, 0.94), 531))):
        pts = [(-400, 1300)]
        for x in np.linspace(-400, 2400, 40):
            pts.append((x, yb - 60 * math.sin(x * 0.003 + j * 2) - 30 * math.sin(x * 0.008 + j)))
        pts.append((2400, 1300))
        piece(ctx, np.array(pts), col, seed=sd, u=u * 2, shadow=1.5)
    for i, (x, h) in enumerate(((180, 300), (330, 380), (1500, 340), (1700, 420), (1860, 280), (60, 240))):
        fir(ctx, x, 830 + (i % 2) * 20, h, 540 + i * 30, (GREEN, GREEN_D), u=u, snowcap=True)
    # Haus
    wall = np.array([(690, 470), (1310, 470), (1310, 905), (690, 905)])
    piece2(ctx, wall, CREAM, CREAM2, (1000, 300), (1000, 1000), seed=560, u=u, shadow=2)
    # Fensterläden etc.
    for (wx, wy, lit) in ((760, 560, 0), (1110, 560, 1)):
        fr = rect_pts(wx - 10, wy - 10, 150, 160)
        piece(ctx, fr, WHITE, seed=561 + wx, u=u)
        g2 = cairo.LinearGradient(0, wy, 0, wy + 140)
        if lit:
            g2.add_color_stop_rgb(0, 0.98, 0.78, 0.46)
            g2.add_color_stop_rgb(1, 0.95, 0.62, 0.35)
        else:
            g2.add_color_stop_rgb(0, 0.42, 0.46, 0.58)
            g2.add_color_stop_rgb(1, 0.32, 0.36, 0.48)
        ctx.set_source(g2)
        ctx.rectangle(wx, wy, 130, 140)
        ctx.fill()
        line(ctx, [(wx + 65, wy), (wx + 65, wy + 140)], WHITE, 8, cap=0)
        line(ctx, [(wx, wy + 70), (wx + 130, wy + 70)], WHITE, 8, cap=0)
        piece(ctx, rect_pts(wx - 22, wy + 145, 174, 16), WHITE, seed=565 + wx, u=u)
        piece(ctx, np.array([(wx - 20, wy + 148), (wx + 152, wy + 148), (wx + 140, wy + 140), (wx - 8, wy + 140)]),
              WHITE, seed=567 + wx, u=u, shadow=0.5, amp=1.0)
    # Tür
    door = np.vstack([[(955, 905)], ellipse_pts(1000, 790, 45, 45, a0=math.pi, a1=2 * math.pi, n=20), [(1045, 905)]])
    piece2(ctx, door, GREEN_L, GREEN, (1000, 700), (1000, 950), seed=570, u=u)
    dot(ctx, 1030, 850, 5, GOLD)
    # Kranz
    piece(ctx, ellipse_pts(1000, 770, 22, 22), GREEN_D, seed=571, u=u)
    dot(ctx, 1000, 770, 11, GREEN)
    dot(ctx, 1000, 789, 5, RED)
    # Dach: zwei gefalzte Flächen
    roofL = np.array([(1000, 205), (640, 500), (1000, 500)])
    roofR = np.array([(1000, 205), (1360, 500), (1000, 500)])
    roof = np.array([(1000, 200), (1370, 505), (630, 505)])
    piece2(ctx, roof, RED_L, RED_D, (1000, 200), (1000, 520), seed=572, u=u, shadow=2.2)
    # Schnee auf dem Dach
    sn = [(1000, 194)]
    for x in np.linspace(1000, 1385, 10):
        sn.append((x, 194 + (x - 1000) * 0.83 - 6))
    sn.append((1380, 520))
    for x in np.linspace(1380, 620, 18):
        yy = 194 + abs(x - 1000) * 0.83 + 12 + 10 * math.sin(x * 0.05)
        sn.append((x, yy))
    sn.append((620, 520))
    piece(ctx, np.array(sn[:1] + [(x, 194 + (x - 1000) * 0.83 - 4) for x in np.linspace(1000, 1380, 10)] +
                        [(x, 194 + abs(x - 1000) * 0.83 + 22 + 8 * math.sin(x * 0.06)) for x in np.linspace(1380, 620, 24)] +
                        [(x, 194 + abs(x - 1000) * 0.83 - 4) for x in np.linspace(620, 1000, 10)]),
          WHITE, seed=573, u=u, shadow=1.2, amp=1.2)
    # Rundes Dachfenster
    piece(ctx, ellipse_pts(1000, 380, 42, 42), WHITE, seed=574, u=u)
    dot(ctx, 1000, 380, 32, (0.34, 0.38, 0.50))
    # Schornstein
    ch = np.array([(1150, 245), (1215, 245), (1215, 380), (1150, 330)])
    piece2(ctx, ch, RED, RED_D, (1185, 200), (1185, 400), seed=575, u=u)
    piece(ctx, rect_pts(1140, 232, 85, 20), WHITE, seed=576, u=u, amp=1.0)
    # Rauch aus Papier
    for i in range(3):
        k = ((t * 0.35 + i / 3) % 1.0)
        dot(ctx, 1185 + math.sin(k * 6 + i) * 18 + k * 40, 220 - k * 180, 14 + 20 * k, (0.80, 0.84, 0.92), 0.7 * (1 - k))
    # Boden vorn
    pts = [(-400, 1300)] + [(x, 900 + 18 * math.sin(x * 0.006) + 10 * math.sin(x * 0.02)) for x in np.linspace(-400, 2400, 50)] + [(2400, 1300)]
    piece(ctx, np.array(pts), WHITE, seed=580, u=u * 2, shadow=2)
    fir(ctx, 520, 960, 330, 600, (GREEN_L, GREEN), u=u, snowcap=True)
    fir(ctx, 1460, 980, 300, 630, (GREEN_L, GREEN), u=u, snowcap=True)
    # Weg
    path_pts = np.array([(960, 905), (1040, 905), (1120, 1200), (880, 1200)])
    piece(ctx, path_pts, (0.88, 0.90, 0.95), seed=590, u=u, shadow=0.3)


def exterior_emissive(ctx, t, amt=1.0):
    fl = 0.92 + 0.08 * math.sin(t * 7) * math.sin(t * 3.1)
    glow(ctx, 1175, 630, 260, WARM, 0.35 * amt * fl)
    glow(ctx, 1175, 630, 110, (1.0, 0.8, 0.5), 0.25 * amt * fl)
    # durchscheinende Papierwand
    glow(ctx, 1000, 700, 520, (1.0, 0.62, 0.32), 0.10 * amt)
    glow(ctx, 1620, 190, 220, (0.9, 0.9, 1.0), 0.12)


# ====================================================================== Zimmer
CAL_ORDER = [7, 19, 2, 13, 22, 10, 16, 4, 11, 24, 1, 20, 9, 14, 21, 5, 17, 3, 12, 23, 8, 15, 6, 18]


def wall(ctx):
    u = 2.0
    ctx.rectangle(-200, -200, 3000, FLOOR + 200)
    ctx.set_source_rgb(*CREAM)
    ctx.fill()
    # Ziehharmonika-Falzung der Papierwand
    pw = 96
    x = -200
    i = 0
    while x < 2800:
        a = CREAM if i % 2 == 0 else mix(CREAM, CREAM2, 0.75)
        ctx.rectangle(x, -200, pw, FLOOR + 200)
        ctx.set_source_rgb(*a)
        ctx.fill()
        line(ctx, [(x, -200), (x, FLOOR)], darker(CREAM2, 0.93), 0.8, alpha=0.6, cap=0)
        x += pw
        i += 1
    # zarte Sternchen-Tapete
    r = np.random.RandomState(9)
    for k in range(70):
        sx, sy = r.uniform(-150, 2750), r.uniform(-100, 940)
        piece(ctx, star_pts(sx, sy, 7, 3, 5, rot=r.uniform(0, 1)), mix(CREAM2, PINK, 0.35), seed=900 + k, u=0.6,
              shadow=0, amp=0.2, outline=False, alpha=0.7)


def window(ctx, t, L, sock=0.0, sock_t=0.0):
    u = 2.0
    x0, y0, x1, y1 = 1000, 260, 1400, 700
    sky_top = mix((0.20, 0.25, 0.36), (0.66, 0.80, 0.93), L)
    sky_bot = mix((0.31, 0.37, 0.50), (0.99, 0.88, 0.78), L)
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *sky_top)
    g.add_color_stop_rgb(1, *sky_bot)
    ctx.set_source(g)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.fill()
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    # Landschaft draußen
    hill = [(x0 - 20, y1 + 10)] + [(x, 610 - 25 * math.sin(x * 0.012)) for x in np.linspace(x0 - 20, x1 + 20, 16)] + [(x1 + 20, y1 + 10)]
    piece(ctx, np.array(hill), mix((0.70, 0.76, 0.86), (0.97, 0.96, 0.98), L), seed=950, u=u, shadow=1)
    for i, (fx, fh) in enumerate(((1060, 130), (1130, 90), (1300, 150), (1360, 100))):
        fir(ctx, fx, 640, fh, 960 + i * 7, (mix(GREEN_D, GREEN, L), mix((0.08, 0.22, 0.17), GREEN_D, L)), u=1.2,
            snowcap=True)
    snow(ctx, t, x0, y0, x1, y1, 55, 7, 1.0, 1.0)
    ctx.restore()
    # Rahmen
    for p in (rect_pts(x0 - 18, y0 - 18, x1 - x0 + 36, 22), rect_pts(x0 - 18, y1 - 4, x1 - x0 + 36, 22),
              rect_pts(x0 - 18, y0 - 18, 22, y1 - y0 + 36), rect_pts(x1 - 4, y0 - 18, 22, y1 - y0 + 36)):
        piece(ctx, p, WHITE, seed=int(p[0, 0] + p[0, 1]), u=u, shadow=1.2)
    piece(ctx, rect_pts(1194, y0, 12, y1 - y0), WHITE, seed=971, u=u)
    piece(ctx, rect_pts(x0, 474, x1 - x0, 12), WHITE, seed=972, u=u)
    # Fensterbank
    piece2(ctx, np.array([(975, 700), (1425, 700), (1440, 725), (960, 725)]), WHITE, WHITE2, (900, 712), (1500, 712),
           seed=973, u=u, shadow=1.5)
    # Riegel
    piece(ctx, ellipse_pts(1200, 480, 7, 7), GOLD, seed=974, u=u * 0.5)
    # Vorhänge (gefältelt)
    for side in (-1, 1):
        cx = 1000 - 30 if side < 0 else 1400 + 30
        folds = 5
        for f in range(folds):
            w = 22
            xa = cx + side * (f - folds / 2) * w * 0.9
            col = PINK if f % 2 == 0 else PINK_D
            pts = np.array([(xa - w / 2, 220), (xa + w / 2, 220), (xa + w / 2 + side * 6, 560), (xa + w / 2 - side * 4, 760),
                            (xa - w / 2 - side * 4, 760), (xa - w / 2 + side * 6, 560)])
            piece(ctx, pts, col, seed=980 + f + (side + 1) * 10, u=u, shadow=0.8)
        piece(ctx, rect_pts(cx - 60, 530, 120, 18), RED, seed=995 + side, u=u)
    piece(ctx, rect_pts(930, 206, 540, 18), WOOD_D, seed=999, u=u, shadow=1.5)
    # umgedrehte Socke am Riegel
    if sock > 0:
        sw = math.sin(sock_t * 3.2) * 0.12 * (1 - min(1, sock_t * 0.3)) + 0.04
        ctx.save()
        ctx.translate(1244, 640)
        piece(ctx, rect_pts(-4, -10, 8, 16), WOOD_L, seed=1003, u=0.5, shadow=0.4)
        ctx.translate(0, 4)
        ctx.rotate(sw)
        ctx.scale(0.55, 0.55 * smooth(sock))
        sk = np.array([(-11, 0), (11, 0), (12, 62), (26, 74), (30, 88), (18, 96), (-4, 92), (-12, 80)])
        inside = (0.93, 0.80, 0.78)
        piece2(ctx, sk, inside, mix(inside, PINK_D, 0.5), (0, -10), (8, 100), seed=1001, u=0.8, amp=0.9)
        # Nähte und Fusseln -> 'auf links'
        ctx.set_dash([3, 2.5])
        line(ctx, [(-10, 6), (-10, 78), (-2, 90), (18, 94)], (0.72, 0.42, 0.42), 1.2)
        line(ctx, [(10, 6), (11, 62), (26, 76)], (0.72, 0.42, 0.42), 1.2)
        ctx.set_dash([])
        piece(ctx, rect_pts(-12, -2, 24, 10), (0.88, 0.70, 0.68), seed=1002, u=0.8, shadow=0.3)
        for k in range(6):
            line(ctx, [(-9 + k * 3.6, 9), (-9 + k * 3.6, 18)], (0.85, 0.62, 0.60), 0.9)
        ctx.restore()


def lantern(ctx, t, x=640):
    u = 2.0
    sw = math.sin(t * 0.8) * 0.02
    ctx.save()
    ctx.translate(x, -60)
    ctx.rotate(sw)
    line(ctx, [(0, 0), (0, 200)], INK, 1.4)
    cy, rx, ry = 270, 74, 66
    bands = 9
    for i in range(bands):
        a0 = -math.pi / 2 + math.pi * i / bands
        a1 = -math.pi / 2 + math.pi * (i + 1) / bands
        ya, yb = cy + ry * math.sin(a0), cy + ry * math.sin(a1)
        wa, wb = rx * math.cos(a0), rx * math.cos(a1)
        p = np.array([(-wa, ya), (wa, ya), (wb, yb), (-wb, yb)])
        piece(ctx, p, RED_L if i % 2 == 0 else RED, seed=1100 + i, u=u, shadow=0.4 if i == bands - 1 else 0, amp=0.3)
    piece(ctx, rect_pts(-30, cy - ry - 10, 60, 14), GOLD_D, seed=1110, u=u)
    piece(ctx, rect_pts(-30, cy + ry - 4, 60, 14), GOLD_D, seed=1111, u=u)
    line(ctx, [(0, cy + ry + 10), (0, cy + ry + 40)], RED_D, 3)
    piece(ctx, ellipse_pts(0, cy + ry + 44, 7, 9), RED_D, seed=1112, u=0.6, amp=0.4)
    ctx.restore()


def wall_drawing(ctx):
    """Das Bild des Kindes an der Wand über dem Bett."""
    u = 1.5
    x, y, w, h = 300, 430, 170, 130
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate(-0.04)
    ctx.translate(-w / 2, -h / 2)
    piece(ctx, rect_pts(0, 0, w, h), WHITE, seed=1200, u=u, shadow=1.5)
    crayon_drawing(ctx, 0, 0, w, h, 1.0)
    for tx in (14, w - 14):
        piece(ctx, rot_pts(rect_pts(tx - 14, -8, 28, 14), 0.3 if tx < 50 else -0.3, tx, -1), (0.95, 0.93, 0.75),
              seed=1201 + tx, u=u * 0.5, shadow=0.2, alpha=0.85)
    ctx.restore()


def crayon_drawing(ctx, x, y, w, h, lw):
    """Kinderzeichnung: Sonne, Haus, Kind, Hund – als Wachsmalstrich."""
    def P(px, py):
        return (x + px * w, y + py * h)
    k = lw * w / 170
    # Sonne
    ctx.save()
    sx, sy = P(0.8, 0.22)
    for i in range(9):
        a = i * 0.7
        line(ctx, [(sx + math.cos(a) * 15 * k, sy + math.sin(a) * 15 * k), (sx + math.cos(a) * 24 * k, sy + math.sin(a) * 24 * k)], YELLOW_D, 3.2 * k)
    dot(ctx, sx, sy, 11 * k, YELLOW_D)
    ctx.restore()
    # Haus
    line(ctx, [P(0.1, 0.85), P(0.1, 0.5), P(0.38, 0.5), P(0.38, 0.85), P(0.1, 0.85)], RED, 3.4 * k)
    line(ctx, [P(0.06, 0.52), P(0.24, 0.28), P(0.42, 0.52)], RED_D, 3.4 * k)
    line(ctx, [P(0.2, 0.85), P(0.2, 0.68), P(0.28, 0.68), P(0.28, 0.85)], BROWN, 2.6 * k)
    # Kind
    cx, cy = P(0.56, 0.5)
    ctx.new_path()
    ctx.arc(cx, cy, 8 * k, 0, 6.3)
    ctx.set_source_rgb(*BLUE_D)
    ctx.set_line_width(2.6 * k)
    ctx.stroke()
    line(ctx, [P(0.56, 0.56), P(0.56, 0.74)], BLUE_D, 2.6 * k)
    line(ctx, [P(0.47, 0.62), P(0.65, 0.6)], BLUE_D, 2.6 * k)
    line(ctx, [P(0.5, 0.86), P(0.56, 0.74), P(0.62, 0.86)], BLUE_D, 2.6 * k)
    # Hund
    line(ctx, [P(0.7, 0.8), P(0.72, 0.7), P(0.86, 0.7), P(0.88, 0.8)], BROWN, 3 * k)
    dot(ctx, *P(0.9, 0.66), 6 * k, BROWN)
    line(ctx, [P(0.72, 0.7), P(0.68, 0.64)], BROWN, 2.4 * k)
    # Gras
    line(ctx, [P(0.02, 0.92)] + [P(0.04 + 0.06 * i, 0.88 if i % 2 else 0.93) for i in range(16)], GREEN_L, 2.4 * k)


def bed(ctx, t, state='sleep', breathe=0.0, blink=False, joy=0.3):
    u = 2.0
    # Kopfteil mit Herz
    hb = np.vstack([[(140, FLOOR)], ellipse_pts(172, 720, 34, 40, a0=math.pi, a1=2 * math.pi, n=16), [(206, FLOOR)]])
    piece2(ctx, hb, RED_L, RED, (172, 600), (172, 1100), seed=1300, u=u)
    hrt = []
    for a in np.linspace(0, 2 * math.pi, 30):
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        hrt.append((172 + hx * 1.1, 775 + hy * 1.1))
    piece(ctx, np.array(hrt), PINK, seed=1301, u=u * 0.6, shadow=-0.5)
    # Fußteil
    fb = np.vstack([[(770, FLOOR)], ellipse_pts(796, 860, 26, 28, a0=math.pi, a1=2 * math.pi, n=14), [(822, FLOOR)]])
    piece2(ctx, fb, RED_L, RED, (796, 800), (796, 1100), seed=1302, u=u)
    # Matratze
    piece(ctx, rect_pts(196, 900, 584, 44), WHITE, seed=1303, u=u)
    piece2(ctx, rect_pts(190, 940, 596, 52), RED, RED_D, (190, 960), (800, 960), seed=1304, u=u)
    for lx in (210, 750):
        piece(ctx, rect_pts(lx, 990, 22, FLOOR - 990), RED_D, seed=1305 + lx, u=u)
    # Kopfkissen
    piece2(ctx, ellipse_pts(285, 885, 78, 26), WHITE, WHITE2, (220, 880), (360, 880), seed=1310, u=u)
    if state == 'sleep':
        child_head(ctx, 292, 848, 46, 0.2, sleep=True, u=1.4, tilt=-0.35)
        hump = 1 + 0.04 * breathe
        top = []
        for x in np.linspace(330, 785, 24):
            k = (x - 330) / 455
            hh = 42 * math.sin(clamp(k * 1.25) * math.pi) ** 0.8 * hump + 8
            top.append((x, 906 - hh))
        bl = np.array(top + [(800, 960), (318, 960), (318, 880)])
        p = piece(ctx, bl, PINK, seed=1320, u=u)
        _patch(ctx, p)
        piece(ctx, np.array([(318, 868), (340, 862), (352, 960), (318, 960)]), CREAM, seed=1321, u=u, shadow=0.6)
        # Zzz als Papierschnipsel? Nein: kleine Sternchen über dem Kopf
    else:
        bl = np.array([(560, 900), (640, 880), (720, 878), (800, 890), (800, 960), (560, 960)])
        p = piece(ctx, bl, PINK, seed=1322, u=u)
        _patch(ctx, p)
        piece(ctx, np.array([(545, 893), (575, 880), (590, 960), (548, 960)]), CREAM, seed=1323, u=u, shadow=0.6)


def _patch(ctx, poly):
    ctx.save()
    path(ctx, poly)
    ctx.clip()
    cols = [PINK, MINT, YELLOW, LILAC, BLUE_L, PINK_D]
    r = np.random.RandomState(13)
    for i in range(10):
        for j in range(3):
            x = 300 + i * 52
            y = 830 + j * 52
            c = cols[(i * 2 + j) % len(cols)]
            tri = np.array([(x, y), (x + 52, y), (x, y + 52)]) if (i + j) % 2 else np.array([(x + 52, y), (x + 52, y + 52), (x, y + 52)])
            path(ctx, tri)
            ctx.set_source_rgb(*c)
            ctx.fill()
    for i in range(11):
        line(ctx, [(300 + i * 52, 800), (300 + i * 52, 1000)], CREAM, 1.6, alpha=0.7)
    ctx.restore()


def dog_basket(ctx, t, awake=False):
    u = 2.0
    piece2(ctx, ellipse_pts(915, fy(40), 95, 30), WOOD_L, WOOD, (915, 900), (915, 1200), seed=1400, u=u)
    br = 1 + 0.03 * math.sin(t * 2.2)
    # schlafender Hund (Papier)
    body = ellipse_pts(915, fy(30) - 22 * br, 70, 30 * br)
    piece2(ctx, body, (0.90, 0.75, 0.55), (0.82, 0.64, 0.45), (915, 950), (930, 1150), seed=1401, u=u)
    piece(ctx, ellipse_pts(865, fy(30) - 30, 30, 25), (0.90, 0.75, 0.55), seed=1402, u=u)
    piece(ctx, ellipse_pts(852, fy(30) - 36, 16, 26, rot=0.5), (0.55, 0.36, 0.22), seed=1403, u=u)
    if awake:
        dot(ctx, 878, fy(30) - 36, 3.6, INK)
    else:
        arc_stroke(ctx, 878, fy(30) - 38, 4, 0.2, 2.9, INK, 1.6)
    dot(ctx, 893, fy(30) - 26, 4, INK)
    piece(ctx, ellipse_pts(976, fy(30) - 18, 22, 10, rot=-0.3), (0.82, 0.64, 0.45), seed=1404, u=u)
    piece2(ctx, np.array([(820, fy(40) - 6), (1010, fy(40) - 6), (990, fy(40) + 26), (840, fy(40) + 26)]), WOOD, WOOD_D,
           (915, 1000), (915, 1200), seed=1405, u=u)


def calendar(ctx, dayf, shake=0.0):
    u = 1.6
    x0, y0 = 1880, 170
    line(ctx, [(x0 + 30, y0 + 4), (2120, 118), (x0 + 450, y0 + 4)], INK, 1.6)
    dot(ctx, 2120, 118, 4, GOLD_D)
    piece2(ctx, rect_pts(x0, y0, 480, 350), RED, RED_D, (x0 + 240, y0 - 10), (x0 + 240, y0 + 400), seed=1500, u=u, shadow=2)
    piece(ctx, rect_pts(x0 + 8, y0 + 8, 464, 334), GREEN, seed=1501, u=u, shadow=0.3)
    for idx in range(24):
        n = CAL_ORDER[idx]
        c, r = idx % 6, idx // 6
        dx, dy = x0 + 24 + c * 74, y0 + 22 + r * 81
        w, h = 62, 70
        o = clamp(dayf - (n - 1))
        # Fach
        piece(ctx, rect_pts(dx, dy, w, h), (0.25, 0.14, 0.12), seed=1510 + n, u=u * 0.5, shadow=0, amp=0.2)
        if o > 0.05:
            ic = (n % 4)
            cx, cy = dx + w / 2, dy + h / 2
            if n == 24:
                piece(ctx, star_pts(cx, cy, 24, 10), GOLD, seed=1540, u=0.6, shadow=0.4)
            elif ic == 0:
                piece(ctx, star_pts(cx, cy, 16, 7), YELLOW, seed=1541 + n, u=0.6, shadow=0.4)
            elif ic == 1:
                piece(ctx, np.array([(cx, cy - 18), (cx + 14, cy + 12), (cx - 14, cy + 12)]), GREEN_L, seed=1541 + n, u=0.6, shadow=0.4)
            elif ic == 2:
                hrt = [(cx + 0.9 * 16 * math.sin(a) ** 3, cy - 0.9 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
                       for a in np.linspace(0, 6.28, 26)]
                piece(ctx, np.array(hrt), PINK_D, seed=1541 + n, u=0.6, shadow=0.4)
            else:
                piece(ctx, ellipse_pts(cx, cy, 13, 13), (0.86, 0.66, 0.40), seed=1541 + n, u=0.6, shadow=0.4)
        # Türchen dreht sich um linkes Scharnier
        ang = o * 1.9
        ww = w * math.cos(ang)
        col = GOLD if n == 24 else CREAM
        if ww >= 0:
            d = np.array([(dx, dy), (dx + ww, dy - 4 * math.sin(ang)), (dx + ww, dy + h + 4 * math.sin(ang)), (dx, dy + h)])
            piece(ctx, d, col if o < 0.5 else darker(col, 0.9), seed=1570 + n, u=u * 0.5, shadow=0.6, amp=0.3)
            if ww > 20:
                ctx.save()
                ctx.translate(dx + ww / 2, dy + h / 2 + 4)
                ctx.scale(max(0.05, ww / w), 1)
                ctx.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(30)
                s = str(n)
                ext = ctx.text_extents(s)
                ctx.move_to(-ext.x_advance / 2, ext.height / 2 - 2)
                ctx.set_source_rgb(*(RED_D if n != 24 else RED_D))
                ctx.show_text(s)
                ctx.restore()
        else:
            d = np.array([(dx, dy), (dx + ww, dy - 4 * math.sin(ang)), (dx + ww, dy + h + 4 * math.sin(ang)), (dx, dy + h)])
            piece(ctx, d, darker(col, 0.82), seed=1570 + n, u=u * 0.5, shadow=0.6, amp=0.3)


def table(ctx, t, st):
    u = 2.0
    for lx in (1872, 2378):
        piece2(ctx, rect_pts(lx, 780, 26, FLOOR - 780), WOOD, WOOD_D, (lx + 13, 700), (lx + 13, 1100), seed=1600 + lx, u=u)
    piece(ctx, np.array([(1850, 745), (2420, 745), (2428, 762), (1842, 762)]), WOOD_L, seed=1603, u=u, shadow=0.4)
    piece(ctx, rect_pts(1842, 762, 586, 26), WOOD, seed=1604, u=u, shadow=1.5)
    # Läufer
    rn = [(2010, 746), (2250, 746), (2256, 762), (2256, 806)]
    for i in range(12):
        x = 2256 - (i + 1) * 20.5
        rn.append((x + 10, 816 if i % 2 == 0 else 806))
    rn.append((2004, 806))
    rn.append((2004, 762))
    piece(ctx, np.array(rn), RED, seed=1605, u=u, shadow=1.0)
    for x in np.linspace(2020, 2240, 12):
        line(ctx, [(x, 764), (x, 798)], RED_L, 1.2, alpha=0.6)
    # kleine Tanne im Topf
    fir(ctx, 2360, 742, 110, 1610, (GREEN_L, GREEN), u=1.2)
    piece2(ctx, np.array([(2336, 712), (2384, 712), (2378, 748), (2342, 748)]), RED_L, RED, (2360, 700), (2360, 760), seed=1620, u=1.2)
    # Mehlspuren
    fl = st.get('flour', 0.0)
    if fl > 0:
        nprint = 22
        for i in range(int(nprint * fl)):
            x = 1950 + i * 17
            side = 1 if i % 2 else -1
            y = 752 + side * 2.6
            dot(ctx, x, y, 3.0, WHITE, 0.95)
            dot(ctx, x + 3.6, y, 2.0, WHITE, 0.95)
        r = np.random.RandomState(3)
        for i in range(40):
            x = r.uniform(1940, 1950 + int(nprint * fl) * 17)
            dot(ctx, x, 748 + r.uniform(0, 12), r.uniform(0.5, 1.6), WHITE, 0.8)
    # Teller + Keks
    ck = st.get('cookie', None)
    if ck is not None:
        piece(ctx, ellipse_pts(2190, 753, 34, 7), WHITE, seed=1630, u=u, shadow=0.6)
        piece(ctx, ellipse_pts(2190, 752, 25, 4.6), WHITE2, seed=1631, u=u, shadow=0, amp=0.2)
        cx, cy = 2190, 731
        piece2(ctx, ellipse_pts(cx, cy, 20, 20), (0.90, 0.70, 0.44), (0.83, 0.61, 0.36), (cx + 4, cy - 30), (cx - 2, cy + 30),
               seed=1632, u=0.8, amp=0.8)
        for (dx, dy) in ((-8, -7), (7, -9), (-3, 6), (9, 5), (-11, 4)):
            dot(ctx, cx + dx, cy + dy, 2.0, (0.38, 0.22, 0.15))
        pr = st.get('cookie_print', 0.0)
        if pr > 0:
            hc = (0.62, 0.43, 0.26)
            ctx.save()
            ctx.translate(cx + 1, cy + 3)
            dot(ctx, 0, 0, 4.2, hc, pr)
            for i, a in enumerate((-2.3, -1.85, -1.5, -1.15, -0.4)):
                ln = 6.5 if i in (1, 2) else 5.6
                if i == 4:
                    ln = 5
                ctx.save()
                ctx.rotate(a + 1.57)
                ctx.scale(1, 1)
                ctx.rectangle(-1.1, -ln - 3, 2.2, ln)
                ctx.set_source_rgba(*hc, pr)
                ctx.fill()
                ctx.restore()
            ctx.restore()


def stack(ctx, n, pop=0.0):
    """Wachsender Stapel der Wichtelbriefe auf dem Tisch."""
    cols = [CREAM, (0.97, 0.88, 0.86), (0.90, 0.95, 0.90), (0.96, 0.93, 0.82), (0.92, 0.90, 0.97)]
    r = np.random.RandomState(21)
    offs = r.uniform(-5, 5, 30)
    rots = r.uniform(-0.05, 0.05, 30)
    for i in range(int(n)):
        y = 752 - i * 6.5
        k = 1.0
        dyp = 0
        if i == int(n) - 1 and pop > 0:
            dyp = -30 * (1 - smooth(pop))
        x = 1965 + offs[i]
        p = rot_pts(rect_pts(x - 40, y - 6.5 + dyp, 80, 6.5), rots[i], x, y)
        piece(ctx, p, cols[i % len(cols)], seed=1700 + i, u=1.0, shadow=0.6, amp=0.3)
        dot(ctx, x + 18, y - 3.2 + dyp, 2.0, RED, 0.9)


def baseboard(ctx):
    u = 2.0
    piece(ctx, np.array([(-200, 1000), (2800, 1000), (2800, FLOOR), (-200, FLOOR)]), GREEN, seed=1800, u=u, shadow=0.6, amp=0.3)
    piece(ctx, np.array([(-200, 996), (2800, 996), (2800, 1006), (-200, 1006)]), GREEN_L, seed=1801, u=u, shadow=0.3, amp=0.2)


def floor(ctx):
    u = 2.0
    ctx.rectangle(-200, FLOOR, 3000, 600)
    ctx.set_source_rgb(*WOOD)
    ctx.fill()
    y = FLOOR
    i = 0
    while y < 1700:
        hh = 26 + i * 7
        col = WOOD_L if i % 2 == 0 else mix(WOOD_L, WOOD, 0.5)
        piece(ctx, rect_pts(-200, y, 3000, hh), col, seed=1810 + i, u=u, shadow=0.3, amp=0.3)
        y += hh
        i += 1
    # runder Teppich
    piece2(ctx, ellipse_pts(1250, fy(190), 260, 46), MINT, mix(MINT, GREEN_L, 0.25), (1250, 1000), (1250, 1300), seed=1830, u=u)
    piece(ctx, ellipse_pts(1250, fy(190), 205, 34), CREAM, seed=1831, u=u, shadow=0.3)


def wichtel_door(ctx, o, inner_lit=0.0):
    """Winzige Tür in der Fußleiste. o: 0 zu .. 1 offen."""
    u = 0.6
    x0, x1, top = DOOR_X0, DOOR_X1, DOOR_TOP
    w = x1 - x0
    # Rahmen
    fr = np.vstack([[(x0 - 7, FLOOR)], ellipse_pts((x0 + x1) / 2, top + w / 2, w / 2 + 7, w / 2 + 7, a0=math.pi, a1=2 * math.pi, n=24), [(x1 + 7, FLOOR)]])
    piece2(ctx, fr, CREAM, CREAM3, ((x0 + x1) / 2, top - 20), ((x0 + x1) / 2, FLOOR), seed=1900, u=u, shadow=1.0)
    arch = np.vstack([[(x0, FLOOR)], ellipse_pts((x0 + x1) / 2, top + w / 2, w / 2, w / 2, a0=math.pi, a1=2 * math.pi, n=24), [(x1, FLOOR)]])
    # Innenraum
    path(ctx, arch)
    g = cairo.RadialGradient((x0 + x1) / 2, FLOOR - 20, 2, (x0 + x1) / 2, FLOOR - 20, 60)
    g.add_color_stop_rgb(0, *mix((0.30, 0.18, 0.12), (0.95, 0.70, 0.42), inner_lit))
    g.add_color_stop_rgb(1, *mix((0.22, 0.13, 0.09), (0.62, 0.34, 0.18), inner_lit))
    ctx.set_source(g)
    ctx.fill()
    if o > 0.02:
        ctx.save()
        path(ctx, arch)
        ctx.clip()
        for k in range(3):
            ctx.rectangle(x0 + 12 + k * 7, FLOOR - 7 - k * 6, w, 6)
            ctx.set_source_rgba(0.55, 0.32, 0.18, 0.7)
            ctx.fill()
        ctx.restore()
    ang = o * 1.75
    cw = math.cos(ang)
    leaf = arch.copy()
    leaf[:, 0] = x0 + (leaf[:, 0] - x0) * cw
    if o < 0.999:
        col = RED if cw > 0 else RED_D
        piece(ctx, leaf, col, seed=1901, u=u, shadow=0.5)
        if cw > 0.15:
            # Bretter
            for k in (0.33, 0.66):
                line(ctx, [(x0 + w * k * cw, top + 8), (x0 + w * k * cw, FLOOR - 2)], RED_D, 0.6)
            dot(ctx, x0 + w * 0.8 * cw, top + 44, 2.0, GOLD)
            # Rundfenster
            ctx.save()
            ctx.translate(x0 + w * 0.5 * cw, top + 18)
            ctx.scale(max(cw, 0.01), 1)
            dot(ctx, 0, 0, 7.5, CREAM)
            dot(ctx, 0, 0, 6, (0.30, 0.18, 0.12))
            line(ctx, [(-6, 0), (6, 0)], CREAM, 1.0)
            line(ctx, [(0, -6), (0, 6)], CREAM, 1.0)
            ctx.restore()
    return arch, leaf, cw


def door_emissive(ctx, o, lit, t, arch, cw):
    """Warmes Licht hinter / aus der Wichteltür."""
    if lit <= 0.001:
        return
    x0, x1, top = DOOR_X0, DOOR_X1, DOOR_TOP
    w = x1 - x0
    fl = 0.94 + 0.06 * math.sin(t * 9) * math.sin(t * 4.3)
    if o > 0.02:
        ctx.save()
        path(ctx, arch)
        ctx.clip()
        glow(ctx, (x0 + x1) / 2, FLOOR - 20, 70, (1.0, 0.75, 0.45), 0.22 * lit * fl)
        ctx.restore()
        # Lichtkegel auf dem Boden
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(0, FLOOR, 0, FLOOR + 70)
        g.add_color_stop_rgba(0, 1.0, 0.72, 0.40, 0.22 * lit * o * fl)
        g.add_color_stop_rgba(1, 1.0, 0.72, 0.40, 0.0)
        ctx.set_source(g)
        ctx.move_to(x0, FLOOR)
        ctx.line_to(x1, FLOOR)
        ctx.line_to(x1 + 60, FLOOR + 70)
        ctx.line_to(x0 - 40, FLOOR + 70)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    else:
        # geschlossen: Licht durch Ritzen, Rundfenster und Schlitz
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        ctx.set_source_rgba(1.0, 0.75, 0.42, 0.95 * lit * fl)
        ctx.new_path()
        ctx.arc((x0 + x1) / 2, top + 18, 6, 0, 2 * math.pi)
        ctx.fill()
        path(ctx, arch)
        ctx.set_line_width(1.6)
        ctx.stroke()
        ctx.rectangle(x0, FLOOR - 1.5, w, 1.5)
        ctx.fill()
        g = cairo.LinearGradient(0, FLOOR, 0, FLOOR + 30)
        g.add_color_stop_rgba(0, 1.0, 0.72, 0.40, 0.55 * lit * fl)
        g.add_color_stop_rgba(1, 1.0, 0.72, 0.40, 0.0)
        ctx.set_source(g)
        ctx.move_to(x0, FLOOR)
        ctx.line_to(x1, FLOOR)
        ctx.line_to(x1 + 30, FLOOR + 30)
        ctx.line_to(x0 - 30, FLOOR + 30)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    # durchscheinende Papierwand um die Tür
    glow(ctx, (x0 + x1) / 2, FLOOR - 30, 190, (1.0, 0.62, 0.30), 0.22 * lit * fl)
    glow(ctx, (x0 + x1) / 2, FLOOR - 20, 70, (1.0, 0.75, 0.45), 0.25 * lit * fl)


def room(ctx, t, st, tex):
    """Ganzes Zimmer. st: Zustandsdict; st['actors']: Liste callables(ctx) im Vordergrund;
    st['emissive']: Liste callables(ctx) nach der Tönung."""
    L = st.get('L', 0.0)
    wall(ctx)
    window(ctx, t, L, st.get('sock', 0.0), st.get('sock_t', 0.0))
    lantern(ctx, t)
    wall_drawing(ctx)
    calendar(ctx, st.get('dayf', 0.0))
    baseboard(ctx)
    arch, leaf, cw = wichtel_door(ctx, st.get('door', 0.0), st.get('door_lit', 0.0))
    floor(ctx)
    bed(ctx, t, st.get('bed', 'sleep'), breathe=math.sin(t * 1.8))
    dog_basket(ctx, t, awake=L > 0.5)
    table(ctx, t, st)
    stack(ctx, st.get('stack', 0), st.get('stack_pop', 0.0))
    for a in st.get('floor_items', []):
        a(ctx)
    for a in st.get('actors', []):
        a(ctx)
    texture(ctx, tex, 2.2)
    tint(ctx, L)
    # Licht
    if L > 0.01:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(1000, 300, 1500, 1300)
        g.add_color_stop_rgba(0, 1.0, 0.85, 0.6, 0.10 * L)
        g.add_color_stop_rgba(1, 1.0, 0.85, 0.6, 0.0)
        ctx.set_source(g)
        ctx.move_to(1000, 700)
        ctx.line_to(1400, 700)
        ctx.line_to(1800, 1460)
        ctx.line_to(1180, 1460)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    else:
        pass
    if L < 0.99:
        n = 1 - L
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(1000, 300, 1400, 1300)
        g.add_color_stop_rgba(0, 0.55, 0.65, 0.9, 0.10 * n)
        g.add_color_stop_rgba(1, 0.55, 0.65, 0.9, 0.0)
        ctx.set_source(g)
        ctx.move_to(1000, 700)
        ctx.line_to(1400, 700)
        ctx.line_to(1650, 1460)
        ctx.line_to(1150, 1460)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    door_emissive(ctx, st.get('door', 0.0), st.get('door_lit', 0.0), t, arch, cw)
    for e in st.get('emissive', []):
        e(ctx)
