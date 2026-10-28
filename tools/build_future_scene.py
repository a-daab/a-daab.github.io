#!/usr/bin/env python3
"""Draw the art for the 'Imagine a future' scene on the TransparaTrade page: a Mithila-style eye, and the six icons of
a supply chain (raw materials, spinning, weaving, finishing, shipping, customer). White fine line on the orange section.
Written to src/templates/future-art.html as SVG <defs> that the page includes; assets/js/future.js places and lights them.

TEST-RUN ARTWORK like the rest of the motif layer: replace with art made with Nepali artists.
    python3 tools/build_future_scene.py
"""
import math, pathlib, sys, random

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_web_icons as bi                                     # shared hand-drawn helpers and the six web icons

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "templates" / "future-art.html"
ORANGE = "#CC5500"
bi.ID_PREFIX = "fa"
bi.R = random.Random(41)
n, path, line, dot, smooth, jit, ring, shape = bi.n, bi.path, bi.line, bi.dot, bi.smooth, bi.jit, bi.ring, bi.shape


def eye():
    """A front-facing eye: almond with double outline, fine lashes, a patterned iris and a solid pupil. Centred on (0, 0)."""
    o = ""
    top = [(-130, 0), (-98, -30), (-62, -50), (-22, -60), (22, -60), (62, -50), (98, -30), (130, 0)]
    bot = [(130, 0), (96, 28), (58, 44), (20, 52), (-20, 52), (-58, 44), (-96, 28)]
    almond = top + bot
    o += path(smooth([jit(p, .6) for p in almond], True), 1.8, ORANGE)
    o += path(smooth([jit((x * .9, y * .86), .4) for x, y in almond], True), .8)
    # lashes along the upper lid
    for i in range(1, len(top) - 1):
        x, y = top[i]
        for dx in (-9, 0, 9):
            px = max(-120, min(120, x + dx))
            py = -60 * math.sqrt(max(0.0, 1 - (px / 130) ** 2)) * 0.98
            L = 10 + abs(i - 3.5) * -1.2 + 6
            nx, ny = px / 130 * .55, -1
            o += line((px, py - 2), (px + nx * L * .6, py - 2 + ny * L), .9, amp=.1, over=0)
    # brow: a dotted arc and a fine line above it
    o += path(smooth([(-112, -66), (-60, -96), (0, -104), (60, -96), (112, -66)]), .9)
    for i in range(-5, 6):
        x = i * 19
        y = -100 + (i * i) * .55 - 3
        o += dot(x, y - 6, .9)
    # iris
    o += ring(0, 0, 40, 1.5, ORANGE) + ring(0, 0, 33, .8)
    for i in range(28):
        t = i * 2 * math.pi / 28
        o += line((math.cos(t) * 20, math.sin(t) * 20), (math.cos(t) * 31, math.sin(t) * 31), .7, amp=.05, over=0)
    for i in range(14):
        t = (i + .5) * 2 * math.pi / 14
        o += dot(math.cos(t) * 36.5, math.sin(t) * 36.5, 1.05)
    o += ring(0, 0, 18, .9, ORANGE)
    o += path(smooth([(math.cos(t) * 14, math.sin(t) * 14) for t in [i * math.pi / 4 for i in range(8)]], True), None, "solid")   # pupil
    o += f'<circle cx="-6" cy="-6" r="3.6" fill="{ORANGE}" stroke="none"/>'
    # tear duct and corner flowers
    o += ring(-120, 1, 3.4, .8) + ring(120, 1, 3.4, .8)
    return f'<g id="fe-eye" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{o}</g>'


def hemp():
    """A young hemp plant: stem, two pairs of leaves with veins, and the soil mound."""
    o = ""
    o += path(smooth([(24, 41), (23.4, 32), (24.4, 22), (24, 12)]), 1.0)
    for side in (-1, 1):
        for (y, L) in ((31, 14), (21, 11)):
            tip = (24 + side * L, y - 8)
            pts = [(24, y), (24 + side * L * .5, y - 6.5), tip, (24 + side * L * .55, y - 1.5)]
            o += path(smooth([jit(p, .25) for p in pts], True), .9, "none")
            o += line((24, y - 1), (tip[0] - side * 2, tip[1] + 1.5), .5, amp=.05, over=0)
    o += path(smooth([(24, 12), (21.4, 8), (24, 4), (26.6, 8)], True), .9, ORANGE)
    o += path(smooth([(8, 43), (16, 39.5), (24, 38.6), (32, 39.5), (40, 43)]), 1.0)
    o += bi.dotted((11, 45), (37, 45), 3.2, .5)
    return o


def icons():
    chain = [("hemp", hemp()), ("spin", bi.materials()), ("weave", bi.artisan()), ("finish", bi.production()), ("ship", bi.delivery()), ("buy", bi.consumer())]
    out = ""
    for i, (name, body) in enumerate(chain):
        body = body.replace('"#fff"', '"none"').replace(f'"{ORANGE}"', '"none"')   # drawn in the section's own orange: interiors stay open so only light reveals them
        out += (f'<g id="ico-{i}" fill="none" stroke="currentColor" stroke-width=".9" stroke-linecap="round" stroke-linejoin="round" '
                f'transform="translate(-24 -24)">{body}</g>')
    return out


def build():
    return f'<defs>{eye()}{icons()}</defs>\n'


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
