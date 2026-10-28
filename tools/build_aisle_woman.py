#!/usr/bin/env python3
"""Draw the woman (seen from behind) for the TransparaTrade aisle scene in a Nepali Mithila manner - double outlines, fine
hatching, dots, fish-eye and flower motifs, drawn in one thin orange line - and write it as an SVG fragment that the
TransparaTrade page includes (src/templates/woman-back.html).

TEST-RUN ARTWORK, like the rest of the motif layer: replace with art made with Nepali artists.
    python3 tools/build_aisle_woman.py
Coordinates are in the scene's 1000 x 700 space: she stands at x = 500 with her feet on the floor line y = 690.
"""
import math, pathlib, sys, random

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_web_icons as bi                                     # shared hand-drawn helpers (smooth, jit, line, dot, hatch ...)

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "templates" / "woman-back.html"
bi.ID_PREFIX = "wm"
bi.R = random.Random(5)
n, path, line, dot, smooth, jit = bi.n, bi.path, bi.line, bi.dot, bi.smooth, bi.jit
W = 1.5                  # outline weight
F = 0.85                 # fine line weight


def shape(pts, w=W, fill="#fff", a=1.0):
    return path(smooth([jit(p, a) for p in pts], True), w, fill)


def ring(cx, cy, r, w=F, fill=None):
    return bi.ring(cx, cy, r, w, fill)


def hatch_poly(pts, angle, gap, w=0.7):
    return bi.hatch(pts, angle, gap, w)


def mirror(pts, cx=500):
    return [(2 * cx - x, y) for x, y in pts]


def dots_along(pts, gap=9, r=1.3):
    out = ""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / gap))
        for i in range(k):
            out += dot(x0 + (x1 - x0) * i / k, y0 + (y1 - y0) * i / k, r)
    return out


def fisheye(cx, cy, w=16, h=7):
    """The Mithila fish / eye motif."""
    pts = [(cx - w, cy), (cx - w * .4, cy - h), (cx + w * .5, cy - h * .8), (cx + w, cy), (cx + w * .5, cy + h * .8), (cx - w * .4, cy + h)]
    return shape(pts, F, "#fff", .3) + ring(cx - w * .05, cy, h * .42, F) + dot(cx - w * .05, cy, 1.4)


def flower(cx, cy, r=9, petals=8):
    o = ring(cx, cy, r * .28, F) + dot(cx, cy, 1.2)
    for i in range(petals):
        t = i * 2 * math.pi / petals
        a = (cx + math.cos(t) * r * .45, cy + math.sin(t) * r * .45)
        b = (cx + math.cos(t) * r, cy + math.sin(t) * r)
        o += path(smooth([a, ((a[0] + b[0]) / 2 + math.sin(t) * 2.2, (a[1] + b[1]) / 2 - math.cos(t) * 2.2), b, ((a[0] + b[0]) / 2 - math.sin(t) * 2.2, (a[1] + b[1]) / 2 + math.cos(t) * 2.2)], True), F)
    return o


def band(y0, y1, xl, xr, motif="dots"):
    """A decorated horizontal border between two rules, running between two (sloped) side edges given as functions of y."""
    o = line((xl(y0), y0), (xr(y0), y0), W, amp=.2) + line((xl(y1), y1), (xr(y1), y1), W, amp=.2)
    ym = (y0 + y1) / 2
    if motif == "dots":
        o += dots_along([(xl(ym) + 8, ym), (xr(ym) - 8, ym)], 9, 1.4)
    elif motif == "fish":
        x = xl(ym) + 22
        while x < xr(ym) - 18:
            o += fisheye(x, ym, 12, 5.2)
            x += 36
    elif motif == "zig":
        pts = []
        x, up = xl(ym) + 6, True
        while x < xr(ym) - 6:
            pts.append((x, ym + (-5 if up else 5)))
            x += 9
            up = not up
        o += path("M" + "L".join(f"{n(px)} {n(py)}" for px, py in pts), F)
    return o


