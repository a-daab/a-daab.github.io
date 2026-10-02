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


# ---------------------------------------------------------------- the mat (hero unroll)
def mat():
    b = []
    r = 62
    dx, dy = 96, -72                      # direction of the roll's axis = width of the mat
    c1 = (r + 8, 330)                     # front end-face centre
    c2 = (c1[0] + dx, c1[1] + dy)
    # roll: cylinder body (two tangents + back arc) and the front face with the cream-binding spiral
    nl = math.hypot(dx, dy)
    nx, ny = -dy / nl * r, dx / nl * r    # perpendicular offset to tangent points
    b.append(line(c1[0] + nx, c1[1] + ny, c2[0] + nx, c2[1] + ny, w=3.4))
    b.append(line(c1[0] - nx, c1[1] - ny, c2[0] - nx, c2[1] - ny, w=3.4))
    a0, a1 = math.atan2(-ny, -nx), math.atan2(ny, nx)
    arc = [(c2[0] + r * math.cos(a0 + (a1 - a0 + (2 * math.pi if a1 < a0 else 0)) * t / 8),
            c2[1] + r * math.sin(a0 + (a1 - a0 + (2 * math.pi if a1 < a0 else 0)) * t / 8)) for t in range(9)]
    b.append(path(arc, w=3.4, a=.4))
    b.append(circle(c1[0], c1[1], r, w=3.6))
    sp = []
    for k in range(0, 70):
        a = k * .36
        rr = 5 + a * 3.9
        if rr < r - 4:
            sp.append((c1[0] + rr * math.cos(a), c1[1] + rr * math.sin(a)))
    b.append(path(sp, w=2.8, a=.4))
    b.append(path([(x + 3.5, y + 3.5) for x, y in sp[3:]], w=1.2, a=.4))
    for t in range(1, 6):  # stripes seen on the rolled body
        k = t / 6
        b.append(path([(c1[0] + nx * (1 - 2 * k) + dx * .12, c1[1] + ny * (1 - 2 * k) + dy * .12),
                       (c1[0] + nx * (1 - 2 * k) + dx * .6, c1[1] + ny * (1 - 2 * k) + dy * .6)], w=1.1, a=.5))
    # flat mat, oblique. Starts under the roll's bottom tangent and runs right; the page scales it with scroll.
    ox, oy = c1[0] - ny * 0 + 0, c1[1] + r
    L = 400
    flat = []
    for off in (0, 1):
        ex, ey = ox + dx * off, oy + dy * off
        flat.append(path([(ex, ey), (ex + L / 2, ey + 2), (ex + L, ey)], w=3.4))
        flat.append(path([(ex + 6, ey - 6 * (1 - 2 * off)), (ex + L / 2, ey + 2 - 6 * (1 - 2 * off)), (ex + L - 6, ey - 6 * (1 - 2 * off))], w=1.3))
    flat.append(line(ox + L, oy, ox + L + dx, oy + dy, w=3.4))
    x = ox + 14
    kinds = ["hatch", "open", "dots", "dash"]
    i = 0
    while x < ox + L - 24:
        wband = R.choice([14, 20, 26, 34])
        kind = kinds[i % 4]
        step = 6 if kind == "hatch" else 10
        for sidx in range(int(wband / step)):
            xx = x + sidx * step
            if kind in ("hatch", "open"):
                flat.append(line(xx, oy - 8, xx + dx * .9, oy + dy * .9 + 4, w=1.1 if kind == "hatch" else 2))
            elif kind == "dots":
                for q in range(1, 7):
                    flat.append(circle(xx + dx * q / 7.4, oy + dy * q / 7.4 - 4, 1.2, w=1.6))
            else:
                for q in range(0, 5):
                    flat.append(line(xx + dx * q / 5.4, oy + dy * q / 5.4 - 6, xx + dx * (q + .55) / 5.4, oy + dy * (q + .55) / 5.4 - 6, w=1.6))
        x += wband + 6
        i += 1
    for k in range(14):  # knotted fringe at the far short end
        t = (k + .5) / 14
        sx, sy = ox + L + dx * t, oy + dy * t
        flat.append(path([(sx, sy), (sx + 18, sy + 1 + R.uniform(-1, 1)), (sx + 30, sy + R.uniform(-2, 3))], w=1.6, a=.5))
        flat.append(circle(sx + 31, sy + 1, 1.8, w=1.8))
    b.append(f'<g class="mat-flat">{"".join(flat)}</g>')
    write("mat", (0, 190, 620, 330), "".join(b))


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


if __name__ == "__main__":
    for fn in (hemp, ret, spin, hank, hands, spool, loom, sari, sewing, mat, water, leaves, bloom, rosette, border, favicon):
        fn()
    print("motifs written to", OUT)
