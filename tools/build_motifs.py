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
def mat_roll():
    W, H = 600, 92
    b = []
    x0, x1, yt, yb = 40, 566, 12, 80
    b.append(path([(x0, yt), (300, yt - 2), (x1, yt)], w=3.4, a=.5))
    b.append(path([(x0, yb), (300, yb + 2), (x1, yb)], w=3.4, a=.5))
    b.append(path([(x0, yt + 7), (300, yt + 5), (x1, yt + 7)], w=1.2, a=.4))      # cream binding, doubled line
    b.append(path([(x0, yb - 7), (300, yb - 5), (x1, yb - 7)], w=1.2, a=.4))
    # left end face with the spiral of the binding
    cy, ry, rx = (yt + yb) / 2, (yb - yt) / 2, 26
    b.append(ellipse(x0, cy, rx, ry, w=3.4, n=16))
    sp = []
    for k in range(0, 60):
        t = k * .42
        rr = .10 + t * .062
        if rr < .93:
            sp.append((x0 + rx * rr * math.cos(t) * .9, cy + ry * rr * math.sin(t)))
    b.append(path(sp, w=2.2, a=.3))
    # right end: the curve of the cylinder
    b.append(path([(x1, yt), (x1 + 22, cy), (x1, yb)], w=3.4, a=.5))
    b.append(path([(x1, yt + 7), (x1 + 13, cy), (x1, yb - 7)], w=1.2, a=.4))
    # stripes seen along the rolled body: bands of changing rhythm
    x = x0 + 40
    i = 0
    while x < x1 - 20:
        wb = R.choice([10, 16, 24, 34])
        kind = i % 4
        if kind == 0:
            for q in range(int(wb / 5)):
                b.append(line(x + q * 5, yt + 14, x + q * 5 + R.uniform(-.8, .8), yb - 14, w=1.1))
        elif kind == 1:
            b.append(line(x + 2, yt + 14, x + 2, yb - 14, w=2.2)); b.append(line(x + wb - 2, yt + 14, x + wb - 2, yb - 14, w=2.2))
        elif kind == 2:
            for q in range(int(wb / 9) + 1):
                for yy in range(int(yt + 20), int(yb - 14), 10):
                    b.append(f'<path d="M{f(x + q * 9)} {f(yy)}h0" stroke-width="3"/>')
        else:
            for q in range(int(wb / 8) + 1):
                for yy in range(int(yt + 16), int(yb - 18), 16):
                    b.append(line(x + q * 8, yy, x + q * 8, yy + 8, w=1.6))
        x += wb + 10
        i += 1
    write("mat-roll", (W, H), "".join(b))


def mat_sheet():
    W, H = 600, 640
    b = []
    x0, x1, y1 = 40, 566, 596
    # binding down both long edges (doubled lines)
    for xx in (x0, x1):
        b.append(path([(xx, -4), (xx + R.uniform(-1, 1), 300), (xx, y1)], w=3.4, a=.5))
    for xx in (x0 + 7, x1 - 7):
        b.append(path([(xx, -4), (xx + R.uniform(-1, 1), 300), (xx, y1)], w=1.2, a=.4))
    b.append(path([(x0, y1), (300, y1 + 2), (x1, y1)], w=3.4, a=.5))
    b.append(path([(x0, y1 - 7), (300, y1 - 5), (x1, y1 - 7)], w=1.2, a=.4))
    # stripes run the short way across the mat; each band has its own rhythm
    y = 10
    i = 0
    while y < y1 - 30:
        hb = R.choice([14, 22, 30, 44, 60])
        kind = i % 5
        top, bot = y, min(y + hb, y1 - 22)
        if kind == 0:                       # dense hatching
            yy = top
            while yy < bot:
                b.append(path([(x0 + 14, yy), (300, yy + R.uniform(-.8, .8)), (x1 - 14, yy)], w=1.1, a=.3)); yy += 5
        elif kind == 1:                     # open spacing, two heavy lines
            for yy in (top + 3, bot - 3):
                b.append(path([(x0 + 14, yy), (300, yy + R.uniform(-1, 1)), (x1 - 14, yy)], w=2.4, a=.4))
        elif kind == 2:                     # dotted runs
            yy = top + 6
            while yy < bot:
                d = "".join(f"M{f(xx)} {f(yy)}h0" for xx in range(x0 + 20, x1 - 14, 11))
                b.append(f'<path d="{d}" stroke-width="3"/>'); yy += 11
        elif kind == 3:                     # dashed runs
            yy = top + 6
            while yy < bot:
                d = "".join(f"M{f(xx)} {f(yy)}h8" for xx in range(x0 + 16, x1 - 24, 16))
                b.append(f'<path d="{d}" stroke-width="1.8"/>'); yy += 10
        else:                               # zig-zag
            yy = top + 4
            pts = [(xx, yy + (hb - 8 if (k % 2) else 0) * .5) for k, xx in enumerate(range(x0 + 16, x1 - 10, 14))]
            b.append(path(pts, w=1.6, a=.3))
        y = bot + 8
        i += 1
    # knotted fringe at the free end
    for k in range(27):
        xx = x0 + 6 + k * (x1 - x0 - 12) / 26
        b.append(path([(xx, y1), (xx + R.uniform(-3, 3), y1 + 18), (xx + R.uniform(-4, 4), y1 + 34)], w=1.6, a=.4))
        b.append(f'<path d="M{f(xx)} {f(y1 + 14)}h0" stroke-width="4"/>')
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
            tp = math.sin(math.pi * i / (n - 1)) ** .5
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
# as the visitor scrolls; some carry a needle that leads the way.
# =====================================================================================================
SW = 1200


