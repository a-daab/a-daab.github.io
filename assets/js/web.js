/* How It Works: the web of six connected parts.
   - Lines are runs of stitches between every pair of nodes; hovering (or focusing / tapping) a line explains how its two nodes connect.
   - The mouse acts like a gentle gravity well: nodes and lines drift slightly toward it and ease back when it leaves.
   Reduced motion: no drifting; the explanations still work. */
(function () {
  'use strict';
  var root = document.getElementById('web-figure');
  if (!root) return;
  var svg = root.querySelector('svg'), tip = document.getElementById('web-tip');
  var data = JSON.parse(document.getElementById('web-data').textContent);
  var NS = 'http://www.w3.org/2000/svg';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var R_NODE = 46;

  /* Irregular hand-placed layouts (viewBox units). `bend` curves each of the 15 lines (pairs in node order) so no line passes behind a node. */
  var LAYOUTS = {
    wide: { w: 1000, h: 640, pull: 15, linePull: 28, radius: 300,
      pos: { consumer: [110, 330], artisan: [300, 110], materials: [430, 470], production: [650, 250], fair: [780, 540], delivery: [910, 300] }, bend: [-0.208, 0.127, 0.184, -0.146, 0.16, -0.08, 0.218, -0.117, -0.211, 0.087, -0.175, 0.245, 0.234, 0.19, -0.149] },
    narrow: { w: 420, h: 800, pull: 9, linePull: 17, radius: 230,
      pos: { consumer: [100, 90], artisan: [320, 210], materials: [90, 360], production: [320, 480], fair: [100, 630], delivery: [310, 725] }, bend: [-0.208, 0.127, 0.184, -0.209, 0.081, -0.08, 0.218, 0.205, 0.247, 0.087, -0.175, 0.245, 0.234, 0.19, -0.149] }
  };

  /* Icons drawn on a 48-unit grid, one stroke weight, orange. */
  var ICONS = {
    consumer: '<path d="M4 9h6l5 21h22l4-15H12"/><circle cx="18" cy="38" r="3"/><circle cx="34" cy="38" r="3"/>',
    artisan: '<path d="M13 41c-5-3-7-8-7-12l-1-8c0-2 3-2.5 3.5-.5L10 26V12c0-2.2 3-2.2 3 0v12-15c0-2.2 3-2.2 3 0v15-13c0-2.2 3-2.2 3 0v14-9c0-2.2 3-2.2 3 0v18c0 6-3 11-8 13z"/>' +
             '<path d="M38 7v24"/><path d="M37 10h2"/><path d="M38 31c-3 3 2 5-1 9"/>',
    materials: '<path d="M14 8h20M14 40h20M17 8v32M31 8v32"/><path d="M17 14l14 4M17 21l14 4M17 28l14 4"/><path d="M31 36c4 0 6 2 8 4"/>',
    production: '<path d="M8 12h28a6 6 0 0 1 6 6v20"/><path d="M8 12v10h22v16"/><path d="M14 22v10M14 32l-1.5 3"/><circle cx="36" cy="6" r="3"/><path d="M5 38h38v4H5z"/>',
    fair: '<rect x="3" y="11" width="42" height="26" rx="3"/><rect x="7" y="15" width="34" height="18" rx="2" stroke-width="1"/><circle cx="10.5" cy="24" r="1.3"/><circle cx="37.5" cy="24" r="1.3"/>' +
          '<text x="24" y="28" text-anchor="middle" font-size="13" font-weight="700" fill="currentColor" stroke="none">\u0930\u0942</text>',
    delivery: '<rect x="3" y="12" width="26" height="20"/><path d="M29 18h9l6 8v6H29"/><circle cx="13" cy="35" r="3.5"/><circle cx="36" cy="35" r="3.5"/><path d="M3 32h6.5M16.5 32h16M39.5 32h4.5"/>'
  };

  var layout, L, nodes = [], edges = [], idIndex = {}, mouse = { x: 0, y: 0, active: false }, visible = false, raf = 0, lastT = 0;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  /* ---------- build ---------- */
  var gEdges = el('g', {}, svg), gNodes = el('g', {}, svg);
  data.nodes.forEach(function (n, i) {
    idIndex[n.id] = i;
    var g = el('g', { 'class': 'web-node', 'data-id': n.id }, gNodes);
    el('circle', { r: R_NODE, 'class': 'web-disc' }, g);
    var ic = el('g', { 'class': 'web-icon', transform: 'translate(-27.6 -27.6) scale(1.15)' }, g);
    ic.innerHTML = ICONS[n.id];
    var t = el('text', { 'class': 'web-label', y: R_NODE + 26, 'text-anchor': 'middle' }, g);
    t.textContent = n.label;
    nodes.push({ g: g, bx: 0, by: 0, ox: 0, oy: 0, tx: 0, ty: 0 });
  });
  data.edges.forEach(function (e, k) {
    var a = idIndex[e[0]], b = idIndex[e[1]];
    var g = el('g', { 'class': 'web-link' }, gEdges);
    var line = el('path', { 'class': 'web-edge' }, g);
    var hit = el('path', { 'class': 'web-hit', tabindex: 0, role: 'button',
      'aria-label': data.nodes[a].label + ' and ' + data.nodes[b].label + ': ' + e[2] }, g);
    var ed = { a: a, b: b, k: k, line: line, hit: hit, text: e[2], ox: 0, oy: 0, tx: 0, ty: 0, cx: 0, cy: 0 };
    edges.push(ed);
    hit.addEventListener('pointerenter', function (ev) { if (ev.pointerType !== 'touch') show(ed, ev); });
    hit.addEventListener('pointermove', function (ev) { if (ev.pointerType !== 'touch') place(ev.clientX, ev.clientY); });
    hit.addEventListener('pointerleave', function (ev) { if (ev.pointerType !== 'touch') hide(); });
    hit.addEventListener('pointerdown', function (ev) { if (ev.pointerType === 'touch') { ev.stopPropagation(); show(ed, ev); } });
    hit.addEventListener('focus', function () { show(ed, null); });
    hit.addEventListener('blur', hide);
  });

  /* ---------- geometry ---------- */
  function pick() { return root.clientWidth < 640 ? 'narrow' : 'wide'; }
  function applyLayout() {
    var name = pick();
    if (name === layout) return;
    layout = name; L = LAYOUTS[name];
    svg.setAttribute('viewBox', '0 0 ' + L.w + ' ' + L.h);
    data.nodes.forEach(function (n, i) {
      nodes[i].bx = L.pos[n.id][0]; nodes[i].by = L.pos[n.id][1];
      nodes[i].ox = nodes[i].oy = nodes[i].tx = nodes[i].ty = 0;
    });
    edges.forEach(function (e) { e.ox = e.oy = e.tx = e.ty = 0; });
    hide();
    draw();
  }
  function ctrl(e) {
    var A = nodes[e.a], B = nodes[e.b];
    var ax = A.bx + A.ox, ay = A.by + A.oy, bx = B.bx + B.ox, by = B.by + B.oy;
    var dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy) || 1, bend = L.bend[e.k];
    e.cx = (ax + bx) / 2 - dy / len * bend * len + e.ox;
    e.cy = (ay + by) / 2 + dx / len * bend * len + e.oy;
    return 'M' + ax.toFixed(1) + ' ' + ay.toFixed(1) + 'Q' + e.cx.toFixed(1) + ' ' + e.cy.toFixed(1) + ' ' + bx.toFixed(1) + ' ' + by.toFixed(1);
  }
  function draw() {
    nodes.forEach(function (n) { n.g.setAttribute('transform', 'translate(' + (n.bx + n.ox).toFixed(1) + ' ' + (n.by + n.oy).toFixed(1) + ')'); });
    edges.forEach(function (e) { var d = ctrl(e); e.line.setAttribute('d', d); e.hit.setAttribute('d', d); });
  }

  /* ---------- gravity ---------- */
  function pullToward(px, py, max) {
    if (!mouse.active) return [0, 0];
    var dx = mouse.x - px, dy = mouse.y - py, d = Math.hypot(dx, dy) || 1, u = d / L.radius;
    var m = max * u * Math.exp((1 - u * u) / 2);                  /* 0 at the pointer, strongest at one radius away, fading beyond */
    return [dx / d * m, dy / d * m];
  }
  function step(now) {
    raf = 0;
    var dt = lastT ? Math.min(64, now - lastT) : 16; lastT = now;
    var ease = 1 - Math.exp(-dt / 160), moving = mouse.active;
    nodes.forEach(function (n) {
      var t = pullToward(n.bx, n.by, L.pull);
      n.ox += (t[0] - n.ox) * ease; n.oy += (t[1] - n.oy) * ease;
      if (Math.abs(t[0] - n.ox) + Math.abs(t[1] - n.oy) > 0.05) moving = true;
    });
    edges.forEach(function (e) {
      var A = nodes[e.a], B = nodes[e.b];
      var t = pullToward((A.bx + B.bx) / 2, (A.by + B.by) / 2, L.linePull);
      e.ox += (t[0] - e.ox) * ease; e.oy += (t[1] - e.oy) * ease;
      if (Math.abs(t[0] - e.ox) + Math.abs(t[1] - e.oy) > 0.05) moving = true;
    });
    draw();
    if (moving) raf = requestAnimationFrame(step); else lastT = 0;
  }
  function wake() { if (!raf && visible && !reduce) raf = requestAnimationFrame(step); }
  function toSvg(cx, cy) {
    var m = svg.getScreenCTM();
    if (!m) return null;
    var p = new DOMPoint(cx, cy).matrixTransform(m.inverse());
    return [p.x, p.y];
  }
  if (!reduce) {
    window.addEventListener('pointermove', function (ev) {
      if (ev.pointerType === 'touch') return;
      var p = toSvg(ev.clientX, ev.clientY);
      if (!p) return;
      mouse.x = p[0]; mouse.y = p[1]; mouse.active = true; wake();
    }, { passive: true });
    document.documentElement.addEventListener('mouseleave', function () { mouse.active = false; wake(); });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) wake(); }, { rootMargin: '10% 0px' }).observe(root);
  } else visible = true;

  /* ---------- tooltip ---------- */
  var current = null;
  function show(e, ev) {
    if (current) current.line.classList.remove('is-on');
    current = e; e.line.classList.add('is-on');
    tip.innerHTML = '';
    var h = document.createElement('strong');
    h.textContent = data.nodes[e.a].label + ' ↔ ' + data.nodes[e.b].label;
    var p = document.createElement('span');
    p.textContent = e.text;
    tip.appendChild(h); tip.appendChild(p);
    tip.hidden = false;
    if (ev) place(ev.clientX, ev.clientY);
    else {                                                         /* keyboard focus: anchor at the middle of the line */
      var r = e.hit.getBoundingClientRect();
      place(r.left + r.width / 2, r.top + r.height / 2);
    }
  }
  function place(cx, cy) {
    if (tip.hidden) return;
    var rr = root.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = cx - rr.left + 16, y = cy - rr.top + 18;
    if (x + w > rr.width) x = Math.max(0, rr.width - w);
    if (y + h > rr.height) y = Math.max(0, cy - rr.top - h - 14);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hide() {
    if (current) current.line.classList.remove('is-on');
    current = null; tip.hidden = true;
  }
  document.addEventListener('pointerdown', function (ev) { if (ev.pointerType === 'touch' && !ev.target.closest('.web-hit')) hide(); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hide(); });

  applyLayout();
  window.addEventListener('resize', function () { applyLayout(); });
})();
