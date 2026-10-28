/* TransparaTrade: "Imagine a future". An eye casts a beam along a supply chain. The beam starts narrow and lights only the first step;
   as the page scrolls it widens and lengthens, and more of the chain (raw materials to customer) comes into view.
   Reduced motion: the whole chain is lit. */
(function () {
  'use strict';
  var section = document.getElementById('future');
  if (!section) return;
  var svg = section.querySelector('.future__svg'), stage = section.querySelector('.future__stage');
  var chain = document.getElementById('fv-chain'), eyeG = document.getElementById('fv-eye'), beam = document.getElementById('fv-beam');
  var cone = document.getElementById('fv-mask-cone'), grad = document.getElementById('fv-grad');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var NS = 'http://www.w3.org/2000/svg';
  var LABELS = ['Raw materials', 'Spinning', 'Weaving', 'Finishing', 'Shipping', 'Customer'];
  var FR = [0.19, 0.34, 0.5, 0.66, 0.83, 1.0];                 /* distance of each step from the eye, as a share of the usable length */
  var TH = [0, 4, -9, 12, -12, 9];                              /* and how far it sits off the beam's axis, in degrees */

  var G = null, p = reduce ? 1 : 0, target = p, raf = 0, last = 0;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function f1(v) { return Math.round(v * 10) / 10; }

  /* geometry for the current stage shape: wide (the eye on the left, the beam going right) or tall (the eye on top, the beam going down) */
  function layout() {
    var w = stage.clientWidth, h = stage.clientHeight, a = h ? w / h : 1.8, tall = a < 1.05, g = {};
    if (tall) {
      g.vw = 400; g.vh = Math.max(560, Math.min(760, 400 / a)); g.phi = 90; g.ex = 200; g.ey = 82; g.eyeScale = .62; g.r = 30; g.A = g.vh - g.ey - 84; g.iconScale = .78;
    } else {
      g.vh = 540; g.vw = Math.max(1000, g.vh * a); g.phi = 0; g.eyeScale = 1; g.ex = Math.max(150, g.vw * .105); g.ey = g.vh / 2; g.r = 38; g.A = g.vw - g.ex - 96; g.iconScale = 1;
    }
    g.tall = tall;
    return g;
  }
  function polar(g, d, deg) {
    var t = (g.phi + deg) * Math.PI / 180;
    return [g.ex + Math.cos(t) * d, g.ey + Math.sin(t) * d];
  }

  function build() {
    G = layout();
    svg.setAttribute('viewBox', '0 0 ' + f1(G.vw) + ' ' + f1(G.vh));
    chain.textContent = '';
    var pts = FR.map(function (f, i) { return polar(G, f * G.A, TH[i]); });
    /* stitched links between the steps */
    for (var i = 0; i < pts.length - 1; i++) {
      var A = pts[i], B = pts[i + 1], dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
      var s = [A[0] + ux * (G.r + 4), A[1] + uy * (G.r + 4)], e = [B[0] - ux * (G.r + 4), B[1] - uy * (G.r + 4)];
      var bend = (i % 2 ? -1 : 1) * L * .12;
      el('path', { d: 'M' + f1(s[0]) + ' ' + f1(s[1]) + 'Q' + f1((s[0] + e[0]) / 2 - uy * bend) + ' ' + f1((s[1] + e[1]) / 2 + ux * bend) + ' ' + f1(e[0]) + ' ' + f1(e[1]), 'class': 'fv-link' }, chain);
    }
    pts.forEach(function (c, i) {
      var g = el('g', { transform: 'translate(' + f1(c[0]) + ' ' + f1(c[1]) + ')', 'class': 'fv-node' }, chain);
      el('circle', { r: G.r, 'class': 'fv-disc' }, g);
      el('circle', { r: G.r - 5, 'class': 'fv-disc2' }, g);
      var ic = el('g', { transform: 'scale(' + G.iconScale * 1.05 + ')' }, g);
      el('use', { href: '#ico-' + i }, ic);
      var attrs = { y: G.r + 24, 'text-anchor': 'middle', 'class': 'fv-label' };
      if (G.tall) {                                             /* tall layout: the label sits beside its step, on whichever side has room */
        var left = c[0] > G.vw * .55;
        attrs = { x: left ? -(G.r + 10) : G.r + 10, y: 5, 'text-anchor': left ? 'end' : 'start', 'class': 'fv-label' };
      }
      var t = el('text', attrs, g);
      t.textContent = LABELS[i];
    });
    eyeG.setAttribute('transform', 'translate(' + f1(G.ex) + ' ' + f1(G.ey) + ') scale(' + G.eyeScale + ')');
    var end = polar(G, G.A * 1.1, 0);
    grad.setAttribute('x1', f1(G.ex)); grad.setAttribute('y1', f1(G.ey)); grad.setAttribute('x2', f1(end[0])); grad.setAttribute('y2', f1(end[1]));
    paint();
  }

  /* the beam: a fan from the pupil, narrow at first, widening and reaching further with scroll */
  function paint() {
    if (!G) return;
    var alpha = 4 + 26 * p, len = G.A * (0.26 + 0.86 * p);
    var d = 'M' + f1(G.ex) + ' ' + f1(G.ey), k, a;
    for (k = 0; k <= 12; k++) {
      a = -alpha + (2 * alpha) * k / 12;
      var q = polar(G, len, a);
      d += 'L' + f1(q[0]) + ' ' + f1(q[1]);
    }
    d += 'Z';
    beam.setAttribute('d', d);
    cone.setAttribute('d', d);
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
    var was = G && G.tall; var g = layout();
    if (!G || g.tall !== was || Math.abs(g.vw - G.vw) > 1) build();
    update();
  });
  update();
})();