def st(inner, x):
    i = max(0, min(99, int(x / SW * 96)))
    return f'<g class="stitch" style="--i:{i}">{inner}</g>'


def needle():
    return ('<g class="needle"><path d="M0 36L-52 31Q-62 36 -52 41Z" stroke-width="2.4"/><ellipse cx="-50" cy="36" rx="3" ry="2" stroke-width="1.4"/>'
            '<path d="M-52 36C-84 54 -104 20 -140 40" stroke-width="1.6"/></g>')


def write_div(n, body):
    write(f"stitch-{n}", (SW, 72), body)


def dividers():
    # 1 running stitch, two staggered rows
    b = []
    for row, y in enumerate((26, 46)):
        x = 14 + (row * 14)
        while x < SW - 24:
            b.append(st(f'<line x1="{x}" y1="{y + R.uniform(-1, 1):.0f}" x2="{x + 18}" y2="{y + R.uniform(-1, 1):.0f}" stroke-width="2.6"/>', x))
            x += 30
    write_div(1, "".join(b) + needle())
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
    write_div(2, "".join(b) + needle())
    # 3 lotus chain
    b = []
    for k in range(12):
        cx = 50 + k * 100
        g = line(cx - 36, 60, cx - 16, 60, w=2) + line(cx + 16, 60, cx + 36, 60, w=2)
        for a in (-62, -31, 0, 31, 62):
            g += leaf(cx, 56, math.radians(-90 + a), 40 - abs(a) * .12, 8, veins=False)
        g += dotpath([(cx, 58)], w=4)
        b.append(st(g, cx))
    write_div(3, "".join(b))
    # 4 Mithila teeth: triangles with dots over a zig baseline
    b = []
    for k in range(30):
        x = 10 + k * 39.5
        g = f'<path d="M{f(x)} 62L{f(x + 19)} 12L{f(x + 38)} 62Z" stroke-width="2.4"/><path d="M{f(x + 8)} 62L{f(x + 19)} 28L{f(x + 30)} 62" stroke-width="1.2"/>'
        g += dotpath([(x + 19, 42), (x + 19, 52)], w=3)
        b.append(st(g, x))
    write_div(4, "".join(b))
    # 5 thangka flames
    b = []
    for k in range(20):
        x = 8 + k * 59.5
        o = f"M{f(x)} 66C{f(x - 4)} 46 {f(x + 22)} 40 {f(x + 14)} 22C{f(x + 12)} 14 {f(x + 22)} 10 {f(x + 30)} 4C{f(x + 28)} 22 {f(x + 52)} 38 {f(x + 48)} 66"
        g = f'<path d="{o}" stroke-width="2.4"/>'
        g += f'<path d="M{f(x + 10)} 66C{f(x + 8)} 52 {f(x + 26)} 46 {f(x + 24)} 30C{f(x + 36)} 40 {f(x + 40)} 54 {f(x + 38)} 66" stroke-width="1.2"/>'
        g += f'<path d="M{f(x + 22)} 66C{f(x + 22)} 56 {f(x + 28)} 52 {f(x + 28)} 44" stroke-width="1.1"/>' + dotpath([(x + 28, 58)], w=3)
        b.append(st(g, x))
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


if __name__ == "__main__":
    for fn in (fish, peacock, sun, lotus, cloud, mandala, dividers, hemp, ret, spin, hank, hands, spool, loom, sari, sewing, mat_roll, mat_sheet, water, leaves, bloom, rosette, border, favicon):
        fn()
    print("motifs written to", OUT)
