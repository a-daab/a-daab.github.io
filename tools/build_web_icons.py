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


# ------------------------------------------------------------------ the icons
def consumer():
    o = ""
    o += path(smooth([(3, 8), (6.5, 8.6), (9.6, 9)]), 2.4)                                          # handle
    o += poly([(9.6, 9), (14, 28), (38, 28.4), (43, 12.6), (24, 11.2)], 2.3, a=.5)                  # basket
    for x in (18.5, 24, 29.5, 35):                                                                 # carved weave
        o += line((x - 1, 13.2), (x + 1.2, 26.2), 1.3)
    for y in (17.5, 22.5):
        o += line((12.4, y), (41, y - 1.4), 1.3)
    o += path(smooth([(14, 28), (15.6, 33), (35, 33.4)]), 2)                                        # frame under basket
    for cx in (18.5, 34.5):                                                                         # solid wheels, knocked-out hubs
        o += blob(cx, 39.4, 4.1, 4.1, fill="solid", k=8)
        o += blob(cx, 39.4, 1.3, 1.3, fill="#fff", k=5)
    return o


def hand(side):
    """One raised hand with carved finger lines, a palm flower and a sleeve band. side=-1 left hand, +1 right hand (mirrored)."""
    pts = [(14, 44), (7.5, 41), (6, 33), (8.2, 27.5), (6.2, 22.6), (7.6, 20.8), (10.4, 24.2), (10.2, 14), (11.4, 12), (13.4, 13.4), (13.9, 24),
           (14.4, 8.6), (16.2, 7.2), (17.8, 9), (17.9, 22.6), (19.5, 11.4), (21.2, 10.4), (22.6, 12.4), (21.8, 25), (25.2, 15), (27, 15.2), (27.4, 17.4),
           (25.6, 30), (26, 38), (22, 44)]
    sx = side
    def tf(p):
        x, y = p
        x = 16 + (x - 16) * sx
        return (x, y)
    o = path(smooth([jit(tf(p), .3) for p in pts], True), 2.2, "#fff")
    o += line(tf((10.6, 23.6)), tf((11.2, 29)), 1.1)                                                   # finger creases
    o += line(tf((14.2, 23)), tf((14.6, 28)), 1.1)
    o += line(tf((18, 23)), tf((18.2, 28)), 1.1)
    o += line(tf((21.9, 24)), tf((21.9, 29)), 1.1)
    o += flower(*tf((16.6, 34.4)), r=2.2)                                                              # mehndi flower
    o += line(tf((9.4, 40.6)), tf((22.4, 41.2)), 1.8)                                                   # sleeve band
    return o


def artisan():
    """Two hands, tilted toward each other, each with a carved palm flower."""
    left = f'<g transform="translate(-.2 4.2) scale(.95) rotate(-9 16 44)">{hand(1)}</g>'
    right = f'<g transform="translate(18.4 4.2) scale(.95) rotate(9 16 44)">{hand(-1)}</g>'
    return left + right


def materials():
    o = ""
    # solid top and bottom flanges with knocked-out dots
    o += poly([(9, 6.4), (38.6, 6), (39, 11.2), (9.6, 11.6)], 1.2, fill="solid", a=.35)
    o += poly([(9.4, 38), (39, 37.6), (38.6, 43), (9, 43.4)], 1.2, fill="solid", a=.35)
    for x in (14, 19.5, 25, 30.5, 35):
        o += blob(x, 8.8, .7, .7, fill="#fff", k=5, a=.1)
        o += blob(x, 40.6, .7, .7, fill="#fff", k=5, a=.1)
    # barrel wound with plenty of thread: two sets of slanted windings
    o += line((12, 12), (11.6, 37.4), 2)
    o += line((36, 11.8), (36.4, 37.2), 2)
    y = 13.2
    while y < 36:
        o += line((12.4, y + 2.2), (35.8, y - .6), 1.5, amp=.25, over=.1)
        y += 2.55
    y = 13.4
    while y < 35:
        o += line((12.4, y), (35.8, y + 2.4), 1.0, amp=.25, over=.1)
        y += 5.1
    # loose thread end trailing from the bottom, with a curl
    o += path(smooth([(35.8, 34.5), (42, 38), (44, 43), (40.5, 46), (38, 44.2), (39.6, 42.4)]), 1.7)
    return o