def woman():
    o = ""
    # ---- lower garment (the sari wrapped at the waist), hem near the ankles
    skirt_l = lambda y: 452 - (y - 338) * 0.24
    skirt_r = lambda y: 548 + (y - 338) * 0.24
    skirt = [(452, 338), (500, 334), (548, 338)] + [(skirt_r(y) + (3 if i % 2 else -2), y) for i, y in enumerate(range(380, 650, 54))] + \
            [(skirt_r(650), 650), (500, 658), (skirt_l(650), 650)] + [(skirt_l(y) + (-3 if i % 2 else 2), y) for i, y in reversed(list(enumerate(range(380, 650, 54))))]
    o += shape(skirt, W, "#fff", .8)
    # pleats at the back of the waist and long folds down the garment
    for dx, ln in ((-20, 190), (-7, 205), (7, 205), (20, 190)):
        o += line((500 + dx, 346), (500 + dx * 1.7, 346 + ln), F, amp=.4, over=0)
    # hem borders
    o += band(574, 604, skirt_l, skirt_r, "fish")
    o += band(614, 630, skirt_l, skirt_r, "dots")
    o += hatch_poly([(skirt_l(630) + 4, 630), (skirt_r(630) - 4, 630), (skirt_r(650) - 6, 648), (500, 653), (skirt_l(650) + 6, 648)], 52, 5, .6)
    o += line((skirt_l(630), 630), (skirt_r(630), 630), W, amp=.2)
    # ankles and feet seen from behind
    for sx in (-1, 1):
        cx = 500 + sx * 24
        o += shape([(cx - 9, 656), (cx + 9, 656), (cx + 8, 672), (cx - 8, 672)], F, "#fff", .5)
        o += shape([(cx - 17, 678), (cx, 670), (cx + 17, 678), (cx + 19, 689), (cx - 19, 689)], W, "#fff", .6)
        o += line((cx - 12, 678), (cx + 12, 678), F, amp=.2, over=0)
    # ---- blouse / upper back
    blouse = [(442, 276), (462, 262), (500, 258), (538, 262), (558, 276), (562, 306), (552, 340), (500, 346), (448, 340), (438, 306)]
    o += shape(blouse, W, "#fff", .8)
    o += line((500, 266), (500, 340), F, amp=.3, over=0)
    o += dots_along([(452, 336), (548, 336)], 8, 1.2)
    for yy in (296, 312):
        o += dots_along([(446, yy), (472, yy)], 7, 1.0) + dots_along([(528, yy), (554, yy)], 7, 1.0)
    # ---- pallu: the free end of the sari over the left shoulder, hanging down the back
    pallu = [(444, 272), (468, 262), (494, 270), (514, 330), (522, 420), (516, 500), (508, 548), (478, 556), (450, 548), (440, 500), (436, 420), (438, 330)]
    o += shape(pallu, W, "#fff", .9)
    o += shape([(x + (6 if x < 480 else -6), y + (8 if y < 400 else -8)) for x, y in pallu], F, None, .9)
    o += hatch_poly([(450, 350), (506, 350), (512, 420), (508, 474), (450, 474), (444, 420)], 62, 7, .55)
    o += band(478, 508, lambda y: 441, lambda y: 515, "fish")
    o += band(512, 534, lambda y: 440, lambda y: 512, "zig")
    for k in range(8):                                                                  # fringe
        x = 454 + k * 8
        o += line((x, 550), (x - 2 + (k % 2) * 3, 566), F, amp=.3, over=0)
    o += flower(478, 304, 11)
    o += flower(472, 392, 9, 6)
    # ---- arms: the viewer's right arm carries a woven shopping basket
    for sx in (-1, 1):
        arm = [(500 + sx * 58, 280), (500 + sx * 74, 290), (500 + sx * 84, 352), (500 + sx * 92, 410), (500 + sx * 66, 414), (500 + sx * 62, 350)]
        o += shape(arm, W, "#fff", .6)
        o += dots_along([(500 + sx * 64, 344), (500 + sx * 82, 348)], 6, 1.0)
        o += shape([(500 + sx * 66, 410), (500 + sx * 92, 410), (500 + sx * 98, 428), (500 + sx * 80, 440), (500 + sx * 62, 430)], W, "#fff", .6)
    # basket on the right arm
    bx, by = 586, 436
    o += path(smooth([(bx - 22, by - 4), (bx, by - 42), (bx + 22, by - 4)]), W)            # handle
    basket = [(bx - 32, by), (bx + 32, by), (bx + 26, by + 46), (bx - 26, by + 46)]
    o += shape(basket, W, "#fff", .5)
    o += hatch_poly(basket, 45, 5, .55) + hatch_poly(basket, -45, 5, .55)
    o += line((bx - 32, by + 8), (bx + 32, by + 8), W, amp=.2)
    # ---- the braid, hanging down the middle of the back
    seg_y, w = 262, 14.5
    o += shape([(486, 252), (514, 252), (508, 268), (492, 268)], F, "#fff", .4)
    for i in range(10):
        cy = seg_y + 8 + i * 12.2
        ww = w - i * .45
        o += shape([(500 - ww, cy - 2), (500, cy - 7), (500 + ww, cy - 2), (500 + ww * .8, cy + 8), (500, cy + 11), (500 - ww * .8, cy + 8)], F if i else W, "#fff", .5)
        o += line((500 - ww * .6, cy - 1), (500 + ww * .5, cy + 6), .7, amp=.1, over=0)
    o += shape([(493, 386), (507, 386), (506, 394), (494, 394)], W, "#fff", .4)               # tie
    for k in range(5):
        o += line((496 + k * 2, 394), (494 + k * 3, 410), F, amp=.3, over=0)
    # ---- head: hair seen from behind, with a centre parting and flowing hatch lines
    head = [(500 + (x - 500) * 1.2, 214 + (y - 214) * 1.12) for x, y in [(470, 214), (473, 192), (486, 178), (500, 174), (514, 178), (527, 192), (530, 214), (524, 236), (512, 250), (500, 254), (488, 250), (476, 236)]]
    o += shape(head, W, "#fff", .5)
    o += shape([(x + (4 if x < 500 else -4), y + (5 if y < 214 else -5)) for x, y in head], F, None, .4)
    o += line((500, 166), (500, 256), F, amp=.3, over=0)
    for sx in (-1, 1):
        for k in range(5):
            y0 = 186 + k * 11
            o += path(smooth([(500 + sx * 3, y0), (500 + sx * 17, y0 + 6), (500 + sx * 26, y0 + 20)]), .6)
    o += flower(522, 196, 8, 6)                                                           # hair flower
    # ear glimpse and a hair ornament line
    o += dots_along([(478, 188), (484, 180), (494, 175)], 5, 1.0)
    return o


def build():
    return f'<g class="aisle-woman" fill="none" stroke="currentColor" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round">{woman()}</g>\n'


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
