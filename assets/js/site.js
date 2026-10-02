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

  /* Hero: stays pinned while the mat unrolls. If its text block is taller than one screen it is scaled down to fit
     (so the pin still works); only on very short windows does the hero scroll normally. Nothing slides under the nav. */
  function fitHero() {
    var h = d.querySelector('.hero-tall');
    if (!h || !header) return;
    var tx = h.querySelector('.hero-text');
    if (!tx) return;
    h.classList.remove('hero-flow');
    tx.style.removeProperty('--fit');
    var avail = window.innerHeight - header.offsetHeight - 24 - 36;
    var fit = Math.min(1, avail / Math.max(1, tx.offsetHeight));
    if (fit < 0.72) h.classList.add('hero-flow');
    else if (fit < 1) tx.style.setProperty('--fit', fit.toFixed(3));
  }
  fitHero();
  window.addEventListener('resize', fitHero, { passive: true });
  window.addEventListener('load', fitHero);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(fitHero);

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

    function update() {
      queued = false;
      var vh = window.innerHeight, sy = window.pageYOffset;
      for (var k = 0; k < items.length; k++) {
        var m = items[k], o = info.get(m), p;
        if (!hostsVisible.has(o.host)) continue;
        var r = o.host.getBoundingClientRect();
        if (o.mode === 'hero') {                                           /* the mat unrolls as the pinned hero scrolls past */
          var stick = o.host.querySelector('.hero-stick');
          if (stick && getComputedStyle(stick).position === 'sticky') p = clamp(sy / Math.max(1, (r.height - vh) * 0.8));   /* unrolled by 80% of the pinned scroll, then held */
          else if (getComputedStyle(o.host.querySelector('.hero-mat')).position === 'absolute') p = clamp(sy / Math.max(1, r.height * 0.6));   /* wide but short window: unroll over the first part of the hero */
          else { var mr = m.getBoundingClientRect(); p = clamp((vh - mr.top) / (vh * 0.8)); }
        } else if (o.mode === 'self') {                                    /* stitches: from entering the bottom of the screen to mid-screen */
          var sr = m.getBoundingClientRect();
          p = clamp((vh * 0.96 - sr.top) / (vh * 0.5));
        } else if (o.mode === 'end') {                                      /* blooms as the section's end rises into view */
          p = clamp(1 - (r.bottom - vh * 0.55) / (vh * 0.6));
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
