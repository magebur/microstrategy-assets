"""Nahaufnahmen: Pop-up-Briefe beim Auffalten und die Endcard."""
import math
import cairo
import numpy as np
from paper import *
from characters import *
from sets import crayon_drawing, snow, texture

HINGE_Y = 862.0
FRONT_Y = 1052.0
HX0, HX1 = 330.0, 1010.0
DEPTH = 420.0
KP = (FRONT_Y - HINGE_Y) / DEPTH
BASE = (670.0, 925.0)


def insert_bg(ctx):
    u = 2.0
    ctx.rectangle(-100, -100, 2200, 1300)
    ctx.set_source_rgb(*CREAM)
    ctx.fill()
    x = -100
    i = 0
    while x < 2100:
        ctx.rectangle(x, -100, 170, 920)
        ctx.set_source_rgb(*(CREAM if i % 2 == 0 else mix(CREAM, CREAM2, 0.75)))
        ctx.fill()
        line(ctx, [(x, -100), (x, 820)], darker(CREAM2, 0.93), 1.2, alpha=0.6, cap=0)
        x += 170
        i += 1
    r = np.random.RandomState(19)
    for k in range(18):
        sx, sy = r.uniform(-50, 2000), r.uniform(-50, 760)
        piece(ctx, star_pts(sx, sy, 14, 6, 5, rot=r.uniform(0, 1)), mix(CREAM2, PINK, 0.35), seed=2900 + k, u=1.0,
              shadow=0, amp=0.2, outline=False, alpha=0.7)
    piece(ctx, np.array([(-100, 740), (2100, 740), (2100, 830), (-100, 830)]), GREEN, seed=2001, u=u, shadow=1, amp=0.4)
    piece(ctx, np.array([(-100, 734), (2100, 734), (2100, 752), (-100, 752)]), GREEN_L, seed=2002, u=u, shadow=0.4, amp=0.3)
    y = 830
    i = 0
    while y < 1200:
        hh = 70 + i * 25
        piece(ctx, rect_pts(-100, y, 2200, hh), WOOD_L if i % 2 == 0 else mix(WOOD_L, WOOD, 0.5), seed=2010 + i, u=u,
              shadow=0.4, amp=0.4)
        y += hh
        i += 1


def card_geom(a):
    ca, sa = math.cos(a), math.sin(a)
    yfree = HINGE_Y + DEPTH * (KP * ca - sa)
    spread = 50 * ca
    xl, xr = HX0 - spread, HX1 + spread
    return yfree, xl, xr


def _bpt(a, d, x):
    """Punkt auf der Rückwand: Abstand d vom Falz (0..DEPTH), x in Falz-Koordinate (HX0..HX1)."""
    ca, sa = math.cos(a), math.sin(a)
    y = HINGE_Y + d * (KP * ca - sa)
    cx = (HX0 + HX1) / 2
    xs = cx + (x - cx) * (1 + 50 / 340 * ca * d / DEPTH)
    return xs, y


def hand(ctx, x, y, side, seed):
    # Ärmel vom unteren Bildrand
    sx = x + (120 if side > 0 else -60)
    line(ctx, [(sx, 1200), (x + 6 * side, y + 20)], BLUE, 58)
    line(ctx, [(sx, 1200), (x + 6 * side, y + 20)], BLUE_L, 46)
    piece(ctx, ellipse_pts(x + 6 * side, y + 26, 34, 18), BLUE_D, seed=seed + 3, u=1.4)
    piece2(ctx, ellipse_pts(x, y, 38, 33), SKIN, SKIN_D, (x + 10, y - 50), (x + 6, y + 50), seed=seed, u=1.4)
    piece(ctx, ellipse_pts(x - 30 * side, y - 4, 13, 20, rot=0.5 * side), SKIN, seed=seed + 1, u=1.0)


def sparkle(ctx, x, y, s, a, col=(1.0, 0.92, 0.6)):
    if a <= 0 or s <= 0:
        return
    piece(ctx, star_pts(x, y, s, s * 0.32, 4), col, seed=int(x * 7 + y) % 9999, u=0.5, shadow=0.4, amp=0.2, alpha=a)


