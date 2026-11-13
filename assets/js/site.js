/* YOGAMATY — navigation + scroll-driven motif layer. No dependencies, sets no cookies, stores nothing. */
(function () {
  'use strict';
  var d = document, body = d.body;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var header = d.getElementById('site-header');

  /* ---------------- Navigation ---------------- */
  var nav = d.getElementById('nav'), burger = d.getElementById('burger');
  var menu = d.getElementById('shop-menu'), shopBtn = d.getElementById('shop-btn');
  var closeTimer, focusOpenedAt = 0;

  function setShop(open) {
    clearTimeout(closeTimer);
    menu.classList.toggle('open', open);
    shopBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function setNav(open) {
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    body.style.overflow = open ? 'hidden' : '';
    if (!open) setShop(false);
  }
  var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (min-width: 901px)');

  if (menu && shopBtn) {
    shopBtn.addEventListener('click', function () {
      /* keyboard focus already opened it a moment ago: Enter/Space should confirm, not toggle it shut */
      if (menu.classList.contains('open') && Date.now() - focusOpenedAt < 600) return;
      setShop(!menu.classList.contains('open'));
    });
    menu.addEventListener('mouseenter', function () { if (canHover && canHover.matches) setShop(true); });
    menu.addEventListener('mouseleave', function () {
      if (canHover && canHover.matches) { closeTimer = setTimeout(function () { setShop(false); }, 160); }
    });
    /* keyboard: opening on focus only when focus arrived by keyboard, so a mouse click is not toggled twice */
    menu.addEventListener('focusin', function () {
      try { if (shopBtn.matches(':focus-visible') || (menu.contains(d.activeElement) && d.activeElement !== shopBtn)) { if (!menu.classList.contains('open')) focusOpenedAt = Date.now(); setShop(true); } } catch (e) {}
    });
    menu.addEventListener('focusout', function (e) {
      if (!menu.contains(e.relatedTarget)) setShop(false);
    });
    d.addEventListener('click', function (e) { if (!menu.contains(e.target)) setShop(false); });
  }
  if (burger && nav) {
    burger.addEventListener('click', function () { setNav(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a');
      if (a) setNav(false);
    });
  }
  d.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (menu && menu.classList.contains('open')) { setShop(false); shopBtn.focus(); }
    else if (nav && nav.classList.contains('open')) { setNav(false); burger.focus(); }
  });
  if (window.matchMedia) {
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (e) { if (e.matches) setNav(false); });
  }

  /* Shadow appears once the page scrolls past the hero (Design §4) */
  if ('IntersectionObserver' in window && header) {
    var target = d.querySelector('.sec--hero, .sec--head');
    if (target) {
      new IntersectionObserver(function (es) {
        var r = es[0];
        header.classList.toggle('is-scrolled', !r.isIntersecting && r.boundingClientRect.bottom < 120);
      }, { rootMargin: '-' + (header.offsetHeight || 64) + 'px 0px 0px 0px' }).observe(target);
    }
  }

  /* "Why transparency": raise the left column so its first paragraph's text top lines up with the top of the quote on the right */
  function alignWhy() {
    var left = d.querySelector('#why .why-left'), q = d.querySelector('#why .quote');
    if (!left || !q) return;
    left.style.removeProperty('--why-shift');
    if (window.innerWidth <= 820) return;
    var para = left.querySelector('h2 ~ p');
    if (!para) return;
    var pr = para.getBoundingClientRect(), qr = q.getBoundingClientRect();
    var pfs = parseFloat(getComputedStyle(para).fontSize), qfs = parseFloat(getComputedStyle(q).fontSize);
    /* compare where the letters start (cap height), not the line boxes: ~0.30em below the top of the text in Mulish, ~0.29em in Cormorant */
    var pTop = pr.top + (pr.height > 0 ? ((parseFloat(getComputedStyle(para).lineHeight) || pfs * 1.65) - pfs) / 2 : 0) + 0.30 * pfs * 0.9;
    var qTop = qr.top + (((parseFloat(getComputedStyle(q).lineHeight) || qfs * 1.3) - qfs) / 2) + 0.29 * qfs * 0.9;
    left.style.setProperty('--why-shift', Math.round(qTop - pTop - 2) + 'px');
  }
  alignWhy();
  window.addEventListener('resize', alignWhy, { passive: true });
  window.addEventListener('load', alignWhy);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(alignWhy);

  /* Home hero: --hp runs 0 → 1 while the hero scrolls away; the handwoven layer settles onto the mat beneath it (css/site.css).
     Eased a little every frame so it glides between scroll events. With reduced motion it stays as drawn: floating. */
  (function () {
    var h = d.querySelector('.hero');
    if (!h || reduce) return;
    var cur = 0, raf = 0, last = 0;
    function tick(now) {
      raf = 0;
      var dt = last ? Math.min(64, now - last) : 16; last = now;
      var top = d.querySelector('.hero-top');
      var t = Math.max(0, Math.min(1, window.pageYOffset / Math.max(1, (top ? top.offsetHeight : h.offsetHeight) * 0.62)));
      cur += (t - cur) * (1 - Math.exp(-dt / 90));
      if (Math.abs(t - cur) < 0.001) { cur = t; last = 0; } else raf = requestAnimationFrame(tick);
      h.style.setProperty('--hp', cur.toFixed(4));
    }
    function kick() { if (!raf) raf = requestAnimationFrame(tick); }
    window.addEventListener('scroll', kick, { passive: true });
    window.addEventListener('resize', kick, { passive: true });
    kick();
  })();

  /* ---------------- Motif layer ----------------
     Rules (Design §6): only artwork moves; text never does. Motion is caused by scroll. CSS transforms/opacity only.
     IntersectionObserver decides which motifs are on screen; a single rAF-throttled passive listener updates just those.
     Reduced motion: nothing here runs, the CSS static compositions apply. */
  var motion = null;
  function initMotifs() {
    var items = [], info = new Map(), hostsVisible = new Set(), observed = new Set(), queued = false, io = null;
    var active = !(reduce || !('IntersectionObserver' in window));

    function register() {
      [].slice.call(d.querySelectorAll('.motif, .stitchdiv, .flow')).forEach(function (m) {
        if (info.has(m)) return;
        var u = m.getAttribute('data-mask');                       /* artwork loads after first paint */
        if (u) m.style.setProperty('--mask', 'url("' + new URL(u, document.baseURI).href + '")');
        var host = m.closest('.sec') || m;
        info.set(m, {
          speed: parseFloat(m.getAttribute('data-speed') || '1'),
          rot: parseFloat(m.getAttribute('data-rot') || '0'),
          dx: parseFloat(m.getAttribute('data-dx') || '0'),
          scale: parseFloat(m.getAttribute('data-scale') || '0'),
          mode: m.getAttribute('data-progress') || (m.classList.contains('stitchdiv') || m.classList.contains('flow') ? 'self' : 'view'),
          host: host
        });
        items.push(m);
        /* visibility is tracked per section, not per motif: a motif that has animated itself off-screen must keep updating */
        if (active && !observed.has(host)) { observed.add(host); io.observe(host); }
      });
    }
    function schedule() { if (!queued) { queued = true; requestAnimationFrame(update); } }
    function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

    if (active) {
      io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) hostsVisible.add(e.target); else hostsVisible.delete(e.target); });
        schedule();
      }, { rootMargin: '30% 0px 30% 0px' });
    }
    register();
    body.classList.remove('motifs-pending');
    motion = { refresh: function () { register(); schedule(); } };
    if (!active) return;

    /* Scroll events arrive in steps while the page itself scrolls on the compositor, so motifs driven straight from them look choppy.
       Each motif therefore eases toward its target value a little every frame (critically damped, frame-rate independent). */
    var lastT = 0;
    function update(now) {
      queued = false;
      var dt = lastT ? Math.min(64, now - lastT) : 16;
      lastT = now;
      var ease = 1 - Math.exp(-dt / 70), more = false;
      var vh = window.innerHeight, sy = window.pageYOffset;
      for (var k = 0; k < items.length; k++) {
        var m = items[k], o = info.get(m), p;
        if (!hostsVisible.has(o.host)) continue;
        var r = o.host.getBoundingClientRect();
        if (o.mode === 'page') {                                    /* a page-top border: empty at the top, drawn left to right over the first 40% of a screen of scrolling */
          p = clamp(sy / Math.max(1, vh * 0.4));
        } else if (o.mode === 'self') {                                    /* stitches: from entering the bottom of the screen to mid-screen */
          var sr = m.getBoundingClientRect();
          p = clamp((vh * 0.96 - sr.top) / (vh * 0.5));
        } else if (o.mode === 'end') {                                      /* blooms as the section's end rises into view */
          p = clamp(1 - (r.bottom - vh * 0.55) / (vh * 0.6));
        } else p = clamp((vh - r.top) / (vh + r.height));                  /* 0 entering, 1 leaving */
        var centre = r.top + r.height / 2 - vh / 2;
        var cur = o.cur;
        if (!cur) cur = o.cur = { p: p, c: centre };                       /* first frame: no easing from nothing */
        else { cur.p += (p - cur.p) * ease; cur.c += (centre - cur.c) * ease; }
        if (Math.abs(p - cur.p) > 0.0004 || Math.abs(centre - cur.c) > 0.3) more = true; else { cur.p = p; cur.c = centre; }
        p = cur.p; centre = cur.c;
        m.style.setProperty('--p', p.toFixed(4));
        if (o.speed !== 1) m.style.setProperty('--ty', (-(1 - o.speed) * centre).toFixed(1));
        if (o.rot) m.style.setProperty('--rot', (o.rot * (p - 0.5)).toFixed(1));
        if (o.dx) m.style.setProperty('--tx', (o.dx * (p - 0.5)).toFixed(1));
        if (o.scale) m.style.setProperty('--sc', (1 + (p - 0.5) * o.scale).toFixed(3));
      }
      if (more) schedule();
    }
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    schedule();
  }
  window.YM_motion = { refresh: function () { if (motion) motion.refresh(); } };

  function afterFirstPaint() {
    var go = function () { requestAnimationFrame(function () { setTimeout(initMotifs, 0); }); };
    if (d.readyState === 'complete') go(); else window.addEventListener('load', go);
  }
  afterFirstPaint();

  /* Strings for scripts that need them */
  window.YM_T = function (key, fallback) {
    try {
      var s = JSON.parse(d.getElementById('i18n').textContent);
      return key.split('.').reduce(function (o, k) { return o[k]; }, s) || fallback || key;
    } catch (e) { return fallback || key; }
  };
})();
