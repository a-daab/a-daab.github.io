/* TransparaTrade: the aisle with the "vertigo effect" (a dolly zoom).
   A woman, seen from behind, stands still while the grocery-store aisle in front of her changes its perspective as the page scrolls:
   the camera is imagined to dolly forward while the lens zooms out, so she keeps her size while the aisle opens wide and then closes in to a deep corridor.
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
  var K = 290, VPX = 500, VPY = 226, T = 3.2, WALL = 1.9, VH = 850;
  var SHELVES = [0.15, 0.75, 1.35, 1.95], CELL = 0.55, D0 = 0.05, N = 22;
  var BACK = D0 + CELL * N;

  /* Food-like products, each with a label that carries the question mark.
     kinds: 0 cereal box, 1 jar, 2 tin can, 3 bottle, 4 bag of flour or rice, 5 carton.  [min, max] width as a share of its shelf slot, height as a share of 0.58 m */
  var KINDS = [
    { w: [.55, .7], h: [.86, .98] }, { w: [.6, .75], h: [.5, .7] }, { w: [.5, .62], h: [.45, .6] },
    { w: [.34, .46], h: [.8, .98] }, { w: [.65, .8], h: [.6, .8] }, { w: [.5, .6], h: [.7, .9] }
  ];
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
  function mkItem(o) {
    var kd = KINDS[o.kind];
    o.wf = kd.w[0] + rnd() * (kd.w[1] - kd.w[0]);
    o.hf = kd.h[0] + rnd() * (kd.h[1] - kd.h[0]);
    return o;
  }
  var items = [];
  [-1, 1].forEach(function (w) {
    for (var r = 0; r < 3; r++) for (var i = 0; i < N; i++) items.push(mkItem({ w: w, r: r, i: i, kind: Math.floor(rnd() * 6) }));
  });
  var backItems = [];
  for (var rr = 0; rr < 3; rr++) for (var cc = 0; cc < 5; cc++) backItems.push(mkItem({ r: rr, c: cc, kind: Math.floor(rnd() * 6) }));

  /* the question mark, in a unit box */
  var Q = [[.30, .28], [.33, .17], [.42, .11], [.52, .10], [.62, .14], [.68, .24], [.65, .34], [.55, .43], [.50, .52], [.50, .60]];
  var DOT = [[.46, .73], [.54, .73], [.54, .81], [.46, .81]];

  var tNow = reduce ? T * 0.55 : T, tTarget = tNow, raf = 0, lastT = 0;

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

  /* draws one product and its question mark; returns [outline, inner, question] path data. `label` is the unit box [u0, v0, u1, v1] the question mark sits in */
  function product(F, kind, px, minH) {
    var out = '', inn = '', label = [.2, .3, .8, .8], q = '', k;
    if (kind === 0) {                                                       /* cereal box: flap, a window with the label */
      out = poly(F, [[0, 0], [1, 0], [1, 1], [0, 1]]);
      inn = seg(F, [0, .07], [1, .07]) + poly(F, [[.12, .14], [.88, .14], [.88, .7], [.12, .7]]) + seg(F, [.12, .86], [.88, .86]);
      label = [.18, .17, .82, .67];
    } else if (kind === 1) {                                                /* jar: ridged lid, neck, round shoulders, label band */
      out = poly(F, [[.14, 0], [.86, 0], [.86, .17], [.14, .17]]) + poly(F, [[.2, .17], [.8, .17], [.8, .24], [.93, .34], [.97, .5], [.97, .9], [.88, 1], [.12, 1], [.03, .9], [.03, .5], [.07, .34], [.2, .24]]);
      inn = seg(F, [.14, .06], [.86, .06]) + seg(F, [.14, .12], [.86, .12]) + poly(F, [[.03, .46], [.97, .46], [.97, .86], [.03, .86]]);
      label = [.14, .48, .86, .84];
    } else if (kind === 2) {                                                /* tin can: rims and a wrap-around label */
      out = poly(F, [[0, .04], [1, .04], [1, .96], [0, .96]]) + seg(F, [0, .1], [1, .1]) + seg(F, [0, .9], [1, .9]);
      inn = poly(F, [[0, .24], [1, .24], [1, .76], [0, .76]]);
      label = [.12, .27, .88, .74];
    } else if (kind === 3) {                                                /* bottle: cap, neck, shoulders, label */
      out = poly(F, [[.4, 0], [.6, 0], [.6, .09], [.4, .09]]) + poly(F, [[.42, .09], [.58, .09], [.58, .3], [.84, .42], [.84, .94], [.74, 1], [.26, 1], [.16, .94], [.16, .42], [.42, .3]]);
      inn = poly(F, [[.16, .56], [.84, .56], [.84, .88], [.16, .88]]);
      label = [.22, .58, .78, .86];
    } else if (kind === 4) {                                                /* bag of flour or rice: crimped top, label */
      out = poly(F, [[0, .12], [.1, .02], [.2, .12], [.3, .02], [.4, .12], [.5, .02], [.6, .12], [.7, .02], [.8, .12], [.9, .02], [1, .12], [1, 1], [0, 1]]);
      inn = seg(F, [0, .2], [1, .2]) + poly(F, [[.1, .34], [.9, .34], [.9, .82], [.1, .82]]);
      label = [.16, .37, .84, .8];
    } else {                                                                /* carton: gabled top, label */
      out = poly(F, [[0, .22], [1, .22], [1, 1], [0, 1]]) + poly(F, [[0, .22], [.5, 0], [1, .22]]);
      inn = seg(F, [.5, 0], [.5, .22]) + poly(F, [[.12, .4], [.88, .4], [.88, .86], [.12, .86]]);
      label = [.18, .43, .82, .83];
    }
    if (px >= minH) {
      var lw = label[2] - label[0], lh = label[3] - label[1];
      for (k = 0; k < Q.length; k++) {
        var p = F(label[0] + lw * (.2 + Q[k][0] * .6), label[1] + lh * (Q[k][1] / .85) * .9);
        q += (k ? 'L' : 'M') + pt(p[0], p[1]);
      }
      for (k = 0; k < DOT.length; k++) {
        var p2 = F(label[0] + lw * (.2 + DOT[k][0] * .6), label[1] + lh * (DOT[k][1] / .85) * .9);
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
      var hb = SHELVES[b.r] + .02, ht = hb + b.hf * .58;
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
      var hb2 = SHELVES[it.r] + .02, ht2 = hb2 + it.hf * .58;
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
    tTarget = reduce ? T * 0.55 : T * (1 - p);
    if (bottom && !reduce) {
      var bo = Math.max(0, Math.min(1, (p - 0.45) / 0.25));
      bottom.style.setProperty('--bo', String(bo));
      bottom.classList.toggle('is-live', bo > 0.5);                 /* the link in the line can be clicked only once the line has faded in */
    }
    if (!raf) raf = requestAnimationFrame(frame);
  }
  /* The scene is shifted down just far enough that the shelf tops, which fan out from the vanishing point, pass below the headline. */
  var TOPSLOPE = 0.35 / WALL;                                  /* how steeply the top shelf line rises per unit of sideways distance */
  function fitView() {
    var st = section.querySelector('.aisle__stage'), w = st.clientWidth, h = st.clientHeight;
    var a = h ? w / h : 1.4, u = 0;
    var head = section.querySelector('.aisle__line--top');
    if (head && h) {
      var sr = st.getBoundingClientRect(), rg = document.createRange();
      rg.selectNodeContents(head);
      var tr = rg.getBoundingClientRect();
      var need = (tr.bottom - sr.top) + 14 + TOPSLOPE * (tr.width / 2);      /* px: headline bottom, a gap, and the line's rise over half the text width */
      if (need < h) u = Math.max(0, Math.min(260, (need * VH - VPY * h) / (h - need)));
    }
    var vh = VH + u, vw = vh * a;
    svg.setAttribute('viewBox', f1(VPX - vw / 2) + ' ' + f1(-u) + ' ' + f1(vw) + ' ' + f1(vh));
  }

  if (bottom && reduce) bottom.classList.add('is-live');
  draw();
  fitView();
  if (!reduce) {
    window.addEventListener('scroll', update, { passive: true });
  }
  window.addEventListener('resize', function () { fitView(); update(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fitView(); });
  update();
})();
