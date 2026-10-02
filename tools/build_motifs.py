#!/usr/bin/env python3
"""Generate the motif layer (assets/motifs/*.svg).

TEST-RUN ARTWORK. These are procedurally drawn placeholders in the spirit of the Design document
(monochrome block-print line drawings, no shading, carved weight variation). Final artwork is to be
made with Nepali Mithila / embroidery artists; drop replacement SVGs into assets/motifs/ using the same
file names and the same conventions:
  - single color via currentColor (the page sets it: white on orange sections, #CC5500 on white)
  - no fills except 'none'
  - classes the motion layer hooks into: .shuttle  .layer-1/2/3  .mat-flat  and stitches carrying style="--i:N"
"""
import math, random, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "motifs"
OUT.mkdir(parents=True, exist_ok=True)
R = random.Random(11)


def f(n):
    return str(int(round(n)))


def jit(pts, a=1.1):
    return [(x + R.uniform(-a, a), y + R.uniform(-a, a)) for x, y in pts]


def smooth(pts, closed=False):
    """Catmull-Rom through points -> cubic Bezier path data."""
    n = len(pts)
    if n < 3:
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)
    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d + ("Z" if closed else "")


def path(pts, w=None, closed=False, a=1.0, cls="", extra=""):
    w = w if w is not None else R.choice([1.6, 2, 2.4, 3])
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{smooth(jit(pts, a), closed)}" stroke-width="{w}"{extra}/>'


def line(x1, y1, x2, y2, w=None, extra=""):
    w = w if w is not None else R.choice([1.4, 1.8, 2.2])
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke-width="{w}"{extra}/>'


def circle(cx, cy, r, w=2):
    pts = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [i * math.pi / 6 for i in range(12)]]
    return path(pts, w=w, closed=True, a=r * 0.015)


def ellipse(cx, cy, rx, ry, rot=0, w=2, n=14):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return path(pts, w=w, closed=True, a=0.6)


def rot_pt(x, y, ang, ox=0, oy=0):
    c, s = math.cos(ang), math.sin(ang)
    return (ox + x * c - y * s, oy + x * s + y * c)


def leaf(cx, cy, ang, length, width, veins=True):
    """Lens-shaped leaf pointing along `ang` (radians), base at cx,cy. Double outline + vein + hatch."""
    out = []
    for k, scale in enumerate((1.0, 0.72)):
        L, W = length * scale, width * scale
        b = rot_pt(0, 0, ang, cx, cy)
        up = [rot_pt(L * t, -W * math.sin(math.pi * t) ** 0.8, ang, cx, cy) for t in (0, .2, .45, .7, .9, 1)]
        dn = [rot_pt(L * t, W * math.sin(math.pi * t) ** 0.8, ang, cx, cy) for t in (1, .9, .7, .45, .2, 0)]
        out.append(path(up + dn[1:], w=2.6 if k == 0 else 1.4, closed=True, a=.7))
    tip = rot_pt(length * .96, 0, ang, cx, cy)
    out.append(line(cx, cy, tip[0], tip[1], w=1.6))
    if veins:
        for t in (.25, .4, .55, .7, .84):
            for s in (-1, 1):
                a0 = rot_pt(length * t, 0, ang, cx, cy)
                a1 = rot_pt(length * (t + .1), s * width * .55 * math.sin(math.pi * t), ang, cx, cy)
                out.append(line(a0[0], a0[1], a1[0], a1[1], w=1.2))
    return "".join(out)


def svg(vb, body, extra=""):
    box = vb if len(vb) == 4 else (0, 0, vb[0], vb[1])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box[0]} {box[1]} {box[2]} {box[3]}" fill="none" stroke="currentColor" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"{extra}>{body}</svg>')


def write(name, vb, body, extra=""):
    (OUT / f"{name}.svg").write_text(svg(vb, body, extra), encoding="utf-8")


# ---------------------------------------------------------------- hemp
def hemp():
    b = []
    for ox, h, lean in ((70, 330, -10), (170, 395, 4), (265, 300, 12)):
        base = (ox, 430)
        top = (ox + lean, 430 - h)
        mid = [(ox + lean * t + math.sin(t * 5) * 3, 430 - h * t) for t in (0, .25, .5, .75, 1)]
        b.append(path(mid, w=3))
        b.append(path([(x + 7, y) for x, y in mid], w=1.6))
        for i, t in enumerate((.18, .36, .54, .72)):
            x, y = ox + lean * t, 430 - h * t
            b.append(line(x - 4, y, x + 11, y, w=1.6))
            s = -1 if i % 2 else 1
            b.append(leaf(x + 3, y, math.radians(-90 + s * 62), 54 - i * 5, 11, veins=False))
        # palmate crown
        for a in (-80, -52, -26, 0, 26, 52, 80):
            L = 98 - abs(a) * .55 + R.uniform(-4, 4)
            b.append(leaf(top[0], top[1], math.radians(-90 + a), L, 13))
        for k in range(4):
            gx = ox - 16 + k * 10
            b.append(line(gx, 432, gx + R.uniform(-8, 8), 446, w=1.4))
    b.append(path([(0, 432), (110, 430), (230, 434), (330, 431)], w=2.4))
    for x in range(8, 330, 14):
        b.append(line(x, 440, x + 6, 440, w=1.6))
    write("hemp", (0, -90, 340, 560), "".join(b))


# ---------------------------------------------------------------- retting tub
def ret():
    b = [ellipse(150, 150, 120, 30, w=3), ellipse(150, 150, 108, 24, w=1.4)]
    b.append(path([(30, 150), (42, 300), (70, 345)], w=3))
    b.append(path([(270, 150), (258, 300), (230, 345)], w=3))
    b.append(path([(70, 345), (150, 362), (230, 345)], w=3))
    for y in (190, 225, 260, 295):  # staves
        b.append(path([(36 + (y - 150) * .04, y), (150, y + 14), (264 - (y - 150) * .04, y)], w=1.4))
    for i in range(7):  # fibre hanks drooping over the rim
        x = 70 + i * 26
        b.append(path([(x, 140), (x + 8, 100 - i % 3 * 8), (x - 4, 62 - i % 2 * 14)], w=2))
        b.append(path([(x + 5, 142), (x + 15, 104 - i % 3 * 8), (x + 3, 70 - i % 2 * 14)], w=1.2))
    for r in (40, 70, 100):
        b.append(ellipse(150, 152, r, r * .22, w=1.2))
    for k in range(5):
        b.append(path([(60 + k * 45, 410), (80 + k * 45, 400), (100 + k * 45, 410)], w=1.6))
    write("ret", (300, 430), "".join(b))


# ---------------------------------------------------------------- drop spindle + hank
def spin():
    b = []
    cx, cy = 150, 300
    b.append(line(cx, 60, cx, 430, w=3))
    b.append(circle(cx, cy, 62, w=3))
    b.append(circle(cx, cy, 52, w=1.4))
    for i in range(16):  # whorl petals
        a = i * math.pi / 8
        p0 = (cx + 14 * math.cos(a), cy + 14 * math.sin(a))
        p1 = (cx + 48 * math.cos(a), cy + 48 * math.sin(a))
        b.append(line(p0[0], p0[1], p1[0], p1[1], w=1.4))
    b.append(circle(cx, cy, 12, w=2))
    for k in range(10):  # thread wound on shaft
        y = 90 + k * 10
        b.append(path([(cx - 9, y), (cx, y + 5), (cx + 9, y)], w=1.4))
    b.append(path([(cx, 60), (cx + 40, 36), (cx + 90, 70), (cx + 120, 30), (cx + 140, 10)], w=1.8))
    for k in range(5):
        y = 380 + k * 10
        b.append(path([(cx - 5, y), (cx + 4, y + 4)], w=1.4))
    write("spin", (300, 450), "".join(b))


def hank():
    b = [path([(10, 40), (150, 36), (290, 42)], w=3.4), path([(10, 50), (150, 46), (290, 52)], w=1.4)]
    for x in (60, 150, 240):
        for k in range(9):
            b.append(path([(x - 22 + k * 1.5, 46), (x - 30 + k * 3, 120), (x - 24 + k * 3.4, 200),
                           (x + 6 + k * 2, 240), (x + 22 + k * 1.5, 200), (x + 28, 120), (x + 22, 46)], w=1.3, a=.5))
    write("hank", (300, 260), "".join(b))


# ---------------------------------------------------------------- hands holding thread
def hand(tx, ty, rot=0, mirror=False):
    """One open hand, fingers up, thumb to the right. Outline smoothed through hand-placed points."""
    pts = [(-30, 70), (-38, 10), (-40, -40), (-38, -72), (-34, -100), (-26, -108), (-18, -100), (-17, -76),
           (-17, -118), (-9, -130), (-1, -118), (-1, -80), (0, -134), (9, -146), (18, -134), (18, -80),
           (19, -120), (27, -132), (35, -120), (36, -70), (40, -40), (46, -34), (64, -52), (80, -80),
           (88, -86), (93, -76), (78, -36), (54, 0), (36, 28), (30, 70)]
    g = [path(pts, w=3, a=.4)]
    # inner contour offset toward the palm centre (the doubled line of block prints)
    inner = [(x * .86, (y + 30) * .86 - 30) for x, y in pts[:-3]]
    g.append(path(inner, w=1.2, a=.5))
    for (x, y, wd) in ((-26, -78, 14), (-9, -92, 14), (9, -100, 14), (27, -90, 14)):  # finger joints
        g.append(line(x - wd / 2, y, x + wd / 2, y + 1, w=1.2))
        g.append(line(x - wd / 2, y - 22, x + wd / 2, y - 21, w=1.2))
    for k in range(4):  # palm lines
        g.append(path([(-24 + k * 9, -34 + k * 3), (-12 + k * 9, -14), (-6 + k * 9, 14)], w=1.1, a=.5))
    for yy in (52, 60, 68):  # bangles at the wrist
        g.append(path([(-32, yy), (0, yy + 5), (32, yy)], w=2.4 if yy == 60 else 1.4, a=.4))
    for k in range(9):
        g.append(line(-26 + k * 6.5, 54, -24 + k * 6.5, 58, w=1))
    tr = f"translate({tx} {ty}) rotate({rot})" + (" scale(-1 1)" if mirror else "")
    return f'<g transform="{tr}">{"".join(g)}</g>'


def hands():
    b = [hand(150, 330, 28), hand(350, 330, -28, mirror=True)]
    cx, cy, r = 250, 150, 78
    b.append(circle(cx, cy, r, w=3))
    for k in range(-5, 6):  # thread wound round a ball: nested arcs
        pts = [(cx + r * math.sin(t) * math.cos(k * .26), cy - r * math.cos(t) * .9 + k * 5 + R.uniform(-.6, .6)) for t in (-1.35, -.7, 0, .7, 1.35)]
        b.append(path(pts, w=1.2, a=.4))
    for k in range(12):
        a0 = k * math.pi / 6
        b.append(line(cx + 70 * math.cos(a0), cy + 70 * math.sin(a0), cx + 80 * math.cos(a0 + .2), cy + 80 * math.sin(a0 + .2), w=1.2))
    b.append(path([(cx + 60, cy - 50), (cx + 120, cy - 70), (cx + 150, cy - 40), (cx + 190, cy - 80)], w=1.8))
    write("hands", (500, 360), "".join(b))


# ---------------------------------------------------------------- spool
def spool():
    b = [ellipse(150, 70, 100, 26, w=3), ellipse(150, 70, 86, 20, w=1.4),
         ellipse(150, 330, 100, 26, w=3), ellipse(150, 330, 86, 20, w=1.4)]
    b += [line(50, 70, 50, 330, w=3), line(250, 70, 250, 330, w=3)]  # (hidden by body lines below, reads as flange cheeks)
    b = b[:4] + [path([(50, 70), (46, 200), (50, 330)], w=3), path([(250, 70), (254, 200), (250, 330)], w=3)]
    # winding: crossed diagonals
    for k in range(26):
        x0 = 74 + k * 6.6
        b.append(path([(x0, 92), (x0 + 16 + R.uniform(-2, 2), 210), (x0 - 4, 308)], w=1.3, a=.5))
    for k in range(14):
        x0 = 80 + k * 12.5
        b.append(path([(x0, 306), (x0 - 18, 200), (x0 + 4, 96)], w=1.1, a=.5))
    for k in range(18):  # flange radial ticks
        a = k * math.pi / 9
        b.append(line(150 + 90 * math.cos(a), 70 + 22 * math.sin(a), 150 + 100 * math.cos(a), 70 + 26 * math.sin(a), w=1.2))
    b.append(path([(250, 330), (280, 360), (250, 392), (200, 396), (170, 380)], w=2))
    write("spool", (320, 410), "".join(b))


# ---------------------------------------------------------------- loom (+ shuttle)
def loom():
    b = []
    # posts, beams
    for x in (30, 470):
        b.append(path([(x, 20), (x + 2, 200), (x - 2, 380)], w=4))
        b.append(path([(x + 14, 20), (x + 16, 200), (x + 12, 380)], w=1.6))
        for y in range(40, 370, 22):
            b.append(line(x + 3, y, x + 12, y + 2, w=1.2))
    b.append(path([(24, 30), (250, 24), (484, 30)], w=4))
    b.append(path([(24, 46), (250, 40), (484, 46)], w=1.6))
    b.append(path([(24, 368), (250, 372), (484, 368)], w=4))
    # warp threads
    for x in range(58, 450, 7):
        top = 50
        bot = 250 + (x % 5) * 1.5
        b.append(line(x, top, x, bot, w=1.1))
    # reed / beater
    b.append(path([(50, 150), (250, 146), (450, 150)], w=3))
    b.append(path([(50, 176), (250, 172), (450, 176)], w=3))
    for x in range(64, 440, 14):
        b.append(line(x, 150, x, 176, w=1.4))
    # woven cloth in bands of varied rhythm
    y = 258
    rhythms = [(2, 1), (1, 0), (3, 2), (1, 0), (2, 1), (4, 3)]
    for i, (a, g) in enumerate(rhythms):
        yy = y + i * 18
        b.append(path([(58, yy), (250, yy + 2), (448, yy)], w=2.2))
        x = 60
        while x < 446:
            if i % 3 == 0:
                b.append(line(x, yy + 3, x + 4, yy + 15, w=1.2))
                x += 7
            elif i % 3 == 1:
                b.append(circle(x + 2, yy + 9, 1.4, w=1.6))
                x += 10
            else:
                b.append(line(x, yy + 9, x + 8, yy + 9, w=1.6))
                x += 13
    b.append(path([(58, 366), (250, 366), (448, 366)], w=2.4))
    # shuttle (boat) — moves with scroll
    sh = [path([(0, 0), (22, -9), (70, -9), (96, 0), (70, 9), (22, 9)], w=3, closed=True),
          line(18, 0, 78, 0, w=1.4), path([(6, 0), (-18, 6), (-34, 2)], w=1.6)]
    for x in (28, 44, 60):
        sh.append(line(x, -5, x + 3, 5, w=1.2))
    # the shuttle sits in the shed; the page slides it sideways as you scroll
    b.append(f'<g class="shuttle"><g transform="translate(200 163)">{"".join(sh)}</g></g>')
    write("loom", (500, 390), "".join(b))


