/* TransparaTrade: the aisle with the "vertigo effect" (a dolly zoom).
   A woman, seen from behind, stands still while the grocery-store aisle in front of her stretches as the page scrolls:
   the camera is imagined to dolly back while the lens zooms in, so she keeps her size and the background changes its perspective.
   Every product on the shelves carries a question mark. Reduced motion: a still frame, no pinned scroll. */
(function () {
  'use strict';
  var section = document.getElementById('aisle');
  if (!section) return;
  var svg = section.querySelector('.aisle__svg'), world = document.getElementById('aisle-world');
  var bottom = section.querySelector('.aisle__line--bottom');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var NS = 'http://www.w3.org/2000/svg';

  /* Scene (1000 x 700): K px per metre at the woman's distance, eye level on y = VPY, floor at her feet y = 690. */
  var K = 290, VPX = 500, VPY = 226, T = 3.2, WALL = 1.35;
  var SHELVES = [0.15, 0.75, 1.35, 1.95], CELL = 0.55, D0 = 0.3, N = 22;
  var BACK = D0 + CELL * N;

  /* A deterministic scatter of products: kind, width and height fractions. */
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
  var items = [];
  [-1, 1].forEach(function (w) {
    for (var r = 0; r < 3; r++) for (var i = 0; i < N; i++) {
      items.push({ w: w, r: r, i: i, kind: Math.floor(rnd() * 4), wf: 0.6 + rnd() * 0.25, hf: 0.62 + rnd() * 0.32 });
    }
  });
  var backItems = [];
  for (var rr = 0; rr < 3; rr++) for (var cc = 0; cc < 5; cc++) backItems.push({ r: rr, c: cc, kind: Math.floor(rnd() * 4), wf: 0.62 + rnd() * 0.2, hf: 0.66 + rnd() * 0.3 });

  /* the question mark, in a unit box */
  var Q = [[.30, .28], [.33, .17], [.42, .11], [.52, .10], [.62, .14], [.68, .24], [.65, .34], [.55, .43], [.50, .52], [.50, .60]];
  var DOT = [[.46, .73], [.54, .73], [.54, .81], [.46, .81]];

  var tNow = reduce ? T * 0.45 : 0, tTarget = tNow, raf = 0, lastT = 0;

  function mk(name, attrs) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    world.appendChild(e);
    return e;
  }
  var pStruct = mk('path', { 'class': 'ai-struct' }), pOut = mk('path', { 'class': 'ai-out' }), pIn = mk('path', { 'class': 'ai-in' }), pQ = mk('path', { 'class': 'ai-q' });

  function f1(v) { return (Math.round(v * 10) / 10); }
  function pt(x, y) { return f1(x) + ' ' + f1(y); }

  /* a product face = a quad given by its left/right edges, each with a top and a bottom y; (u,v) in the unit square maps onto it */
  function face(x1, yt1, yb1, x2, yt2, yb2) {
    return function (u, v) {
      var yt = yt1 + u * (yt2 - yt1), yb = yb1 + u * (yb2 - yb1);
      return [x1 + u * (x2 - x1), yt + v * (yb - yt)];
    };
  }
  function poly(F, pts) {
    var s = '';
    for (var k = 0; k < pts.length; k++) { var p = F(pts[k][0], pts[k][1]); s += (k ? 'L' : 'M') + pt(p[0], p[1]); }
    return s + 'Z';
  }
  function seg(F, a, b) { var p = F(a[0], a[1]), q = F(b[0], b[1]); return 'M' + pt(p[0], p[1]) + 'L' + pt(q[0], q[1]); }

  /* draws one product (all four kinds) and its question mark; returns [outline, inner, question] path data */
  function product(F, kind, px, minH) {
    var out = '', inn = '', q = '', body = [0, 1];
    if (kind === 0) {
      out = poly(F, [[0, 0], [1, 0], [1, 1], [0, 1]]);
      inn = poly(F, [[.1, .08], [.9, .08], [.9, .92], [.1, .92]]);
    } else if (kind === 1) {
      out = poly(F, [[0, 0], [1, 0], [1, 1], [0, 1]]);
      inn = seg(F, [0, .16], [1, .16]) + seg(F, [0, .84], [1, .84]);
      body = [.16, .84];
    } else if (kind === 2) {
      out = poly(F, [[0, .36], [1, .36], [1, 1], [0, 1]]) + poly(F, [[.33, .1], [.67, .1], [.67, .36], [.33, .36]]) + poly(F, [[.28, 0], [.72, 0], [.72, .1], [.28, .1]]);
      inn = seg(F, [0, .52], [1, .52]);
      body = [.36, 1];
    } else {
      out = poly(F, [[.08, 0], [.92, 0], [.92, .2], [.08, .2]]) + poly(F, [[0, .2], [1, .2], [1, 1], [0, 1]]);
      inn = poly(F, [[.1, .3], [.9, .3], [.9, .92], [.1, .92]]);
      body = [.2, 1];
    }
    if (px >= minH) {
      var v0 = body[0] + (body[1] - body[0]) * .12, v1 = body[1] - (body[1] - body[0]) * .1, k;
      for (k = 0; k < Q.length; k++) {
        var uu = .2 + Q[k][0] * .6, vv = v0 + Q[k][1] * (v1 - v0) / .85;
        var p = F(uu, vv);
        q += (k ? 'L' : 'M') + pt(p[0], p[1]);
      }
      for (k = 0; k < DOT.length; k++) {
        var p2 = F(.2 + DOT[k][0] * .6, v0 + DOT[k][1] * (v1 - v0) / .85);
        q += (k ? 'L' : 'M') + pt(p2[0], p2[1]);
      }
      q += 'Z';
    }
    return [out, inn, q];
  }

  function draw() {
    var t = tNow;
    function S(d) { return K * (1 + t) / (d + t); }
    function X(w, s) { return VPX + w * WALL * s; }
    function Y(h, s) { return VPY + (1.6 - h) * s; }
    var st = '', po = '', pi = '', pq = '', i, it, k;

    /* back wall (face on) */
    var sb = S(BACK), bx0 = X(-1, sb), bx1 = X(1, sb);
    st += 'M' + pt(bx0, Y(0, sb)) + 'L' + pt(bx1, Y(0, sb)) + 'L' + pt(bx1, Y(1.95, sb)) + 'L' + pt(bx0, Y(1.95, sb)) + 'Z';
    for (k = 1; k < 3; k++) st += 'M' + pt(bx0, Y(SHELVES[k], sb)) + 'L' + pt(bx1, Y(SHELVES[k], sb));
    backItems.forEach(function (b) {
      var cw = (bx1 - bx0) / 5, x0 = bx0 + b.c * cw + cw * (1 - b.wf) / 2, x1 = bx0 + (b.c + 1) * cw - cw * (1 - b.wf) / 2;
      var hb = SHELVES[b.r] + .02, ht = hb + b.hf * .55;
      var F = face(x0, Y(ht, sb), Y(hb, sb), x1, Y(ht, sb), Y(hb, sb));
      var r = product(F, b.kind, Y(hb, sb) - Y(ht, sb), 9);
      po += r[0]; pi += r[1]; pq += r[2];
    });

    /* shelf boards, base and uprights run the whole length of each wall */
    var s0 = S(D0), sN = S(BACK);
    for (var w = -1; w <= 1; w += 2) {
      for (k = 0; k < SHELVES.length; k++) st += 'M' + pt(X(w, s0), Y(SHELVES[k], s0)) + 'L' + pt(X(w, sN), Y(SHELVES[k], sN));
      st += 'M' + pt(X(w, s0), Y(0, s0)) + 'L' + pt(X(w, sN), Y(0, sN));
      for (i = 0; i <= N; i += 4) {
        var si = S(D0 + CELL * i);
        st += 'M' + pt(X(w, si), Y(0, si)) + 'L' + pt(X(w, si), Y(SHELVES[3], si));
      }
    }
    /* floor tile seams */
    for (i = 0; i <= N; i++) {
      var sf = S(D0 + CELL * i);
      st += 'M' + pt(X(-1, sf), Y(0, sf)) + 'L' + pt(X(1, sf), Y(0, sf));
    }
    /* products, far to near so nearer ones can hide farther ones */
    for (k = items.length - 1; k >= 0; k--) {
      it = items[k];
      var da = D0 + CELL * it.i, db = da + CELL, m = (1 - it.wf) / 2 * CELL;
      var s1 = S(da + m), s2 = S(db - m);
      var hb2 = SHELVES[it.r] + .02, ht2 = hb2 + it.hf * .55;
      var F2 = face(X(it.w, s1), Y(ht2, s1), Y(hb2, s1), X(it.w, s2), Y(ht2, s2), Y(hb2, s2));
      var pxH = Y(hb2, s2) - Y(ht2, s2);
      if (pxH < 2.5) continue;
      var r2 = product(F2, it.kind, pxH, 11);
      po += r2[0]; pi += r2[1]; pq += r2[2];
    }
    pStruct.setAttribute('d', st); pOut.setAttribute('d', po); pIn.setAttribute('d', pi); pQ.setAttribute('d', pq);
  }

  /* ---------- scroll-driven dolly ---------- */
  function progress() {
    var r = section.getBoundingClientRect(), span = r.height - window.innerHeight;
    if (span <= 0) return 0;
    return Math.max(0, Math.min(1, -r.top / span));
  }
  function frame(now) {
    raf = 0;
    var dt = lastT ? Math.min(64, now - lastT) : 16; lastT = now;
    var ease = 1 - Math.exp(-dt / 110);
    tNow += (tTarget - tNow) * ease;
    if (Math.abs(tTarget - tNow) < 0.002) tNow = tTarget;
    draw();
    if (tNow !== tTarget) raf = requestAnimationFrame(frame); else lastT = 0;
  }
  function update() {
    var p = progress();
    tTarget = reduce ? T * 0.45 : T * p;
    if (bottom && !reduce) bottom.style.setProperty('--bo', String(Math.max(0, Math.min(1, (p - 0.45) / 0.25))));
    if (!raf) raf = requestAnimationFrame(frame);
  }
  function fitView() {
    var st = section.querySelector('.aisle__stage'), w = st.clientWidth, h = st.clientHeight;
    svg.setAttribute('viewBox', h && w / h < 1.15 ? '240 130 520 570' : '0 0 1000 700');
  }

  draw();
  fitView();
  if (!reduce) {
    window.addEventListener('scroll', update, { passive: true });
  }
  window.addEventListener('resize', function () { fitView(); update(); });
  update();
})();
