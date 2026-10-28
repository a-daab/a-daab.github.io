#!/usr/bin/env python3
"""Draw the six node icons for the How It Works web in a hand-cut, block-print manner (wobbly lines, carved solids,
hatch marks, overshooting strokes) and write them into the marked block of assets/js/web.js.

TEST-RUN ARTWORK, like the rest of the motif layer: replace with art made with Nepali artists.
    python3 tools/build_web_icons.py
Icons live on a 48-unit grid. Strokes use currentColor; solids use fill="currentColor"; knock-outs use fill="#fff".
"""
import math, random, pathlib, re

R = random.Random(23)
JS = pathlib.Path(__file__).resolve().parent.parent / "assets" / "js" / "web.js"


def n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def jit(p, a=0.45):
    return (p[0] + R.uniform(-a, a), p[1] + R.uniform(-a, a))


def smooth(pts, closed=False):
    """Catmull-Rom through the points -> cubic Bezier path data."""
    k = len(pts)
    if k < 3:
        return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts)
    P = (lambda i: pts[i % k]) if closed else (lambda i: pts[max(0, min(k - 1, i))])
    d = f"M{n(pts[0][0])} {n(pts[0][1])}"
    for i in range(k if closed else k - 1):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}"
    return d + ("Z" if closed else "")


def path(d, w=None, fill=None, extra=""):
    a = f' stroke-width="{w}"' if w else ""
    if fill == "solid":
        a += ' fill="currentColor" stroke="none"'
    elif fill:
        a += f' fill="{fill}"'
    return f'<path d="{d}"{a}{extra}/>'


