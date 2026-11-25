"""Zeitleiste 'Wichtelbriefe – Die Mission' (60 s, 24 fps)."""
import math
import cairo
import numpy as np
from paper import *
from engine import *
from chars2 import *
from characters import child_head, pajama_dots, flame, candle, quill
from sets2 import *
from sets2 import _fir
from overlays import banner, banner_k, url_tag

DUR = 60.0
TEXTS = [(1.0, 5.0, "„Jede Nacht schreibt er einen Brief.“"),
         (18.85, 22.45, "Doch heute Nacht …"),
         (51.85, 55.45, "Ein Brief nur für dich.")]


def camk(t, keys):
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            k = ease(t, a[0], b[0])
            return tuple(lerp(a[i], b[i], k) for i in range(1, len(a)))
    return keys[-1][1:]


def path_pt(t, keys):
    """Weicher Pfad durch (t, x, y)-Stützpunkte (Catmull-Rom in der Zeit)."""
    ts = [k[0] for k in keys]
    if t <= ts[0]:
        return keys[0][1], keys[0][2]
    if t >= ts[-1]:
        return keys[-1][1], keys[-1][2]
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    p0 = keys[max(0, i - 1)]
    p1 = keys[i]
    p2 = keys[i + 1]
    p3 = keys[min(len(keys) - 1, i + 2)]
    u = (t - p1[0]) / (p2[0] - p1[0])
    out = []
    for d in (1, 2):
        a, b, c, e = p0[d], p1[d], p2[d], p3[d]
        out.append(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - e) * u * u + (-a + 3 * b - 3 * c + e) * u ** 3))
    return out[0], out[1]


# ------------------------------------------------------------------ globale Zustände
def L_at(t):
    if t < 40.2:
        return 0.0
    if t < 50.0:
        return 0.55 * smooth(lin(t, 40.2, 43.5)) + 0.3 * smooth(lin(t, 43.5, 49.0))
    return 0.9


def storm_at(t):
    return smooth(lin(t, 10.6, 10.9)) * (1 - smooth(lin(t, 16.3, 18.0)))


def base_st(t, camx):
    s = storm_at(t)
    st = dict(L=L_at(t), storm=s, curtain=s * (0.8 + 0.2 * math.sin(t * 3)) + (0.15 if 18 < t < 40 else 0),
              win_open=smooth(lin(t, 10.6, 10.8)) * (1 + 0.08 * math.sin(t * 13) * s) if t >= 10.6 else 0.0,
              rattle=s, camx=camx, gdoor=0.0, gdoor_lit=0.6 if t < 47 else 0.9, swing=0.2, kid_open=0.0,
              kid_light=0.0)
    if t >= 18.0:
        st['win_open'] = 0.55 + 0.05 * math.sin(t * 0.7)
    return st


LETTER_STORM = [(12.6, 1404, 1010), (13.1, 1350, 900), (13.8, 1500, 650), (14.6, 1800, 430), (15.4, 2150, 520),
                (16.1, 2450, 720), (16.8, 2260, 880), (17.3, 2050, 975), (17.8, 1925, 1082)]
FLIGHT = [(36.4, 3930, 150), (37.2, 3680, 250), (38.0, 3240, 440), (38.65, 2780, 720), (39.2, 2480, 905),
          (39.7, 2180, 870), (40.4, 1640, 820), (41.2, 1050, 905), (42.0, 640, 1040)]


def room_frame(t, W, H, cam, st, chars=None, front=None, fg=False, emissive=None, extra_tint=None, particles=None):
    cx, cy, z = cam
    st['camx'] = cx
    M = cam_matrix(W, H, cx, cy, z)
    layers = [Layer(lambda c: wall_layer(c, t, st), M, None, 2.0),
              Layer(lambda c: furniture_layer(c, t, st), M, (9, 14, 18, 0.40), 2.0)]
    if chars:
        layers.append(Layer(lambda c: [f(c) for f in chars], M, (4, 7, 8, 0.38), 2.4))
    layers.append(Layer(lambda c: (sofa_front(c, t, st), [f(c) for f in (front or [])]), M, (6, 10, 12, 0.35), 2.0))
    if particles:
        layers.append(Layer(lambda c: particles(c), M, (5, 9, 10, 0.25), None))
    if fg:
        Mf = cam_matrix(W, H, cx, cy, z, k=1.55)
        layers.append(Layer(lambda c: foreground_props(c, t, st), Mf, (16, 24, 30, 0.45), 1.6))
    surf, octx = compose(W, H, layers)
    octx.set_matrix(M)
    tint_all(octx, extra_tint or light_col(st['L']))
    room_emissive(octx, t, st)
    if emissive:
        for e in emissive:
            e(octx)
    return surf


def room_emissive(ctx, t, st):
    L = st['L']
    fl = 0.9 + 0.1 * math.sin(t * 7.3) * math.sin(t * 3.1)
    # Kaminglut, durch die Papierwand gefiltert
    glow(ctx, 2500, 960, 700 * fl, (1.0, 0.45, 0.18), 0.30 * (1 - 0.5 * L))
    glow(ctx, 2500, 1010, 180, (1.0, 0.6, 0.25), 0.45 * fl)
    # Wichteltür / Stube hinter der Wand
    gl = st.get('gdoor_lit', 0.6)
    gx = (GD[0] + GD[1]) / 2
    glow(ctx, gx, FLOOR - 30, 230, (1.0, 0.62, 0.30), 0.22 * gl * fl)
    glow(ctx, gx, FLOOR - 20, 70, (1.0, 0.75, 0.45), 0.18 * gl * fl)
    if st.get('gdoor', 0) > 0.05:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(0, FLOOR, 0, FLOOR + 90)
        g.add_color_stop_rgba(0, 1.0, 0.72, 0.40, 0.25 * st['gdoor'])
        g.add_color_stop_rgba(1, 1.0, 0.72, 0.40, 0.0)
        ctx.set_source(g)
        ctx.move_to(GD[0], FLOOR)
        ctx.line_to(GD[1], FLOOR)
        ctx.line_to(GD[1] + 70, FLOOR + 90)
        ctx.line_to(GD[0] - 50, FLOOR + 90)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    # Kalender: die 24 leuchtet
    if '_cal24' in st:
        x, y = st['_cal24']
        p = 0.85 + 0.15 * math.sin(t * 2.6)
        glow(ctx, x, y, 120 * p, (1.0, 0.82, 0.40), 0.35 * (1 - 0.6 * L))
        glow(ctx, x, y, 40, (1.0, 0.92, 0.6), 0.3 * (1 - 0.6 * L))
    # Morgenlicht durchs Fenster und durch die Vorhänge
    if L > 0.01:
        glow(ctx, 1700, 520, 600, (1.0, 0.72, 0.45), 0.22 * L)
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(1450, 500, 1900, 1300)
        g.add_color_stop_rgba(0, 1.0, 0.82, 0.55, 0.16 * L)
        g.add_color_stop_rgba(1, 1.0, 0.82, 0.55, 0.0)
        ctx.set_source(g)
        ctx.move_to(1450, 770)
        ctx.line_to(1950, 770)
        ctx.line_to(2350, 1500)
        ctx.line_to(1500, 1500)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    else:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(1450, 500, 1800, 1300)
        g.add_color_stop_rgba(0, 0.6, 0.7, 0.95, 0.10)
        g.add_color_stop_rgba(1, 0.6, 0.7, 0.95, 0.0)
        ctx.set_source(g)
        ctx.move_to(1450, 770)
        ctx.line_to(1950, 770)
        ctx.line_to(2150, 1500)
        ctx.line_to(1550, 1500)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    kl = st.get('kid_light', 0.0)
    if kl > 0:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(0, FLOOR - 4, 0, FLOOR + 80)
        g.add_color_stop_rgba(0, 1.0, 0.85, 0.6, 0.55 * kl)
        g.add_color_stop_rgba(1, 1.0, 0.85, 0.6, 0.0)
        ctx.set_source(g)
        ox = KID[0] + (KID[1] - KID[0]) * math.cos(st.get('kid_open', 0) * 1.2)
        ctx.move_to(KID[0], FLOOR - 3)
        ctx.line_to(KID[1], FLOOR - 3)
        ctx.line_to(KID[1] + 120, FLOOR + 80)
        ctx.line_to(KID[0] - 60, FLOOR + 80)
        ctx.close_path()
        ctx.fill()
        if st.get('kid_open', 0) > 0.02:
            ctx.rectangle(ox, KID[2], KID[1] - ox, FLOOR - KID[2])
            ctx.set_source_rgba(1.0, 0.85, 0.6, 0.25 * kl)
            ctx.fill()
        ctx.restore()