# ---------------------------------------------------------------- sari strip pile (3 layers)
def sari():
    layers = {1: [], 2: [], 3: []}
    pat = ["hatch", "dots", "dash", "zig", "hatch", "dots", "dash", "zig", "hatch"]
    for i in range(9):
        y = 40 + i * 34
        L = layers[1 + i % 3]
        x0, x1 = 30 + R.uniform(0, 30), 380 - R.uniform(0, 30)
        top = [(x0 + (x1 - x0) * t / 5, y + math.sin(t * 1.3 + i) * 6) for t in range(6)]
        bot = [(x, yy + 24) for x, yy in top]
        L.append(path(top, w=2.6, a=.8))
        L.append(path(bot, w=2.6, a=.8))
        L.append(line(top[0][0], top[0][1], bot[0][0], bot[0][1], w=2))
        L.append(line(top[-1][0], top[-1][1], bot[-1][0], bot[-1][1], w=2))
        p = pat[i]
        x = x0 + 8
        while x < x1 - 8:
            yy = y + math.sin((x - x0) / (x1 - x0) * 5 * 1.3 + i) * 6
            if p == "hatch":
                L.append(line(x, yy + 3, x + 6, yy + 21, w=1.1)); x += 7
            elif p == "dots":
                L.append(circle(x, yy + 12, 1.6, w=1.8)); x += 11
            elif p == "dash":
                L.append(line(x, yy + 12, x + 9, yy + 12, w=1.6)); x += 15
            else:
                L.append(path([(x, yy + 20), (x + 5, yy + 5), (x + 10, yy + 20)], w=1.3, a=.3)); x += 12
    body = "".join(f'<g class="layer-{k}">{"".join(v)}</g>' for k, v in layers.items())
    write("sari", (410, 360), body)


# ---------------------------------------------------------------- sewing: needle + stitched line
def sewing():
    b = []
    # a long needle on the diagonal, tip pushed through the stitch line
    tip, eye = (214, 396), (40, 36)
    ang = math.atan2(tip[1] - eye[1], tip[0] - eye[0])
    L = math.hypot(tip[0] - eye[0], tip[1] - eye[1])
    up = [rot_pt(L * t, -9 * (1 - t) ** .6 * (1 if t > .06 else .6), ang, eye[0], eye[1]) for t in (0, .1, .35, .65, .9, 1)]
    dn = [rot_pt(L * t, 9 * (1 - t) ** .6 * (1 if t > .06 else .6), ang, eye[0], eye[1]) for t in (1, .9, .65, .35, .1, 0)]
    b.append(path(up + dn[1:], w=3.4, closed=True, a=.5))
    e = rot_pt(26, 0, ang, eye[0], eye[1])
    b.append(ellipse(e[0], e[1], 4, 12, rot=ang, w=2))
    mid = rot_pt(L * .5, 0, ang, eye[0], eye[1])
    b.append(line(e[0] + 20, e[1] + 14, mid[0], mid[1], w=1.4))
    # thread looping down from the eye
    b.append(path([e, (e[0] - 30, e[1] + 60), (e[0] + 18, e[1] + 120), (e[0] - 28, e[1] + 190), (e[0] + 10, e[1] + 260), (150, 372), (170, 414)], w=2, a=.8))
    # bound edge (two rules) with stitches revealed in sequence
    b.append(path([(110, 392), (300, 396), (700, 392)], w=3))
    b.append(path([(110, 436), (300, 440), (700, 436)], w=3))
    n = 36
    for i in range(n):
        x = 126 + i * 16
        b.append(f'<line class="stitch" x1="{x}" y1="{f(414 + R.uniform(-1, 1))}" x2="{x + 10}" y2="{f(414 + R.uniform(-1, 1))}" stroke-width="2.6" style="--i:{i}"/>')
    write("sewing", (720, 460), "".join(b))