def line(p, q, w=None, amp=0.35, over=0.7):
    """A hand-cut stroke: slight overshoot at both ends and a gentle bow."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    a = (p[0] - ux * over, p[1] - uy * over)
    b = (q[0] + ux * over, q[1] + uy * over)
    mid = ((a[0] + b[0]) / 2 - uy * R.uniform(-amp, amp) * 2, (a[1] + b[1]) / 2 + ux * R.uniform(-amp, amp) * 2)
    return path(smooth([jit(a, .25), mid, jit(b, .25)]), w)


def poly(pts, w=None, closed=True, a=0.4, fill=None):
    return path(smooth([jit(p, a) for p in pts], closed), w, fill)


def blob(cx, cy, rx, ry, w=None, fill=None, a=0.35, k=9, rot=0):
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k + rot
        pts.append((cx + math.cos(t) * rx * R.uniform(.94, 1.06), cy + math.sin(t) * ry * R.uniform(.94, 1.06)))
    return path(smooth([jit(p, a * .5) for p in pts], True), w, fill)


def dot(x, y, r=1.1):
    return path(smooth([(x + math.cos(t) * r, y + math.sin(t) * r) for t in (0, 1.6, 3.1, 4.7)], True), None, "solid")


def rect_lines(x0, y0, x1, y1, w=None):
    return "".join([line((x0, y0), (x1, y0), w), line((x1, y0), (x1, y1), w), line((x1, y1), (x0, y1), w), line((x0, y1), (x0, y0), w)])


def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [((x - cx) * c - (y - cy) * s + cx, (x - cx) * s + (y - cy) * c + cy) for x, y in pts]


def flower(x, y, r=2.2):
    out = ""
    for i in range(4):
        t = i * math.pi / 2 + .4
        out += dot(x + math.cos(t) * r, y + math.sin(t) * r, .8)
    return out + dot(x, y, .8)


# ------------------------------------------------------------------ Mithila-style helpers
_ids = [0]
ID_PREFIX = ""          # set by generators whose output shares a page with others, so clipPath ids never collide
TH, FINE = 0.9, 0.55      # outline and fine-line weights


def uid(prefix="m"):
    _ids[0] += 1
    return f"{ID_PREFIX}{prefix}{_ids[0]}"


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def inset(pts, f):
    cx, cy = centroid(pts)
    return [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in pts]


def shape(pts, w=TH, fill=None, a=0.22):
    return path(smooth([jit(p, a) for p in pts], True), w, fill)


def double(pts, f=0.84, fill=None):
    """Mithila double outline: the figure and a finer line inside it."""
    return shape(pts, TH, fill) + shape(inset(pts, f), FINE, None, .12)


def ring(cx, cy, r, w=FINE, fill=None):
    k = 10
    return path(smooth([(cx + math.cos(2 * math.pi * i / k) * r * R.uniform(.97, 1.03), cy + math.sin(2 * math.pi * i / k) * r * R.uniform(.97, 1.03)) for i in range(k)], True), w, fill)


def hatch(pts, angle=45, gap=2.6, w=0.5, keep=None):
    """Parallel fine lines filling a shape (clipped to it) - the Mithila filled-figure look."""
    cid = uid("c")
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs) - 3, max(xs) + 3, min(ys) - 3, max(ys) + 3
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    big = max(x1 - x0, y1 - y0) * 1.5
    lines = ""
    t = -big
    while t <= big:
        p, q = rot([(cx - big, cy + t), (cx + big, cy + t)], cx, cy, angle)
        lines += f"M{n(p[0])} {n(p[1])}L{n(q[0])} {n(q[1])}"
        t += gap
    return (f'<clipPath id="{cid}"><path d="{smooth(pts, True)}"/></clipPath>'
            f'<path d="{lines}" clip-path="url(#{cid})" stroke-width="{w}"/>')


def dotted(p, q, gap=2.4, r=0.5):
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    k = max(1, int(L / gap))
    return "".join(dot(p[0] + (q[0] - p[0]) * i / k, p[1] + (q[1] - p[1]) * i / k, r) for i in range(k + 1))


def petals(cx, cy, r=2.6, k=8, pr=.55):
    return "".join(dot(cx + math.cos(i * 2 * math.pi / k) * r, cy + math.sin(i * 2 * math.pi / k) * r, pr) for i in range(k)) + dot(cx, cy, .7)


def wheel(cx, cy, r):
    o = ring(cx, cy, r, TH) + ring(cx, cy, r * .5, FINE) + dot(cx, cy, .7)
    for i in range(6):
        t = i * math.pi / 3 + .3
        o += line((cx + math.cos(t) * r * .5, cy + math.sin(t) * r * .5), (cx + math.cos(t) * r * .92, cy + math.sin(t) * r * .92), .5, amp=.05, over=0)
    return o


def capsule(x0, y0, x1, y1, hw, tf):
    """A finger: flat base at (x0,y0), rounded tip at (x1,y1); points are mapped through tf."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    tipx, tipy = x1 - ux * hw, y1 - uy * hw
    pts = [(x0 + nx * hw, y0 + ny * hw), (tipx + nx * hw, tipy + ny * hw)]
    for i in range(1, 6):
        t = math.pi * i / 6
        pts.append((tipx + nx * hw * math.cos(t) + ux * hw * math.sin(t), tipy + ny * hw * math.cos(t) + uy * hw * math.sin(t)))
    pts += [(tipx - nx * hw, tipy - ny * hw), (x0 - nx * hw, y0 - ny * hw)]
    return [tf(p) for p in pts]


# ------------------------------------------------------------------ the icons
def consumer():
    o = ""
    o += path(smooth([(3.6, 7.6), (7, 7.8), (10, 11)]), TH)                                              # handle
    o += dot(3.4, 7.6, .8)
    basket = [(10, 11.2), (42, 13), (38, 29.4), (14.4, 29)]
    o += double(basket, .86, "#fff")
    o += hatch(inset(basket, .86), 52, 3.0, .5) + hatch(inset(basket, .86), -52, 3.0, .5)               # woven lattice
    o += path(smooth([(14.4, 29), (16.2, 34.2), (36.4, 34.6)]), TH)                                      # frame
    o += dotted((12.5, 8.4), (40.5, 10.2), 3.2, .5)                                                      # dotted rim
    o += wheel(19, 40, 3.7) + wheel(34.6, 40.4, 3.7)
    return o


