#!/usr/bin/env python3
"""Draw the 'What would transparency actually look like?' picture: a shirt with a sewn-in label, and a handheld scanner reading it.
Mithila-style thin orange line (double outlines, hatching, dots, fish-eye and flower motifs). Written to src/templates/scan-art.html,
which the TransparaTrade page includes inside an <svg viewBox="0 0 900 520">.

TEST-RUN ARTWORK like the rest of the motif layer: replace with art made with Nepali artists.
    python3 tools/build_scan_art.py
"""
import math, pathlib, sys, random

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_web_icons as bi                                     # shared hand-drawn helpers

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "templates" / "scan-art.html"
bi.ID_PREFIX = "sc"
bi.R = random.Random(77)
n, path, line, dot, smooth, jit, ring = bi.n, bi.path, bi.line, bi.dot, bi.smooth, bi.jit, bi.ring
W, F = 1.8, 1.0           # outline and fine-line weight (scene units; strokes are not scaled)


def shape(pts, w=W, fill="#fff", a=1.0, closed=True):
    return path(smooth([jit(p, a) for p in pts], closed), w, fill)


def dotted(p, q, gap=9, r=1.3):
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    k = max(1, int(L / gap))
    return "".join(dot(p[0] + (q[0] - p[0]) * i / k, p[1] + (q[1] - p[1]) * i / k, r) for i in range(k + 1))


def fish(cx, cy, w=15, h=6):
    pts = [(cx - w, cy), (cx - w * .4, cy - h), (cx + w * .5, cy - h * .8), (cx + w, cy), (cx + w * .5, cy + h * .8), (cx - w * .4, cy + h)]
    return shape(pts, F, "#fff", .3) + ring(cx - w * .05, cy, h * .4, F) + dot(cx - w * .05, cy, 1.2)


def flower(cx, cy, r=14, petals=8):
    o = ring(cx, cy, r * .26, F) + dot(cx, cy, 1.4)
    for i in range(petals):
        t = i * 2 * math.pi / petals
        a = (cx + math.cos(t) * r * .45, cy + math.sin(t) * r * .45)
        b = (cx + math.cos(t) * r, cy + math.sin(t) * r)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        o += path(smooth([a, (mid[0] + math.sin(t) * 3, mid[1] - math.cos(t) * 3), b, (mid[0] - math.sin(t) * 3, mid[1] + math.cos(t) * 3)], True), F)
    return o


def shirt():
    o = ""
    body = [(215, 70), (262, 50), (330, 108), (398, 50), (445, 70), (548, 128), (568, 150), (522, 222), (466, 192), (462, 470), (200, 470), (196, 192), (140, 222), (94, 150), (114, 128)]
    o += shape(body, W, "#fff", 1.2)
    o += shape([(x + (3 if x < 330 else -3) * (1 if y > 100 else 0), y + 3) for x, y in body], F, None, .8)       # second, finer outline
    # neckline and collar band
    o += path(smooth([(262, 50), (296, 96), (330, 108), (364, 96), (398, 50)]), F)
    o += path(smooth([(262, 50), (300, 118), (330, 130), (360, 118), (398, 50)]), W)
    for i in range(7):
        t = i / 6
        x = 270 + t * 120
        y = 62 + 40 * math.sin(math.pi * t) + 14
        o += dot(x, y, 1.3)
    # sleeves: cuff bands with dots
    o += line((516, 178), (558, 154), W, amp=.2) + dotted((522, 190), (554, 168), 9, 1.2)
    o += line((148, 178), (106, 154), W, amp=.2) + dotted((142, 190), (110, 168), 9, 1.2)
    # chest medallion and side motifs
    o += flower(330, 236, 30, 10) + ring(330, 236, 38, F)
    for sx in (-1, 1):
        o += fish(330 + sx * 112, 236, 16, 6.5)
        o += dotted((330 + sx * 60, 236), (330 + sx * 92, 236), 8, 1.1)
    o += bi.hatch([(214, 300), (446, 300), (446, 330), (214, 330)], 45, 7, .6)
    o += line((214, 300), (446, 300), F, amp=.2) + line((214, 330), (446, 330), F, amp=.2)
    # hem band
    o += line((202, 446), (460, 446), W, amp=.2)
    x = 224
    while x < 440:
        o += fish(x, 458, 11, 4.2)
        x += 34
    return o