def storm_flakes(t, intensity_fn, region=(1300, 300, 2700, 1100), n=70, seed=3):
    """Wirbelnde, gestanzte Papierschneeflocken im Raum."""
    r = np.random.RandomState(seed)
    birth = r.uniform(10.6, 17.0, n)
    life = r.uniform(2.0, 4.0, n)
    sz = r.uniform(6, 15, n)
    ph = r.uniform(0, 6.28, n)
    y0 = r.uniform(260, 760, n)
    sp = r.uniform(200, 420, n)

    def draw(c):
        for i in range(n):
            a = t - birth[i]
            if a < 0 or a > life[i]:
                continue
            k = a / life[i]
            x = 1500 + sp[i] * a + 60 * math.sin(a * 3 + ph[i])
            y = y0[i] + 140 * a * a * 0.25 + 70 * math.sin(a * 2.2 + ph[i] * 2) + 120 * a
            al = min(1, a * 4) * min(1, (life[i] - a) * 2)
            draw_snowflake(c, x, y, sz[i], a * 3 + ph[i], al)
    return draw


# ------------------------------------------------------------------ Requisiten in der Hand
def letter_item(scale=1.0, back=False):
    def f(c, h, when):
        if when != 'over':
            return
        letter_flat(c, h[0] + 1, h[1] - 8 * scale, 22 * scale, 15 * scale, 0.05, u=0.35, seed=7110)
    return f


def fold_plane_item(k, singe=0.0, t=0.0):
    """Brief -> Papierflieger (k 0..1) in den Händen."""
    def f(c, h, when):
        if when != 'over':
            return
        x, y = h[0] + 2, h[1] - 6
        if k < 0.35:
            q = k / 0.35
            letter_flat(c, x, y, 24, 16 * (1 - 0.3 * q), 0.0, seal=RED, u=0.35, seed=7111, bend=0.1 * math.sin(q * 9))
            # Ecken klappen ein
            for sg in (-1, 1):
                pts = np.array([(x + sg * 12, y - 8), (x + sg * 12 * (1 - q), y - 8), (x + sg * 12, y - 8 + 8 * q)])
                piece(c, pts, CREAM2, seed=7112 + sg, u=0.35, shadow=0.5, amp=0.05)
        elif k < 0.7:
            q = (k - 0.35) / 0.35
            pts = np.array([(x - 12 * (1 - 0.6 * q), y - 6), (x + 14, y - 1 - 3 * q), (x - 12 * (1 - 0.6 * q), y + 7 * (1 - q) + 2)])
            piece(c, pts, CREAM, seed=7113, u=0.35, shadow=0.7, amp=0.05)
            line(c, [(x - 10, y), (x + 13, y - 1)], CREAM3, 0.5)
        else:
            q = (k - 0.7) / 0.3
            plane(c, x, y - 2, 0.55 + 0.25 * q, rot=-0.1, facing=-1, singe=singe, t=t, roll=1 - q)
    return f


# ================================================================== Einstellungen
def shot_establish(t, W, H):
    cam = camk(t, [(0.0, 1380, 620, 0.95), (2.0, 790, 920, 1.95)])
    st = base_st(t, cam[0])
    st['gdoor_lit'] = 0.9
    return room_frame(t, W, H, cam, st)


def shot_room(t, W, H):
    cam = camk(t, [(2.0, 222, 236, 5.4), (6.2, 206, 240, 5.8)])
    tt = twos(t)
    M = cam_matrix(W, H, *cam)
    stroke = scribble_pts(0, 0, 60, 4, 4.5, seed=55, h=1.2)
    flour = [np.array([(0, 0)])]
    # Unterschrift-Schnörkel (letzter Schnörkel)
    sw = [np.array([(40 + 18 * k + 4 * math.sin(k * 14), 15 + 3 * math.sin(k * 9) - 2 * k) for k in np.linspace(0, 1, 40)])]
    state = {}

    def desk_items(c):
        ang = math.atan2(234 - 242, 246 - 140)
        wk = smooth(lin(tt, 3.4, 3.95))
        wk2 = smooth(lin(tt, 4.0, 4.55))
        c.save()
        c.translate(208, 236)
        c.rotate(ang)
        c.scale(0.62, 0.62)
        if tt < 4.6:
            w = 74 * (1 - 0.5 * wk) * (1 - 0.5 * wk2)
            # Blatt
            piece(c, rect_pts(-37, -10, 74 * (1 - 0.5 * wk) if wk < 1 else 37, 20 * (1 - 0.45 * wk2)), CREAM, seed=9500, u=0.35, shadow=0.6, amp=0.1)
            if wk < 0.98:
                c.save()
                c.rectangle(-37, -11, 74, 22)
                c.clip()
                for s in stroke:
                    line(c, [(p[0] - 32, p[1] * 0.55 - 7) for p in s if p[0] < 70 * (1 - wk)], INK, 0.35, alpha=0.75)
                pr = lin(tt, 2.05, 3.25)
                tip = draw_scribbles(c, [np.column_stack([s[:, 0] - 32, s[:, 1] * 0.5 - 4]) for s in sw], INK, 0.5, pr)
                c.restore()
                if tip is not None and tt < 3.3:
                    m = c.get_matrix()
                    state['tip'] = c.user_to_device(*tip)
                if wk > 0.02:
                    # Klappe (rechte Hälfte) dreht über den Falz
                    cwk = math.cos(wk * math.pi)
                    fl = np.array([(0, -10), (37 * cwk, -10 - 6 * math.sin(wk * math.pi)), (37 * cwk, 10 - 6 * math.sin(wk * math.pi)), (0, 10)])
                    piece(c, fl, CREAM if cwk > 0 else CREAM2, seed=9501, u=0.35, shadow=0.8, amp=0.05)
            if wk2 > 0.02:
                cw2 = math.cos(wk2 * math.pi)
                fl2 = np.array([(-37, 0), (0, 0), (0, 10 * cw2 - 5 * math.sin(wk2 * math.pi)), (-37, 10 * cw2 - 5 * math.sin(wk2 * math.pi))])
                piece(c, fl2, CREAM2 if cw2 < 0 else CREAM, seed=9502, u=0.35, shadow=0.8, amp=0.05)
                if wk2 > 0.95:
                    dot(c, -18, 3, 3, RED)
        c.restore()
        # Kerze auf dem Pult
        candle(c, 168, 240, 0.85)

    def gnome_fn(c):
        if tt < 4.75:
            hand = None
            tip = state.get('tip')
            if tip is not None and tt < 3.3:
                inv = cairo.Matrix(*M)
                inv.invert()
                wx, wy = inv.transform_point(*tip)
                hand = ((wx - 274) / -1.0, (wy - 270) / 1.0)
            elif 3.3 <= tt < 4.7:
                k = (tt - 3.3) / 1.4
                hand = (20 + 8 * math.sin(k * 12), -12 - 4 * abs(math.sin(k * 12)))
            P = gp(bob=-13, footB=(4, 26), footF=(10, 27), handF=hand, handB=(14, -10), eyes='open', look=-0.6,
                   sway=0.2 * math.sin(tt * 2), tilt=0.16)
            if tt < 3.3:
                P['item'] = lambda cc, h, w: quill(cc, h[0], h[1], ang=-1.9 + 0.15 * math.sin(tt * 25)) if w == 'over' else None
            gnome(c, 274, 270, P, 1.0, -1, tt)
        elif tt < 5.6:
            k = ease(tt, 4.75, 5.15)
            x = lerp(274, 300, k)
            y = lerp(270, 300, k) - math.sin(k * math.pi) * 14
            pk = tt > 5.15
            P = gp(handF=(10, -30) if not pk else (6, -20), handB=(-10, -28) if not pk else (-6, -18), pack=pk, eyes='open',
                   squash=0.08 * math.sin(lin(tt, 5.1, 5.35) * math.pi))
            if not pk:
                P['item'] = letter_item(0.9)
            gnome(c, x, y, P, 1.0, -1, tt)
        else:
            k = lin(tt, 5.6, 6.2)
            x = lerp(300, 120, k)
            gnome(c, x, 300, pose_sneak(tt * 9, pack=True), 1.0, -1, tt)

    layers = [Layer(lambda c: gnome_room(c, t, {}), M, None, 6.0),
              Layer(desk_items, M, (3, 5, 6, 0.4), 6.0),
              Layer(gnome_fn, M, (3, 5, 6, 0.4), 6.0)]
    surf, octx = compose(W, H, layers)
    octx.set_matrix(M)
    tint_all(octx, (0.62, 0.62, 0.78))
    fl = 1 + 0.06 * math.sin(t * 17) + 0.04 * math.sin(t * 29)
    glow(octx, 168, 222, 330 * fl, (1.0, 0.62, 0.30), 0.42)
    glow(octx, 168, 222, 90, (1.0, 0.82, 0.55), 0.35)
    flame(octx, 168.2, 225.4, 0.85, t)
    return surf