def production():
    o = ""
    # one carved C-shaped body: arm, column, throat, bed
    o += poly([(5, 11), (33, 10.4), (38.6, 13.4), (40.4, 22), (39.6, 34), (44.6, 35.2), (44.8, 43), (3.6, 43.6), (3.8, 35.2), (5.4, 34.4), (30.4, 34.8), (31.6, 21.4), (5.4, 20.6)], 2.2, a=.35)
    o += line((8.4, 15.6), (28, 15.4), 1.2)                                                              # carved band on the arm
    o += flower(35, 16.4, 2)
    o += blob(43.2, 16.2, 3.2, 3.2, 1.7, "#fff", k=8)                                                    # hand wheel
    o += line((43.2, 13.4), (43.2, 19), 1.0) + line((40.4, 16.2), (46, 16.2), 1.0)
    o += blob(20, 6, 2.4, 2.4, 1.5, "#fff", k=7)                                                         # thread spool on top
    o += path(smooth([(20, 8.4), (16, 11), (12.4, 14), (11.6, 20.4)]), 1.1)                             # thread down to the needle
    o += line((11.6, 20.6), (11.6, 31.4), 1.8)                                                           # needle
    o += poly([(10.2, 31), (13, 31), (11.6, 35.6)], 1, fill="solid", a=.1)
    o += poly([(3.6, 38.6), (44.8, 38.4), (44.8, 43), (3.6, 43.6)], 1, fill="solid", a=.3)             # solid bed face
    for x in (6, 12, 18, 24, 30, 36, 41):                                                                # stitches in the fabric
        o += f'<path d="M{n(x)} 41l2.6 -.1" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/>'
    return o


def note(cx, cy, w, h, deg, glyph=False):
    """A banknote: carved border, inner frame, corner dots, central medallion."""
    hw, hh = w / 2, h / 2
    outer = rot([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh)], cx, cy, deg)
    inner = rot([(cx - hw + 2.4, cy - hh + 2.4), (cx + hw - 2.4, cy - hh + 2.4), (cx + hw - 2.4, cy + hh - 2.4), (cx - hw + 2.4, cy + hh - 2.4)], cx, cy, deg)
    o = path(smooth([jit(p, .3) for p in outer], True), 2.0, "#fff")
    o += path(smooth([jit(p, .25) for p in inner], True), 1.0)
    for dx in (-1, 1):
        x, y = rot([(cx + dx * (hw - 5.2), cy)], cx, cy, deg)[0]
        o += dot(x, y, 1.1)
    mx, my = cx, cy
    o += blob(mx, my, 5.6, 5.6, 1.2, "#fff", k=8)
    if glyph:
        o += f'<text x="{n(mx)}" y="{n(my + 3.4)}" text-anchor="middle" font-size="9.4" font-weight="800" fill="currentColor" stroke="none">रू</text>'
    else:
        o += flower(mx, my, 1.9)
    return o


def coin(cx, cy, r=3.7):
    return blob(cx, cy, r, r * .9, 1.8, "#fff", k=9) + blob(cx, cy, r * .5, r * .45, 1, None, k=6) + dot(cx, cy, .6)


def fair():
    o = ""
    o += note(18.6, 13.2, 30, 17, -12)
    o += note(27.2, 22.6, 31, 18, 6, glyph=True)
    for (x, y) in ((8, 41.6), (13.4, 43), (9.6, 36.8)):
        o += coin(x, y)
    o += coin(38.6, 41, 4)
    o += coin(32.6, 43.4, 3.4)
    return o


def delivery():
    o = ""
    o += poly([(3, 10.6), (28.6, 10.2), (29, 33.4), (3.4, 33.8)], 2.2, a=.4)                          # cargo box
    for x in (9.4, 15.8, 22.2):
        o += line((x, 12.4), (x + .2, 31.6), 1.1)                                                       # carved planks
    o += poly([(29, 17.2), (37.6, 17), (44.6, 25), (44.8, 33.4), (29, 33.6)], 2.2, a=.4)                # cab
    o += poly([(32, 20), (37, 19.8), (41, 24.6), (32.2, 24.8)], 1.3, fill="#fff", a=.2)                 # window
    o += flower(16, 22, 2.4)                                                                           # the painted medallion on the box
    o += line((3.4, 33.8), (44.8, 33.6), 2)
    for cx in (12.6, 36.4):
        o += blob(cx, 37.6, 4.7, 4.7, fill="solid", k=9)
        o += blob(cx, 37.6, 1.4, 1.4, fill="#fff", k=5)
    for x in (2, 12, 22, 32, 42):
        o += line((x, 45.4), (x + 4.4, 45.4), 1.4)                                                      # road dashes
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