# ------------------------------------------------------------------ Pop-ups
def pop_layer(ctx, f, fn):
    if f <= 0.01:
        return
    ctx.save()
    ctx.translate(*BASE)
    ctx.scale(1.25, 1.25 * f)
    # Falzlasche am Fuß
    fn(ctx)
    ctx.restore()


def tab(ctx, x0, x1, col):
    piece(ctx, np.array([(x0, 0), (x1, 0), (x1 + 10, 14), (x0 - 10, 14)]), darker(col, 0.8), seed=int(x0) % 999 + 3000, u=1.0,
          shadow=0.3, amp=0.3)


def popup_dog(ctx, lt, fs):
    def grass(c):
        tab(c, -260, 260, GREEN_L)
        pts = [(-270, 0)]
        for i in range(27):
            pts.append((-270 + i * 20 + 10, -38 - (i % 3) * 8 if i % 2 == 0 else -14))
        pts.append((270, 0))
        piece2(c, np.array(pts), GREEN_L, GREEN, (0, -60), (0, 10), seed=3010, u=1.4)
        # Ball
        piece2(c, ellipse_pts(190, -42, 30, 30), RED_L, WHITE, (170, -80), (205, 0), seed=3011, u=1.0)

    def dogf(c):
        wag = math.sin(lt * 15) * 0.45
        dc, dd = (0.90, 0.75, 0.55), (0.82, 0.64, 0.45)
        # Schwanz
        c.save()
        c.translate(70, -70)
        c.rotate(-0.6 + wag)
        piece(c, np.array([(0, -8), (78, -14), (84, -2), (0, 10)]), dd, seed=3020, u=1.0)
        c.restore()
        piece2(c, ellipse_pts(0, -110, 92, 108), dc, dd, (14, -230), (22, 10), seed=3021, u=1.4)
        piece(c, ellipse_pts(-4, -100, 46, 70), CREAM, seed=3022, u=1.2, shadow=0.5)
        for px in (-42, 38):
            piece(c, ellipse_pts(px, -12, 30, 16), dc, seed=3023 + px, u=1.0)
        # Halsband
        piece(c, np.array([(-62, -188), (62, -188), (58, -170), (-58, -170)]), RED, seed=3025, u=1.0)
        piece(c, star_pts(0, -160, 14, 6), GOLD, seed=3026, u=0.6, shadow=0.4)
        # Kopf
        tilt = math.sin(lt * 2.5) * 0.08
        c.save()
        c.translate(0, -250)
        c.rotate(tilt)
        for side in (-1, 1):
            c.save()
            c.translate(side * 62, -40)
            c.rotate(side * (0.25 + 0.08 * math.sin(lt * 6 + side)))
            piece(c, np.array([(-18, -6), (18, -6), (24, 70), (0, 92), (-22, 70)]), (0.55, 0.36, 0.22), seed=3030 + side, u=1.2)
            c.restore()
        piece2(c, ellipse_pts(0, 0, 82, 78), dc, dd, (12, -90), (20, 90), seed=3032, u=1.4)
        piece(c, ellipse_pts(0, 30, 44, 32), CREAM, seed=3033, u=1.2, shadow=0.5)
        piece(c, ellipse_pts(0, 12, 16, 11), INK, seed=3034, u=0.6, shadow=0.3)
        piece(c, ellipse_pts(0, 58, 12, 15), (0.95, 0.52, 0.56), seed=3035, u=0.6, shadow=0.3)
        for sx in (-1, 1):
            dot(c, sx * 30, -18, 9, INK)
            dot(c, sx * 30 - 3, -22, 3, WHITE)
        c.restore()

    def heart(c):
        bob = math.sin(lt * 3) * 10
        hrt = [(170 + 2.2 * 16 * math.sin(a) ** 3, -380 + bob - 2.2 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
               for a in np.linspace(0, 6.28, 40)]
        piece2(c, np.array(hrt), RED_L, RED, (170, -460), (170, -300), seed=3040, u=1.0)

    pop_layer(ctx, fs[0], grass)
    pop_layer(ctx, fs[1], dogf)
    pop_layer(ctx, fs[2], heart)


def popup_tooth(ctx, lt, fs):
    def gum(c):
        tab(c, -200, 200, PINK)
        pts = [(-220, 0)] + [(x, -90 * math.sin((x + 220) / 440 * math.pi) ** 0.6) for x in np.linspace(-220, 220, 30)] + [(220, 0)]
        piece2(c, np.array(pts), PINK, PINK_D, (0, -120), (0, 10), seed=3100, u=1.4)
        for sx in (-150, 150):
            piece(c, np.array([(sx - 40, -70), (sx + 40, -70), (sx + 34, -150), (sx - 34, -150)]) if False else
                  ellipse_pts(sx, -86, 40, 50), WHITE, seed=3101 + sx, u=1.2)

    def tooth(c):
        wob = math.sin(lt * 11) * 0.16 * (0.6 + 0.4 * math.sin(lt * 2))
        c.save()
        c.translate(0, -70)
        c.rotate(wob)
        pts = []
        for a in np.linspace(math.pi, 2 * math.pi, 20):
            pts.append((95 * math.cos(a), -150 + 120 * math.sin(a) * 0.9))
        pts += [(95, -150), (88, -40), (60, 10), (30, 0), (0, -30), (-30, 0), (-60, 10), (-88, -40)]
        piece2(c, np.array(pts), WHITE, WHITE2, (25, -300), (20, 20), seed=3110, u=1.4)
        for sx in (-1, 1):
            arc_stroke(c, sx * 32, -150, 12, 1.15 * math.pi, 1.85 * math.pi, INK, 6)
            c.save()
            c.translate(sx * 50, -115)
            c.scale(1, 0.6)
            dot(c, 0, 0, 14, (0.97, 0.6, 0.6), 0.6)
            c.restore()
        arc_stroke(c, 0, -125, 24, 0.2 * math.pi, 0.8 * math.pi, INK, 6)
        c.restore()
        # Wackel-Linien
        for sx in (-1, 1):
            k = 0.5 + 0.5 * math.sin(lt * 11 + (0 if sx < 0 else 3))
            for j in range(3):
                arc_stroke(c, 0, -170, 130 + j * 22, (1.12 if sx < 0 else -0.25 - 0.05) * math.pi + j * 0.0,
                           (1.25 if sx < 0 else -0.12) * math.pi, mix(PINK_D, RED_L, k), 5)

    def stars(c):
        for i, (x, y) in enumerate(((-210, -310), (220, -280), (-160, -400), (170, -420))):
            sparkle(c, x, y + math.sin(lt * 4 + i) * 8, 26 + 6 * math.sin(lt * 5 + i), 1.0, YELLOW)

    pop_layer(ctx, fs[0], gum)
    pop_layer(ctx, fs[1], tooth)
    pop_layer(ctx, fs[2], stars)


def popup_drawing(ctx, lt, fs):
    def easel(c):
        tab(c, -170, 170, WOOD)
        for (x0, x1) in ((-150, -110), (150, 110)):
            piece(c, np.array([(x0 - 10, 0), (x0 + 10, 0), (x1 + 6, -400), (x1 - 6, -400)]), WOOD_D, seed=3200 + x0, u=1.2)
        piece(c, rect_pts(-170, -110, 340, 16), WOOD, seed=3203, u=1.2)

    def pic(c):
        sw = math.sin(lt * 2.4) * 0.03
        c.save()
        c.translate(0, -255)
        c.rotate(sw)
        piece(c, rect_pts(-170, -150, 340, 270), WOOD, seed=3210, u=1.4)
        piece(c, rect_pts(-154, -134, 308, 238), WHITE, seed=3211, u=1.2, shadow=0.6)
        crayon_drawing(c, -150, -130, 300, 230, 1.3)
        c.restore()

    def crayons(c):
        for i, (col, x) in enumerate(((RED, -120), (BLUE_D, -40), (YELLOW_D, 40), (GREEN_L, 120))):
            c.save()
            c.translate(x, -20)
            c.rotate(-0.3 + i * 0.2)
            piece(c, rect_pts(-10, -60, 20, 70), col, seed=3220 + i, u=1.0)
            piece(c, np.array([(-10, -60), (10, -60), (0, -82)]), darker(col, 0.8), seed=3225 + i, u=0.6)
            piece(c, rect_pts(-10, -40, 20, 26), WHITE, seed=3230 + i, u=0.6, shadow=0)
            c.restore()

    pop_layer(ctx, fs[0], easel)
    pop_layer(ctx, fs[1], pic)
    pop_layer(ctx, fs[2], crayons)


def paper_star(ctx, cx, cy, R, unf, rot, glowk=0.0, seed=3300):
    """3D-Papierstern: 10 Facetten hell/dunkel, entfaltet sich wie ein Fächer."""
    n = 5
    r2 = R * 0.45
    pts = []
    for i in range(2 * n):
        r = R if i % 2 == 0 else r2
        a = -math.pi / 2 + i * math.pi / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(max(unf, 0.02), 1)
    light = mix(GOLD, (1, 0.97, 0.8), glowk * 0.6)
    dark = mix(GOLD_D, GOLD, glowk * 0.5)
    outline = np.array(pts)
    for k in (1.0, 0.55):
        ctx.save()
        ctx.translate(4 * k, 7 * k)
        path(ctx, outline)
        ctx.set_source_rgba(0.25, 0.14, 0.1, 0.12)
        ctx.fill()
        ctx.restore()
    for i in range(2 * n):
        p0 = pts[i]
        p1 = pts[(i + 1) % (2 * n)]
        tri = np.array([(0, 0), p0, p1])
        path(ctx, tri)
        ctx.set_source_rgb(*(light if i % 2 == 0 else dark))
        ctx.fill()
    for i in range(2 * n):
        line(ctx, [(0, 0), pts[i]], darker(GOLD_D, 0.85), 1.6, alpha=0.6)
    path(ctx, outline)
    ctx.set_source_rgba(*darker(GOLD_D, 0.8), 0.9)
    ctx.set_line_width(2.0)
    ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ Insert-Szene
POP = {'dog': popup_dog, 'tooth': popup_tooth, 'drawing': popup_drawing}
LETTER_COL = {'dog': (0.97, 0.88, 0.86), 'tooth': (0.90, 0.95, 0.90), 'drawing': (0.92, 0.90, 0.97), 'star': GOLD}


def insert(ctx, lt, kind, dur, joy0, joy1, tex, t_open=(0.35, 1.15)):
    t_tw = twos(lt)
    zoom = 1.0 + 0.035 * lt / dur
    ctx.save()
    ctx.translate(960, 540)
    ctx.scale(zoom, zoom)
    ctx.translate(-960, -540)
    insert_bg(ctx)
    oa = ease(lt, *t_open)
    a = oa * math.pi / 2
    a_deg = oa * 90
    # Zeitpunkt Pop-up
    t30 = t_open[0] + (t_open[1] - t_open[0]) * 0.36
    fs = [spring(lin(t_tw, t30 + d, t30 + d + 1.1)) for d in (0.0, 0.10, 0.28)]
    popped = lin(lt, t30 + 0.15, t30 + 0.6)
    joy = lerp(joy0, joy1, smooth(lin(lt, t30 + 0.3, t30 + 1.2)))
    # ---------------- Kind (rechts)
    star_mode = kind == 'star'
    sr = lin(lt, 1.7, 2.7) if star_mode else 0
    bounce = 0.0
    if popped > 0:
        bounce = -abs(math.sin((lt - t30) * 7)) * 18 * math.exp(-(lt - t30) * 1.2) * (1.6 if kind in ('drawing', 'star') else 1)
    jump = 0.0
    if kind == 'drawing' and lt > t30 + 0.5:
        jump = max(0.0, math.sin((lt - t30 - 0.5) * 9)) * 26 * math.exp(-(lt - t30 - 0.5) * 0.8)
    hy = 445 + bounce - jump
    shoulders = np.array([(1190, 1120), (1810, 1120), (1720, 700 - jump), (1280, 700 - jump)])
    piece2(ctx, shoulders, BLUE_L, BLUE, (1530, 650), (1560, 1150), seed=2100, u=2.0)
    pajama_dots(ctx, shoulders, 8, r=9, n=12)
    piece(ctx, ellipse_pts(1500, 700 - jump, 60, 22), SKIN_D, seed=2101, u=1.4, shadow=0.4)
    look = (-0.9, 0.7) if popped < 0.5 else (-0.8, -0.1)
    if star_mode and sr > 0:
        look = (-0.7, -0.9)
    blink = (int(lt * 10) % 31) == 7 and popped < 0.1
    mo = 0.0
    if popped > 0:
        mo = clamp(1 - (lt - t30 - 0.15) * 1.6) * 0.9
    child_head(ctx, 1500, hy, 220, joy, blink, look, gap=(kind == 'tooth'), u=3.0, seed=220, mouth_o=mo,
               tilt=-0.06 + 0.04 * math.sin(lt * 2))
    # ---------------- Karte: Bodenteil
    bot = np.array([(HX0, HINGE_Y), (HX1, HINGE_Y), (HX1 + 50, FRONT_Y), (HX0 - 50, FRONT_Y)])
    inner = CREAM
    piece(ctx, bot, mix(inner, CREAM2, 0.5), seed=2200, u=1.6, shadow=2.0)
    if a_deg > 20:
        ctx.save()
        path(ctx, bot)
        ctx.clip()
        st = scribble_pts(HX0 + 40, HINGE_Y + 40, 560, 3, 44, seed=sum(map(ord, kind)) % 1000, h=10, sy=0.55)
        draw_scribbles(ctx, st, INK, 2.2, 1.0, alpha=0.55 * clamp((a_deg - 20) / 30))
        ctx.restore()
    # ---------------- Rückwand
    yfree, xl, xr = card_geom(a)
    back = np.array([_bpt(a, 0, HX0), _bpt(a, 0, HX1), _bpt(a, DEPTH, HX1), _bpt(a, DEPTH, HX0)])
    outer = LETTER_COL[kind]
    if yfree > HINGE_Y:
        # Außenseite sichtbar (Brief noch zu)
        p = piece(ctx, back, outer, seed=2201, u=1.6, shadow=1.2)
        ctx.save()
        path(ctx, p)
        ctx.clip()
        cx, cy = _bpt(a, DEPTH * 0.55, (HX0 + HX1) / 2)
        sq = (yfree - HINGE_Y) / (FRONT_Y - HINGE_Y)
        ctx.translate(cx, cy)
        ctx.scale(1, max(sq, 0.05))
        # Umschlag-V
        line(ctx, [(-340, -200), (0, 40), (340, -200)], darker(outer, 0.85), 3)
        if kind == 'star':
            piece(ctx, star_pts(0, 40, 46, 20), GOLD_D if kind == 'star' else RED, seed=2202, u=1.0, shadow=0.6)
            dot(ctx, 0, 40, 16, RED)
        else:
            piece(ctx, ellipse_pts(0, 40, 38, 38), RED, seed=2202, u=1.0, shadow=0.6)
            piece(ctx, star_pts(0, 40, 20, 9), RED_D, seed=2203, u=0.6, shadow=0)
        st = scribble_pts(-90, 120, 260, 2, 34, seed=77, h=9)
        draw_scribbles(ctx, st, INK, 2.6, 1.0, alpha=0.8)
        ctx.restore()
    else:
        p = piece(ctx, back, CREAM, seed=2204, u=1.6, shadow=1.6)
        # Falz-Schattierung: leicht dunkler, solange schräg
        k = clamp((90 - a_deg) / 60)
        path(ctx, p)
        ctx.set_source_rgba(0.5, 0.35, 0.25, 0.12 * k)
        ctx.fill()
        ctx.save()
        path(ctx, p)
        ctx.clip()
        top_y = _bpt(a, DEPTH, HX0)[1]
        sq = (HINGE_Y - top_y) / DEPTH
        ctx.translate(0, HINGE_Y)
        ctx.scale(1, max(sq, 0.02))
        ctx.translate(0, -HINGE_Y)
        st = scribble_pts(HX0 + 70, HINGE_Y - DEPTH + 80, 540, 5, 46, seed=sum(map(ord, kind)) % 999 + 3, h=11)
        draw_scribbles(ctx, st, INK, 2.6, 1.0, alpha=0.85)
        # Schnörkel-Rahmen
        for (x, y) in ((HX0 + 30, HINGE_Y - DEPTH + 30), (HX1 - 30, HINGE_Y - DEPTH + 30)):
            for j in range(3):
                arc_stroke(ctx, x, y, 8 + j * 6, 0, math.pi * 1.5, RED_L, 2.2)
        ctx.restore()
    # Falz-Linie
    line(ctx, [(HX0, HINGE_Y), (HX1, HINGE_Y)], CREAM3, 2.0)
    # ---------------- Pop-up
    if not star_mode:
        POP[kind](ctx, t_tw, fs)
    else:
        star_scene(ctx, lt, t_tw, fs)
    # ---------------- Hände
    rel = smooth(lin(lt, t_open[1] - 0.25, t_open[1] + 0.3))
    for side, xx in ((-1, HX0), (1, HX1)):
        fx, fyy = _bpt(a, DEPTH, xx)
        fx += side * 20
        rest = (HX0 - 120, 1010) if side < 0 else (HX1 + 140, 1010)
        hx = lerp(fx, rest[0], rel)
        hyy = lerp(fyy, rest[1], rel)
        if lt < t_open[0]:
            hyy += math.sin(lt * 6) * 4
        hand(ctx, hx, hyy, side, 2300 + side)
    # Funkeln
    if popped > 0:
        r = np.random.RandomState(5)
        n = 7 if kind != 'star' else 14
        for i in range(n):
            ph = r.uniform(0, 1)
            k = ((lt - t30) * 0.8 + ph) % 1.0
            x = BASE[0] + r.uniform(-360, 360)
            y = BASE[1] - r.uniform(120, 520) - k * 60
            s = 18 * math.sin(k * math.pi) * popped
            sparkle(ctx, x, y, s, 1.0)
    texture(ctx, tex, 1.2)
    # warmes Morgenlicht
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    g = cairo.LinearGradient(0, 0, 900, 1080)
    g.add_color_stop_rgba(0, 1.0, 0.85, 0.6, 0.16)
    g.add_color_stop_rgba(1, 1.0, 0.85, 0.6, 0.0)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()
    if star_mode:
        star_light(ctx, lt)
    ctx.restore()


STAR_C0 = (670.0, 700.0)


def star_state(lt):
    unf = smooth(lin(lt, 0.95, 1.75))
    rise = ease(lt, 1.75, 2.8)
    cx = lerp(STAR_C0[0], 760, rise)
    cy = lerp(STAR_C0[1], 360, rise)
    R = lerp(165, 215, rise)
    rot = (1 - unf) * 1.6 + 0.08 * math.sin(lt * 1.8) * rise
    gl = smooth(lin(lt, 1.6, 3.0))
    return unf, cx, cy, R, rot, gl


def star_scene(ctx, lt, t_tw, fs):
    if lt < 0.9:
        return
    unf, cx, cy, R, rot, gl = star_state(lt)
    # Faltblatt-Fächer, aus dem der Stern kommt
    if unf < 0.95:
        f = spring(lin(t_tw, 0.8, 1.4))
        ctx.save()
        ctx.translate(*BASE)
        ctx.scale(1, f)
        tab(ctx, -60, 60, GOLD)
        ctx.restore()
    paper_star(ctx, cx, cy, R * max(0.3, spring(lin(t_tw, 0.85, 1.6))), unf, rot, gl)


def star_light(ctx, lt):
    if lt < 1.4:
        return
    unf, cx, cy, R, rot, gl = star_state(lt)
    pul = 1 + 0.06 * math.sin(lt * 5)
    # Strahlen
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    for i in range(14):
        a = i * 2 * math.pi / 14 + lt * 0.25
        g = cairo.RadialGradient(cx, cy, R * 0.6, cx, cy, 1300)
        g.add_color_stop_rgba(0, 1.0, 0.85, 0.5, 0.10 * gl)
        g.add_color_stop_rgba(1, 1.0, 0.85, 0.5, 0.0)
        ctx.set_source(g)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a - 0.05) * 1500, cy + math.sin(a - 0.05) * 1500)
        ctx.line_to(cx + math.cos(a + 0.05) * 1500, cy + math.sin(a + 0.05) * 1500)
        ctx.close_path()
        ctx.fill()
    ctx.restore()
    glow(ctx, cx, cy, 900 * pul, (1.0, 0.70, 0.35), 0.38 * gl)
    glow(ctx, cx, cy, R * 1.6, (1.0, 0.92, 0.65), 0.45 * gl)
    paper_star(ctx, cx, cy, R, unf, rot, gl)
    glow(ctx, cx, cy, R * 0.7, (1.0, 0.95, 0.8), 0.35 * gl)
    # Gesicht wird angestrahlt
    glow(ctx, 1450, 450, 420, (1.0, 0.7, 0.4), 0.16 * gl)


