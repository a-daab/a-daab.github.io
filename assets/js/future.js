/* TransparaTrade: "Imagine a future". An eye, centred at the top, looks down at six steps of a supply chain. The steps are drawn in the same orange
   as the section, so they cannot be seen until light falls on them. A slice of light comes from the pupil and, at first, lights only the last step,
   the customer. As the page scrolls the slice widens back along the chain (shipping, finishing, weaving, spinning) until raw materials is lit too.
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
  var SHORT = ['Materials', 'Spinning', 'Weaving', 'Finishing', 'Shipping', 'Customer'];

  var G = null, pts = [], p = reduce ? 1 : 0, target = p, raf = 0, last = 0;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function f1(v) { return Math.round(v * 10) / 10; }

  /* wide: the eye top-centre and a gently waving row of steps below it. tall (phone): the same, with the steps in two staggered rows. */
  function layout() {
    var w = stage.clientWidth, h = stage.clientHeight, a = h ? w / h : 1.8, g = { tall: a < 1.05 };
    if (g.tall) {
      g.vw = 400; g.vh = Math.max(540, Math.min(700, 400 / a)); g.ex = 200; g.ey = 80; g.eyeScale = .6; g.icon = 1.05; g.half = 27; g.font = 10.5;
    } else {
      g.vh = 540; g.vw = Math.max(1000, g.vh * a); g.ex = g.vw / 2; g.ey = 96; g.eyeScale = .85; g.icon = 1.7; g.half = 44; g.font = 13;
      g.rowY = 392; g.step = Math.min(210, (g.vw - 200) / 5);
    }
    return g;
  }

  function build() {
    G = layout();
    svg.setAttribute('viewBox', '0 0 ' + f1(G.vw) + ' ' + f1(G.vh));
    chain.textContent = '';
    var i;
    if (G.tall) pts = LABELS.map(function (l, k) {               /* a shallow U below the eye, so the steps sit at clearly different bearings */
      var t = (-70 + 28 * k) * Math.PI / 180, ry = Math.min(250, G.vh - G.ey - 190);
      return [G.ex + 150 * Math.sin(t) / Math.sin(70 * Math.PI / 180), G.ey + 120 + ry * Math.cos(t)];
    });
    else pts = LABELS.map(function (l, k) { return [G.ex + (k - 2.5) * G.step, G.rowY + (k % 2 ? 16 : -16)]; });
    for (i = 0; i < pts.length - 1; i++) {                       /* stitched links between neighbouring steps */
      var A = pts[i], B = pts[i + 1], dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, r = G.half + 4;
      var s = [A[0] + ux * r, A[1] + uy * r], e = [B[0] - ux * r, B[1] - uy * r], bend = G.tall ? 0 : (i % 2 ? -1 : 1) * L * .1;
      el('path', { d: 'M' + f1(s[0]) + ' ' + f1(s[1]) + 'Q' + f1((s[0] + e[0]) / 2 - uy * bend) + ' ' + f1((s[1] + e[1]) / 2 + ux * bend) + ' ' + f1(e[0]) + ' ' + f1(e[1]), 'class': 'fv-link' }, chain);
    }
    pts.forEach(function (c, k) {
      var g = el('g', { transform: 'translate(' + f1(c[0]) + ' ' + f1(c[1]) + ')', style: 'color:' + ORANGE }, chain);
      el('use', { href: '#ico-' + k, transform: 'scale(' + G.icon + ')' }, g);
      var t = el('text', { y: G.half + (G.tall ? 17 + (k % 2 ? 13 : 0) : 26), 'text-anchor': 'middle', 'class': 'fv-label', 'font-size': G.font }, g);
      t.textContent = G.tall ? SHORT[k] : LABELS[k];
    });
    eyeG.setAttribute('transform', 'translate(' + f1(G.ex) + ' ' + f1(G.ey) + ') scale(' + G.eyeScale + ')');
    /* reach of the light: a little beyond the furthest label */
    var far = 0;
    pts.forEach(function (c) { far = Math.max(far, Math.hypot(c[0] - G.ex, c[1] + G.half + 30 - G.ey)); });
    G.R = far * 1.12;
    grad.setAttribute('cx', f1(G.ex)); grad.setAttribute('cy', f1(G.ey)); grad.setAttribute('r', f1(G.R));
    /* each step's bearing from the eye (0 = straight down, positive to the right) and the half-angle its icon spans */
    G.th = pts.map(function (c) { return Math.atan2(c[0] - G.ex, c[1] - G.ey); });
    G.dl = pts.map(function (c) { return Math.atan((G.half + (G.tall ? 22 : 54)) / Math.hypot(c[0] - G.ex, c[1] - G.ey)); });
    paint();
  }

  /* the slice of light: fixed on the right just past the customer, its left edge sweeping back along the chain with scroll */
  function paint() {
    if (!G) return;
    var n = pts.length - 1;
    var aR = G.th[n] + G.dl[n], aL0 = G.th[n] - G.dl[n], aL1 = G.th[0] - G.dl[0];
    var aL = aL0 + (aL1 - aL0) * p;
    var d = 'M' + f1(G.ex) + ' ' + f1(G.ey), k, a;
    for (k = 0; k <= 20; k++) {
      a = aL + (aR - aL) * k / 20;
      d += 'L' + f1(G.ex + Math.sin(a) * G.R) + ' ' + f1(G.ey + Math.cos(a) * G.R);
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