def shot_cal_door(t, W, H):
    cam = camk(t, [(6.2, 1010, 390, 2.35), (6.9, 1012, 392, 2.45), (7.75, 700, 965, 3.3), (8.0, 706, 968, 3.35)])
    st = base_st(t, cam[0])
    tt = twos(t)
    st['gdoor'] = ease(t, 7.15, 7.5) * (1 - ease(t, 7.85, 8.0) * 0)
    st['gdoor_lit'] = 0.95
    chars = []
    if tt >= 7.45:
        k = lin(tt, 7.45, 8.0)
        gx = lerp(665, 712, k)

        def g(c):
            gnome(c, gx, fy(lerp(0, 18, k)), pose_sneak(tt * 9, pack=True, eyes='open'), 1.0, 1, tt)
        chars.append(g)
    return room_frame(t, W, H, cam, st, chars)


def shot_sneak(t, W, H):
    tt = twos(t)
    gx = lerp(712, 1405, lin(tt, 8.0, 10.6))
    if t < 10.2:
        cam = (gx + 70, 975, 3.2)
    else:
        cam = camk(t, [(10.2, 1405 + 70, 975, 3.2), (10.95, 1600, 660, 1.4), (12.0, 1560, 740, 1.55)])
    st = base_st(t, cam[0])

    def g(c):
        if tt < 10.6:
            P = pose_sneak(tt * 7.5, pack=True)
        else:
            k = smooth(lin(tt, 10.6, 10.8))
            P = gp(tilt=lerp(0.1, -0.22, k) + 0.04 * math.sin(tt * 15), crouch=0.4, footB=(-10, 0), footF=(6, 0), handB=(14, -30),
                   handF=(18, -34), eyes='wide' if tt < 11.3 else 'squint', sway=-1.2 * k + 0.3 * math.sin(tt * 11), pack=True)
        gnome(c, gx, fy(20), P, 1.0, 1, tt)
    flakes = storm_flakes(t, None)
    return room_frame(t, W, H, cam, st, [g], fg=t < 10.4, particles=flakes if t > 10.6 else None)


def shot_storm(t, W, H):
    tt = twos(t)
    cam = camk(t, [(12.0, 1440, 975, 3.6), (12.6, 1440, 975, 3.6), (13.3, 1420, 850, 2.2), (14.2, 1700, 580, 1.7),
                   (15.2, 2150, 620, 1.7), (16.2, 2350, 780, 2.0), (17.2, 2080, 930, 2.6), (17.8, 1990, 985, 3.2), (18.0, 1990, 985, 3.4)])
    st = base_st(t, cam[0])
    chars = []
    gx = 1405 if tt < 13.4 else lerp(1405, 1600, ease(tt, 13.4, 14.6))

    def g(c):
        if tt < 12.6:
            P = gp(tilt=-0.22 + 0.04 * math.sin(tt * 15), crouch=0.4, footB=(-10, 0), footF=(6, 0), handB=(14, -30), handF=(18, -34),
                   eyes='squint', sway=-1.2 + 0.3 * math.sin(tt * 11), pack=True)
        elif tt < 13.4:
            P = gp(tilt=-0.1, footB=(-6, 0), footF=(6, -3), handB=(8, -60), handF=(16, -66), eyes='wide', sway=-1.0)
        elif tt < 14.6:
            P = pose_run(tt * 16, eyes='wide')
        else:
            P = pose_freeze(look=0.5)
        gnome(c, gx, fy(20), P, 1.0, 1, tt)
    chars.append(g)

    def letter(c):
        if tt < 12.6:
            return
        x, y = path_pt(t, LETTER_STORM)
        land = lin(t, 17.5, 17.8)
        rot = (math.sin(t * 5.1) * 0.9 + math.sin(t * 2.3) * 0.6 + t * 1.2) * (1 - land) + 0.08 * land
        bend = 0.25 * math.sin(t * 13) * (1 - land)
        sc = 1.0
        letter_flat(c, x, y, 24 * sc, 16 * sc, rot, u=0.35, seed=7110, bend=bend)
    chars.append(letter)
    # schlafende Katze im Körbchen
    chars.insert(0, lambda c: cat(c, 2090, 1062, cp(mode='sleep', eyeF=0, eyeB=0, breath=math.sin(t * 2.4), tail_ph=t), 0.95, -1, t))
    chars.insert(1, lambda c: basket(c, t, st, front=True))
    flakes = storm_flakes(t, None)
    return room_frame(t, W, H, cam, st, chars, particles=flakes)


def cat_letter(c, t, x=1925):
    letter_flat(c, x, 1086, 24, 15, 0.08, u=0.35, seed=7110, bend=0.0)


def shot_cat_wakes(t, W, H):
    cam = camk(t, [(18.0, 1990, 985, 3.4), (21.0, 1985, 985, 3.7)])
    st = base_st(t, cam[0])
    tt = twos(t)
    eyeF = smooth(lin(tt, 19.0, 19.25))
    pup = 0.85 - 0.8 * smooth(lin(tt, 19.55, 20.1))
    C = cp(mode='sleep', eyeF=eyeF, eyeB=0, pupil=pup, breath=math.sin(t * 2.4), tail_ph=t * 0.6 if tt < 20 else t * 3,
           look=(-1, 0.4), ears=0.15 * smooth(lin(tt, 20, 20.3)))
    letter_land = lin(t, 18.0, 18.35)

    def lt(c):
        cat_letter(c, t)
    return room_frame(t, W, H, cam, st, [lambda c: cat(c, 2090, 1062, C, 0.95, -1, t), lambda c: basket(c, t, st, front=True), lt])