# ---------------------------------------------------------------- the mat (hero unroll, vertical)
# Two pieces: a horizontal roll that spans the right half of the hero, and the sheet that hangs from it.
# The page slides the sheet down out of the roll as the visitor scrolls (translateY only).
def stripe_band(x0, x1, y, h, kind, w_hint=1.1):
    """One weft-faced stripe running across the mat, drawn as a line rhythm (block-print translation of colour)."""
    out = []
    mid = y + h / 2
    if kind == "hatch":                                    # dense ribbing
        yy = y + 1.2
        while yy < y + h:
            out.append(path([(x0, yy), ((x0 + x1) / 2, yy + R.uniform(-.5, .5)), (x1, yy)], w=w_hint, a=.2)); yy += 3.6
    elif kind == "open":                                   # open spacing: two firm lines, nothing between
        for yy in (y + 1.5, y + h - 1.5):
            out.append(path([(x0, yy), ((x0 + x1) / 2, yy + R.uniform(-.7, .7)), (x1, yy)], w=2.2, a=.2))
    elif kind == "dots":                                   # dotted runs
        rows = max(1, int(h // 9))
        for r in range(rows):
            yy = y + (r + .5) * h / rows
            out.append(dotpath([(xx + (5 if r % 2 else 0), yy) for xx in range(int(x0) + 6, int(x1) - 4, 10)], w=2.6))
    elif kind == "dash":                                   # dashed runs
        rows = max(1, int(h // 8))
        for r in range(rows):
            yy = y + (r + .5) * h / rows
            d = "".join(f"M{xx + (7 if r % 2 else 0)} {f(yy)}h9" for xx in range(int(x0) + 4, int(x1) - 14, 19))
            out.append(f'<path d="{d}" stroke-width="1.7"/>')
    elif kind == "zig":                                    # zig-zag
        amp = max(2.5, h / 2 - 2)
        out.append(path([(xx, mid + (amp if (k % 2) else -amp)) for k, xx in enumerate(range(int(x0) + 4, int(x1), 11))], w=1.5, a=.2))
    elif kind == "wave":
        amp = max(2.2, h / 2 - 2)
        out.append(path([(xx, mid + amp * math.sin(xx / 9.0)) for xx in range(int(x0) + 4, int(x1), 6)], w=1.6, a=.2))
    else:                                                  # double line with a dotted centre
        for yy in (y + 1.5, y + h - 1.5):
            out.append(line(x0, yy, x1, yy, w=1.4))
        out.append(dotpath([(xx, mid) for xx in range(int(x0) + 6, int(x1) - 4, 8)], w=2.4))
    out.append(line(x0, y + h + 1.5, x1, y + h + 1.5, w=0.9))   # fine seam between stripes
    return "".join(out)


def stripe_run(x0, x1, y_start, y_end, seed_kinds=None):
    kinds = ["hatch", "open", "dots", "dash", "hatch", "wave", "zig", "double", "hatch", "dots", "open", "dash"]
    out = []
    y = y_start
    i = 0
    while y < y_end - 8:
        h = R.choice([7, 9, 11, 14, 18, 24, 32])
        h = min(h, y_end - y - 3)
        kind = kinds[(i * 5 + R.randint(0, 2)) % len(kinds)]
        if kind in ("dots", "dash") and h < 9:
            h = 10
        out.append(stripe_band(x0, x1, y, h, kind))
        y += h + 3
        i += 1
    return "".join(out)


def mat_roll():
    """The rolled mat seen from the side: a thick cylinder whose stripes run along its length, the plain binding
    spiralling visibly at the open (left) end."""
    W, H = 600, 124
    b = []
    x0, x1, yt, yb = 48, 566, 8, 116
    b.append(path([(x0, yt), (300, yt - 2), (x1, yt)], w=3.4, a=.4))
    b.append(path([(x0, yb), (300, yb + 2), (x1, yb)], w=3.4, a=.4))
    # stripes along the roll body
    b.append(stripe_run(x0 + 26, x1 - 8, yt + 8, yb - 6))
    # right end: curve of the cylinder with the binding's edge
    b.append(path([(x1, yt), (x1 + 20, (yt + yb) / 2), (x1, yb)], w=3.4, a=.4))
    b.append(path([(x1 - 9, yt + 9), (x1 + 8, (yt + yb) / 2), (x1 - 9, yb - 9)], w=1.4, a=.3))
    # left end face: an ellipse; the cream binding spirals inwards as a plain double band between striped layers
    cy = (yt + yb) / 2
    rx, ry = 34, (yb - yt) / 2
    b.append(f'<ellipse cx="{x0}" cy="{f(cy)}" rx="{rx}" ry="{f(ry)}" style="fill:var(--orange)" stroke-width="3.4"/>')
    for k in range(0, 3):                                   # binding: two parallel spiral edges = a plain band
        pts_a, pts_b = [], []
        for n in range(0, 90):
            t = n / 89
            ang = t * 3.3 * 2 * math.pi
            rr = 1 - t * .92
            pts_a.append((x0 + rx * rr * math.cos(ang), cy + ry * rr * math.sin(ang)))
            rr2 = rr - .055
            pts_b.append((x0 + rx * rr2 * math.cos(ang), cy + ry * rr2 * math.sin(ang)))
        if k == 0:
            b.append(path(pts_a, w=2.4, a=.2)); b.append(path(pts_b, w=2.4, a=.2))
    for n in range(40):                                     # the striped layers between the turns, as short dashes
        t = n / 40
        ang = t * 3.3 * 2 * math.pi + .26
        rr = (1 - t * .92) - .03
        px, py = x0 + rx * rr * math.cos(ang), cy + ry * rr * math.sin(ang)
        b.append(dotpath([(px, py)], w=2.2))
    write("mat-roll", (W, H), "".join(b))


def mat_sheet():
    """The unrolled mat: weft-faced stripes across the short way, plain cream binding on every side, knotted fringe at the free end."""
    W, H = 600, 640
    b = []
    xo0, xo1 = 34, 566            # outer edge of the binding
    bw = 15                       # binding width
    xi0, xi1 = xo0 + bw, xo1 - bw
    yb0, yb1 = 570, 586           # bottom binding
    # binding on both long edges and the free end: plain band (outer line, inner line, a fine stitch line down the middle)
    for xo, xi in ((xo0, xi0), (xo1, xi1)):
        b.append(path([(xo, -4), (xo + R.uniform(-1, 1), 300), (xo, yb1)], w=3.4, a=.5))
        b.append(path([(xi, -4), (xi + R.uniform(-1, 1), 300), (xi, yb0)], w=1.6, a=.4))
        xm = (xo + xi) / 2
        b.append(f'<path d="' + "".join(f"M{f(xm)} {y}v6" for y in range(0, yb1 - 8, 14)) + '" stroke-width="1"/>')
    b.append(path([(xo0, yb1), (300, yb1 + 2), (xo1, yb1)], w=3.4, a=.5))
    b.append(path([(xi0, yb0), (300, yb0 + 1), (xi1, yb0)], w=1.6, a=.4))
    b.append(f'<path d="' + "".join(f"M{x} {f((yb0 + yb1) / 2)}h6" for x in range(int(xi0) + 6, int(xi1) - 6, 14)) + '" stroke-width="1"/>')
    # the stripe field
    b.append(stripe_run(xi0 + 3, xi1 - 3, 4, yb0 - 4))
    # knotted fringe: strands gathered into small knots
    for k in range(18):
        cx = xo0 + 12 + k * (xo1 - xo0 - 24) / 17
        for d in (-4, 0, 4):
            b.append(path([(cx + d, yb1), (cx + d * 1.6 + R.uniform(-1, 1), yb1 + 22), (cx + d * 2.2 + R.uniform(-2, 2), yb1 + 40)], w=1.5, a=.4))
        b.append(f'<path d="M{f(cx - 5)} {yb1 + 8}q5 7 10 0" stroke-width="2.2"/>' + dotpath([(cx, yb1 + 12)], w=4))
    write("mat-sheet", (W, H), "".join(b), extra=' preserveAspectRatio="none"')


# ---------------------------------------------------------------- water, leaves, bloom, rosette
def water():
    b = []
    for k in range(7):
        y = 40 + k * 30
        pts = [(x, y + math.sin(x / 38 + k * .9) * 11) for x in range(0, 601, 50)]
        b.append(path(pts, w=[3, 1.6, 2.4][k % 3], a=.5))
        if k % 2 == 0:
            pts2 = [(x + 14, y + 10 + math.sin(x / 38 + k * .9) * 11) for x in range(0, 560, 50)]
            b.append(path(pts2, w=1.2, a=.5))
    for (x, y) in ((90, 20), (300, 6), (500, 18)):
        b.append(path([(x, y - 14), (x - 8, y + 4), (x, y + 10), (x + 8, y + 4), (x, y - 14)], w=2, closed=False))
    write("water", (600, 250), "".join(b))


def leaves():
    b = []
    spec = [(60, 80, 30, 110, 24), (210, 40, 150, 90, 20), (330, 150, -30, 130, 28), (130, 240, 80, 100, 22), (300, 320, 200, 120, 26)]
    for (x, y, a, L, W) in spec:
        b.append(leaf(x, y, math.radians(a), L, W))
    for k in range(6):
        b.append(circle(30 + k * 62, 380 + (k % 2) * 14, 3, w=1.8))
    write("leaves", (420, 420), "".join(b))


def petals(cx, cy, n, r0, r1, w, rot=0.0, double=True):
    out = []
    for k in range(n):
        a = rot + k * 2 * math.pi / n
        L = r1 - r0
        def P(t, s):
            x, y = r0 + L * t, s * w * math.sin(math.pi * t) ** .8
            return rot_pt(x, y, a, cx, cy)
        up = [P(t, -1) for t in (0, .25, .55, .85, 1)]
        dn = [P(t, 1) for t in (1, .85, .55, .25, 0)]
        out.append(path(up + dn[1:], w=2.4, closed=True, a=.6))
        if double:
            tip = rot_pt(r0 + L * .86, 0, a, cx, cy)
            base = rot_pt(r0 + L * .18, 0, a, cx, cy)
            out.append(line(base[0], base[1], tip[0], tip[1], w=1.2))
    return "".join(out)


def bloom():
    b = [petals(200, 200, 14, 60, 190, 20, rot=.1), petals(200, 200, 10, 36, 140, 22, rot=.3),
         petals(200, 200, 8, 14, 84, 15, rot=.0), circle(200, 200, 16, w=2.6)]
    for k in range(18):
        a = k * math.pi / 9
        b.append(line(200 + 24 * math.cos(a), 200 + 24 * math.sin(a), 200 + 38 * math.cos(a), 200 + 38 * math.sin(a), w=1.3))
    write("bloom", (400, 400), "".join(b))


def rosette():
    b = [circle(100, 100, 94, w=2.4), circle(100, 100, 86, w=1.2)]
    for k in range(24):
        a = k * math.pi / 12
        b.append(line(100 + 86 * math.cos(a), 100 + 86 * math.sin(a), 100 + 94 * math.cos(a), 100 + 94 * math.sin(a), w=1.3))
    b.append(petals(100, 100, 12, 30, 80, 12, rot=.1))
    b.append(petals(100, 100, 6, 10, 46, 9, rot=.5, double=False))
    b.append(circle(100, 100, 8, w=2.4))
    write("rosette", (200, 200), "".join(b))


# ---------------------------------------------------------------- embroidery border (stitches draw in)
def border():
    b = []
    W, H = 1200, 80
    b.append(line(0, 14, W, 14, w=2.4))
    b.append(line(0, 66, W, 66, w=2.4))
    # running stitch rules above and below
    i = 0
    for x in range(0, W, 16):
        b.append(f'<line class="stitch" x1="{x}" y1="22" x2="{x + 9}" y2="22" stroke-width="2" style="--i:{i}"/>')
        b.append(f'<line class="stitch" x1="{x}" y1="58" x2="{x + 9}" y2="58" stroke-width="2" style="--i:{i}"/>')
        i += 1
    n = 12
    step = W / n
    for k in range(n):
        cx = step * (k + .5)
        # diamond lotus unit
        b.append(f'<g class="stitch" style="--i:{int(k * 75 / n)}">' + path([(cx, 26), (cx + 24, 40), (cx, 54), (cx - 24, 40)], w=2.4, closed=True, a=.5)
                 + path([(cx, 32), (cx + 15, 40), (cx, 48), (cx - 15, 40)], w=1.2, closed=True, a=.4)
                 + circle(cx, 40, 3, w=1.8)
                 + line(cx - 38, 40, cx - 28, 40, w=2) + line(cx + 28, 40, cx + 38, 40, w=2) + '</g>')
    write("border", (W, H), "".join(b))


def favicon():
    pts = [(32 + (4 + k * .92) * math.cos(k * .5), 32 + (4 + k * .92) * math.sin(k * .5)) for k in range(0, 44)]
    body = f'<rect width="64" height="64" rx="10" fill="#CC5500" stroke="none"/>' \
           f'<path d="{smooth(pts)}" stroke="#fff" stroke-width="3.4" fill="none"/>'
    (OUT.parent / "favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" stroke-linecap="round">{body}</svg>', encoding="utf-8")



# =====================================================================================================
# Mithila (Madhubani) and thangka-inspired motifs. Test-run drawings: dense double outlines, hatch / dot /
# scale fills, eyed feathers and fish, flame and cloud scrolls. Final artwork is to come from Nepali artists.
# =====================================================================================================
def dotpath(pts, w=2.4):
    d = "".join(f"M{f(x)} {f(y)}h0" for x, y in pts)
    return f'<path d="{d}" stroke-width="{w}"/>' if d else ""


def hatch_lines(x0, y0, x1, y1, ang, gap, w=1.1):
    """Parallel lines at `ang` degrees across a box (use inside a clipPath)."""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = math.hypot(x1 - x0, y1 - y0) / 2 + 4
    d, k = "", -L
    while k <= L:
        px, py = cx + nx * k, cy + ny * k
        d += f"M{f(px - dx * L)} {f(py - dy * L)}L{f(px + dx * L)} {f(py + dy * L)}"
        k += gap
    return f'<path d="{d}" stroke-width="{w}"/>'


_clip = [0]


def clipped(prefix, shape_pts, inner, a=.0):
    _clip[0] += 1
    cid = f"{prefix}{_clip[0]}"
    return (f'<clipPath id="{cid}"><path d="{smooth(shape_pts, True)}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{inner}</g>')


def lens_pts(x0, x1, cy, h, n=7, skew=0.0):
    up = [(x0 + (x1 - x0) * t, cy - h * math.sin(math.pi * t) ** .75 * (1 - skew * (t - .5))) for t in [i / (n - 1) for i in range(n)]]
    dn = [(x0 + (x1 - x0) * t, cy + h * math.sin(math.pi * t) ** .75 * (1 + skew * (t - .5))) for t in [1 - i / (n - 1) for i in range(n)]]
    return up + dn[1:-1]


def scales(x0, x1, y0, y1, step=18, w=1.3):
    d = ""
    r = 0
    y = y0
    while y < y1:
        x = x0 + (step / 2 if r % 2 else 0)
        while x < x1:
            d += f"M{f(x)} {f(y)}q{f(step / 2)} {f(step * .8)} {f(step)} 0"
            x += step
        y += step * .55
        r += 1
    return f'<path d="{d}" stroke-width="{w}"/>'


def eye(cx, cy, r, w=2.2):
    return circle(cx, cy, r, w=w) + circle(cx, cy, r * .5, w=1.6) + dotpath([(cx, cy)], w=r * .35)


# ---------------------------------------------------------------- fish (Mithila)
def fish():
    b = []
    body = lens_pts(110, 372, 120, 62, n=9, skew=.18)
    b.append(path(body, w=3.4, closed=True, a=.5))
    inner = [(110 + (x - 110) * .9 + 12, 120 + (y - 120) * .84) for x, y in body]
    b.append(path(inner, w=1.4, closed=True, a=.4))
    b.append(clipped("fs", inner, scales(112, 372, 76, 170, 17, 1.2) + hatch_lines(250, 60, 372, 180, 70, 7, .9)))
    for k in range(5):                                            # gill arcs
        b.append(path([(284 - k * 4, 84 + k * 2), (292 - k * 5, 120), (284 - k * 4, 158 - k * 2)], w=1.4, a=.4))
    b.append(eye(332, 104, 15))
    b.append(path([(372, 122), (362, 128), (352, 126)], w=2, a=.3))  # mouth
    # dorsal fin
    for k in range(5):
        x = 170 + k * 28
        b.append(path([(x, 70 - k * 1.5), (x + 6, 20 + abs(k - 2) * 8), (x + 22, 62 - k)], w=2, a=.4))
        b.append(line(x + 8, 62 - k, x + 11, 34 + abs(k - 2) * 8, w=1))
    # belly fins
    for k in range(3):
        x = 200 + k * 30
        b.append(path([(x, 172), (x - 10, 205), (x + 18, 184)], w=2, a=.4))
    # tail, with radial hatching
    tail = [(112, 120), (70, 58), (30, 28), (44, 76), (22, 120), (44, 164), (30, 212), (70, 182)]
    b.append(path(tail, w=3, closed=True, a=.6))
    for k in range(7):
        a = math.radians(-28 + k * 9.3)
        b.append(line(108, 120, 108 - math.cos(a) * 80, 120 + math.sin(a) * 86, w=1.2))
    for (x, y, r) in ((402, 84, 6), (414, 58, 4), (396, 40, 3)):    # bubbles
        b.append(circle(x, y, r, w=1.6))
    write("fish", (430, 240), "".join(b))


# ---------------------------------------------------------------- peacock (Mithila) — feathers open with scroll
def peacock():
    b = []
    ox, oy = 250, 330
    feathers = []
    for k in range(-6, 7):
        g = []
        L = 245 - abs(k) * 6
        # feather: tall lens pointing up from the body, double outline, eyed tip, comb hatching
        pts_up = [(-13 * math.sin(math.pi * t) ** .8, -L * t) for t in (0, .15, .4, .7, .9, 1)]
        pts_dn = [(13 * math.sin(math.pi * t) ** .8, -L * t) for t in (1, .9, .7, .4, .15, 0)]
        g.append(path([(ox + x, oy + 40 + y) for x, y in pts_up + pts_dn[1:]], w=2.2, closed=True, a=.5))
        g.append(line(ox, oy + 40, ox, oy + 40 - L * .8, w=1.1))
        for q in range(1, 9):
            y = oy + 40 - L * .08 * q * 1.6
            g.append(line(ox, y, ox - 11 * math.sin(math.pi * q / 11), y - 6, w=.9))
            g.append(line(ox, y, ox + 11 * math.sin(math.pi * q / 11), y - 6, w=.9))
        ey = oy + 40 - L * .84
        g.append(ellipse(ox, ey, 11, 15, w=1.8, n=12))
        g.append(ellipse(ox, ey + 1, 6, 9, w=1.4, n=10))
        g.append(dotpath([(ox, ey + 2)], w=5))
        feathers.append(f'<g class="feather" style="--k:{k}">{"".join(g)}</g>')
    b.append("".join(feathers))
    # body with scale rows
    body = [(ox + 52 * math.cos(t), oy + 64 * math.sin(t)) for t in [i * math.pi / 8 for i in range(16)]]
    b.append(path(body, w=3.4, closed=True, a=.5))
    b.append(path([(ox + 44 * math.cos(t), oy + 56 * math.sin(t)) for t in [i * math.pi / 8 for i in range(16)]], w=1.2, closed=True, a=.4))
    d = ""
    yy = oy - 44
    r = 0
    while yy < oy + 46:
        half = 44 * math.sqrt(max(0, 1 - ((yy - oy) / 58) ** 2)) - 6
        x = ox - half + (7 if r % 2 else 0)
        while x < ox + half - 8:
            d += f"M{f(x)} {f(yy)}q7 10 14 0"
            x += 14
        yy += 9
        r += 1
    b.append(f'<path d="{d}" stroke-width="1.2"/>')
    # neck, head, crest
    neck = [(ox + 22, oy - 40), (ox + 46, oy - 90), (ox + 30, oy - 140), (ox + 56, oy - 180)]
    b.append(path(neck, w=3.4, a=.5))
    b.append(path([(x + 16, y + 6) for x, y in neck], w=3.4, a=.5))
    for k in range(5):
        b.append(path([(ox + 40 + k * 2, oy - 60 - k * 22), (ox + 55 + k * 2, oy - 66 - k * 22)], w=1.2, a=.3))
    b.append(circle(ox + 66, oy - 192, 17, w=3))
    b.append(eye(ox + 70, oy - 196, 6, w=1.6))
    b.append(path([(ox + 83, oy - 190), (ox + 108, oy - 184), (ox + 84, oy - 178)], w=2.4, closed=True, a=.3))
    for k, ang in enumerate((-70, -92, -114)):
        a = math.radians(ang)
        b.append(line(ox + 66, oy - 208, ox + 66 + math.cos(a) * 34, oy - 208 + math.sin(a) * 34, w=1.6))
        b.append(circle(ox + 66 + math.cos(a) * 40, oy - 208 + math.sin(a) * 40, 5, w=1.6))
    # legs and ground
    for lx in (ox - 14, ox + 18):
        b.append(line(lx, oy + 64, lx, oy + 112, w=2.6))
        for tx in (-14, 0, 14):
            b.append(line(lx, oy + 112, lx + tx, oy + 124, w=2))
    b.append(path([(ox - 130, oy + 128), (ox, oy + 130), (ox + 130, oy + 128)], w=2.4, a=.6))
    b.append(dotpath([(ox - 120 + i * 16, oy + 140) for i in range(16)], w=2.2))
    write("peacock", (500, 480), "".join(b))


# ---------------------------------------------------------------- rayed sun (Mithila)
def sun():
    b = []
    cx = cy = 250
    for k in range(20):
        a = k * 2 * math.pi / 20
        # straight triangular ray, double outline + hatch
        b.append(path([rot_pt(100, -15, a, cx, cy), rot_pt(210, 0, a, cx, cy), rot_pt(100, 15, a, cx, cy)], w=2.4, closed=False, a=.5))
        b.append(path([rot_pt(116, -7, a, cx, cy), rot_pt(190, 0, a, cx, cy), rot_pt(116, 7, a, cx, cy)], w=1.1, a=.4))
        for q in (130, 148, 166):
            p0, p1 = rot_pt(q, -9 + (q - 130) * .15, a, cx, cy), rot_pt(q, 9 - (q - 130) * .15, a, cx, cy)
            b.append(line(p0[0], p0[1], p1[0], p1[1], w=1))
        # wavy ray between
        a2 = a + math.pi / 20
        wav = [rot_pt(104 + t * 11, math.sin(t * 1.5) * 7, a2, cx, cy) for t in range(11)]
        b.append(path(wav, w=1.8, a=.3))
    for r, w in ((98, 3.4), (90, 1.4), (70, 2.4), (60, 1.2)):
        b.append(circle(cx, cy, r, w=w))
    b.append(dotpath([(cx + 80 * math.cos(k * math.pi / 18), cy + 80 * math.sin(k * math.pi / 18)) for k in range(36)], w=2.6))
    b.append(petals(cx, cy, 12, 14, 56, 11, rot=.1))
    b.append(circle(cx, cy, 12, w=2.4))
    b.append(dotpath([(cx, cy)], w=8))
    write("sun", (500, 500), "".join(b))


# ---------------------------------------------------------------- thangka lotus throne
def lotus():
    b = []
    cx, cy = 250, 215
    for k in range(-4, 5):                                       # back row: pointed petals
        a = math.radians(-90 + k * 19)
        b.append(leaf(cx, cy, a, 170 - abs(k) * 9, 17, veins=False))
        for q in range(1, 5):
            b.append(dotpath([rot_pt((170 - abs(k) * 9) * (.25 + q * .15), 0, a, cx, cy)], w=2.2))
    for k in range(-3, 4):                                       # front row: fuller petals, offset between the back ones
        a = math.radians(-90 + k * 24 + (0 if k else 0))
        a += math.radians(0)
        b.append(leaf(cx, cy + 14, a + math.radians(0), 108 - abs(k) * 5, 24, veins=False))
        tip = rot_pt(92 - abs(k) * 4, 0, a, cx, cy + 14)
        b.append(line(*rot_pt(26, 0, a, cx, cy + 14), tip[0], tip[1], w=1.2))
    for rr in (1, 2):                                            # beaded base
        pts = [(cx - 150 + i * 14, cy + 38 + rr * 14 + 4 * math.sin(i * .8)) for i in range(22)]
        b.append(dotpath(pts, w=3))
    b.append(path([(cx - 160, cy + 26), (cx, cy + 36), (cx + 160, cy + 26)], w=3.4, a=.5))
    b.append(path([(cx - 150, cy + 72), (cx, cy + 82), (cx + 150, cy + 72)], w=2.4, a=.5))
    write("lotus", (500, 330), "".join(b))


# ---------------------------------------------------------------- thangka ruyi cloud
def ribbon(pts, offs, ws):
    n = len(pts)
    nrm = []
    for i in range(n):
        a, c = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = c[0] - a[0], c[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nrm.append((-dy / L, dx / L))
    out = []
    for o, w in zip(offs, ws):
        q = []
        for i, (p, (nx, ny)) in enumerate(zip(pts, nrm)):
            tp = max(0.0, math.sin(math.pi * i / (n - 1))) ** .5
            q.append((p[0] + nx * o * tp, p[1] + ny * o * tp))
        out.append(path(q, w=w, a=.35))
    return "".join(out)


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def cloud_curl(cx, cy, scale, tail_dx, flip=1):
    pts = bez((cx + tail_dx * flip, cy + 52 * scale), (cx + tail_dx * .72 * flip, cy + 110 * scale),
              (cx + 70 * scale * flip, cy + 100 * scale), (cx + 66 * scale * flip, cy + 0))
    for k in range(1, 70):
        a = -k * .27
        r = 66 * scale - k * .88 * scale
        if r < 4: break
        pts.append((cx + flip * r * math.cos(a), cy + r * math.sin(a)))
    return ribbon(pts, (-8 * scale, -4 * scale, 0, 4 * scale, 8 * scale), (1.3, 1.6, 3.2, 1.6, 1.3))


def cloud():
    b = [cloud_curl(120, 100, 1.0, 360), cloud_curl(420, 72, .55, 150, flip=-1), cloud_curl(300, 140, .4, 110)]
    write("cloud", (560, 260), "".join(b))


# ---------------------------------------------------------------- thangka mandala
def mandala():
    b = []
    c = 300
    b.append(circle(c, c, 290, w=3.4)); b.append(circle(c, c, 280, w=1.4))
    b.append(dotpath([(c + 270 * math.cos(k * math.pi / 40), c + 270 * math.sin(k * math.pi / 40)) for k in range(80)], w=2.6))
    b.append(petals(c, c, 24, 190, 262, 15, rot=0.0))
    b.append(circle(c, c, 186, w=2.4))
    b.append(dotpath([(c + 176 * math.cos(k * math.pi / 24), c + 176 * math.sin(k * math.pi / 24)) for k in range(48)], w=2.4))
    b.append(petals(c, c, 16, 112, 172, 20, rot=.1))
    b.append(circle(c, c, 108, w=3)); b.append(circle(c, c, 100, w=1.2))
    for k in range(8):                                           # vajra points
        a = k * math.pi / 4
        b.append(path([rot_pt(100, -14, a, c, c), rot_pt(134, 0, a, c, c), rot_pt(100, 14, a, c, c)], w=2.2, a=.4))
    b.append(petals(c, c, 8, 18, 94, 18, rot=.2))
    b.append(petals(c, c, 8, 6, 44, 11, rot=.0, double=False))
    b.append(circle(c, c, 12, w=2.6)); b.append(dotpath([(c, c)], w=8))
    for k in range(4):                                           # gates
        a = k * math.pi / 2
        p = rot_pt(286, 0, a, c, c)
        b.append(circle(p[0], p[1], 14, w=2.4)); b.append(circle(p[0], p[1], 6, w=1.6))
    write("mandala", (600, 600), "".join(b))


# =====================================================================================================
# Stitched dividers: every stroke is a `.stitch` carrying --i, so the page can reveal them left to right
# as the visitor scrolls.
# =====================================================================================================
SW = 1200


def st(inner, x):
    i = max(0, min(99, int(x / SW * 96)))
    return f'<g class="stitch" style="--i:{i}">{inner}</g>'


def write_div(n, body):
    write(f"stitch-{n}", (SW, 72), body)


def dividers():
    # 1 two lines of plain running stitch with a repeating Nepali-pattern band between them
    b = []
    for y in (12, 60):
        x = 8
        while x < SW - 24:
            b.append(st(f'<line x1="{x}" y1="{y}" x2="{x + 18}" y2="{y}" stroke-width="2.6"/>', x)); x += 30
    k = 0
    x = 18
    while x < SW - 30:
        if k % 2 == 0:       # diamond with a dot
            b.append(st(f'<path d="M{x} 36l11 -13l11 13l-11 13z" stroke-width="2.2"/><path d="M{x + 5} 36l6 -7l6 7l-6 7z" stroke-width="1.2"/>' + dotpath([(x + 11, 36)], w=3), x))
        else:                # hourglass of two triangles between small stitched dots
            b.append(st(f'<path d="M{x} 25h22l-22 22h22z" stroke-width="2.2"/>' + dotpath([(x - 6, 36), (x + 28, 36)], w=3), x))
        x += 36
        k += 1
    write_div(1, "".join(b))
    # 2 cross-stitch row with diamonds
    b = []
    x = 20
    k = 0
    while x < SW - 40:
        if k % 6 == 5:
            b.append(st(f'<path d="M{x} 36l14 -16l14 16l-14 16z" stroke-width="2.2"/><path d="M{x + 7} 36l7 -8l7 8l-7 8z" stroke-width="1.4"/>', x)); x += 46
        else:
            b.append(st(f'<line x1="{x}" y1="26" x2="{x + 14}" y2="46" stroke-width="2.4"/><line x1="{x + 14}" y1="26" x2="{x}" y2="46" stroke-width="2.4"/>', x)); x += 24
        k += 1
    for y in (14, 58):
        xx = 8
        while xx < SW - 20:
            b.append(st(f'<line x1="{xx}" y1="{y}" x2="{xx + 10}" y2="{y}" stroke-width="1.6"/>', xx)); xx += 20
    write_div(2, "".join(b))
    # 3 a simple wave stitch: one sine wave worked as a row of short stitches that follow the curve
    b = []
    def wave_y(x):
        return 36 + 11 * math.sin(x / 60.0 * math.pi)
    x = 10.0
    while x < 1128:                                                             # the last stitch before the X has been dropped
        pts = [(x + t * 3.2, wave_y(x + t * 3.2)) for t in range(0, 6)]       # each stitch is ~16 units long and follows the wave
        b.append(st(f'<path d="{smooth2(pts)}" stroke-width="2.8"/>', x))
        x += 25
    # the wave ends in an embroidered X, like X marks the spot: two crossing arms worked as hollow bars with thread edges,
    # ladder stitches across them, a dot at each arm end and a button at the centre
    cx, cy, r = 1150, wave_y(1150) + 9, 19
    HOLLOW = "var(--divbg,#fff)"
    xm = f"M{cx - r} {cy - r}L{cx + r} {cy + r}M{cx + r} {cy - r}L{cx - r} {cy + r}"
    g = f'<path d="{xm}" stroke-width="10.5"/><path d="{xm}" style="stroke:{HOLLOW}" stroke-width="5.2"/>'
    tk = ""
    for sgn in (1, -1):
        for k in range(-7, 8):
            t = k * 2.5
            px, py = cx + t, cy + sgn * t
            tk += f"M{px - 3.1 * sgn:.1f} {py - 3.1:.1f}L{px + 3.1 * sgn:.1f} {py + 3.1:.1f}"
    g += f'<path d="{tk}" stroke-width="1.5"/>'
    for sgx in (-1, 1):
        for sgy in (-1, 1):
            g += f'<circle cx="{cx + sgx * (r + 7)}" cy="{cy + sgy * (r + 7)}" r="2.6" stroke-width="1.8"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="6.2" style="fill:{HOLLOW}" stroke-width="2.4"/><circle cx="{cx}" cy="{cy}" r="1.9" stroke-width="1.6"/>'
    b.append(st(g, 1150))
    write_div(3, "".join(b))
    # 4 Mithila teeth: triangles with dots over a zig baseline
    b = []
    for k in range(30):
        x = 10 + k * 39.5
        g = f'<path d="M{f(x)} 62L{f(x + 19)} 12L{f(x + 38)} 62Z" stroke-width="2.4"/><path d="M{f(x + 8)} 62L{f(x + 19)} 28L{f(x + 30)} 62" stroke-width="1.2"/>'
        g += dotpath([(x + 19, 42), (x + 19, 52)], w=3)
        b.append(st(g, x))
    write_div(4, "".join(b))
    # 5 Nepali stepped-diamond (dhaka-style) geometric border
    def stepped(cx, cy, n, step):
        q = []
        for k in range(n):
            q += [(cx + step * (k + 1), cy - step * (n - k)), (cx + step * (k + 1), cy - step * (n - k - 1))]
        q = [(cx, cy - n * step)] + q
        quad = q + [(cx + n * step, cy)]
        pts = quad + [(x, 2 * cy - y) for x, y in reversed(quad)] + [(2 * cx - x, 2 * cy - y) for x, y in quad] + [(2 * cx - x, y) for x, y in reversed(quad)]
        return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
    b = []
    for k in range(15):
        cx = 40 + k * 80
        g = f'<path d="{stepped(cx, 36, 4, 7)}" stroke-width="2.4"/><path d="{stepped(cx, 36, 2, 7)}" stroke-width="1.6"/>' + dotpath([(cx, 36)], w=4.5)
        b.append(st(g, cx - 28))
        sx = cx + 40
        sq = "".join(f'<rect x="{sx - 3}" y="{y - 3}" width="6" height="6" stroke-width="1.6"/>' for y in (18, 36, 54))
        b.append(st(sq, sx))
    for yy in (4, 68):
        xx = 8
        while xx < SW - 20:
            b.append(st(f'<line x1="{xx}" y1="{yy}" x2="{xx + 8}" y2="{yy}" stroke-width="1.6"/>', xx)); xx += 18
    write_div(5, "".join(b))
    # 6 floral vine scroll
    b = []
    pts = [(x, 36 + 13 * math.sin(x / 62)) for x in range(0, SW + 1, 12)]
    for k in range(0, len(pts) - 1, 2):
        seg = pts[k:k + 3]
        if len(seg) == 3:
            b.append(st(path(seg, w=2.2, a=.3), seg[0][0]))
    for k in range(12):
        x = 40 + k * 100
        y = 36 + 13 * math.sin(x / 62)
        up = -1 if k % 2 == 0 else 1
        g = leaf(x, y, math.radians(-90 * up + 25 * up), 34, 9, veins=False) + leaf(x, y, math.radians(-90 * up - 35 * up), 26, 7, veins=False)
        sp = [(x + 22 + (3 + t * .9) * math.cos(t * .6 + 1), y - up * 6 + (3 + t * .9) * math.sin(t * .6 + 1)) for t in range(0, 22)]
        g += path(sp[::2], w=1.5, a=.2) + dotpath([(x + 48, y + 2 * up)], w=3)
        b.append(st(g, x))
    write_div(6, "".join(b))
    # 7 fish-scale scallops
    b = []
    for row, y in enumerate((18, 36, 54)):
        x = 6 + (row % 2) * 22
        while x < SW - 30:
            b.append(st(f'<path d="M{x} {y}q22 30 44 0" stroke-width="2"/>', x)); x += 44
    write_div(7, "".join(b))
    # 8 feather / herringbone stitch down a centre line
    b = []
    x = 10
    while x < SW - 30:
        b.append(st(f'<path d="M{x} 18l16 18l16 -18" stroke-width="2.4"/><path d="M{x + 16} 36v22" stroke-width="2.4"/>', x)); x += 34
    for xx in range(0, SW, 24):
        b.append(st(dotpath([(xx + 6, 66)], w=3), xx))
    write_div(8, "".join(b))

    # 9 an embroidered metal chain. Every link passes through the hole of the next one; where two links cross, one is over at the top
    # crossing and the other is over at the bottom crossing, so they visibly lock. Links are worked in satin stitch.
    BG = 'style="fill:var(--divbg,#fff)"'
    RX, RY, HX, HY = 25, 15, 14.5, 6.5
    PITCH = 34

    def ring(cx, cy, seed):
        rng = random.Random(seed)
        o = f"M{cx - RX} {cy}a{RX} {RY} 0 1 0 {2 * RX} 0a{RX} {RY} 0 1 0 {-2 * RX} 0z"
        h = f"M{cx - HX} {cy}a{HX} {HY} 0 1 0 {2 * HX} 0a{HX} {HY} 0 1 0 {-2 * HX} 0z"
        d = ""
        n = 30
        for k in range(n):
            ang = k * 2 * math.pi / n
            if math.radians(205) < ang < math.radians(250):                  # sheen: stitches left out at the upper left
                continue
            ax, ay = cx + (HX - .5 + rng.uniform(-.4, .4)) * math.cos(ang), cy + (HY - .3) * math.sin(ang)
            a2 = ang + .17
            bx, by = cx + (RX + .4 + rng.uniform(-.5, .5)) * math.cos(a2), cy + (RY + .4) * math.sin(a2)
            if abs(by - ay) < 0.4 * abs(bx - ax) or abs(bx - ax) < 0.55 * abs(by - ay):   # no near-horizontal or near-vertical stitches
                continue
            d += f"M{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}"
        return (f'<path d="{o}{h}" fill-rule="evenodd" {BG} stroke="none"/><path d="{o}" stroke-width="1.6"/><path d="{h}" stroke-width="1.6"/>')

    b = []
    cy = 36
    x = -38
    k = 0
    while x < SW + 40:
        g = ring(x, cy, 100 + k)
        if k > 0:                                                            # redraw the previous link over this one at the TOP crossing
            px = x - PITCH
            g += (f'<clipPath id="lk{k}"><rect x="{px + RX - 20}" y="{cy - RY - 3}" width="22" height="{RY + 3}"/></clipPath>'
                  f'<g clip-path="url(#lk{k})">{ring(px, cy, 100 + k - 1)}</g>')
        b.append(st(g, max(0, x - 30)))
        x += PITCH
        k += 1
    write_div(9, "".join(b))
    # 10 Nepali textile band with eye imagery between zigzag borders
    b = []
    for k in range(30):
        x = 6 + k * 40
        b.append(st(f'<path d="M{x} 14l10 -9l10 9l10 -9" stroke-width="1.8"/><path d="M{x} 58l10 9l10 -9l10 9" stroke-width="1.8"/>', x))
    for k in range(10):
        cx = 60 + k * 120
        eye_g = (f'<path d="M{cx - 34} 36Q{cx} 10 {cx + 34} 36Q{cx} 62 {cx - 34} 36Z" stroke-width="2.6"/>'
                 f'<path d="M{cx - 24} 36Q{cx} 18 {cx + 24} 36Q{cx} 54 {cx - 24} 36Z" stroke-width="1.2"/>'
                 f'<circle cx="{cx}" cy="36" r="11" stroke-width="2.2"/><circle cx="{cx}" cy="36" r="5" stroke-width="1.6"/>' + dotpath([(cx, 36)], w=3)
)
        b.append(st(eye_g, cx - 34))
        mx = cx + 60
        mot = (f'<path d="M{mx} 22l9 14l-9 14l-9 -14z" stroke-width="2"/>' + dotpath([(mx, 36), (mx - 20, 36), (mx + 20, 36)], w=3))
        b.append(st(mot, mx))
    write_div(10, "".join(b))




# =====================================================================================================
# Home-page feature illustrations (Mithila-style, single colour). Inline SVGs animated by scroll variables.
# =====================================================================================================
def spiral(cx, cy, r, turns=2.4, start=0.0, dirn=1, n=70, w=1.6, a=.25, inner=2.5):
    pts = []
    for k in range(n + 1):
        t = k / n
        ang = start + dirn * turns * 2 * math.pi * t
        rr = inner + (r - inner) * t
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return path(pts, w=w, a=a)


# ---------------------------------------------------------------- loom: sari strips woven in as you scroll
SARI_KINDS = ["paisley", "temple", "bandhani", "vine", "check", "ikat", "zari", "buti", "eye", "chevron"]


def sari_pattern(kind, x0, x1, y, h):
    """A strip cut from a sari, in a recognisable sari design (drawn as line work)."""
    o = []
    mid = y + h / 2
    if kind == "paisley":                                   # classic paisley (ambi): round bulb, tail curling up and over
        for i, x in enumerate(range(int(x0) + 14, int(x1) - 18, 30)):
            fl = 1 if i % 2 == 0 else -1
            pts = [(x + 14 * fl, y + 3), (x + 15 * fl, y + 10), (x + 9 * fl, y + h - 3), (x, y + h - 3), (x - 6 * fl, y + 14), (x - 2 * fl, y + 6), (x + 5 * fl, y + 5), (x + 9 * fl, y + 9)]
            o.append(path(pts, w=1.6, a=.1, closed=True))
            inner = [(x + 4 * fl + (px - x) * .45, y + 12 + (py - y - 12) * .45) for px, py in pts]
            o.append(path(inner, w=1, a=.1, closed=True))
            o.append(dotpath([(x + 3 * fl, y + 15), (x + 8 * fl, y + 11), (x - 1 * fl, y + 11)], w=2))
    elif kind == "temple":                                  # temple (gopuram) border: stepped triangles over a zari line
        o.append(line(x0, y + h - 3, x1, y + h - 3, w=1.4))
        for x in range(int(x0) + 4, int(x1) - 14, 14):
            o.append(f'<path d="M{x} {y + h - 3}l7 -{h - 8}l7 {h - 8}" stroke-width="1.5"/>')
            o.append(dotpath([(x + 7, y + h - 9)], w=2))
        o.append(line(x0, y + 2, x1, y + 2, w=1))
    elif kind == "bandhani":                                # tie-dye dot clusters on a lattice
        for r, yy in enumerate((y + h * .3, y + h * .72)):
            for x in range(int(x0) + 8 + (11 if r else 0), int(x1) - 8, 22):
                o.append(dotpath([(x, yy), (x - 3.5, yy - 3.5), (x + 3.5, yy - 3.5), (x - 3.5, yy + 3.5), (x + 3.5, yy + 3.5)], w=1.8))
    elif kind == "vine":                                    # floral jaal: a flowing vine with leaves and small blooms
        pts = [(x, mid + 5 * math.sin(x / 15.0)) for x in range(int(x0) + 4, int(x1) - 4, 8)]
        o.append(path(pts, w=1.3, a=.1))
        for i, x in enumerate(range(int(x0) + 14, int(x1) - 14, 24)):
            yy = mid + 5 * math.sin(x / 15.0)
            up = -1 if i % 2 == 0 else 1
            o.append(leaf(x, yy, math.radians(-90 * up - 25), 11, 3.2, veins=False))
            o.append(dotpath([(x + 12, yy + up * 5)], w=3))
    elif kind == "check":                                   # kota-style check
        for x in range(int(x0) + 4, int(x1) - 2, 8):
            o.append(line(x, y + 1.5, x, y + h - 1.5, w=1.4 if (x // 8) % 3 == 0 else .8))
        for yy in (y + 4, y + h / 2, y + h - 4):
            o.append(line(x0 + 2, yy, x1 - 2, yy, w=1.4 if yy == y + h / 2 else .8))
    elif kind == "ikat":                                    # ikat: feathered diamonds
        for x in range(int(x0) + 14, int(x1) - 14, 26):
            o.append(f'<path d="M{x - 11} {mid}l11 -{h / 2 - 3:.0f}l11 {h / 2 - 3:.0f}l-11 {h / 2 - 3:.0f}z" stroke-width="1.5"/><path d="M{x - 5} {mid}l5 -6l5 6l-5 6z" stroke-width="1.1"/>')
            o.append(f'<path d="M{x - 17} {mid}h-5M{x + 17} {mid}h5M{x - 15} {mid - 4}l-4 -2M{x - 15} {mid + 4}l-4 2M{x + 15} {mid - 4}l4 -2M{x + 15} {mid + 4}l4 2" stroke-width="1"/>')
    elif kind == "zari":                                    # zari stripes: a bold gold line flanked by fine ones, dotted between
        for dy, w in ((-8, .9), (-5, 1.6), (0, 2.6), (5, 1.6), (8, .9)):
            o.append(line(x0 + 2, mid + dy * (h / 24), x1 - 2, mid + dy * (h / 24), w=w))
        o.append(dotpath([(x, mid - 2.5 * h / 24) for x in range(int(x0) + 8, int(x1) - 4, 10)], w=1.6))
    elif kind == "buti":                                    # buti: small scattered flowers in offset rows
        for r, yy in enumerate((y + h * .32, y + h * .7)):
            for x in range(int(x0) + 10 + (13 if r else 0), int(x1) - 10, 26):
                o.append(dotpath([(x + 3.6 * math.cos(a), yy + 3.6 * math.sin(a)) for a in [k * 2 * math.pi / 5 for k in range(5)]], w=2.2))
                o.append(dotpath([(x, yy)], w=2.6))
    elif kind == "eye":                                     # peacock-eye motif
        for x in range(int(x0) + 14, int(x1) - 14, 28):
            o.append(ellipse(x, mid, 11, h / 2 - 3, w=1.4, n=12)); o.append(circle(x, mid, 4.5, w=1.3)); o.append(dotpath([(x, mid)], w=2.4))
            o.append(f'<path d="M{x - 14} {mid}h-4M{x + 14} {mid}h4" stroke-width="1"/>')
    else:                                                   # chevron / kangura zigzag border
        for yy in (y + 8, y + h - 8):
            o.append(path([(x, yy + (5 if (k % 2) else -5)) for k, x in enumerate(range(int(x0) + 4, int(x1), 9))], w=1.4, a=.1))
    return "".join(o)


def weave():
    W, H = 560, 760
    xs = [40 + i * 20 for i in range(25)]
    top, bot = 24, H - 24
    b = []
    # only a top and a bottom beam: the warp is tied to them, there are no side posts
    for yy, ww in ((12, 3.4), (22, 1.4), (H - 22, 1.4), (H - 12, 3.4)):
        b.append(path([(18, yy), (280, yy + R.uniform(-1, 1)), (542, yy)], w=ww, a=.4))
    for x in xs:                                                  # warp threads
        b.append(line(x, top, x, bot, w=1.3))
    y = 44
    j = 0
    inv_rng = random.Random(23)                                   # which strips are orange-with-white (fixed, not changing per page load)
    prev_inv = False
    while y + 24 < bot - 6:
        h = 24
        inv = inv_rng.random() < 0.4
        if inv and prev_inv and inv_rng.random() < 0.6:           # avoid long runs of the same colourway
            inv = False
        prev_inv = inv
        if inv:
            g = [f'<rect x="30" y="{y}" width="500" height="{h}" style="fill:#E35A00;stroke:#E35A00" stroke-width="2.4"/>',
                 f'<g stroke="#fff">{sari_pattern(SARI_KINDS[j % len(SARI_KINDS)], 36, 524, y, h)}</g>']
        else:
            g = [f'<rect x="30" y="{y}" width="500" height="{h}" fill="#fff" stroke-width="2.4"/>',
                 sari_pattern(SARI_KINDS[j % len(SARI_KINDS)], 36, 524, y, h)]
        b.append(f'<g class="weft" style="--j:{j};--dir:{1 if j % 2 == 0 else -1}">{"".join(g)}</g>')
        for k, x in enumerate(xs):                                # the thread passes over the strip here
            if (j + k) % 2 == 1:
                halo, core = ("#E35A00", "#fff") if inv else ("#fff", "currentColor")
                b.append(f'<line x1="{x}" y1="{y - 1}" x2="{x}" y2="{y + h + 1}" style="stroke:{halo}" stroke-width="3.6"/>'
                         f'<line x1="{x}" y1="{y - 1}" x2="{x}" y2="{y + h + 1}" style="stroke:{core}" stroke-width="1.3"/>')
        y += 30
        j += 1
    write("weave", (W, H), "".join(b), extra=' preserveAspectRatio="none"')


# ---------------------------------------------------------------- hands, palms up, cupped; arms from the top right
def hand_up(tx, ty, rot, mirror=False, arm=560):
    pts = [(-30, 70), (-38, 10), (-40, -40), (-38, -72), (-34, -100), (-26, -108), (-18, -100), (-17, -76),
           (-17, -118), (-9, -130), (-1, -118), (-1, -80), (0, -134), (9, -146), (18, -134), (18, -80),
           (19, -120), (27, -132), (35, -120), (36, -70), (40, -40), (46, -34), (64, -52), (80, -80),
           (88, -86), (93, -76), (78, -36), (54, 0), (36, 28), (30, 70)]
    g = [path(pts, w=3.2, a=.4)]
    g.append(path([(x * .86, (y + 30) * .86 - 30) for x, y in pts[:-3]], w=1.2, a=.5))
    for (x, y) in ((-26, -78), (-9, -92), (9, -100), (27, -90)):
        g.append(line(x - 7, y, x + 7, y + 1, w=1.2)); g.append(line(x - 7, y - 22, x + 7, y - 21, w=1.2))
    # mehndi-style palm decoration: rings, spiral and dots
    g.append(circle(0, -8, 24, w=1.6)); g.append(circle(0, -8, 17, w=1.2)); g.append(spiral(0, -8, 13, 2.2, w=1.4, a=.2))
    g.append(dotpath([(24 * math.cos(k * math.pi / 5), -8 + 24 * math.sin(k * math.pi / 5)) for k in range(10)], w=2.4))
    # forearm: two long edges, bangles and a chain of diamonds
    g.append(path([(-30, 70), (-34, 300), (-30, arm)], w=3.2, a=.8)); g.append(path([(30, 70), (34, 300), (30, arm)], w=3.2, a=.8))
    for yy in (82, 98, 114):
        g.append(path([(-32, yy), (0, yy + 6), (32, yy)], w=2.6 if yy == 98 else 1.5, a=.4))
    for yy in range(140, arm - 20, 46):
        g.append(f'<path d="M0 {yy}l9 14l-9 14l-9 -14z" stroke-width="1.6"/>' + dotpath([(0, yy + 14)], w=3))
        g.append(path([(-30, yy + 14), (-18, yy + 2), (-30, yy - 10)], w=1.2, a=.2)); g.append(path([(30, yy + 14), (18, yy + 2), (30, yy - 10)], w=1.2, a=.2))
    tr = f"translate({tx} {ty}) rotate({rot})" + (" scale(-1 1)" if mirror else "")
    return f'<g transform="{tr}">{"".join(g)}</g>'


def hands_cup():
    # two cupped hands, scaled up, meeting at the lower left; the forearms run off the top right edge
    b = ['<g transform="translate(-30 -40) scale(1.5)">' + hand_up(176, 318, 206) + hand_up(290, 418, 238) + '</g>']
    write("hands-cup", (640, 780), "".join(b))


# ---------------------------------------------------------------- spiral clouds and spiral rain
def spiral_cloud(cx, cy, s=1.0):
    out = []
    discs = [(-118, 14, 32), (118, 14, 32), (-66, -10, 44), (66, -10, 44), (0, -26, 56)]
    for dx, dy, r in discs:
        x, y, r = cx + dx * s, cy + dy * s, r * s
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#fff" stroke-width="2.6"/>')
        out.append(circle(x, y, r * .84, w=1.2))
        out.append(spiral(x, y, r * .78, turns=2.5, w=1.8, dirn=1 if dx >= 0 else -1, n=44))
    for k, yy in enumerate((cy + 42 * s, cy + 52 * s, cy + 62 * s)):
        pts = [(cx - 150 * s + t * 30 * s, yy + math.sin(t * 1.1 + k) * 4) for t in range(11)]
        out.append(path(pts, w=[2.4, 1.6, 1.2][k], a=.3))
    return "".join(out)


def f2(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def smooth2(pts, closed=False):
    """Catmull-Rom through points -> cubic Bezier, two decimals and no jitter (smooth, steady lines)."""
    n = len(pts)
    d = f"M{f2(pts[0][0])} {f2(pts[0][1])}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{f2(c1[0])} {f2(c1[1])} {f2(c2[0])} {f2(c2[1])} {f2(p2[0])} {f2(p2[1])}"
    return d + ("Z" if closed else "")


def sspiral(cx, cy, r, turns=2.2, dirn=1, start=0.0, n=48, w=2, inner=.06, rot=0.0, squash=1.0):
    pts = []
    for k in range(n + 1):
        t = k / n
        ang = start + dirn * turns * 2 * math.pi * t
        rr = r * (inner + (1 - inner) * t)
        pts.append((cx + rr * math.cos(ang), cy + rr * squash * math.sin(ang)))
    return f'<path d="{smooth2(pts)}" stroke-width="{w}"/>'


# ---------------------------------------------------------------------------------------------------------------
# Cloud in the style of the supplied reference: a big round swirl at the centre, a mound behind it, and several different
# ribbons that sweep out and curl into spirals. Parts are painted back to front so they flow into one another.
# ---------------------------------------------------------------------------------------------------------------
def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def covered(x, y, shapes):
    for kind, d in shapes:
        if kind == "circ":
            cx, cy, r = d
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                return True
        elif point_in_poly(x, y, d):
            return True
    return False


# ---------------------------------------------------------------------------------------------------------------
# One wide cloud in the style of a traditional auspicious cloud: a crown of overlapping spiral-coil lobes, each ribbed like a
# shell, with a pointed tail sweeping out at each end. Lobes are painted back to front. The top is cut by the section edge.
# ---------------------------------------------------------------------------------------------------------------


def coil_lobe(cx, cy, R, dirn, start, turns=2.05):
    """A round lobe: white-filled outline holding a two-turn spiral coil. The bands between turns are ribbed with ticks, a thin ring
    runs just inside the outline, and the core ends in a dot."""
    big = R >= 22
    ow = 3.2 if big else max(1.6, R * .13)
    out = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#fff" stroke-width="{ow:.2f}"/>']
    if R >= 14:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{f2(R * .92)}" stroke-width="{1.0 if big else .8}"/>')
    n = 90 if big else 48
    r_out, r_in = R * .85, R * .09
    def rad(t):
        return r_out + (r_in - r_out) * t
    pts = []
    for k in range(n + 1):
        t = k / n
        ang = start + dirn * turns * 2 * math.pi * t
        pts.append((cx + rad(t) * math.cos(ang), cy + rad(t) * math.sin(ang)))
    out.append(f'<path d="{smooth2(pts)}" stroke-width="{2.5 if big else max(1.1, R * .09):.2f}"/>')
    step = 13 if big else 22
    ticks = ""
    for deg in range(0, int(360 * turns) - 20, step):               # ribs across every band between one turn and the next
        t0 = deg / (360 * turns)
        t1 = t0 + 1 / turns
        if t1 > 1:
            break
        ang = start + dirn * turns * 2 * math.pi * t0
        r0, r1 = rad(t0), rad(t1)
        if abs(r0 - r1) < 3.2:
            continue
        ticks += f"M{f2(cx + (r0 - 1.6) * math.cos(ang))} {f2(cy + (r0 - 1.6) * math.sin(ang))}L{f2(cx + (r1 + 1.6) * math.cos(ang))} {f2(cy + (r1 + 1.6) * math.sin(ang))}"
    out.append(f'<path d="{ticks}" stroke-width="{1.1 if big else .8}"/>')
    if big:
        out.append(dotpath([(cx + R * .1 * math.cos(start), cy + R * .1 * math.sin(start))], w=3.2))
    return "".join(out)


LOBES = [   # (cx, cy, R, dirn, start angle): back to front
    (300, 62, 62, 1, 0.3), (212, 98, 52, -1, 2.6), (394, 98, 50, 1, 4.2), (150, 152, 40, -1, 1.0), (456, 150, 42, 1, 3.4),
    (268, 88, 30, -1, 1.7), (346, 96, 28, 1, 5.3), (176, 122, 26, 1, 0.5), (432, 118, 27, -1, 2.9),
    (240, 146, 50, 1, 5.0), (380, 150, 52, -1, 0.9), (306, 138, 44, 1, 3.9),
    (112, 186, 28, 1, 4.1), (492, 184, 29, -1, 1.3),
    (150, 204, 36, 1, 2.2), (452, 202, 38, -1, 5.6), (214, 200, 48, -1, 4.4), (392, 204, 48, 1, 1.6), (303, 196, 54, -1, 0.2),
    (268, 134, 22, -1, 3.1), (344, 150, 20, 1, 0.4),
]

# short chains of smaller lobes at the two ends (listed from the body outwards)
TAIL_LOBES = [(88, 214, 21), (66, 221, 16), (48, 226, 12)]
CLOUD_SCALE = 1.12                 # widens the cloud so it fills the right half
CLOUD_YMAX = 250                   # lowest point of the cloud in its own (upright) coordinates
CLOUD_HIDE = 55                    # units of the cloud's top (about a fifth of it) tucked under the previous section
CLOUD_H = 228


def cloud_circles():
    """All main circles (cx, cy, R, dirn, start) in upright coordinates, left tail, right tail, then the body."""
    out = []
    for mirror in (False, True):
        for i, (x, y, R) in enumerate(reversed(TAIL_LOBES)):
            out.append((600 - x if mirror else x, y, R, 1 if (i % 2) ^ mirror else -1, i * 1.3))
    for (cx, cy, R, d, st_) in LOBES:
        out.append((cx, cy, R, d, st_))
    return out


def extra_edge_lobes(mains):
    """A few extra circles set at random spots on the outline, so the silhouette is not uniformly round."""
    rng = random.Random(41)
    extras = []
    tries = 0
    while len(extras) < 12 and tries < 400:
        tries += 1
        cx, cy, R = rng.choice(mains)[:3]
        out_ang = math.atan2(cy - 150, cx - 300)
        ang = out_ang + rng.uniform(-1.1, 1.1)
        r = rng.uniform(11, 21)
        x, y = cx + R * .92 * math.cos(ang), cy + R * .92 * math.sin(ang)
        deep = sum(1 for (mx, my, mr, *_r) in mains if (x - mx) ** 2 + (y - my) ** 2 < (mr * .8) ** 2)
        if deep > 0:                                        # skip spots that are inside the cloud, keep ones on its edge
            continue
        if any((x - ex) ** 2 + (y - ey) ** 2 < (er + r) ** 2 * .35 for ex, ey, er in extras):
            continue
        extras.append((round(x, 1), round(y, 1), round(r, 1)))
    return extras


def cloud_build():
    mains = cloud_circles()
    extras = extra_edge_lobes(mains)
    out = []
    shapes = []
    for i, (x, y, r) in enumerate(extras):                   # extras sit behind the body so only their outer bulge shows
        out.append(coil_lobe(x, y, r, 1 if i % 2 else -1, i * 2.1))
        shapes.append(("circ", (x, y, r)))
    tails = [c for c in mains[:2 * len(TAIL_LOBES)]]
    body = mains[2 * len(TAIL_LOBES):]
    for (cx, cy, R, d, st_) in tails + body:
        out.append(coil_lobe(cx, cy, R, d, st_))
        shapes.append(("circ", (cx, cy, R)))
    return "".join(out), shapes


CLOUD_CACHE = (None, None)


def _tr():
    s_ = CLOUD_SCALE
    return 300 + 300 * s_, CLOUD_YMAX * s_ - CLOUD_HIDE, s_


def view_covered(x, y):
    tx, ty, s_ = _tr()
    return covered((tx - x) / s_, (ty - y) / s_, CLOUD_CACHE[1])


def clouds_band():
    """The cloud is turned 180 degrees so its crown hangs down; only a sliver of its top edge is tucked under the section above."""
    global CLOUD_CACHE
    inner, shapes = cloud_build()
    CLOUD_CACHE = (inner, shapes)
    tx, ty, s_ = _tr()
    write("clouds", (600, CLOUD_H), f'<g transform="translate({f2(tx)} {f2(ty)}) scale({-s_} {-s_})">{inner}</g>')


def teardrop2(cx, cy, r):
    h = r * 2.5
    return (f"M{f2(cx)} {f2(cy - h)}C{f2(cx + r * .22)} {f2(cy - h * .6)} {f2(cx + r)} {f2(cy - r * 1.1)} {f2(cx + r)} {f2(cy)}"
            f"A{f2(r)} {f2(r)} 0 0 1 {f2(cx - r)} {f2(cy)}C{f2(cx - r)} {f2(cy - r * 1.1)} {f2(cx - r * .22)} {f2(cy - h * .6)} {f2(cx)} {f2(cy - h)}Z")


def rain():
    """Teardrops with smooth swirls. Each starts hidden behind a cloud and falls straight down to its own resting height.
    Positions come from a jittered grid (even spread); the order they fall in is shuffled."""
    if CLOUD_CACHE[0] is None:
        clouds_band()
    rng = random.Random(8)
    cols, rows = 6, 4
    cells = [(c, r_) for c in range(cols) for r_ in range(rows)]
    rng.shuffle(cells)
    order = list(range(len(cells)))
    rng.shuffle(order)
    b = []
    for i, (c, r_) in enumerate(cells):
        r = rng.uniform(10, 14)
        h = r * 2.5
        pick = None
        for attempt in range(60):                                # find an x, inside this column, where a whole drop can start hidden
            x = 22 + (c + rng.uniform(.1, .9)) * (556 / cols)
            for y0 in range(250, 4, -2):
                pts = [(x, y0 - h), (x - r, y0), (x + r, y0), (x, y0 + r), (x - r * .6, y0 - h * .5), (x + r * .6, y0 - h * .5), (x, y0 - h * .5)]
                if all(py < 0 or view_covered(px, py) for px, py in pts):
                    pick = (x, y0)
                    break
            if pick:
                break
        if not pick:
            pick = (22 + (c + .5) * (556 / cols), -h - 4)          # fall back to starting just above the top edge (clipped)
        x, y0 = pick
        y_end = 840 + rng.uniform(0, 160)                         # every drop falls past the divider and out of the section
        dist = max(40, y_end - y0)
        td = teardrop2(x, y0, r)
        inner = teardrop2(x, y0 + r * .08, r * .72)
        g = (f'<path d="{td}" stroke-width="2.2"/><path d="{inner}" stroke-width="1"/>' +
             sspiral(x, y0 + r * .02, r * .56, turns=2.1, dirn=1 if i % 2 else -1, n=44, w=1.5, start=rng.uniform(0, 6)))
        rank = order[i]
        b.append(f'<g class="raindrop" style="--s:{.05 + .36 * rank / len(cells):.3f};--d:{dist / 560:.3f}">{g}</g>')
    write("rain", (600, 700), "".join(b))


# ---------------------------------------------------------------- lotus that blooms from the bottom centre
def lotus_bloom():
    """A clean lotus: three rows of single-outline petals (7, 5 and 3), each filled white so the front row hides the one behind,
    with one centre vein per petal. Rows spread apart as the page scrolls (see .petal in site.css)."""
    cx, cy = 250, 250
    def petal(L, w):
        return (f"M{cx} {cy}C{cx - w} {cy - L * .35:.1f} {cx - w * .55:.1f} {cy - L * .86:.1f} {cx} {cy - L}"
                f"C{cx + w * .55:.1f} {cy - L * .86:.1f} {cx + w} {cy - L * .35:.1f} {cx} {cy}Z")
    b = []
    rows = [(3, 22, 190, 34), (2, 28, 152, 38), (1, 38, 112, 34)]     # (half-count, spread per petal in degrees, length, half-width)
    for half, sp, L, w in rows:
        for k in range(-half, half + 1):
            g = f'<path d="{petal(L - abs(k) * 4, w)}" fill="#fff" stroke-width="2.6"/>'
            g += f'<path d="M{cx} {cy - 14}L{cx} {cy - (L - abs(k) * 4) * .72:.1f}" stroke-width="1.3"/>'
            b.append(f'<g class="petal" style="--k:{k};--sp:{sp}deg">{g}</g>')
    b.append(path([(60, 262), (250, 274), (440, 262)], w=3.2, a=.5))
    b.append(path([(110, 286), (250, 296), (390, 286)], w=2.2, a=.5))
    write("lotus-bloom", (500, 330), "".join(b))


# ---------------------------------------------------------------- sun in spirals
def sun_spiral():
    b = []
    cx = cy = 200
    b.append(circle(cx, cy, 78, w=3.2)); b.append(circle(cx, cy, 70, w=1.3))
    b.append(spiral(cx, cy, 64, turns=4.2, w=2.2, n=140, a=.3))
    b.append(dotpath([(cx + 88 * math.cos(k * math.pi / 14), cy + 88 * math.sin(k * math.pi / 14)) for k in range(28)], w=2.6))
    for k in range(16):
        a = k * 2 * math.pi / 16
        p0, p1 = rot_pt(98, 0, a, cx, cy), rot_pt(140, 0, a, cx, cy)
        b.append(line(p0[0], p0[1], p1[0], p1[1], w=1.8))
        sc = rot_pt(156, 0, a, cx, cy)
        b.append(spiral(sc[0], sc[1], 17, turns=2.2, start=a, dirn=1 if k % 2 else -1, w=2, n=40))
        b.append(circle(sc[0], sc[1], 17, w=1.2))
    write("sun-spiral", (400, 400), "".join(b))


# ---------------------------------------------------------------- Nepali village, clothesline with clothes and a YogaMaty
def newari_window(cx, top, ww, hh):
    """A carved wooden window with an arched head, lattice and a ring of dots, in the style of Newari houses."""
    l, r, bt = cx - ww / 2, cx + ww / 2, top + hh
    k = ww / 2
    g = [f'<path d="M{l:.1f} {bt:.1f}V{top + k:.1f}A{k:.1f} {k:.1f} 0 0 1 {r:.1f} {top + k:.1f}V{bt:.1f}Z" stroke-width="1.9"/>']
    g.append(f'<path d="M{l + 3:.1f} {bt - 3:.1f}V{top + k:.1f}A{k - 3:.1f} {k - 3:.1f} 0 0 1 {r - 3:.1f} {top + k:.1f}V{bt - 3:.1f}Z" stroke-width="1"/>')
    g.append(f'<path d="M{cx - k / 2:.1f} {top + k:.1f}V{bt - 3:.1f}M{cx:.1f} {top + 3:.1f}V{bt - 3:.1f}M{cx + k / 2:.1f} {top + k:.1f}V{bt - 3:.1f}M{l + 3:.1f} {top + k + (hh - k) / 2:.1f}H{r - 3:.1f}" stroke-width="1"/>')
    g.append(dotpath([(cx + (k + 5) * math.cos(math.pi * (1 + j / 6)), top + k + (k + 5) * math.sin(math.pi * (1 + j / 6))) for j in range(1, 6)], w=2))
    return "".join(g)


def mithila_band(xl, xr, y):
    """A narrow painted border: two rules with a zigzag and a dot in each point."""
    n = max(2, int((xr - xl) / 9))
    st_ = (xr - xl) / n
    pts = [(xl + i * st_, y + (3 if i % 2 else -3)) for i in range(n + 1)]
    return (line(xl, y - 5, xr, y - 5, w=1) + line(xl, y + 5, xr, y + 5, w=1) + path(pts, w=1.1) +
            dotpath([(xl + (i + .5) * st_ * 2, y + (0)) for i in range(int(n / 2))], w=1.8))


def lotus_motif(cx, cy, r):
    return (f'<path d="M{cx - r} {cy}Q{cx - r * .5} {cy - r * 1.3} {cx} {cy - r * 1.4}Q{cx + r * .5} {cy - r * 1.3} {cx + r} {cy}Q{cx} {cy + r * .5} {cx - r} {cy}" stroke-width="1.3"/>'
            f'<path d="M{cx} {cy - r * 1.4}V{cy + r * .15}M{cx - r * .55} {cy - r * .6}Q{cx - r * .2} {cy - r * .1} {cx} {cy + r * .15}M{cx + r * .55} {cy - r * .6}Q{cx + r * .2} {cy - r * .1} {cx} {cy + r * .15}" stroke-width="1"/>')


def house(x, w, h, roof, tiers=1):
    """A Newari-style house: brick walls with painted Mithila bands, carved arched windows, a tiered pagoda roof with upturned eaves, hanging fringe and a pinnacle."""
    b = []
    y1 = 186
    sh = h / tiers
    r = roof * .55
    for i in range(tiers):
        inset = i * w * .1
        xl, xr = x + inset, x + w - inset
        wy1 = y1 - i * (sh + r)
        wy0 = wy1 - sh
        ww = xr - xl
        b.append(f'<path d="M{xl:.1f} {wy1:.1f}V{wy0:.1f}H{xr:.1f}V{wy1:.1f}" stroke-width="2.4"/>')
        b.append(mithila_band(xl + 5, xr - 5, wy0 + 9))
        top = wy0 + 18
        if i == 0:                                                   # ground storey: arched door, lotus above, a window each side
            dw = max(12, ww * .22)
            dh = min(sh * .5, 30)
            b.append(f'<path d="M{(xl + xr) / 2 - dw / 2:.1f} {wy1:.1f}V{wy1 - dh + dw / 2:.1f}A{dw / 2:.1f} {dw / 2:.1f} 0 0 1 {(xl + xr) / 2 + dw / 2:.1f} {wy1 - dh + dw / 2:.1f}V{wy1:.1f}" stroke-width="2"/>')
            b.append(dotpath([((xl + xr) / 2, wy1 - dh * .45)], w=2.6))
            if wy1 - dh - top > 12:
                b.append(lotus_motif((xl + xr) / 2, wy1 - dh - 7, 6))
            for fx in (.17, .83):
                wwid = ww * .15
                hh = max(14, sh * .36)
                b.append(newari_window(xl + ww * fx, wy1 - hh - sh * .14, wwid, hh))
            b.append(dotpath([(xl + 7 + j * 11, wy1 - 5) for j in range(int((ww - 14) / 11) + 1)], w=1.6))
        else:                                                        # upper storeys: a row of three carved windows (the tikijhya in the middle)
            for fx, k in ((.2, .7), (.5, 1.0), (.8, .7)):
                wwid = ww * .17 * (1.25 if k == 1.0 else 1)
                hh = max(14, sh * .52)
                b.append(newari_window(xl + ww * fx, top - 1, wwid, min(hh, wy1 - top - 4)))
        # roof of this storey: upswept eaves, tile strokes, hanging fringe
        ov = 9 + (tiers - i) * 3
        ex0, ex1 = xl - ov, xr + ov
        ry = wy0
        b.append(f'<path d="M{ex0:.1f} {ry - 4:.1f}Q{xl - 2:.1f} {ry + 3:.1f} {xl + ov * .7:.1f} {ry - r * .45:.1f}L{xl + ov + 5:.1f} {ry - r:.1f}H{xr - ov - 5:.1f}L{xr - ov * .7:.1f} {ry - r * .45:.1f}Q{xr + 2:.1f} {ry + 3:.1f} {ex1:.1f} {ry - 4:.1f}Z" stroke-width="2.4"/>')
        n = int((ex1 - ex0) / 8)
        for j in range(1, n):
            tx = ex0 + (ex1 - ex0) * j / n
            u = (tx - (ex0 + ex1) / 2) / ((ex1 - ex0) / 2)
            top_y = ry - r + max(0, abs(u) - .62) * r * 1.6
            b.append(f'<path d="M{tx:.1f} {top_y:.1f}V{ry - 1:.1f}" stroke-width=".9"/>')
        b.append(dotpath([(ex0 + 6 + j * 8, ry + 6) for j in range(int((ex1 - ex0 - 12) / 8) + 1)], w=1.5))
    # pinnacle (gajur)
    cx = x + w / 2
    ty = y1 - tiers * (sh + r)
    b.append(line(cx, ty, cx, ty - 12, w=1.8))
    b.append(f'<path d="M{cx - 5:.1f} {ty - 5:.1f}h10M{cx - 3.5:.1f} {ty - 9:.1f}h7" stroke-width="1.6"/>')
    b.append(f'<path d="M{cx - 2.5:.1f} {ty - 12:.1f}L{cx:.1f} {ty - 21:.1f}L{cx + 2.5:.1f} {ty - 12:.1f}Z" stroke-width="1.4"/>')
    return "".join(b)


def house_thatch(x, w, h):
    """A simple village hut: plain mud walls with an ochre-painted base, a small door and window, a thick thatched roof and a curl of cooking smoke."""
    y1 = 186
    y0 = y1 - h
    rise = h * .62
    b = [f'<path d="M{x} {y1}V{y0}H{x + w}V{y1}" stroke-width="2.4"/>']
    b.append(line(x, y1 - 12, x + w, y1 - 12, w=1.2))
    b.append(dotpath([(x + 6 + j * 9, y1 - 6) for j in range(int((w - 12) / 9) + 1)], w=1.6))
    dw = w * .22
    b.append(f'<path d="M{x + w * .22:.1f} {y1}V{y0 + h * .3:.1f}H{x + w * .22 + dw:.1f}V{y1}" stroke-width="2"/>')
    b.append(f'<rect x="{x + w * .62:.1f}" y="{y0 + h * .22:.1f}" width="{w * .17:.1f}" height="{h * .26:.1f}" stroke-width="1.8"/>')
    b.append(f'<path d="M{x - 9} {y0 + 3}L{x + w * .2:.1f} {y0 - rise:.1f}H{x + w * .8:.1f}L{x + w + 9} {y0 + 3}Z" stroke-width="2.4"/>')
    for j in range(1, 7):                                            # thatch: a few long soft strokes, a ragged fringe at the eaves
        tx = x - 9 + (w + 18) * j / 7
        b.append(f'<path d="M{tx:.1f} {y0 + 1:.1f}L{x + w * (.2 + .6 * j / 7):.1f} {y0 - rise + 3:.1f}" stroke-width="1"/>')
    b.append(path([(x - 9 + (w + 18) * j / 14, y0 + 3 + (3 if j % 2 else 0)) for j in range(15)], w=1.2))
    sx, sy = x + w * .72, y0 - rise - 2                              # smoke
    pts = [(sx + 5 * math.sin(t * .9), sy - t * 3.6) for t in range(9)]
    b.append(path(pts, w=1.2, a=.2))
    return "".join(b)


def house_stone(x, w, h):
    """A hill-village house: two storeys of plain stone-and-mud wall, a wooden balcony across the upper floor, and a low tin roof."""
    y1 = 186
    sh = h / 2
    ym = y1 - sh
    y0 = y1 - h
    b = [f'<path d="M{x} {y1}V{y0}H{x + w}V{y1}" stroke-width="2.4"/>']
    b.append(line(x, ym, x + w, ym, w=1.4))
    # ground floor: door and small window
    b.append(f'<path d="M{x + w * .14:.1f} {y1}V{ym + sh * .3:.1f}H{x + w * .14 + w * .2:.1f}V{y1}" stroke-width="2"/>')
    b.append(f'<rect x="{x + w * .58:.1f}" y="{ym + sh * .3:.1f}" width="{w * .16:.1f}" height="{sh * .3:.1f}" stroke-width="1.8"/>')
    # balcony
    by = ym - 2
    b.append(f'<path d="M{x - 6} {by:.1f}H{x + w + 6}" stroke-width="2"/>')
    b.append(f'<path d="M{x - 6} {by - 11:.1f}H{x + w + 6}" stroke-width="1.6"/>')
    b.append(f'<path d="' + "".join(f"M{x - 4 + j * 8} {by:.1f}v-11" for j in range(int((w + 8) / 8) + 1)) + '" stroke-width="1.1"/>')
    # upper floor: two small shuttered windows
    for fx in (.2, .62):
        b.append(f'<rect x="{x + w * fx:.1f}" y="{y0 + sh * .22:.1f}" width="{w * .18:.1f}" height="{sh * .38:.1f}" stroke-width="1.8"/>')
    b.append(dotpath([(x + 7 + j * 10, y0 + 7) for j in range(int((w - 14) / 10) + 1)], w=1.6))
    # low pitched tin roof
    rise = sh * .48
    b.append(f'<path d="M{x - 8} {y0}L{x + w / 2:.1f} {y0 - rise:.1f}L{x + w + 8} {y0}Z" stroke-width="2.4"/>')
    b.append(path([(x + 6, y0 - 3), (x + w / 2, y0 - rise + 4), (x + w - 6, y0 - 3)], w=1.1, a=.0))
    b.append(f'<path d="M{x + w * .3:.1f} {y0 - 1:.1f}L{x + w / 2:.1f} {y0 - rise + 9:.1f}L{x + w * .7:.1f} {y0 - 1:.1f}" stroke-width="1"/>')
    return "".join(b)


def rhododendron_tree(cx, base=186, seed=5):
    """A lali gurans (tree rhododendron), Nepal's national flower: a gnarled leaning trunk, forking branches, irregular clumps of leaves and clusters of blossom."""
    rng = random.Random(seed)
    b = []
    clumps = []

    def jit(v, k=1.0):
        return v + rng.uniform(-k, k)

    def limb(x, y, ang, ln, wid, depth):
        ex, ey = x + ln * math.cos(ang), y + ln * math.sin(ang)
        bend = rng.uniform(-.35, .35) * ln
        mx, my = (x + ex) / 2 + bend * -math.sin(ang), (y + ey) / 2 + bend * math.cos(ang)
        b.append(f'<path d="M{x:.1f} {y:.1f}Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke-width="{wid:.1f}"/>')
        if depth == 0 or ln < 9:
            clumps.append((ex, ey, ang))
            return
        n = 2 if depth > 1 or rng.random() < .5 else 3
        spread = rng.uniform(.5, .8)
        for k in range(n):
            da = (k - (n - 1) / 2) * spread + rng.uniform(-.2, .2)
            limb(ex, ey, ang + da, ln * rng.uniform(.62, .78), max(1.0, wid * .62), depth - 1)
        if rng.random() < .7:                                          # a short side twig partway along
            clumps.append((mx + rng.uniform(-3, 3), my + rng.uniform(-3, 3), ang))

    # trunk: leans a little, wider at the base with roots, wrinkled bark
    lean = rng.uniform(-.12, .1)
    tx0, ty0 = cx, base
    tx1, ty1 = cx + 8 * lean * 10 / 3 + 4, base - 60
    for off, wid in ((-5.5, 2.2), (5.5, 2.2)):
        b.append(f'<path d="M{tx0 + off * 1.9:.1f} {base}C{tx0 + off * .7:.1f} {base - 16} {tx0 + off * .9 - 2:.1f} {base - 34} {tx1 + off * .6:.1f} {ty1}" stroke-width="{wid}"/>')
    b.append(f'<path d="M{tx0 - 16:.1f} {base}C{tx0 - 9:.1f} {base - 3} {tx0 - 8:.1f} {base - 8} {tx0 - 6:.1f} {base - 14}M{tx0 + 16:.1f} {base}C{tx0 + 9:.1f} {base - 3} {tx0 + 8:.1f} {base - 8} {tx0 + 6:.1f} {base - 14}" stroke-width="1.6"/>')
    for k in range(7):                                                  # bark
        yy = base - 10 - k * 7
        xx = tx0 + rng.uniform(-3, 3) + (tx1 - tx0) * (k / 8)
        b.append(f'<path d="M{xx - 2:.1f} {yy:.1f}q2 -3 {rng.uniform(-1, 3):.1f} -6" stroke-width="1"/>')
    limb(tx1 - 1, ty1 + 2, -math.pi / 2 + lean - .5, 28, 3.4, 2)
    limb(tx1 + 1, ty1 + 2, -math.pi / 2 + lean + .45, 30, 3.4, 2)
    limb(tx1, ty1 + 4, -math.pi / 2 + lean + .02, 26, 3.0, 2)
    # foliage clumps (irregular blobs) with leaves, and blossom on some
    for i, (x, y, ang) in enumerate(clumps):
        r = rng.uniform(10, 14)
        n = 9
        pts = [(x + r * rng.uniform(.75, 1.2) * math.cos(2 * math.pi * k / n), y - r * .2 + r * .8 * rng.uniform(.75, 1.2) * math.sin(2 * math.pi * k / n)) for k in range(n)]
        d = ""
        for k in range(n):
            (x0, y0), (x1, y1) = pts[k], pts[(k + 1) % n]
            m0 = ((pts[k - 1][0] + x0) / 2, (pts[k - 1][1] + y0) / 2)
            if k == 0:
                d += f"M{m0[0]:.1f} {m0[1]:.1f}"
            d += f"Q{x0:.1f} {y0:.1f} {(x0 + x1) / 2:.1f} {(y0 + y1) / 2:.1f}"
        b.append(f'<path d="{d}Z" stroke-width="1.8"/>')
        for _ in range(3):                                              # leaves: small pointed ovals fanning outward
            lx, ly_ = x + rng.uniform(-r * .6, r * .6), y - r * .2 + rng.uniform(-r * .4, r * .4)
            la = rng.uniform(0, 2 * math.pi)
            L = rng.uniform(5.5, 8)
            ex, ey = lx + L * math.cos(la), ly_ + L * math.sin(la)
            px_, py_ = -math.sin(la) * L * .28, math.cos(la) * L * .28
            b.append(f'<path d="M{lx:.1f} {ly_:.1f}Q{(lx + ex) / 2 + px_:.1f} {(ly_ + ey) / 2 + py_:.1f} {ex:.1f} {ey:.1f}Q{(lx + ex) / 2 - px_:.1f} {(ly_ + ey) / 2 - py_:.1f} {lx:.1f} {ly_:.1f}Z" stroke-width="1"/>')
        if i % 2 == 0:                                                  # a bunch of blossoms
            for _ in range(2):
                fx, fy = x + rng.uniform(-r * .45, r * .45), y - r * .25 + rng.uniform(-r * .3, r * .3)
                b.append("".join(f'<circle cx="{fx + 2.2 * math.cos(q * 2 * math.pi / 5):.1f}" cy="{fy + 2.2 * math.sin(q * 2 * math.pi / 5):.1f}" r="1.6" stroke-width=".9"/>' for q in range(5)))
    b.append(dotpath([(cx + rng.uniform(-34, 34), base + rng.uniform(-6, -1)) for _ in range(9)], w=1.8))   # fallen petals
    return f'<g transform="translate({cx} {base}) scale(1.12) translate({-cx} {-base})">' + "".join(b) + "</g>"


def village():
    b = []
    W = 900
    b.append(path([(0, 187), (450, 189), (900, 187)], w=2.4, a=.5))
    b.append(dotpath([(8 + i * 14, 196) for i in range(63)], w=2))
    # yard fence
    for x in range(6, 150, 18):
        b.append(line(x, 186, x, 164, w=1.6))
    b.append(line(6, 172, 148, 172, w=1.4)); b.append(line(6, 180, 148, 180, w=1.2))
    # leftmost house, then neighbours
    b.append(house(170, 120, 92, 30, 2))
    b.append(house_thatch(316, 92, 46))
    b.append(house_stone(430, 104, 86))
    b.append(house(566, 112, 124, 30, 3))
    b.append(house_stone(702, 80, 66))
    b.append(rhododendron_tree(822))
    # clothesline between two poles in the yard: smaller, with the clothes hanging from the line by their shoulders / waists
    px0, px1, pt = 14, 148, 104
    b.append(line(px0, 186, px0, pt, w=2.4)); b.append(line(px1, 186, px1, pt, w=2.4))

    def ly(x):
        return 108 + 5 * math.sin(math.pi * (x - px0) / (px1 - px0))
    b.append(path([(x, ly(x)) for x in range(px0, px1 + 1, 6)] + [(px1, ly(px1))], w=1.3, a=.2))
    # kurta
    cx = 38
    y = ly(cx)
    b.append(f'<path d="M{cx - 6} {y:.1f}l-13 7l4 6l6 -3v20h18v-20l6 3l4 -6l-13 -7q-6 5 -12 0z" stroke-width="1.7"/>' + dotpath([(cx, y + 14), (cx, y + 20)], w=2))
    # the YogaMaty, folded over the line: stripes, bound edge, fringe
    mx0, mx1 = 62, 88
    y = ly((mx0 + mx1) / 2)
    my1 = y + 40
    b.append(f'<path d="M{mx0} {y:.1f}H{mx1}V{my1:.1f}H{mx0}Z" fill="#fff" stroke-width="2.2"/><path d="M{mx0 + 3} {y + 3:.1f}V{my1 - 2:.1f}M{mx1 - 3} {y + 3:.1f}V{my1 - 2:.1f}" stroke-width="1"/>')
    yy = y + 7
    kind = 0
    while yy < my1 - 7:
        if kind % 3 == 0:
            b.append(f'<path d="M{mx0 + 5} {yy:.1f}H{mx1 - 5}M{mx0 + 5} {yy + 3.5:.1f}H{mx1 - 5}" stroke-width="1"/>'); yy += 8
        elif kind % 3 == 1:
            b.append(dotpath([(x, yy) for x in range(mx0 + 7, mx1 - 3, 6)], w=2)); yy += 7
        else:
            b.append(f'<path d="M{mx0 + 5} {yy + 3:.1f}l4 -4l4 4l4 -4l4 4" stroke-width="1"/>'); yy += 8
        kind += 1
    for x in range(mx0 + 2, mx1, 4):
        b.append(line(x, my1, x, my1 + 7, w=1))
    # sari length with a patterned border
    sx0, sx1 = 98, 112
    y = ly((sx0 + sx1) / 2)
    b.append(f'<path d="M{sx0} {y:.1f}H{sx1}V{y + 44:.1f}H{sx0}Z" stroke-width="1.7"/><path d="M{sx0} {y + 36:.1f}H{sx1}M{sx0} {y + 40:.1f}H{sx1}" stroke-width="1"/>' + dotpath([(105, y + 9), (105, y + 17), (105, y + 25)], w=2))
    # small trousers hung by the waist
    cx = 133
    y = ly(cx)
    b.append(f'<path d="M{cx - 9} {y:.1f}H{cx + 9}V{y + 4:.1f}L{cx + 8} {y + 28:.1f}H{cx + 2}L{cx} {y + 11:.1f}L{cx - 2} {y + 28:.1f}H{cx - 8}L{cx - 9} {y + 4:.1f}Z" stroke-width="1.6"/>')
    # pegs
    for px in (33, 43, 62, 88, 101, 109, 128, 138):
        b.append(dotpath([(px, ly(px) - 1)], w=2.4))
    write("village", (900, 210), "".join(b))


# ---------------------------------------------------------------- the passport flow (A-E): interactive Mithila-style piece
NODES = [("A", "Hemp"), ("B", "Reclaimed saris"), ("C", "Weaving"), ("D", "Finishing"), ("E", "Distribution")]


def picto(i, cx, cy):
    g = []
    if i == 0:                                                    # hemp leaf fan
        g.append(line(cx, cy + 30, cx, cy + 6, w=2))
        for a in (-64, -32, 0, 32, 64):
            g.append(leaf(cx, cy + 12, math.radians(-90 + a), 34 - abs(a) * .1, 8, veins=False))
    elif i == 1:                                                  # strips of sari
        for k, dy in enumerate((-18, 0, 18)):
            top = [(cx - 32 + t * 8, cy + dy - 6 + math.sin(t + k) * 3) for t in range(9)]
            g.append(path(top, w=2, a=.2)); g.append(path([(x, y + 12) for x, y in top], w=2, a=.2))
            g.append(dotpath([(cx - 26 + t * 13, cy + dy + 2 + math.sin(t * 1.6 + k)) for t in range(5)], w=2.2) if k != 1 else
                     f'<path d="' + "".join(f"M{cx - 28 + t * 8} {cy + dy - 2}l4 8" for t in range(8)) + '" stroke-width="1"/>')
    elif i == 2:                                                  # warp and weft
        for k in range(6):
            g.append(line(cx - 25 + k * 10, cy - 28, cx - 25 + k * 10, cy + 28, w=1.4))
        for j in range(5):
            y = cy - 20 + j * 10
            for k in range(5):
                if (j + k) % 2:
                    g.append(f'<rect x="{cx - 25 + k * 10 + 1}" y="{y - 3}" width="8" height="6" fill="#CC5500" stroke-width="1.4"/>')
    elif i == 3:                                                  # a ring of running stitches around a cross-stitch
        g.append(f'<path d="' + "".join(f"M{cx + 28 * math.cos(a):.0f} {cy + 28 * math.sin(a):.0f}l{-5 * math.sin(a):.0f} {5 * math.cos(a):.0f}" for a in [k * math.pi / 8 for k in range(16)]) + '" stroke-width="2.2"/>')
        g.append(f'<path d="M{cx - 11} {cy - 11}l22 22M{cx + 11} {cy - 11}l-22 22" stroke-width="2.4"/>' + dotpath([(cx, cy - 20), (cx, cy + 20), (cx - 20, cy), (cx + 20, cy)], w=3))
    else:                                                         # a home
        g.append(f'<path d="M{cx - 26} {cy + 24}V{cy - 4}H{cx + 26}V{cy + 24}Z" stroke-width="2.2"/><path d="M{cx - 34} {cy - 4}L{cx - 14} {cy - 24}H{cx + 14}L{cx + 34} {cy - 4}Z" stroke-width="2.2"/>')
        g.append(f'<path d="M{cx - 6} {cy + 24}v-14h12v14" stroke-width="1.8"/><path d="M{cx - 22} {cy + 2}h10v8h-10zM{cx + 12} {cy + 2}h10v8h-10z" stroke-width="1.4"/>' + dotpath([(cx, cy - 14)], w=3))
    return "".join(g)


def node(i, cx, cy, vertical=False):
    letter, name = NODES[i]
    pic = (circle(cx, cy, 54, w=3) + circle(cx, cy, 46, w=1.3) + picto(i, cx, cy) +
           dotpath([(cx + 62 * math.cos(k * math.pi / 8), cy + 62 * math.sin(k * math.pi / 8)) for k in range(16)], w=2.6))
    if vertical:
        label = f'<text x="{cx + 92}" y="{cy + 10}" class="fl-name">{name}</text>'
    else:
        label = f'<text x="{cx}" y="{cy + 112}" text-anchor="middle" class="fl-name">{name}</text>'
    hit = (f'<circle cx="{cx}" cy="{cy}" r="68" fill="transparent" stroke="none"/>' +
           (f'<rect x="{cx + 80}" y="{cy - 40}" width="270" height="84" fill="transparent" stroke="none"/>' if vertical else
            f'<rect x="{cx - 110}" y="{cy + 84}" width="220" height="40" fill="transparent" stroke="none"/>'))
    return (f'<a class="flow-node" href="__{letter}__" aria-label="{name} — see this stage in the passport">'
            f'{hit}<g class="pic">{pic}</g>{label}</a>')


def thread_strands(p0, p1, sag, bow_dir=(0, 1), offs=(-2.2, .3, 2.1), n=44, skew=1.0, wob=0.0, phase=0.0, freq=3.1):
    """A straight, taut thread made of three strands that lie almost on top of each other (they drift a little apart and together).
    The thread sags a little between its ends, along bow_dir; the same slack is used everywhere so the tension looks even."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    nx, ny = -uy, ux
    if (nx * bow_dir[0] + ny * bow_dir[1]) < 0:
        nx, ny = -nx, -ny
    out = []
    for k, off in enumerate(offs):
        q = []
        for i in range(n + 1):
            t = i / n
            tt = t ** skew                                           # skew moves the lowest point of the sag off-centre
            bow = sag * (1 - (2 * tt - 1) ** 2) + wob * math.sin(math.pi * t) * math.sin(freq * math.pi * t + phase + k * .5)
            o = off * (1 + .35 * math.sin(t * math.pi * 2 + k * 1.7))
            q.append((p0[0] + (p1[0] - p0[0]) * t + nx * (bow + o), p0[1] + (p1[1] - p0[1]) * t + ny * (bow + o)))
        out.append(f'<path d="{smooth2(q[::2] + [q[-1]])}" stroke-width="1.9"/>')
    return "".join(out)


def sag_for(length):
    return 14 * math.sqrt(max(length, 60) / 218.0)


def needle_parts(eye, rot, length=130):
    """A tilted sewing needle whose eye (a slot) sits at `eye`. Returns (tail_behind, needle, local_to_world) pieces."""
    th = math.radians(rot)
    ox, oy = eye[0] - 19 * math.cos(th), eye[1] - 19 * math.sin(th)
    L = length
    body = (f"M0 -5.5L{L * .8:.1f} -3.4Q{L * .95:.1f} -1.2 {L} 0Q{L * .95:.1f} 1.2 {L * .8:.1f} 3.4L0 5.5Q-5 0 0 -5.5Z")
    slot = "M10 0a9 2.3 0 1 0 18 0a9 2.3 0 1 0 -18 0z"
    tail = "".join(f'<path d="M19 0Q{31 + d:.1f} {9 + d:.1f} {40 + d * 1.4:.1f} {30 + d:.1f}" stroke-width="1.9"/>' for d in (-1.8, 0.2, 2.0))
    tr = f"translate({ox:.2f} {oy:.2f}) rotate({rot})"
    behind = f'<g transform="{tr}">{tail}</g>'
    front = (f'<g transform="{tr}"><path d="{body}" style="fill:var(--orange)" stroke-width="2.4"/>'
             f'<path d="{slot}" stroke-width="1.6"/><path d="M34 -1.6L{L * .78:.1f} -0.9" stroke-width="1"/></g>')
    return behind, front


def flow():
    # horizontal (desktop): five circles on one line, thread enters from off the left edge of the page and runs through them to a tilted needle
    b = []
    cy = 128
    xs = [118, 330, 542, 754, 966]
    R_ = 58
    # left run-in: from far off the page to the first circle
    p0, p1 = (-760, cy), (xs[0] - R_, cy)
    b.append(st(thread_strands(p0, p1, 24, skew=1.3, wob=7.0, phase=1.1, freq=8.5, n=160), 0))
    VAR = [(1.0, .82, 2.2, 0.3), (.72, 1.2, 1.6, 2.1), (1.3, .9, 2.6, 4.0), (.88, 1.12, 1.9, 5.2)]     # (sag scale, skew, wobble, phase) per span
    for i in range(4):
        p0, p1 = (xs[i] + R_, cy), (xs[i + 1] - R_, cy)
        sc, sk, wb, ph = VAR[i]
        b.append(st(thread_strands(p0, p1, sag_for(p1[0] - p0[0]) * sc, skew=sk, wob=wb, phase=ph), xs[i] + 70))
    eye = (1114, cy + 6)
    behind, front = needle_parts(eye, -14)
    p0 = (xs[4] + R_, cy)
    b.append(st(behind, 1080))
    b.append(st(front, 1080))
    b.append(st(thread_strands(p0, eye, sag_for(eye[0] - p0[0]) * 1.15, skew=.9, wob=2.0, phase=3.3), xs[4] + 70))      # in front of the needle, ending in its eye
    for i in range(5):
        b.append(node(i, xs[i], cy))
    write("flow-h", (1200, 262), "".join(b))
    # vertical (phones): thread runs down through the circles into a tilted needle below
    b = []
    X = 80
    ys = [90, 290, 490, 690, 890]

    def stv(inner, y):
        i = max(0, min(99, int(y / 1150 * 96)))
        return f'<g class="stitch" style="--i:{i}">{inner}</g>'
    b.append(stv(thread_strands((X, -300), (X, ys[0] - 60), sag_for(120), bow_dir=(1, 0)), 0))
    for i in range(4):
        p0, p1 = (X, ys[i] + 60), (X, ys[i + 1] - 60)
        b.append(stv(thread_strands(p0, p1, sag_for(abs(p1[1] - p0[1])), bow_dir=(1, 0)), ys[i] + 60))
    eye = (X + 3, 1010)
    behind, front = needle_parts(eye, 90 - 14)
    b.append(stv(behind, 1000))
    b.append(stv(front, 1000))
    b.append(stv(thread_strands((X, ys[4] + 60), eye, sag_for(abs(eye[1] - ys[4] - 60)), bow_dir=(1, 0)), ys[4] + 60))
    for i in range(5):
        b.append(node(i, X, ys[i], vertical=True))
    write("flow-v", (400, 1150), "".join(b))


if __name__ == "__main__":
    for fn in (weave, hands_cup, clouds_band, rain, lotus_bloom, sun_spiral, village, flow, fish, peacock, sun, lotus, cloud, mandala, dividers, hemp, ret, spin, hank, hands, spool, loom, sari, sewing, mat_roll, mat_sheet, water, leaves, bloom, rosette, border, favicon):
        fn()
    print("motifs written to", OUT)
