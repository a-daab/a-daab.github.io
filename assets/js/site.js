/* YogaMaty — navigation + scroll-driven motif layer. No dependencies, sets no cookies, stores nothing. */
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

  /* ---------------- Motif layer ----------------
     Rules (Design §6): only artwork moves; text never does. Motion is caused by scroll. CSS transforms/opacity only.
     IntersectionObserver decides which motifs are on screen; a single rAF-throttled passive listener updates just those.
     Reduced motion: nothing here runs, the CSS static compositions apply. */
  var motion = null;
  function initMotifs() {
    var vis = [], info = new Map(), queued = false, io = null;
    var active = !(reduce || !('IntersectionObserver' in window));

    function register() {
      [].slice.call(d.querySelectorAll('.motif, .stitchdiv')).forEach(function (m) {
        if (info.has(m)) return;
        var u = m.getAttribute('data-mask');                       /* artwork loads after first paint */
        if (u) m.style.setProperty('--mask', 'url("' + new URL(u, document.baseURI).href + '")');
        info.set(m, {
          speed: parseFloat(m.getAttribute('data-speed') || '1'),
          rot: parseFloat(m.getAttribute('data-rot') || '0'),
          dx: parseFloat(m.getAttribute('data-dx') || '0'),
          scale: parseFloat(m.getAttribute('data-scale') || '0'),
          mode: m.getAttribute('data-progress') || (m.classList.contains('stitchdiv') ? 'self' : 'view'),
          host: m.closest('.sec') || m
        });
        if (active) io.observe(m);
      });
    }
    function schedule() { if (!queued) { queued = true; requestAnimationFrame(update); } }
    function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

    if (active) {
      io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          var i = vis.indexOf(e.target);
          if (e.isIntersecting && i < 0) vis.push(e.target);
          else if (!e.isIntersecting && i > -1) vis.splice(i, 1);
        });
        schedule();
      }, { rootMargin: '30% 0px 30% 0px' });
    }
    register();
    body.classList.remove('motifs-pending');
    motion = { refresh: function () { register(); schedule(); } };
    if (!active) return;

    function update() {
      queued = false;
      var vh = window.innerHeight, sy = window.pageYOffset;
      for (var k = 0; k < vis.length; k++) {
        var m = vis[k], o = info.get(m), p;
        var r = o.host.getBoundingClientRect();
        if (o.mode === 'hero') {                                           /* the mat unrolls as the pinned hero scrolls past */
          var stick = o.host.querySelector('.hero-stick');
          if (stick && getComputedStyle(stick).position === 'sticky') p = clamp(sy / Math.max(1, r.height - vh));
          else { var mr = m.getBoundingClientRect(); p = clamp((vh - mr.top) / (vh * 0.8)); }
        } else if (o.mode === 'self') {                                    /* stitches: from entering the bottom of the screen to mid-screen */
          var sr = m.getBoundingClientRect();
          p = clamp((vh * 0.96 - sr.top) / (vh * 0.5));
        } else p = clamp((vh - r.top) / (vh + r.height));                  /* 0 entering, 1 leaving */
        var centre = r.top + r.height / 2 - vh / 2;
        m.style.setProperty('--p', p.toFixed(3));
        if (o.speed !== 1) m.style.setProperty('--ty', (-(1 - o.speed) * centre).toFixed(1));
        if (o.rot) m.style.setProperty('--rot', (o.rot * (p - 0.5)).toFixed(1));
        if (o.dx) m.style.setProperty('--tx', (o.dx * (p - 0.5)).toFixed(1));
        if (o.scale) m.style.setProperty('--sc', (1 + (p - 0.5) * o.scale).toFixed(3));
      }
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
