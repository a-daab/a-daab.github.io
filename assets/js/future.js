/* TransparaTrade: "Imagine a future". An eye, centred at the top, looks down at a row of supply-chain steps. The steps are drawn in the same orange as the
   section, so they only show where light falls on them. A slice of light widens from the eye as the page scrolls: first only the middle of the row is
   lit, then every step, raw materials to customer. On a phone the steps stack beneath the eye and the slice also lengthens, so they appear top to bottom.
   Reduced motion: everything is lit. */
(function () {
  'use strict';
  var section = document.getElementById('future');
  if (!section) return;
  var svg = section.querySelector('.future__svg'), stage = section.querySelector('.future__stage');
  var chain = document.getElementById('fv-chain'), eyeG = document.getElementById('fv-eye'), beam = document.getElementById('fv-beam');
  var grad = document.getElementById('fv-grad');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var NS = 'http://www.w3.org/2000/svg';
  var ORANGE = '#CC5500';
  var LABELS = ['Raw materials', 'Spinning', 'Weaving', 'Finishing', 'Shipping', 'Customer'];
  var FR = [0.19, 0.34, 0.5, 0.66, 0.83, 1.0];                 /* tall layout: distance of each step from the eye, as a share of the usable length */
  var TH = [0, 4, -9, 12, -12, 9];                              /* and how far it sits off the beam's axis, in degrees */

  var G = null, p = reduce ? 1 : 0, target = p, raf = 0, last = 0;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function f1(v) { return Math.round(v * 10) / 10; }
  function polar(g, d, deg) {
    var t = (g.phi + deg) * Math.PI / 180;
    return [g.ex + Math.cos(t) * d, g.ey + Math.sin(t) * d];
  }

  /* wide: the eye top-centre, a row of six steps below it, a slice of light that widens. tall: the eye on top, the steps stacked below it. */
  function layout() {
    var w = stage.clientWidth, h = stage.clientHeight, a = h ? w / h : 1.8, g = { tall: a < 1.05, phi: 90 };
    if (g.tall) {
      g.vw = 400; g.vh = Math.max(560, Math.min(760, 400 / a)); g.ex = 200; g.ey = 84; g.eyeScale = .62; g.A = g.vh - g.ey - 84; g.icon = 1.25; g.half = 34;
    } else {
      g.vh = 540; g.vw = Math.max(1000, g.vh * a); g.ex = g.vw / 2; g.ey = 96; g.eyeScale = .85; g.icon = 1.7; g.half = 44;
      g.rowY = 392; g.step = Math.min(210, (g.vw - 200) / 5);
    }
    return g;
  }

  function build() {
    G = layout();
    svg.setAttribute('viewBox', '0 0 ' + f1(G.vw) + ' ' + f1(G.vh));
    chain.textContent = '';
    var pts, i;
    if (G.tall) pts = FR.map(function (f, k) { return polar(G, f * G.A, TH[k]); });
    else pts = LABELS.map(function (l, k) { return [G.ex + (k - 2.5) * G.step, G.rowY + (k % 2 ? 16 : -16)]; });
    for (i = 0; i < pts.length - 1; i++) {                       /* stitched links between neighbouring steps */
      var A = pts[i], B = pts[i + 1], dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, r = G.half + 4;
      var s = [A[0] + ux * r, A[1] + uy * r], e = [B[0] - ux * r, B[1] - uy * r], bend = (i % 2 ? -1 : 1) * L * .1;
      el('path', { d: 'M' + f1(s[0]) + ' ' + f1(s[1]) + 'Q' + f1((s[0] + e[0]) / 2 - uy * bend) + ' ' + f1((s[1] + e[1]) / 2 + ux * bend) + ' ' + f1(e[0]) + ' ' + f1(e[1]), 'class': 'fv-link' }, chain);
    }
    pts.forEach(function (c, k) {
      var g = el('g', { transform: 'translate(' + f1(c[0]) + ' ' + f1(c[1]) + ')', style: 'color:' + ORANGE }, chain);
      el('use', { href: '#ico-' + k, transform: 'scale(' + G.icon + ')' }, g);
      var attrs = { y: G.half + 26, 'text-anchor': 'middle', 'class': 'fv-label' };
      if (G.tall) {                                             /* tall layout: the label sits beside its step, on whichever side has room */
        var left = c[0] > G.vw * .55;
        attrs = { x: left ? -(G.half + 8) : G.half + 8, y: 5, 'text-anchor': left ? 'end' : 'start', 'class': 'fv-label' };
      }
      var t = el('text', attrs, g);
      t.textContent = LABELS[k];
    });
    eyeG.setAttribute('transform', 'translate(' + f1(G.ex) + ' ' + f1(G.ey) + ') scale(' + G.eyeScale + ')');
    var endY = G.tall ? G.ey + G.A * 1.1 : G.rowY + 185;
    grad.setAttribute('x1', f1(G.ex)); grad.setAttribute('y1', f1(G.ey)); grad.setAttribute('x2', f1(G.ex)); grad.setAttribute('y2', f1(endY));
    paint();
  }

  /* the slice of light: a fan from the pupil, narrow at first, widening (and, on a phone, lengthening) with scroll */
  function paint() {
    if (!G) return;
    var alpha, len;
    if (G.tall) { alpha = 14 + 22 * p; len = G.A * (0.26 + 0.86 * p); }
    else { alpha = 19 + 46 * p; len = (G.rowY - G.ey) / Math.cos(Math.min(alpha, 80) * Math.PI / 180) + 200; }
    var d = 'M' + f1(G.ex) + ' ' + f1(G.ey), k, a;
    for (k = 0; k <= 16; k++) {
      a = -alpha + (2 * alpha) * k / 16;
      var q = polar(G, len, a);
      d += 'L' + f1(q[0]) + ' ' + f1(q[1]);
    }
    beam.setAttribute('d', d + 'Z');
  }

  function progress() {
    var r = section.getBoundingClientRect(), span = r.height - window.innerHeight;
    if (span <= 0) return 1;
    return Math.max(0, Math.min(1, -r.top / span));
  }
  function frame(now) {
    raf = 0;
    var dt = last ? Math.min(64, now - last) : 16; last = now;
    p += (target - p) * (1 - Math.exp(-dt / 120));
    if (Math.abs(target - p) < 0.002) p = target;
    paint();
    if (p !== target) raf = requestAnimationFrame(frame); else last = 0;
  }
  function update() {
    target = reduce ? 1 : progress();
    if (!raf) raf = requestAnimationFrame(frame);
  }

  build();
  if (!reduce) window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', function () {
    var was = G && G.tall, g = layout();
    if (!G || g.tall !== was || Math.abs(g.vw - G.vw) > 1) build();
    update();
  });
  update();
})();