def hand(ox, oy, sx, tilt, s=1.04):
    def tf(p):
        x, y = p
        x, y = x * sx * s, y * s
        c, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return (ox + x * c - y * sn, oy + x * sn + y * c)
    o = ""
    # sleeve with bangles
    sleeve = [tf(p) for p in [(-4.6, 2.5), (4.6, 2.5), (5.4, 11), (-5.4, 11)]]
    o += shape(sleeve, TH, "#fff") 
    for yy in (5.2, 7.2):
        o += line(tf((-4.9, yy)), tf((4.9, yy)), FINE, amp=.1)
    o += dotted(tf((-4.2, 9.4)), tf((4.2, 9.4)), 1.7, .4)
    # thumb, then the four fingers, then the palm over their bases
    thumb = capsule(-5.8, -1.2, -12, -8.8, 1.9, tf)
    o += shape(thumb, TH, "#fff", .12)
    o += line(tf((-7, -3.2)), tf((-10.2, -7)), .5, amp=.05, over=0)
    for (x, ln, hw) in ((-5.1, 12.4, 1.6), (-1.7, 14.4, 1.65), (1.7, 13, 1.6), (5.1, 10.2, 1.45)):
        f = capsule(x, -7, x, -7 - ln, hw, tf)
        o += shape(f, TH, "#fff", .12)
        o += line(tf((x, -9)), tf((x, -7 - ln + 3.2)), .5, amp=.05, over=0)                            # carved centre line
        o += dot(*tf((x, -7 - ln + 1.6)), .5)
    palm = [(-7, -8), (-2.4, -9.4), (2.4, -9.4), (7, -8), (7.4, -2), (5.2, 2.8), (-5.2, 2.8), (-7.4, -2)]
    o += shape([tf(p) for p in palm], TH, "#fff", .15)
    o += petals(*tf((0, -3.2)), r=2.9 * s, k=8, pr=.5)                                                 # mehndi flower
    o += ring(*tf((0, -3.2)), 1.4 * s, .5)
    return o


def artisan():
    return hand(13.8, 32.6, 1, -7) + hand(34.2, 32.6, -1, 7)


def materials():
    o = ""
    top = [(9.4, 6.4), (38.6, 6), (39, 10.6), (9.8, 11)]
    bot = [(9.6, 37.6), (39, 37.2), (38.6, 42), (9.2, 42.4)]
    o += double(top, .78, "#fff") + double(bot, .78, "#fff")
    o += dotted((12.5, 8.7), (35.6, 8.5), 3.0, .45) + dotted((12.5, 39.9), (35.6, 39.7), 3.0, .45)
    o += line((12, 11), (11.8, 37.6), TH) + line((36.2, 10.8), (36.4, 37.4), TH)                      # barrel sides
    y = 12.4
    while y < 36.4:                                                                                  # plenty of thread: two crossing windings
        o += line((12.2, y + 2.4), (36.2, y - .4), .6, amp=.12, over=0)
        o += line((12.2, y - .2), (36.2, y + 2.2), .5, amp=.12, over=0)
        y += 2.2
    o += path(smooth([(36.3, 35.6), (41, 38.4), (44, 42), (42.2, 45.4), (39.4, 44.2), (40.4, 42)]), .8)   # loose thread, curled
    o += dot(40.4, 41.4, .5)
    return o


def production():
    o = ""
    body = [(5, 11), (33, 10.4), (38.6, 13.4), (40.4, 22), (39.8, 34), (44.4, 35.2), (44.6, 43), (3.6, 43.6), (3.8, 35.2), (5.4, 34.4), (30.4, 34.8), (31.6, 21.4), (5.4, 20.6)]
    o += double(body, .93, "#fff")
    o += hatch([(31.8, 22), (39.2, 22.4), (38.6, 34), (31.4, 34)], 60, 2.0, .45)                        # filled column
    o += dotted((8, 15.6), (28, 15.4), 2.6, .5)
    o += petals(35.4, 16.6, 1.9, 6, .4)
    o += wheel(43.4, 16.4, 3.2)
    o += ring(20, 6, 2.2, TH) + dot(20, 6, .6)                                                        # thread spool on top
    o += path(smooth([(20, 8.2), (16, 11), (12.4, 14), (11.8, 20.2)]), .6)
    o += line((11.8, 20.6), (11.8, 31.4), TH)                                                          # needle
    o += path("M10.8 31.2L12.8 31.2L11.8 34.6Z", .8, "solid")
    o += dotted((6.4, 40.2), (42.4, 40), 2.4, .5)                                                      # stitched line on the bed
    return o