def shot_freeze(t, W, H):
    cam = camk(t, [(21.0, 1610, 1000, 5.2), (22.5, 1612, 1000, 5.6)])
    st = base_st(t, cam[0])
    tt = twos(t)
    P = pose_freeze(look=0.6)
    P['bob'] = 0.6 * math.sin(tt * 30)
    P['sway'] = 0.1 * math.sin(tt * 2)
    if tt > 21.9:
        P['eyes'] = 'open' if int(tt * 12) % 6 else 'shut'
    return room_frame(t, W, H, cam, st, [lambda c: gnome(c, 1600, fy(30), P, 1.0, 1, tt)])


def shot_steal(t, W, H):
    cam = camk(t, [(22.5, 1790, 1000, 2.7), (25.0, 1840, 1000, 2.85)])
    st = base_st(t, cam[0])
    tt = twos(t)
    swipe = smooth(lin(tt, 24.42, 24.55)) * (1 - 0.7 * smooth(lin(tt, 24.6, 24.9)))
    C = cp(mode='sleep', eyeF=1.0, eyeB=smooth(lin(tt, 23.0, 23.2)), pupil=0.08 + 0.5 * smooth(lin(tt, 24.3, 24.4)),
           breath=0.0, tail_ph=t * 4, look=(-1, 0.5), ears=0.6 + 0.3 * swipe, mouth=swipe)
    chars = []

    def catf(c):
        if swipe > 0.05:
            # aufgerichtet zum Prankenhieb
            cat(c, 2090, 1062, cp(mode='stand', eyeF=1, eyeB=1, pupil=0.1, paw=swipe, ears=0.9, mouth=swipe, tail_ph=t * 6, look=(-1, 0.6),
                                  stretch=0.9), 0.95, -1, t)
        else:
            cat(c, 2090, 1062, C, 0.95, -1, t)
    chars.append(catf)
    chars.append(lambda c: basket(c, t, st, front=True))
    has = tt >= 24.5

    def g(c):
        if tt < 23.85:
            k = lin(tt, 22.5, 23.85)
            gx = lerp(1600, 1885, ease(tt, 22.5, 23.85))
            gnome(c, gx, fy(50), pose_sneak(tt * 7, eyes='open'), 1.0, 1, tt)
        elif tt < 24.5:
            k = smooth(lin(tt, 23.95, 24.45))
            P = pose_pull(k, eyes='open' if tt < 24.3 else 'wide')
            gnome(c, 1885, fy(50), P, 1.0, 1, tt)
        else:
            k = lin(tt, 24.55, 25.0)
            gx = lerp(1885, 2050, ease(tt, 24.55, 25.0))
            y = fy(60) - math.sin(lin(tt, 24.5, 24.75) * math.pi) * 22
            P = pose_run(tt * 18, eyes='wide', handB=(2, -58), handF=(8, -60))
            P['item'] = letter_item(1.0)
            gnome(c, gx, y, P, 1.0, 1, tt)

    def lt(c):
        if not has:
            off = -smooth(lin(tt, 24.0, 24.45)) * 10
            cat_letter(c, t, 1925 + off)
    chars.insert(0, lt)
    chars.append(g)
    return room_frame(t, W, H, cam, st, chars)


def chase_pos(t):
    """Wichtel-Position in der Verfolgung (x, y-Fuß, Phase)."""
    if t < 27.0:
        return lerp(2050, 2900, ease(t, 25.0, 27.0) * 0.3 + lin(t, 25.0, 27.0) * 0.7), fy(60)
    if t < 28.8:
        return lerp(2900, 3830, lin(t, 27.0, 28.8)), fy(40)
    k = lin(t, 28.9, 31.9)
    y = lerp(1040, 128, smooth(k) * 0.2 + k * 0.8)
    x = TREE_X + 50 * math.sin(k * 9) * (1 - k * 0.6)
    if t < 28.9:
        return lerp(3830, 3880, lin(t, 28.8, 28.9)), fy(40)
    return x, y


def shot_chase(t, W, H):
    tt = twos(t)
    gx, gy = chase_pos(tt)
    st = base_st(t, gx)
    if t < 28.8:
        cam = (gx + 90, 985, 2.7 if t < 27 else 3.0)
        if t < 25.35:
            cam = camk(t, [(25.0, 1880, 1000, 2.85), (25.35, gx + 90, 985, 2.7)])
    else:
        cam = camk(t, [(28.8, 3800, 985, 2.6), (29.3, TREE_X, gy + 30, 2.2)]) if t < 29.3 else (TREE_X + 10, gy + 40, 2.2)
    st['swing'] = 0.2 + (1.2 * math.exp(-(t % 0.9) * 2) if t > 28.9 else 0)
    under = 27.0 <= t < 28.8
    chars = []
    front = []
    # Katze
    lag = 0.55
    cx_, cy_ = chase_pos(tt - lag)

    def catf(c):
        if tt < 25.15:
            return
        if tt < 28.95 - 0.0 and cy_ > 1000:
            sq = 0.42 if 27.0 + lag <= tt < 28.8 + lag else 0.0
            cat(c, cx_ - 140, cy_, cp(mode='run', ph=tt * 15, eyeF=1, eyeB=1, pupil=0.1, ears=0.5, tail_ph=tt * 8, squash=sq, look=(1, 0)),
                0.8, 1, t)
        else:
            k = lin(tt, 29.35, 32.0)
            yy = lerp(1000, 420, k)
            c.save()
            c.translate(TREE_X - 30, yy)
            c.rotate(-1.4)
            cat(c, 0, 0, cp(mode='climb', ph=tt * 10, eyeF=1, eyeB=1, pupil=0.1, ears=0.5, tail_ph=tt * 6, look=(1, 0)), 0.75, 1, t)
            c.restore()

    def g(c):
        if tt < 28.85:
            P = pose_run(tt * 19, eyes='wide', handB=(2, -58), handF=(8, -60))
            P['item'] = letter_item(1.0)
            gnome(c, gx, gy, P, 1.0, 1, tt)
        else:
            P = pose_climb(tt * 14, eyes='wide')
            P['pack'] = True
            gnome(c, gx, gy, P, 1.0, 1, tt)
    if under:
        chars.append(catf)
        chars.append(g)
    else:
        chars.append(lambda c: basket(c, t, st, front=True))
        chars.append(catf)
        chars.append(g)
    return room_frame(t, W, H, cam, st, chars, front=front, fg=t < 28.8)


def shot_top(t, W, H):
    cam = camk(t, [(32.0, 3960, 185, 3.0), (34.8, 3965, 190, 3.3)])
    st = base_st(t, cam[0])
    st['swing'] = 0.6
    tt = twos(t)
    fk = smooth(lin(tt, 32.3, 34.2))

    def g(c):
        P = gp(footB=(-4, 0), footF=(5, 0), handB=(10, -24 - 3 * math.sin(tt * 20) * (fk < 1)), handF=(15, -26 + 3 * math.sin(tt * 20) * (fk < 1)),
               eyes='wide' if tt > 33.0 else 'open', look=0.4, sway=0.3 * math.sin(tt * 3), tilt=0.05 * math.sin(tt * 4))
        if tt > 34.25:
            P['handB'] = (2, -62)
            P['handF'] = (8, -64)
            P['crouch'] = 0.35 * smooth(lin(tt, 34.3, 34.7))
        P['item'] = fold_plane_item(fk)
        gnome(c, 3995, 132, P, 1.0, -1, tt)

    def catf(c):
        k = smooth(lin(tt, 32.0, 34.4))
        yy = lerp(470, 330, k)
        swipe = smooth(lin(tt, 34.5, 34.65))
        c.save()
        c.translate(TREE_X - 20, yy)
        c.rotate(-1.35)
        cat(c, 0, 0, cp(mode='climb', ph=tt * 6, eyeF=1, eyeB=1, pupil=0.1, ears=0.6, tail_ph=tt * 5, look=(1, -0.5), paw=swipe, mouth=swipe * 0.8),
            0.75, 1, t)
        c.restore()
    return room_frame(t, W, H, cam, st, [catf, g])