def label():
    """The sewn-in label: a double-bordered tag, stitched round its edge, carrying a code and lines of text."""
    o = ""
    x0, y0, x1, y1 = 360, 342, 450, 432
    o += path(f"M{x0} {y0}H{x1}V{y1}H{x0}Z", None, "#fff")
    o += bi.rect_lines(x0, y0, x1, y1, W)
    o += bi.rect_lines(x0 + 5, y0 + 5, x1 - 5, y1 - 5, F)
    for (a, b) in (((x0 - 6, y0 - 6), (x1 + 6, y0 - 6)), ((x1 + 6, y0 - 6), (x1 + 6, y1 + 6)), ((x1 + 6, y1 + 6), (x0 - 6, y1 + 6)), ((x0 - 6, y1 + 6), (x0 - 6, y0 - 6))):
        o += dotted(a, b, 6, 1.0)                                                  # the stitches that hold it on
    # a code: 7 x 7 modules with three corner finders
    rnd = random.Random(5)
    gx, gy, m = x0 + 14, y0 + 12, 8.2
    cells = ""
    for r in range(7):
        for c in range(7):
            finder = (r < 3 and c < 3) or (r < 3 and c > 3) or (r > 3 and c < 3)
            if finder:
                continue
            if rnd.random() < .5:
                cells += f"M{n(gx + c * m)} {n(gy + r * m)}h{n(m - 1)}v{n(m - 1)}h-{n(m - 1)}z"
    o += path(cells, None, "solid")
    for (r, c) in ((0, 0), (0, 4), (4, 0)):
        fx, fy = gx + c * m, gy + r * m
        o += bi.rect_lines(fx, fy, fx + 3 * m - 1, fy + 3 * m - 1, F)
        o += path(f"M{n(fx + m)} {n(fy + m)}h{n(m - 1)}v{n(m - 1)}h-{n(m - 1)}z", None, "solid")
    o += line((x0 + 14, y1 - 17), (x1 - 14, y1 - 17), F, amp=.1, over=0) + line((x0 + 14, y1 - 11), (x1 - 30, y1 - 11), F, amp=.1, over=0)
    return o


def scanner():
    o = ""
    # handle and trigger first, then the head over it
    o += shape([(676, 392), (738, 388), (756, 498), (700, 506), (688, 460)], W, "#fff", .8)
    o += bi.hatch([(690, 420), (736, 416), (748, 490), (704, 496)], 62, 6, .55)
    o += path(smooth([(678, 410), (662, 424), (666, 444), (684, 448)]), W)                          # trigger guard
    o += line((676, 420), (668, 436), W, amp=.1, over=0)
    head = [(562, 330), (726, 318), (754, 332), (758, 384), (736, 398), (574, 404), (556, 392)]
    o += shape(head, W, "#fff", .8)
    o += shape([(x + (4 if x < 650 else -4), y + (4 if y < 360 else -4)) for x, y in head], F, None, .5)
    o += shape([(552, 342), (580, 340), (580, 388), (552, 390)], W, "#fff", .4)                     # the window the light leaves by
    o += bi.hatch([(553, 343), (579, 341), (579, 387), (553, 389)], 50, 4, .5)
    for i in range(4):
        o += dot(618 + i * 22, 346, 2.4)                                                            # indicator dots
    o += flower(704, 360, 13, 8)
    o += dotted((600, 380), (690, 376), 9, 1.2)
    return o


def beam():
    """The fan of light from the window to the label, and the bright scan line that sweeps over the label."""
    o = f'<path class="scan-fan" d="M552 366L452 342L452 432Z" fill="currentColor" fill-opacity=".14" stroke="none"/>'
    o += line((552, 366), (452, 342), F, amp=.1, over=0) + line((552, 366), (452, 432), F, amp=.1, over=0) + line((552, 366), (452, 387), F, amp=.1, over=0)
    # sparkles where the light meets the label
    for (x, y) in ((462, 350), (470, 420), (466, 388)):
        o += path(f"M{x - 5} {y}h10M{x} {y - 5}v10", F)
    o += f'<g class="scan-line"><line x1="356" y1="342" x2="454" y2="342" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><line x1="356" y1="342" x2="454" y2="342" stroke="currentColor" stroke-width="9" stroke-linecap="round" stroke-opacity=".18"/></g>'
    return o


def build():
    return (f'<g fill="none" stroke="currentColor" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round">'
            f'{shirt()}{label()}{beam()}{scanner()}</g>\n')


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