def note(cx, cy, w, h, deg, glyph=False, hatched=False):
    hw, hh = w / 2, h / 2
    outer = rot([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh)], cx, cy, deg)
    o = double(outer, .86, "#fff")
    if hatched:
        o += hatch(inset(outer, .86), 40, 2.4, .4)
    for dx in (-1, 1):
        x, y = rot([(cx + dx * (hw - 4.4), cy)], cx, cy, deg)[0]
        o += petals(x, y, 1.5, 4, .35)
    o += ring(cx, cy, 5.4, TH, "#fff") + ring(cx, cy, 4.4, .4)
    if glyph:
        o += f'<text x="{n(cx)}" y="{n(cy + 3.2)}" text-anchor="middle" font-size="8.4" font-weight="700" fill="currentColor" stroke="none">\u0930\u0942</text>'
    else:
        o += petals(cx, cy, 2.2, 6, .4)
    return o


def coin(cx, cy, r=3.5):
    return ring(cx, cy, r, TH, "#fff") + ring(cx, cy, r * .62, .5) + petals(cx, cy, r * .3, 4, .3)


def fair():
    o = ""
    o += note(18.6, 13.2, 30, 17, -12, hatched=True)
    o += note(27.2, 22.4, 31, 18, 6, glyph=True)
    for (x, y) in ((8.4, 41.4), (14, 43), (10.4, 36.6), (34.6, 43), (40.2, 41.2)):
        o += coin(x, y)
    return o


def delivery():
    o = ""
    box = [(3, 10.6), (28.6, 10.2), (29, 33.4), (3.4, 33.8)]
    o += double(box, .88, "#fff")
    o += hatch(inset(box, .88), 45, 3.2, .45) + hatch(inset(box, .88), -45, 3.2, .45)                   # lattice on the cargo box
    o += ring(15.8, 22, 5, TH, "#fff") + petals(15.8, 22, 2.4, 8, .45) + ring(15.8, 22, 1.2, .4)       # the painted medallion
    cab = [(29, 17.2), (37.6, 17), (44.6, 25), (44.8, 33.4), (29, 33.6)]
    o += double(cab, .9, "#fff")
    o += shape([(32, 20), (37, 19.8), (41, 24.6), (32.2, 24.8)], FINE, "#fff", .15)                     # window
    o += line((3.4, 33.8), (44.8, 33.6), TH)
    o += wheel(12.6, 37.8, 4.2) + wheel(36.6, 37.8, 4.2)
    o += dotted((2.4, 45.6), (45, 45.4), 2.8, .5)                                                      # road
    return o


def disc(seed):
    """A slightly irregular cut circle, with a second, thinner print slightly out of register."""
    r = random.Random(seed)
    def ring(rad, a):
        pts = [(math.cos(2 * math.pi * i / 14) * rad * r.uniform(1 - a, 1 + a), math.sin(2 * math.pi * i / 14) * rad * r.uniform(1 - a, 1 + a)) for i in range(14)]
        return smooth(pts, True)
    return ring(46, .012), ring(41.5, .02)


ICONS = [("consumer", consumer), ("artisan", artisan), ("materials", materials), ("production", production), ("fair", fair), ("delivery", delivery)]


def build():
    out = "/* ICONS:BEGIN (generated by tools/build_web_icons.py; do not edit by hand) */\n  var ICONS = {\n"
    discs = {}
    for i, (name, fn) in enumerate(ICONS):
        out += f"    {name}: '{fn()}',\n"
        discs[name] = disc(100 + i)
    out = out.rstrip(",\n") + "\n  };\n  var DISCS = {\n"
    out += ",\n".join(f"    {k}: ['{a}', '{b}']" for k, (a, b) in discs.items()) + "\n  };\n  /* ICONS:END */"
    return out


if __name__ == "__main__":
    block = build()
    src = JS.read_text(encoding="utf-8")
    new = re.sub(r"/\* ICONS:BEGIN.*?/\* ICONS:END \*/", lambda m: block, src, flags=re.S)
    JS.write_text(new, encoding="utf-8")
    print("icons written to", JS)