def flight_tau(t):
    return t


def flight_state(tau):
    if tau < 36.4:
        k = lin(tau, 34.8, 36.4)
        x = lerp(3995, 3930, k)
        y = lerp(132, 150, k) - math.sin(k * math.pi) * 30
        return x, y, -0.15
    x, y = path_pt(tau, FLIGHT)
    x2, y2 = path_pt(tau + 0.05, FLIGHT)
    ang = math.atan2(y2 - y, -(x2 - x))
    return x, y, ang


def shot_flight(t, W, H):
    tau = flight_tau(t)
    tt = twos(tau) if t > 36.4 else 34.8 + (t - 34.8) * 0.25
    px, py, ang = flight_state(tt)
    if t < 36.4:
        cam = camk(t, [(34.8, 3960, 210, 3.4), (36.4, 3900, 220, 3.7)])
    else:
        cx, cy = path_pt(tau + 0.2, FLIGHT)
        zz = lerp(3.6, 3.0, smooth(lin(tau, 36.4, 37.2)))
        cam = (cx - 30, cy + 40, zz)
    st = base_st(t, cam[0])
    singe = lin(tau, 39.05, 40.1)
    st['swing'] = 0.4

    def flier(c):
        # Wichtel hängt am Flieger
        P = gp(footB=(-6, 2 + 3 * math.sin(tt * 6)), footF=(4, 4 + 3 * math.sin(tt * 6 + 1)), handB=(-2, -62), handF=(5, -63),
               eyes='wide' if tau < 37.5 else 'open', sway=0.6 + 0.3 * math.sin(tt * 4), tilt=0.1 * math.sin(tt * 3))
        gx, gy = px, py + 74
        gnome(c, gx, gy, P, 1.0, -1, tt)
        plane(c, px - 2, py + 6, 1.6, rot=-ang * 0.6, facing=-1, singe=singe, t=t)
    chars = [flier]
    if t < 36.4:
        def catf(c):
            swipe = smooth(lin(t, 34.85, 35.6))
            c.save()
            c.translate(TREE_X - 20, 330)
            c.rotate(-1.35)
            cat(c, 0, 0, cp(mode='climb', ph=0.5, eyeF=1, eyeB=1, pupil=0.1, ears=0.7, tail_ph=t * 2, look=(1, -0.5), paw=swipe, mouth=0.8),
                0.75, 1, t)
            c.restore()
        chars.insert(0, catf)
    emis = []
    if 38.9 < tau < 40.3:
        r = np.random.RandomState(8)

        def sparks(c):
            for i in range(26):
                b = 38.9 + r.uniform(0, 1.0)
                a = tau - b
                if 0 < a < 0.9:
                    x = 2500 + r.uniform(-80, 80) + a * r.uniform(-60, 60)
                    y = 1010 - a * r.uniform(120, 260)
                    dot(c, x, y, r.uniform(1.5, 3.5) * (1 - a), (1.0, 0.65, 0.25), 1 - a)
        emis.append(sparks)
    if 39.0 < tau < 40.2:
        k = max(0.0, 1 - abs(singe - 0.35) * 2.2)
        emis.append(lambda c: glow(c, px + 30, py + 2, 60, (1.0, 0.55, 0.2), 0.5 * k))
    return room_frame(t, W, H, cam, st, chars, emissive=emis)


def shot_landing(t, W, H):
    tt = twos(t)
    if t < 47.2:
        cam = camk(t, [(42.0, 600, 985, 3.2), (44.2, 570, 985, 3.4), (47.2, 600, 985, 3.3)])
    else:
        cam = camk(t, [(47.2, 600, 985, 3.3), (48.6, 470, 860, 1.9), (50.0, 455, 880, 2.0)])
    st = base_st(t, cam[0])
    st['kid_light'] = smooth(lin(t, 44.3, 44.6))
    st['kid_open'] = smooth(lin(t, 48.0, 49.6)) * 0.75
    st['gdoor'] = smooth(lin(t, 45.85, 46.1)) * (1 - smooth(lin(t, 46.65, 47.0)))
    st['gdoor_lit'] = 0.95
    singe = 1.0
    chars = []
    # Brief / Flieger auf dem Boden
    if tt < 42.6:
        k = ease(tt, 42.0, 42.6)
        px = lerp(640, 545, k)
        py = lerp(1040, fy(28), k)
        chars.append(lambda c: (gnome(c, px + 2, py + 74 * (1 - k) + 0 * k, gp(footB=(-6, 2 * (1 - k)), footF=(4, 3 * (1 - k)), handB=(-2, -62),
                                                                                    handF=(5, -63), eyes='wide', sway=0.6), 1.0, -1, tt),
                                plane(c, px, py + 6 - 0 * k, 1.6, rot=0.05 * (1 - k), facing=-1, singe=singe, t=t)))
    else:
        unf = smooth(lin(tt, 42.7, 44.3))
        placed = tt >= 45.25
        gxx = 560 if tt < 44.9 else (lerp(560, 500, lin(tt, 44.9, 45.25)) if tt < 45.3 else lerp(500, 668, ease(tt, 45.3, 46.3)))

        def g(c):
            if tt < 44.9:
                fr = tt > 44.35
                P = gp(crouch=0.4, footB=(-6, 0), footF=(6, 0), handB=(12, -20 + 4 * math.sin(tt * 30) * (not fr)),
                       handF=(17, -22 - 4 * math.sin(tt * 30) * (not fr)), eyes='wide' if fr else 'open', look=-0.5 if fr else 0.3,
                       sway=0.3 * math.sin(tt * 9))
                P['item'] = fold_plane_item(1 - unf, singe=singe, t=t) if unf < 0.98 else (lambda cc, h, w: letter_flat(cc, h[0] + 2, h[1] - 8, 24, 16, 0.05, u=0.35, seed=7110) if w == 'over' else None)
                gnome(c, gxx, fy(28), P, 1.0, -1, tt)
            elif tt < 45.3:
                P = gp(crouch=0.6, footB=(-6, 0), footF=(8, 0), handB=(12, -8), handF=(18, -6), eyes='wide', look=-0.4)
                gnome(c, gxx, fy(28), P, 1.0, -1, tt)
            elif tt < 46.6:
                clip = tt > 46.15
                if clip:
                    c.save()
                    arch = np.vstack([[(GD[0], FLOOR + 30)], ellipse_pts((GD[0] + GD[1]) / 2, GD[2] + 25, 25, 25, a0=math.pi, a1=2 * math.pi, n=24), [(GD[1], FLOOR + 30)]])
                    path(c, np.vstack([arch, [(GD[1] + 2000, FLOOR + 30), (GD[1] + 2000, -2000), (GD[0] - 2000, -2000), (GD[0] - 2000, FLOOR + 30)]]))
                    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
                    c.rectangle(GD[0], -3000, GD[1] - GD[0], 4100)
                    c.clip()
                    c.set_fill_rule(cairo.FILL_RULE_WINDING)
                gz = lerp(28, 0, lin(tt, 45.9, 46.3))
                gnome(c, gxx, fy(gz), pose_run(tt * 20, eyes='wide', pack=False), 1.0, 1, tt)
                if clip:
                    c.restore()

        def lt(c):
            if placed:
                letter_flat(c, 455, fy(34), 26, 17, 0.02, u=0.35, seed=7110, singe=0.95, t=t)
            elif tt >= 44.9:
                pass
        chars.append(lt)
        if tt < 46.6:
            chars.append(g)
        if t >= 48.7:
            chars.append(lambda c: kid_feet(c, lerp(330, 420, lin(t, 48.7, 50.0)), fy(70), 1.0, t))
    return room_frame(t, W, H, cam, st, chars)


