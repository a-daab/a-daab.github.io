/* Supply chain passport — renders a batch record (/data/batches/<id>.json) into the page.
   One HTML template, any batch: add a batch = add a JSON file. QR codes encode /passport/<batch>?mat=<serial>. */
(function () {
  'use strict';
  var d = document, app = d.getElementById('pp-app');
  if (!app) return;
  var LANG = (window.YM && window.YM.lang) || 'en';
  var ROOT = (window.YM && window.YM.root !== undefined) ? window.YM.root : '/';   /* a relative root is used only by the static preview */
  var IDX = (window.YM && window.YM.idx) || '';
  var T = function (k) { return window.YM_T('passport.' + k, k); };
  var q = new URLSearchParams(location.search);
  var SAFE = /^[A-Za-z0-9_-]{1,40}$/;

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function tr(o) { return o && typeof o === 'object' ? (o[LANG] || o.en || '') : (o || ''); }
  function getJSON(u) { return fetch(u, { credentials: 'omit' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function isPh(v) { return v === null || v === undefined || v === '' || (typeof v === 'string' && v.charAt(0) === '['); }
  function ph(label) { return '<span class="ph">[' + esc(T('add') + ' ' + label.toUpperCase()) + ']</span>'; }

  /* A value is plain, or {v, estimate, method}. Returns HTML. */
  function val(v, label) {
    if (v && typeof v === 'object') {
      if (isPh(v.v)) return ph(label);
      return esc(v.v) + (v.estimate ? ' <span class="small">(' + esc(T('estimate')) + ')</span>' : '');
    }
    if (isPh(v)) return typeof v === 'string' && v.charAt(0) === '[' ? '<span class="ph">' + esc(v) + '</span>' : ph(label);
    return esc(v);
  }
  function how(v, text) {
    var m = (v && typeof v === 'object' && v.method) ? v.method : text;
    return m ? '<details class="how"><summary>' + esc(T('how_measured')) + '</summary><p>' + esc(m) + '</p></details>' : '';
  }

  function resolveBatch(serials) {
    var b = q.get('batch'), mat = q.get('mat');
    if (b && SAFE.test(b)) return b;
    if (mat && serials) {
      var n = parseInt(mat, 10);
      var hit = (serials.ranges || []).filter(function (r) { return n >= r.from && (r.to === null || n <= r.to); })[0];
      if (hit) return hit.batch;
    }
    return window.YM.defaultBatch;
  }

  Promise.all([
    getJSON(ROOT + 'data/tiers.json'),
    getJSON(ROOT + 'data/standards.json').catch(function () { return null; }),
    getJSON(ROOT + 'data/media.json').catch(function () { return {}; }),
    getJSON(ROOT + 'data/serials.json').catch(function () { return null; })
  ]).then(function (r) {
    var tiers = r[0], standards = r[1], media = r[2], serials = r[3];
    var id = resolveBatch(serials);
    return getJSON(ROOT + 'data/batches/' + id + '.json').then(function (batch) { render(tiers, standards, media, batch); },
      function () { app.innerHTML = '<section class="sec sec--white"><div class="wrap wrap--narrow"><p class="lede">' + esc(T('not_found')) + ' <strong>' + esc(id) + '</strong>.</p></div></section>'; });
  }).catch(function () {
    app.innerHTML = '<section class="sec sec--white"><div class="wrap wrap--narrow"><p class="lede">' + esc(T('load_error')) + '</p></div></section>';
  });

  /* ------------------------------------------------------------------ */
  function mediaBlock(tier, subject) {
    var items = media_[tier];
    var label = tier + ' — ' + subject;
    if (!items || !items.length) {
      return '<figure class="media media--land"><div class="media-ph" role="img" aria-label="' + esc(T('media_ph') + ': ' + label) + '"><b>' + esc(label) + '</b></div></figure>';
    }
    return items.map(function (m) {
      var alt = m.alt || (T('media_alt') + ' ' + label);
      if (m.kind === 'video') {
        return '<figure class="media media--land"><video muted loop playsinline preload="none" data-lazyvideo aria-label="' + esc(alt) + '"' +
          (m.poster ? ' poster="' + esc(m.poster) + '"' : '') + ' data-src="' + esc(m.src) + '" style="width:100%;aspect-ratio:3/2;object-fit:cover"></video></figure>';
      }
      return '<figure class="media media--land"><img src="' + esc(m.src) + '" alt="' + esc(alt) + '" loading="lazy" decoding="async" style="width:100%;aspect-ratio:3/2;object-fit:cover"></figure>';
    }).join('');
  }
  var media_ = {};

  function render(tiers, standards, media, b) {
    media_ = media || {};
    var html = [];
    var published = b.status === 'published';
    var mats = b.mats || {};

    /* ---- batch summary ---- */
    html.push('<section class="sec sec--white sec--tight" id="batch"><div class="wrap">');
    if (!published) html.push('<div class="notice" role="note"><strong>' + esc(T('template_title')) + '</strong> ' + esc(T('template_body')) + '</div>');
    html.push('<dl class="pp-meta">' +
      '<div><dt>' + esc(T('product')) + '</dt><dd>YogaMaty</dd></div>' +
      '<div><dt>' + esc(T('batch_id')) + '</dt><dd class="data">' + esc(b.batch_id) + '</dd></div>' +
      '<div><dt>' + esc(T('opened')) + '</dt><dd>' + val(b.opened, T('opened')) + '</dd></div>' +
      '<div><dt>' + esc(T('closed')) + '</dt><dd>' + val(b.closed, T('closed')) + '</dd></div>' +
      '<div><dt>' + esc(T('mats_in_batch')) + '</dt><dd>' + val(mats.count, T('mats_in_batch')) + '</dd></div>' +
      '</dl></div></section>');

    /* ---- this mat ---- */
    var serial = (q.get('mat') || '').replace(/[^0-9A-Za-z-]/g, '').slice(0, 10);
    if (serial) {
      var mr = (b.mat_records || {})[serial] || {};
      html.push('<section class="sec sec--orange sec--tight" id="your-mat"><div class="wrap grid grid--split">' +
        '<div><span class="eyebrow">' + esc(T('your_mat')) + '</span>' +
        '<h2 class="display" style="font-size:clamp(2.4rem,1rem + 5vw,4.4rem)">No. ' + esc(serial) + '</h2>' +
        '<p class="statement">' + esc(T('your_mat_lead')) + ' ' + esc(b.batch_id) + '.</p></div>' +
        '<div><dl class="pp-meta" style="margin:0"><div><dt style="color:#fff">' + esc(T('assembled')) + '</dt><dd>' + val(mr.assembled, T('assembled')) + '</dd></div></dl>' +
        '<div style="margin-top:1.6rem">' + mediaBlock('MAT', serial) + '</div></div></div></section>');
    }

    /* ---- how this data was collected ---- */
    html.push('<section class="sec sec--white sec--pp" id="how-collected"><div class="wrap grid grid--split"><div>' +
      '<span class="eyebrow">' + esc(T('how_collected_eyebrow')) + '</span><h2 class="h1">' + esc(T('how_collected_title')) + '</h2>' +
      '<p>' + esc(T('how_collected_1')) + '</p><p>' + esc(T('how_collected_2')) + '</p>' +
      '<p><a href="' + ROOT + LANG + '/transparatrade/' + IDX + '">' + esc(T('how_collected_link')) + '</a></p></div>' +
      '<div style="background:var(--orange-tint);padding:clamp(22px,3vw,36px)"><h3>' + esc(T('this_batch')) + '</h3>' +
      '<dl class="tier" style="display:grid;border:0;padding:0;grid-template-columns:minmax(120px,40%) 1fr;gap:10px 16px;margin:0">' +
      '<dt>' + esc(T('entered_by')) + '</dt><dd>' + val(b.entered_by, T('entered_by')) + '</dd>' +
      '<dt>' + esc(T('entered_on')) + '</dt><dd>' + val(b.entered_on, T('entered_on')) + '</dd>' +
      '<dt>' + esc(T('verified_how')) + '</dt><dd>' + val(b.verification_note, T('verified_how')) + '</dd>' +
      '</dl></div></div></section>');

    /* ---- electricity disclosure ---- */
    var all = []; tiers.chains.forEach(function (c) { c.tiers.forEach(function (t) { all.push(t); }); });
    var rows = all.filter(function (t) { return t.powered === true || t.powered === false; }).map(function (t) {
      return '<li><span><span class="id">' + esc(t.id) + '</span>' + esc(tr(t.name)) + '</span><span>' +
        (t.powered ? '<span class="badge badge--on">' + esc(T('powered')) + '</span>' : '<span class="badge badge--off">' + esc(T('unpowered')) + '</span>') + '</span></li>';
    }).join('');
    var m = b.metrics || {};
    html.push('<section class="sec sec--white sec--pp" id="electricity"><div class="wrap">' +
      '<span class="eyebrow">' + esc(T('elec_eyebrow')) + '</span><h2 class="h1">' + esc(T('elec_title')) + '</h2>' +
      '<p>' + esc(T('elec_1')) + '</p><p>' + esc(T('elec_2')) + '</p>' +
      '<ul class="elec-list">' + rows + '</ul>' +
      '<div class="metrics"><div class="metric"><div class="val">' + val(m.electricity_kwh_per_mat, T('kwh_per_mat')) + '</div><div class="lbl">' + esc(T('kwh_per_mat')) + '</div>' +
      how(m.electricity_kwh_per_mat, T('elec_how')) + '</div></div></div></section>');

    /* ---- fair wage ---- */
    var w = b.wage || {};
    var pct = isPh(w.percent_of_benchmark) ? null : w.percent_of_benchmark;
    html.push('<section class="sec sec--white sec--pp" id="wage"><div class="wrap">' +
      '<span class="eyebrow">' + esc(T('wage_eyebrow')) + '</span><h2 class="h1">' + esc(T('wage_title')) + '</h2>' +
      '<div class="metrics">' +
      '<div class="metric"><div class="val">' + (isPh(w.npr_per_hour) ? ph(T('hourly_wage')) : 'NPR ' + esc(w.npr_per_hour)) + '</div><div class="lbl">' + esc(T('per_hour')) + '</div></div>' +
      '<div class="metric"><div class="val">' + (pct === null ? ph(T('percent_of_benchmark')) : esc(pct) + '%') + '</div><div class="lbl">' + esc(T('of_benchmark')) + '</div></div>' +
      '</div>' +
      '<dl class="pp-meta"><div><dt>' + esc(T('benchmark')) + '</dt><dd>' + val(w.benchmark_name, T('benchmark')) + '</dd></div>' +
      '<div><dt>' + esc(T('benchmark_source')) + '</dt><dd>' + val(w.benchmark_source, T('benchmark_source')) + (isPh(w.benchmark_date) ? '' : ' · ' + esc(w.benchmark_date)) + '</dd></div>' +
      '<div><dt>' + esc(T('how_wage_set')) + '</dt><dd>' + val(w.how_set, T('how_wage_set')) + '</dd></div>' +
      '<div><dt>' + esc(T('wage_verified_by')) + '</dt><dd>' + val(w.verified_by, T('wage_verified_by')) + '</dd></div></dl>' +
      '<p class="small" style="margin-top:1.4rem">' + esc(T('wage_note')) + '</p></div></section>');

    /* ---- environment (v1: recycled content, electricity above, water, packaging) ---- */
    html.push('<section class="sec sec--white sec--pp" id="environment"><div class="wrap">' +
      '<span class="eyebrow">' + esc(T('env_eyebrow')) + '</span><h2 class="h1">' + esc(T('env_title')) + '</h2>' +
      '<p>' + esc(T('env_rule')) + '</p><div class="metrics">' +
      metric(isPh(m.recycled_content_pct) ? null : m.recycled_content_pct + '%', T('recycled_content'), m.recycled_content_pct, T('recycled_how')) +
      metric(isPh(m.water_l_per_mat) ? null : m.water_l_per_mat + ' L', T('water_per_mat'), m.water_l_per_mat, T('water_how')) +
      metric(isPh(m.packaging_g_per_mat) ? null : m.packaging_g_per_mat + ' g', T('packaging_per_mat'), m.packaging_g_per_mat, T('packaging_how')) +
      '</div><div class="callout"><p>' + esc(T('dye_claim')) + '</p></div></div></section>');

    /* ---- chains ---- */
    html.push('<section class="sec sec--white sec--pp" id="chains"><div class="wrap">');
    tiers.chains.forEach(function (c) {
      html.push('<div id="chain-' + c.id.toLowerCase() + '"><div class="chain-head"><span class="letter" aria-hidden="true">' + c.id + '</span><div><h2 class="h1" style="margin:0">' + esc(tr(c.name)) + '</h2><p style="margin:.4rem 0 0">' + esc(tr(c.intro)) + '</p></div></div>');
      c.tiers.forEach(function (t) {
        var s = (b.stages || {})[t.id] || {};
        var dl = t.fields.map(function (f) {
          return '<dt>' + esc(tr(f.label)) + '</dt><dd>' + val(s[f.key], tr(f.label)) + '</dd>';
        }).join('');
        var badge = t.powered === true ? '<span class="badge badge--on">' + esc(T('powered')) + '</span>' :
          t.powered === false ? '<span class="badge badge--off">' + esc(T('unpowered')) + '</span>' : '';   /* 'confirm' => nothing published */
        html.push('<article class="tier" id="tier-' + t.id.toLowerCase() + '"><span class="tier-no" aria-hidden="true">' + t.id + '</span>' +
          '<div><h3 class="tier-name"><span class="sr-only">' + t.id + ' </span>' + esc(tr(t.name)) + '</h3>' +
          '<p class="small" style="color:#444;max-width:50ch">' + esc(T('records')) + ': ' + esc(tr(t.records)) + '</p>' +
          (dl ? '<dl>' + dl + '</dl>' : '') + (s.note ? '<p class="small" style="margin-top:10px">' + esc(s.note) + '</p>' : '') + badge + '</div>' +
          '<div>' + mediaBlock(t.id, t.subject) + '</div></article>');
      });
      html.push('</div>');
    });
    html.push('</div></section>');

    /* ---- standards ---- */
    if (standards) {
      html.push('<section class="sec sec--white sec--pp" id="standards"><div class="wrap">' +
        '<span class="eyebrow">' + esc(T('standard_eyebrow')) + '</span><h2 class="h1">' + esc(T('standard_title')) + '</h2>' +
        '<p>' + esc(T('standard_lead')) + ' ' + esc(T('last_checked')) + ': ' + val(standards.last_checked, T('last_checked')) + '.</p>' +
        '<table class="facts"><tbody>' + standards.items.map(function (i) {
          return '<tr><th scope="row">' + esc(i.label) + '</th><td>' + (i.value ? esc(i.value) : '<span class="ph">[' + esc(i.ph || T('add')) + ']</span>') + '</td></tr>';
        }).join('') + '</tbody></table></div></section>');
    }

    /* ---- headcount / withheld ---- */
    var hc = b.headcount || {};
    if (hc.withheld) {
      html.push('<section class="sec sec--white sec--tight"><div class="wrap"><p class="small" style="color:#444">' + esc(T('withheld')) + ' ' + (isPh(hc.withheld_reason) ? ph(T('withheld_reason')) : esc(hc.withheld_reason)) + '</p></div></section>');
    }

    /* ---- bridge to TransparaTrade ---- */
    html.push('<section class="sec sec--orange sec--tight"><div class="wrap"><p class="statement">' + esc(T('bridge')) + '</p>' +
      '<div class="btn-row"><a class="btn" href="' + ROOT + LANG + '/transparatrade/' + IDX + '">' + esc(T('bridge_cta')) + '</a>' +
      '<a class="btn btn--ghost" href="' + ROOT + LANG + '/petition/' + IDX + '">' + esc(T('bridge_petition')) + '</a></div></div></section>');

    app.innerHTML = html.join('');
    lazyVideos();
    if (location.hash) { var el = d.getElementById(location.hash.slice(1)); if (el) el.scrollIntoView(); }
  }

  function metric(shown, label, raw, howText) {
    return '<div class="metric"><div class="val">' + (shown === null ? ph(label) : esc(shown)) + '</div><div class="lbl">' + esc(label) + '</div>' + how(raw, howText) + '</div>';
  }

  /* Video: muted, looping, poster-framed, lazy-loaded; at most one playing at a time */
  function lazyVideos() {
    var vids = [].slice.call(d.querySelectorAll('video[data-lazyvideo]'));
    if (!vids.length || !('IntersectionObserver' in window)) return;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting && e.intersectionRatio > .6 && !reduce) {
          vids.forEach(function (o) { if (o !== v) o.pause(); });
          if (!v.src) v.src = v.getAttribute('data-src');
          v.play().catch(function () {});
        } else v.pause();
      });
    }, { threshold: [0, .6] });
    vids.forEach(function (v) { io.observe(v); });
  }
})();
