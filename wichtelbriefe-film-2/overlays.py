"""Texteinblendungen auf aufklappenden Papierstreifen und der flatternde URL-Anhänger."""
import math
import cairo
import numpy as np
from paper import *
from engine import catmull, soft

BROWN_INK = (0.30, 0.18, 0.11)
FONT = "Kurale"


def _text(ctx, txt, size, x, y, col=BROWN_INK, weight=1.1, center=True, alpha=1.0):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(txt)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y)
    ctx.text_path(txt)
    ctx.set_source_rgba(*col, alpha)
    ctx.fill_preserve()
    ctx.set_line_width(weight)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    return e


def text_width(txt, size):
    s = cairo.ImageSurface(cairo.FORMAT_A8, 4, 4)
    c = cairo.Context(s)
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    return c.text_extents(txt).x_advance


def banner(ctx, txt, k, cx=960, cy=205, size=66):
    """Papierstreifen faltet sich auf (k: 0 zu .. 1 offen), Ziehharmonika aus 4 Feldern."""
    if k <= 0.001:
        return
    tw = text_width(txt, size)
    W = tw + 150
    H = size * 1.75
    n = 4
    pw = W / n
    th = (1 - smooth(k)) * math.pi / 2 * 0.97
    c = math.cos(th)
    total = W * c
    x0 = cx - total / 2
    # Schatten des Streifens
    for (o, a) in ((14, 0.10), (9, 0.12), (5, 0.12)):
        ctx.save()
        path(ctx, deckle(rect_pts(x0 + o * 0.5, cy - H / 2 + o, total, H), 9300, 1.6, 1.1))
        ctx.set_source_rgba(0.12, 0.06, 0.04, a * min(1, k * 3))
        ctx.fill()
        ctx.restore()
    strip = deckle(rect_pts(cx - W / 2, cy - H / 2, W, H), 9301, 1.6, 1.4)
    for i in range(n):
        px0 = x0 + i * pw * c
        ctx.save()
        ctx.rectangle(px0 - 0.5, cy - H, pw * c + 1, 2 * H)
        ctx.clip()
        ctx.translate(px0, cy)
        sy = 1 - 0.05 * math.sin(th) * (1 if i % 2 else -1)
        ctx.scale(max(c, 0.02), sy)
        ctx.translate(-(cx - W / 2 + i * pw), -cy)
        ctx.save()
        ctx.rectangle(cx - W / 2 + i * pw, cy - H, pw, 2 * H)
        ctx.clip()
        path(ctx, strip)
        ctx.set_source_rgb(*CREAM)
        ctx.fill_preserve()
        ctx.set_source_rgba(*darker(CREAM2, 0.9), 0.9)
        ctx.set_line_width(1.4)
        ctx.stroke()
        # dünne Zierlinien
        for yy in (cy - H / 2 + 12, cy + H / 2 - 12):
            line(ctx, [(cx - W / 2 + 22, yy), (cx + W / 2 - 22, yy)], RED_L, 1.4, alpha=0.55)
        _text(ctx, txt, size, cx, cy + size * 0.32, weight=1.3)
        ctx.restore()
        # Falzschattierung: abwechselnd zur Lichtseite / weg
        shade = (0.25 if i % 2 else 0.06) * math.sin(th) + 0.02 * (i % 2)
        ctx.rectangle(cx - W / 2 + i * pw, cy - H, pw, 2 * H)
        ctx.set_source_rgba(0.35, 0.22, 0.14, shade)
        ctx.fill()
        ctx.restore()
        if i > 0:
            line(ctx, [(px0, cy - H / 2 + 4), (px0, cy + H / 2 - 4)], CREAM3, 1.0, alpha=0.5 + 0.4 * math.sin(th))


def banner_k(t, t0, t1, d=0.32):
    if t < t0 or t > t1:
        return 0.0
    return min(lin(t, t0, t0 + d), 1 - lin(t, t1 - d, t1))