# ------------------------------------------------------------------ Endcard
LOGO = "wichtelbriefe.com"
SUB = "„24 Briefe. Nur für dein Kind.“"


def endcard(ctx, lt, tex):
    u = 2.0
    ctx.rectangle(-100, -100, 2200, 1300)
    ctx.set_source_rgb(*CREAM)
    ctx.fill()
    x = -100
    i = 0
    while x < 2100:
        ctx.rectangle(x, -100, 160, 1300)
        ctx.set_source_rgb(*(CREAM if i % 2 == 0 else mix(CREAM, CREAM2, 0.6)))
        ctx.fill()
        x += 160
        i += 1
    # Tannenzweige in den Ecken
    for (cx, cy, rot, sd) in ((-30, -20, 0.6, 1), (1950, 1100, 0.6 + math.pi, 2), (1950, -20, math.pi - 0.6, 3), (-30, 1100, -0.6, 4)):
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        line(ctx, [(0, 0), (330, 0)], GREEN_D, 8)
        for k in range(9):
            x = 30 + k * 34
            for sgn in (-1, 1):
                p = np.array([(x, 0), (x + 46, sgn * 40), (x + 58, sgn * 34), (x + 14, 0)])
                piece(ctx, p, GREEN_L if (k + (sgn > 0)) % 2 else GREEN, seed=4000 + sd * 50 + k * 2 + (sgn > 0), u=1.0, shadow=0.6)
        for (bx, by, bc) in ((120, 30, RED), (220, -26, RED_L), (290, 20, GOLD)):
            piece(ctx, ellipse_pts(bx, by, 16, 16), bc, seed=4300 + sd + bx, u=0.8)
        ctx.restore()
    snow(ctx, lt + 10, -50, -50, 1970, 1130, 26, 31, 1.6, 0.5, alpha=0.6)
    # Schriftzug aus gefalteten Briefen
    ctx.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    fsz = 200
    ctx.set_font_size(fsz)
    ext = ctx.text_extents(LOGO)
    x0 = 960 - ext.x_advance / 2
    by = 540
    advs = []
    xx = x0
    for ch in LOGO:
        e = ctx.text_extents(ch)
        advs.append((xx, e))
        xx += e.x_advance
    rs = np.random.RandomState(17)
    starts = []
    for i in range(len(LOGO)):
        ang = rs.uniform(0, 2 * math.pi)
        starts.append((960 + math.cos(ang) * 1300, 540 + math.sin(ang) * 800, rs.uniform(-2, 2)))
    for i, ch in enumerate(LOGO):
        cx0, e = advs[i]
        tc = 0.12 + i * 0.055
        k = lin(lt, tc, tc + 0.75)
        sx, sy, sr = starts[i]
        tx, ty = cx0 + e.x_advance / 2, by - fsz * 0.33
        is_com = i >= len(LOGO) - 4
        col_a = GREEN_L if is_com else RED_L
        col_b = GREEN if is_com else RED
        if k < 1:
            if k <= 0:
                continue
            kk = ease(k, 0, 1)
            px = lerp(sx, tx, kk) + math.sin(kk * math.pi) * 120 * (1 if i % 2 else -1)
            py = lerp(sy, ty, kk) - math.sin(kk * math.pi) * 160
            s = lerp(1.4, 0.55, kk)
            ctx.save()
            ctx.translate(px, py)
            ctx.rotate(sr * (1 - kk))
            mini_letter(ctx, 0, 40 * s, 130 * s, 84 * s, col=[CREAM, (0.97, 0.88, 0.86), (0.90, 0.95, 0.90), (0.92, 0.90, 0.97)][i % 4],
                        u=1.0, seed=4100 + i)
            ctx.restore()
        if k > 0.85:
            # Buchstabe faltet sich auf
            f = spring(lin(lt, tc + 0.68, tc + 1.15))
            ctx.save()
            ctx.translate(tx, ty)
            ctx.scale(max(0.02, f), 1)
            ctx.translate(-tx, -ty)
            ctx.move_to(cx0, by)
            ctx.text_path(ch)
            pth = ctx.copy_path()
            ctx.new_path()
            # Papierrand + Schatten
            for (dx, dy, a) in ((5, 8, 0.14), (2.5, 4, 0.12)):
                ctx.save()
                ctx.translate(dx, dy)
                ctx.append_path(pth)
                ctx.set_source_rgba(0.25, 0.12, 0.08, a)
                ctx.set_line_width(14)
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.stroke_preserve()
                ctx.fill()
                ctx.restore()
            ctx.append_path(pth)
            ctx.set_source_rgb(*WHITE)
            ctx.set_line_width(14)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*col_b)
            ctx.fill()
            # Zweiton-Falz: obere Hälfte heller
            ctx.save()
            ctx.append_path(pth)
            ctx.clip()
            ctx.rectangle(cx0 - 10, by - fsz, e.x_advance + 20, fsz * 0.62)
            ctx.set_source_rgb(*col_a)
            ctx.fill()
            line(ctx, [(cx0 - 10, by - fsz * 0.38), (cx0 + e.x_advance + 10, by - fsz * 0.38)], darker(col_b, 0.8), 1.5, alpha=0.6)
            ctx.restore()
            ctx.append_path(pth)
            ctx.set_source_rgba(*darker(col_b, 0.75), 0.8)
            ctx.set_line_width(1.6)
            ctx.stroke()
            ctx.restore()
    # Untertitel
    sk = smooth(lin(lt, 1.75, 2.35))
    if sk > 0:
        ctx.select_font_face("Fredoka Medium", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(74)
        e = ctx.text_extents(SUB)
        ctx.save()
        ctx.translate(960, 700 + 20 * (1 - sk))
        ctx.scale(1, max(0.02, sk))
        ctx.move_to(-e.x_advance / 2, 0)
        ctx.text_path(SUB)
        pth = ctx.copy_path()
        ctx.new_path()
        ctx.append_path(pth)
        ctx.set_source_rgba(*WHITE, sk)
        ctx.set_line_width(9)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgba(*GREEN_D, sk)
        ctx.fill()
        ctx.restore()
        # kleiner Stern als Akzent
        sparkle(ctx, 960 + e.x_advance / 2 + 50, 676, 22 * sk, sk, GOLD)
        sparkle(ctx, 960 - e.x_advance / 2 - 50, 676, 22 * sk, sk, GOLD)
    texture(ctx, tex, 1.2)