# ------------------------------------------------------------------ Pop-up-Nahaufnahme
HY, FY_, HX0, HX1, DEPTH = 900.0, 1060.0, 300.0, 980.0, 360.0
KP = (FY_ - HY) / DEPTH
BASE = (640.0, 975.0)


def _bpt(a, d, x):
    ca, sa = math.cos(a), math.sin(a)
    y = HY + d * (KP * ca - sa)
    cx = (HX0 + HX1) / 2
    return cx + (x - cx) * (1 + 50 / 340 * ca * d / DEPTH), y


def insert_bg(c, warm=True):
    c.rectangle(-100, -100, 2200, 1300)
    c.set_source_rgb(*CREAM)
    c.fill()
    for i in range(14):
        c.rectangle(-100 + i * 170, -100, 170, 900)
        c.set_source_rgb(*(CREAM if i % 2 == 0 else mix(CREAM, CREAM2, 0.6)))
        c.fill()
    for k in range(40):
        gx = -40 + (k % 10) * 220 + ((k // 10) % 2) * 110
        gy = 40 + (k // 10) * 200
        emboss(c, star_pts(gx, gy, 22, 10), CREAM if (int((gx + 100) / 170) % 2 == 0) else mix(CREAM, CREAM2, 0.6), u=1.4)
    soft(c, [(-100, 790), (2100, 790), (2100, 860), (-100, 860)], GREEN, seed=9601, u=2, n=2)
    y = 860
    i = 0
    while y < 1200:
        hh = 70 + i * 30
        piece(c, rect_pts(-100, y, 2200, hh), WOOD_L if i % 2 == 0 else mix(WOOD_L, WOOD, 0.5), seed=9610 + i, u=2, shadow=0.4, amp=0.1)
        y += hh
        i += 1


def popup_scene(c, lt, fs):
    def lay(f, fn):
        if f <= 0.01:
            return
        c.save()
        c.translate(*BASE)
        c.scale(1.0, f)
        fn(c)
        c.restore()

    def hill(cc):
        soft(cc, [(-60, 10), (-60, 0), (60, 0), (60, 10)], darker(WHITE, 0.85), seed=9700, u=1, n=2)
        pts = [(-320, 0), (-320, -60), (-200, -110), (-60, -90), (80, -130), (220, -100), (320, -70), (320, 0)]
        soft2(cc, pts, WHITE, WHITE2, (0, -150), (20, 10), seed=9701, u=1.4, n=5)
        for i, (fx, fh) in enumerate(((-270, 150), (-215, 110), (270, 170))):
            _fir(cc, fx, -70, fh, 9710 + i * 7, GREEN_L, GREEN, u=1.2)
        for i in range(6):
            draw_snowflake(cc, -250 + i * 100, -300 + 30 * math.sin(lt * 2 + i), 9, lt + i)

    def snowman(cc):
        x = -165
        for (yy, r) in ((-50, 52), (-128, 40), (-190, 30)):
            soft2(cc, ellipse_pts(x, yy, r, r, n=30), WHITE, WHITE2, (x + 10, yy - r - 10), (x + 14, yy + r + 10), seed=9720 + r, u=1.2, n=1)
        for dy in (-60, -38, -120):
            dot(cc, x, dy - 0, 4.5, INK)
        soft(cc, [(x + 4, -192), (x + 42, -186), (x + 4, -184)], (0.95, 0.55, 0.2), seed=9730, u=0.8, n=3)
        for ex in (-10, 10):
            dot(cc, x + ex, -200, 4, INK)
        soft(cc, [(x - 36, -160), (x + 36, -160), (x + 30, -150), (x - 30, -150)], RED, seed=9731, u=1, n=3)
        soft(cc, [(x + 10, -155), (x + 28, -155), (x + 30, -115), (x + 14, -118)], RED_L, seed=9732, u=1, n=3)
        soft(cc, [(x - 32, -218), (x + 32, -218), (x + 30, -212), (x - 30, -212)], INK, seed=9733, u=1, n=2)
        soft(cc, [(x - 20, -214), (x + 20, -214), (x + 18, -258), (x - 18, -258)], INK, seed=9734, u=1, n=2)
        line(cc, [(x - 38, -130), (x - 80, -160), (x - 90, -175)], BROWN, 4)
        line(cc, [(x + 38, -130), (x + 80, -150)], BROWN, 4)

    def kid_sled(cc):
        # Schlitten
        x0 = 20
        soft2(cc, [(x0 - 20, -40), (x0 + 210, -40), (x0 + 220, -58), (x0 - 10, -58)], RED, RED_D, (x0, -70), (x0 + 200, -30), seed=9740, u=1, n=2)
        line(cc, [(x0 - 30, -10), (x0 + 220, -10), (x0 + 250, -30), (x0 + 252, -48)], GOLD_D, 6)
        for sx in (x0 + 20, x0 + 170):
            line(cc, [(sx, -40), (sx, -10)], GOLD_D, 5)
        # Kind auf dem Schlitten
        soft2(cc, [(x0 + 40, -58), (x0 + 150, -58), (x0 + 140, -150), (x0 + 55, -150)], BLUE_L, BLUE, (x0 + 100, -170), (x0 + 100, -50), seed=9741, u=1.2, n=3)
        soft(cc, [(x0 + 120, -70), (x0 + 200, -64), (x0 + 205, -48), (x0 + 120, -50)], BLUE_D, seed=9742, u=1, n=3)
        child_head(cc, x0 + 98, -200, 50, 1.0, False, (0.3, 0.2), u=1.0, seed=230)
        soft(cc, [(x0 + 50, -228), (x0 + 146, -228), (x0 + 136, -270), (x0 + 98, -290), (x0 + 60, -270)], RED, seed=9743, u=1, n=4)
        dot(cc, x0 + 98, -292, 12, WHITE)
        piece(cc, rect_pts(x0 + 48, -236, 100, 14), WHITE, seed=9744, u=1, shadow=0.4, amp=0.4)
        soft(cc, [(x0 + 62, -150), (x0 + 136, -150), (x0 + 130, -136), (x0 + 66, -136)], GREEN_L, seed=9745, u=1, n=2)
        # Hund daneben
        dx = x0 + 260
        dc, dd = (0.90, 0.75, 0.55), (0.82, 0.64, 0.45)
        wag = math.sin(lt * 14) * 0.4
        cc.save()
        cc.translate(dx + 40, -40)
        cc.rotate(-0.5 + wag)
        soft(cc, [(0, -5), (45, -12), (50, -2), (0, 6)], dd, seed=9750, u=1, n=2)
        cc.restore()
        soft2(cc, ellipse_pts(dx, -60, 48, 58, n=30), dc, dd, (dx + 8, -130), (dx + 12, 0), seed=9751, u=1, n=1)
        soft2(cc, ellipse_pts(dx, -140, 42, 40, n=30), dc, dd, (dx + 8, -190), (dx + 10, -100), seed=9752, u=1, n=1)
        for sd in (-1, 1):
            soft(cc, [(dx + sd * 30, -168), (dx + sd * 46, -150), (dx + sd * 44, -100), (dx + sd * 34, -110)], (0.55, 0.36, 0.22), seed=9753 + sd, u=1, n=3)
        piece(cc, ellipse_pts(dx, -126, 22, 15), CREAM, seed=9755, u=1, shadow=0.4, amp=0.1)
        dot(cc, dx, -134, 6, INK)
        for ex in (-15, 15):
            dot(cc, dx + ex, -150, 5, INK)
            dot(cc, dx + ex - 1.5, -152, 1.7, WHITE)
        soft(cc, [(dx - 34, -98), (dx + 34, -98), (dx + 30, -88), (dx - 30, -88)], RED, seed=9756, u=1, n=2)

    lay(fs[0], hill)
    lay(fs[1], snowman)
    lay(fs[2], kid_sled)


def shot_popup(t, W, H):
    lt = t - 50.0
    tt = twos(lt)
    Ms = screen_matrix(W)
    zoom = 1 + 0.03 * lt / 3.5
    M = cairo.Matrix(*Ms)
    M.translate(960, 540)
    M.scale(zoom, zoom)
    M.translate(-960, -540)
    oa = ease(lt, 0.3, 1.0)
    a = oa * math.pi / 2
    t30 = 0.3 + 0.7 * 0.36
    fs = [spring(lin(tt, t30 + d, t30 + d + 1.1)) for d in (0.0, 0.12, 0.28)]
    popped = lin(lt, t30 + 0.15, t30 + 0.6)
    joy = lerp(0.35, 1.0, smooth(lin(lt, t30 + 0.4, t30 + 1.3)))

    def kid(c):
        sh = np.array([(1170, 1140), (1800, 1140), (1700, 840), (1260, 840)])
        piece2(c, sh, BLUE_L, BLUE, (1500, 800), (1530, 1150), seed=9800, u=2, shadow=1)
        pajama_dots(c, sh, 8, r=9, n=12)
        bounce = -abs(math.sin((lt - t30) * 7)) * 14 * math.exp(-(lt - t30) * 1.1) if popped > 0 else 0
        mo = clamp(1 - (lt - t30 - 0.15) * 1.6) * 0.9 if popped > 0 else 0
        look = (-0.9, 0.7) if popped < 0.5 else (-0.8, 0.2)
        child_head(c, 1490, 640 + bounce, 200, joy, False, look, u=2.6, seed=220, mouth_o=mo, tilt=-0.06 + 0.04 * math.sin(lt * 2))

    def card(c):
        bot = np.array([(HX0, HY), (HX1, HY), (HX1 + 50, FY_), (HX0 - 50, FY_)])
        piece(c, bot, mix(CREAM, CREAM2, 0.5), seed=9810, u=1.6, shadow=2)
        yfree = _bpt(a, DEPTH, HX0)[1]
        back = np.array([_bpt(a, 0, HX0), _bpt(a, 0, HX1), _bpt(a, DEPTH, HX1), _bpt(a, DEPTH, HX0)])
        if yfree > HY:
            p = piece(c, back, CREAM, seed=9811, u=1.6, shadow=1.2)
            c.save()
            path(c, p)
            c.clip()
            cx, cy = _bpt(a, DEPTH * 0.55, (HX0 + HX1) / 2)
            sq = (yfree - HY) / (FY_ - HY)
            c.translate(cx, cy)
            c.scale(1, max(sq, 0.05))
            line(c, [(-340, -200), (0, 40), (340, -200)], CREAM3, 3)
            piece(c, ellipse_pts(0, 40, 36, 36), RED, seed=9812, u=1, shadow=0.6)
            c.restore()
            # angesengte Ecke (auf das Papier beschnitten)
            c.save()
            path(c, p)
            c.clip()
            fx, fyy = _bpt(a, DEPTH, HX1)
            c.translate(fx - 10, fyy - 8 * sq)
            c.scale(1, max(sq, 0.1))
            path(c, deckle(ellipse_pts(0, 0, 44, 34, n=20), 9813, 1.5, 1.6))
            c.set_source_rgba(0.25, 0.14, 0.08, 0.85)
            c.fill()
            c.restore()
        else:
            p = piece(c, back, CREAM, seed=9814, u=1.6, shadow=1.6)
            c.save()
            path(c, p)
            c.clip()
            top_y = _bpt(a, DEPTH, HX0)[1]
            sq = (HY - top_y) / DEPTH
            c.translate(0, HY)
            c.scale(1, max(sq, 0.02))
            c.translate(0, -HY)
            draw_scribbles(c, scribble_pts(HX0 + 70, HY - DEPTH + 70, 540, 3, 44, seed=61, h=11), INK, 2.6, 1.0, alpha=0.85)
            path(c, deckle(ellipse_pts(HX1, HY - DEPTH, 52, 44, n=20), 9813, 1.5, 1.6))
            c.set_source_rgba(0.25, 0.14, 0.08, 0.85)
            c.fill()
            c.restore()
            k = clamp((90 - oa * 90) / 60)
            path(c, p)
            c.set_source_rgba(0.5, 0.35, 0.25, 0.12 * k)
            c.fill()
        line(c, [(HX0, HY), (HX1, HY)], CREAM3, 2)
        popup_scene(c, tt, fs)
        # Hände
        rel = smooth(lin(lt, 0.75, 1.3))
        for side, xx in ((-1, HX0), (1, HX1)):
            fx, fyy = _bpt(a, DEPTH, xx)
            rest = (HX0 - 110, 1030) if side < 0 else (HX1 + 120, 1030)
            hx = lerp(fx + side * 20, rest[0], rel)
            hy = lerp(fyy, rest[1], rel)
            sx = hx + (110 if side > 0 else -50)
            line(c, [(sx, 1200), (hx + 6 * side, hy + 20)], BLUE, 56)
            line(c, [(sx, 1200), (hx + 6 * side, hy + 20)], BLUE_L, 44)
            soft2(c, ellipse_pts(hx, hy, 36, 31, n=30), SKIN, SKIN_D, (hx + 10, hy - 50), (hx + 6, hy + 50), seed=9820 + side, u=1.4, n=1)
        if popped > 0:
            r = np.random.RandomState(5)
            for i in range(9):
                k = ((lt - t30) * 0.8 + r.uniform(0, 1)) % 1.0
                x = BASE[0] + r.uniform(-340, 340)
                y = BASE[1] - r.uniform(160, 440) - k * 50
                s = 18 * math.sin(k * math.pi) * popped
                if s > 0.5:
                    piece(c, star_pts(x, y, s, s * 0.35, 4), (1.0, 0.9, 0.55), seed=9830 + i, u=0.5, shadow=0.4, amp=0.05)

    layers = [Layer(lambda c: insert_bg(c), M, None, 1.2),
              Layer(kid, M, (10, 16, 22, 0.35), 1.2),
              Layer(card, M, (10, 16, 20, 0.38), 1.2)]
    surf, octx = compose(W, H, layers)
    octx.set_matrix(M)
    octx.save()
    octx.set_operator(cairo.OPERATOR_ADD)
    g = cairo.LinearGradient(0, 0, 900, 1080)
    g.add_color_stop_rgba(0, 1.0, 0.82, 0.55, 0.16)
    g.add_color_stop_rgba(1, 1.0, 0.82, 0.55, 0.0)
    octx.set_source(g)
    octx.paint()
    octx.restore()
    return surf


def shot_hug(t, W, H):
    lt = t - 53.5
    M = screen_matrix(W)
    sway = math.sin(lt * 2.2) * 0.06

    def kid(c):
        c.save()
        c.translate(960, 1100)
        c.rotate(sway * 0.5)
        c.translate(-960, -1100)
        sh = np.array([(620, 1150), (1300, 1150), (1200, 820), (720, 820)])
        piece2(c, sh, BLUE_L, BLUE, (980, 780), (1000, 1160), seed=9900, u=2, shadow=1)
        pajama_dots(c, sh, 9, r=10, n=14)
        child_head(c, 960, 600, 205, 1.0, False, (0, 0), u=2.6, seed=220, tilt=0.12 + sway)
        # Brief an die Brust gedrückt
        c.save()
        c.translate(960, 935)
        c.rotate(-0.08 + sway)
        p = piece(c, rect_pts(-170, -110, 340, 220), CREAM, seed=9901, u=2, shadow=1.4)
        line(c, [(-170, -108), (0, 10), (170, -108)], CREAM3, 3)
        piece(c, ellipse_pts(0, 14, 28, 28), RED, seed=9902, u=1, shadow=0.5)
        c.save()
        path(c, p)
        c.clip()
        path(c, deckle(ellipse_pts(170, 110, 46, 36, n=20), 9813, 1.5, 1.6))
        c.set_source_rgba(0.25, 0.14, 0.08, 0.85)
        c.fill()
        c.restore()
        c.restore()
        for side in (-1, 1):
            hx, hy = 960 + side * 175, 900 + 20 * side
            line(c, [(960 + side * 330, 1150), (hx, hy + 10)], BLUE, 64)
            line(c, [(960 + side * 330, 1150), (hx, hy + 10)], BLUE_L, 52)
            soft2(c, ellipse_pts(hx, hy, 40, 34, n=30), SKIN, SKIN_D, (hx + 10, hy - 50), (hx + 6, hy + 50), seed=9910 + side, u=1.4, n=1)
        c.restore()
        r = np.random.RandomState(12)
        for i in range(8):
            k = (lt * 0.6 + r.uniform(0, 1)) % 1
            x = 960 + r.uniform(-520, 520)
            y = 760 - k * 300 + r.uniform(-60, 60)
            s = 20 * math.sin(k * math.pi)
            if s > 0.5:
                if i % 2:
                    soft(c, heart_pts(x, y, s * 1.3, 24), RED_L, seed=9920 + i, u=0.6, n=1, shadow=0.4)
                else:
                    piece(c, star_pts(x, y, s, s * 0.35, 4), (1.0, 0.9, 0.55), seed=9930 + i, u=0.5, shadow=0.4, amp=0.05)
    layers = [Layer(lambda c: insert_bg(c), M, None, 1.2), Layer(kid, M, (10, 16, 22, 0.38), 1.2)]
    surf, octx = compose(W, H, layers)
    octx.set_matrix(M)
    glow(octx, 700, 300, 900, (1.0, 0.8, 0.5), 0.14)
    return surf


def shot_keyhole(t, W, H):
    cam = camk(t, [(55.0, 674, 1014, 11.0), (56.0, 676, 1015, 12.5)])
    st = base_st(t, cam[0])
    st['gdoor_lit'] = 0.9
    kx, ky = GD[0] + (GD[1] - GD[0]) * 0.72, GD[2] + 46
    blink = 55.45 < t < 55.6

    def eye(c):
        c.save()
        path(c, catmull(np.array([(0, -5), (2.6, -3.8), (2.4, -0.5), (2.6, 6), (-2.6, 6), (-2.4, -0.5), (-2.6, -3.8)]), 4) + (kx, ky))
        c.clip()
        ox = 0.6 * math.sin(t * 3)
        if not blink:
            dot(c, kx + ox, ky - 1.8, 2.1, (0.10, 0.07, 0.07))
            dot(c, kx + ox - 0.7, ky - 2.6, 0.7, WHITE)
            dot(c, kx + ox + 0.6, ky - 1.0, 0.25, WHITE)
        else:
            c.rectangle(kx - 4, ky - 6, 8, 10)
            c.set_source_rgb(*SKIN)
            c.fill()
            arc_stroke(c, kx + ox, ky - 1.8, 2.0, 0.15 * math.pi, 0.85 * math.pi, INK, 0.35)
        c.restore()
    return room_frame(t, W, H, cam, st, [eye])


def shot_final(t, W, H):
    cam = camk(t, [(56.0, 2060, 990, 3.0), (60.0, 2070, 990, 3.2)])
    st = base_st(t, cam[0])
    tt = twos(t)
    C = cp(mode='sleep', eyeF=0.55, eyeB=0.5, lid=0.55, pupil=0.4, ears=0.85, tail_ph=tt * 5, look=(1, -0.8), head_rot=-0.3)

    def catf(c):
        cat(c, 2110, 1062, C, 0.95, 1, t)

    def tiny(c):
        c.save()
        c.translate(1945, 1080)
        c.rotate(-0.06)
        piece(c, rect_pts(-12, -8, 24, 16), CREAM, seed=9950, u=0.35, shadow=1.0, amp=0.1)
        line(c, [(-12, -7.5), (0, 1), (12, -7.5)], CREAM3, 0.5)
        paw_seal(c, 0, 1.5, 4.2, RED)
        c.restore()
    surf = room_frame(t, W, H, cam, st, [catf, lambda c: basket(c, t, st, front=True), tiny])
    g = smooth(lin(t, 57.0, 58.0))
    if g > 0:
        octx = cairo.Context(surf)
        octx.set_source_rgba(0.12, 0.07, 0.05, 0.35 * g)
        octx.paint()
    return surf


SHOTS = [
    (0.0, 2.0, shot_establish),
    (2.0, 6.2, shot_room),
    (6.2, 8.0, shot_cal_door),
    (8.0, 12.0, shot_sneak),
    (12.0, 18.0, shot_storm),
    (18.0, 21.0, shot_cat_wakes),
    (21.0, 22.5, shot_freeze),
    (22.5, 25.0, shot_steal),
    (25.0, 32.0, shot_chase),
    (32.0, 34.8, shot_top),
    (34.8, 42.0, shot_flight),
    (42.0, 50.0, shot_landing),
    (50.0, 53.5, shot_popup),
    (53.5, 55.0, shot_hug),
    (55.0, 56.0, shot_keyhole),
    (56.0, 60.0, shot_final),
]


def render_frame(t, W, H):
    fn = SHOTS[-1][2]
    for a, b, f in SHOTS:
        if a <= t < b:
            fn = f
            break
    surf = fn(t, W, H)
    ctx = cairo.Context(surf)
    ctx.set_matrix(screen_matrix(W))
    for (a, b, txt) in TEXTS:
        k = banner_k(t, a, b)
        if k > 0:
            banner(ctx, txt, k)
    flutter = 1.0 + 2.0 * storm_at(t)
    url_tag(ctx, t, grow=lin(t, 57.0, 58.0), flutter=flutter, sub=lin(t, 57.8, 58.4))
    img = to_array(surf, W, H)
    img *= post(W, H)
    if t > 59.6:
        img *= 1 - 0.0 * lin(t, 59.6, 60)
    return np.clip(img, 0, 255).astype(np.uint8)


_post = {}


def post(W, H):
    if (W, H) not in _post:
        r = np.random.RandomState(3)
        g = r.randn(H // 2 + 1, W // 2 + 1).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)[:H, :W]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx / W - 0.5) ** 2 * 1.2 + (yy / H - 0.5) ** 2 * 1.6)
        vig = 1 - 0.30 * np.clip(d * 2.2, 0, 1) ** 1.6
        _post[(W, H)] = ((1 + 0.016 * g) * vig)[:, :, None].astype(np.float32)
    return _post[(W, H)]