def url_tag(ctx, t, grow=0.0, flutter=1.0, sub=0.0):
    """Anhänger aus cremefarbenem Papier mit roter Schnur, unten rechts; wächst im Schlussbild zur Mitte."""
    g = smooth(grow)
    w = text_width("wichtelbriefe.com", 37) + 86
    cx = lerp(1880 - w / 2, 960, g)
    cy = lerp(1000, 520, g)
    sc = lerp(1.0, 2.55, g)
    rot = lerp(-0.045 + 0.018 * math.sin(t * 2.3) * flutter + 0.05 * math.sin(t * 9.0) * max(0.0, flutter - 1.0) / 2, 0.0, g)
    rot += 0.01 * math.sin(t * 1.7) * (1 - g)
    h = lerp(74, 128, smooth(sub))
    # Schnur: vom Loch nach oben rechts aus dem Bild (wird im Schlussbild zur Schleife)
    hx, hy = cx - w / 2 * sc + 24 * sc, cy
    ctx.save()
    if g < 0.98:
        sx = lerp(1930, 960, g)
        sy = lerp(905, -40, g)
        mx = (hx + sx) / 2 + 30 * math.sin(t * 2.3) * (1 - g)
        my = (hy + sy) / 2 + 40
        ctx.move_to(hx, hy)
        ctx.curve_to(hx - 30 * sc, hy - 40 * sc, mx, my, sx, sy)
        ctx.set_source_rgba(0.5, 0.08, 0.08, 0.5)
        ctx.set_line_width(4.2 * sc)
        ctx.stroke()
        ctx.move_to(hx, hy)
        ctx.curve_to(hx - 30 * sc, hy - 40 * sc, mx, my, sx, sy)
        ctx.set_source_rgb(*RED)
        ctx.set_line_width(3.0 * sc)
        ctx.stroke()
    ctx.restore()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(sc, sc)
    tag = [(-w / 2 + 26, -h / 2), (w / 2 - 8, -h / 2), (w / 2, -h / 2 + 8), (w / 2, h / 2 - 8), (w / 2 - 8, h / 2), (-w / 2 + 26, h / 2),
           (-w / 2, h / 2 - 22), (-w / 2, -h / 2 + 22)]
    P = deckle(np.array(tag), 9400, 0.8, 0.6)
    for (o, a) in ((7, 0.10), (4, 0.14), (2, 0.12)):
        ctx.save()
        ctx.translate(o * 0.5, o)
        path(ctx, P)
        ctx.set_source_rgba(0.12, 0.06, 0.04, a)
        ctx.fill()
        ctx.restore()
    path(ctx, P)
    ctx.set_source_rgb(*CREAM)
    ctx.fill_preserve()
    ctx.set_source_rgba(*darker(CREAM2, 0.85), 0.9)
    ctx.set_line_width(1.0)
    ctx.stroke()
    # Faserstruktur angedeutet
    r = np.random.RandomState(4)
    for i in range(18):
        x = r.uniform(-w / 2 + 30, w / 2 - 10)
        y = r.uniform(-h / 2 + 6, h / 2 - 6)
        a = r.uniform(0, 3)
        line(ctx, [(x, y), (x + math.cos(a) * 6, y + math.sin(a) * 6)], CREAM3, 0.4, alpha=0.5)
    # Ösenring + Loch
    hxl = -w / 2 + 24
    dot(ctx, hxl, 0, 10, GOLD_D)
    dot(ctx, hxl, 0, 7.6, GOLD)
    dot(ctx, hxl, 0, 5.2, (0.22, 0.14, 0.10))
    # Schnur-Knoten am Loch
    line(ctx, [(hxl, 0), (hxl - 10, -6)], RED, 3.0)
    ty = 12 if sub <= 0 else lerp(12, -6, smooth(sub))
    _text(ctx, "wichtelbriefe.com", 37, 14, ty, weight=0.9)
    if sub > 0:
        line(ctx, [(-90, 10), (118, 10)], RED_L, 0.9, alpha=0.6 * smooth(sub))
        _text(ctx, "24 Briefe. Nur für dein Kind.", 21, 14, 40, weight=0.5, alpha=smooth(sub))
    ctx.restore()
