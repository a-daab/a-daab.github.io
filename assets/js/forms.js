/* YogaMaty forms — allies application, petition (kiosk), wholesale inquiry.
   All three post JSON to one Cloudflare Worker (window.YM.api). Validation here is for friendliness only;
   the Worker validates again server-side. Nothing is stored in the browser. */
(function () {
  'use strict';
  var d = document, YM = window.YM || {};
  var T = function (k, v) {
    var s = window.YM_T('forms.' + k, k);
    if (v) Object.keys(v).forEach(function (n) { s = s.replace('{' + n + '}', v[n]); });
    return s;
  };
  var forms = [].slice.call(d.querySelectorAll('form[data-form]'));
  if (!forms.length) return;

  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var RULES = {
    allies: { required: ['first_name', 'last_name', 'email', 'company', 'statement'], email: 'email', url: 'link', words: { statement: 250 }, skills: true },
    petition: { required: ['name', 'email', 'location'], email: 'email' },
    wholesale: { required: ['name', 'phone', 'email', 'business'], email: 'email', phone: 'phone' }
  };
  var COMMON = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'aol.com', 'proton.me', 'protonmail.com', 'live.com', 'me.com', 'msn.com'];

  /* ---------------- Turnstile ---------------- */
  var widgets = new Map(), tsReady = false;
  function loadTurnstile() {
    if (!YM.turnstile) return;
    window.__ymTurnstile = function () {
      tsReady = true;
      forms.forEach(function (f) {
        var mount = f.querySelector('.cf-turnstile-mount');
        if (mount && window.turnstile) widgets.set(f, window.turnstile.render(mount, { sitekey: YM.turnstile, theme: 'light' }));
      });
    };
    var s = d.createElement('script');
    s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__ymTurnstile';
    s.async = true; s.defer = true; d.head.appendChild(s);
  }
  function tsToken(f) { return widgets.has(f) && window.turnstile ? window.turnstile.getResponse(widgets.get(f)) : ''; }
  function tsReset(f) { if (widgets.has(f) && window.turnstile) window.turnstile.reset(widgets.get(f)); }

  /* ---------------- helpers ---------------- */
  function collect(f) {
    var o = {};
    [].forEach.call(f.elements, function (el) {
      if (!el.name) return;
      var k = el.name.replace(/^ym_/, '');
      if (el.type === 'checkbox') {
        if (k === 'skills') { o.skills = o.skills || []; if (el.checked) o.skills.push(el.value); }
        else o[k] = el.checked;
      } else o[k] = el.value.trim();
    });
    return o;
  }
  function fieldBox(f, key) { return f.querySelector('[data-field="' + key + '"]'); }
  function setErr(f, key, msg) {
    var box = fieldBox(f, key);
    if (!box) return;
    box.classList.toggle('invalid', !!msg);
    var e = box.querySelector('.err');
    if (e) e.textContent = msg || '';
    var input = box.querySelector('input,textarea');
    if (input && input.type !== 'checkbox') input.setAttribute('aria-invalid', msg ? 'true' : 'false');
  }
  function clearErrs(f) { [].forEach.call(f.querySelectorAll('[data-field]'), function (b) { setErr(f, b.getAttribute('data-field'), ''); }); }
  function words(s) { return (s.match(/\S+/g) || []).length; }
  function status(f, msg, isErr) {
    var s = f.querySelector('.form-status');
    if (!s) return;
    s.textContent = msg || '';
    s.classList.toggle('err', !!isErr);
  }
  function stamp(f) { var t = f.querySelector('input[name="t"]'); if (t) t.value = String(Date.now()); }

  function validate(f, type) {
    var r = RULES[type], v = collect(f), bad = [], first = null;
    function fail(k, m) { setErr(f, k, m); bad.push(k); }
    clearErrs(f);
    r.required.forEach(function (k) { if (!v[k]) fail(k, T('required')); });
    if (r.email && v[r.email] && !EMAIL.test(v[r.email])) fail(r.email, T('email'));
    if (r.phone && v[r.phone] && v[r.phone].replace(/\D/g, '').length < 7) fail(r.phone, T('required'));
    if (r.url && v[r.url]) { try { var u = new URL(v[r.url]); if (!/^https?:$/.test(u.protocol)) throw 0; } catch (e) { fail(r.url, T('url')); } }
    if (r.words) Object.keys(r.words).forEach(function (k) { if (v[k] && words(v[k]) > r.words[k]) fail(k, T('words', { max: r.words[k] })); });
    if (r.skills && !(v.skills && v.skills.length) && !v.skills_other) fail('skills', T('skills'));
    if (!v.consent) fail('consent', T('consent'));
    if (bad.length) {
      var box = fieldBox(f, bad[0]);
      var el = box && box.querySelector('input,textarea');
      if (el && el.type !== 'checkbox') el.focus(); else if (box) { var c = f.querySelector('input[name="consent"]'); if (bad[0] === 'consent' && c) c.focus(); else if (box.scrollIntoView) box.scrollIntoView({ block: 'center' }); }
    }
    return bad.length ? null : v;
  }

  /* ---------------- email typo hint ---------------- */
  function lev(a, b) {
    var m = [], i, j;
    for (i = 0; i <= a.length; i++) m[i] = [i];
    for (j = 0; j <= b.length; j++) m[0][j] = j;
    for (i = 1; i <= a.length; i++) for (j = 1; j <= b.length; j++)
      m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    return m[a.length][b.length];
  }
  function typoHint(input) {
    var box = input.closest('.field'), old = box.querySelector('.typo');
    if (old) old.remove();
    var v = input.value.trim(), at = v.lastIndexOf('@');
    if (at < 1) return;
    var dom = v.slice(at + 1).toLowerCase();
    if (!dom || COMMON.indexOf(dom) > -1) return;
    var best = null;
    COMMON.forEach(function (c) { var n = lev(dom, c); if (n > 0 && n <= 2 && (!best || n < best.n)) best = { c: c, n: n }; });
    if (!best) return;
    var sugg = v.slice(0, at + 1) + best.c;
    var el = d.createElement('div'); el.className = 'hint typo';
    var b = d.createElement('button', {}); b.type = 'button';
    b.style.cssText = 'background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;cursor:pointer';
    b.textContent = T('email_suggest', { suggestion: sugg });
    b.addEventListener('click', function () { input.value = sugg; el.remove(); input.focus(); });
    el.appendChild(b); box.appendChild(el);
  }

  /* ---------------- submit ---------------- */
  function submit(f, type, ev) {
    ev.preventDefault();
    var v = validate(f, type);
    if (!v) { status(f, '', false); return; }
    if (!YM.api) { status(f, T('not_live'), true); return; }
    var btn = f.querySelector('button[type="submit"]');
    var payload = Object.assign({}, v, { turnstile: tsToken(f) });
    btn.disabled = true; status(f, T('sending'), false);
    fetch(YM.api.replace(/\/$/, '') + '/' + type, {
      method: 'POST', credentials: 'omit', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { s: r.status, j: j }; }); })
      .then(function (res) {
        btn.disabled = false;
        if (res.s === 200 && res.j.ok) return done(f, type, res.j);
        if (res.s === 429) return status(f, T('rate'), true);
        if (res.s === 422 && res.j.errors) {
          Object.keys(res.j.errors).forEach(function (k) { setErr(f, k, res.j.errors[k]); });
          return status(f, T('generic'), true);
        }
        if (res.s === 403) { tsReset(f); return status(f, T('spam'), true); }
        status(f, T('generic'), true);
      })
      .catch(function () { btn.disabled = false; status(f, T('network'), true); });
  }

  function done(f, type, j) {
    f.reset(); clearErrs(f); status(f, '', false); tsReset(f);
    f.classList.add('is-done');
    var msg = f.querySelector('[data-done-msg]');
    if (msg && type === 'petition') msg.textContent = j.status === 'already_signed' ? T('done_already') : T('done_signed');
    var panel = f.querySelector('.form-done');
    if (panel) { panel.focus({ preventScroll: true }); if (panel.scrollIntoView) panel.scrollIntoView({ block: 'start', behavior: 'smooth' }); }
    if (type === 'petition') loadCount();
  }

  function reset(f) {
    f.classList.remove('is-done'); f.reset(); clearErrs(f); status(f, '', false); stamp(f); tsReset(f);
    [].forEach.call(f.querySelectorAll('.typo'), function (n) { n.remove(); });
    var first = f.querySelector('.form-live input[type="text"], .form-live input[type="email"]');
    if (first) first.focus();
  }

  /* ---------------- init each form ---------------- */
  forms.forEach(function (f) {
    var type = f.getAttribute('data-form');
    f.setAttribute('autocomplete', 'off');
    stamp(f);
    f.addEventListener('submit', function (e) { submit(f, type, e); });
    f.addEventListener('input', function (e) {
      var box = e.target.closest && e.target.closest('[data-field]');
      if (box && box.classList.contains('invalid')) setErr(f, box.getAttribute('data-field'), '');
    });
    var email = f.querySelector('input[type="email"]');
    if (email) email.addEventListener('blur', function () { typoHint(email); });
    var ta = f.querySelector('textarea[data-maxwords]'), cnt = f.querySelector('[data-count]');
    if (ta && cnt) {
      var max = parseInt(ta.getAttribute('data-maxwords'), 10);
      var upd = function () { var n = words(ta.value); cnt.textContent = n + ' / ' + max; cnt.style.color = n > max ? '#9b1c00' : ''; };
      ta.addEventListener('input', upd); upd();
    }
    var rs = f.querySelector('[data-reset]');
    if (rs) rs.addEventListener('click', function () { reset(f); });
  });

  /* ---------------- petition: copy / share / count ---------------- */
  var copyBtn = d.querySelector('[data-copy]');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var src = d.querySelector(copyBtn.getAttribute('data-copy')), text = src.textContent.trim(), orig = copyBtn.textContent;
      var ok = function () { copyBtn.textContent = T('copied'); setTimeout(function () { copyBtn.textContent = orig; }, 2200); };
      var fail = function () { copyBtn.textContent = T('copy_failed'); setTimeout(function () { copyBtn.textContent = orig; }, 3500); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fail);
      else { var r = d.createRange(); r.selectNodeContents(src); var s = getSelection(); s.removeAllRanges(); s.addRange(r); try { d.execCommand('copy') ? ok() : fail(); } catch (e) { fail(); } }
    });
    var share = d.getElementById('share-text');
    if (share) {
      var text = encodeURIComponent(share.textContent.trim()), url = encodeURIComponent(YM.shareUrl || '');
      var map = {
        x: 'https://twitter.com/intent/tweet?text=' + text,
        facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + url,
        whatsapp: 'https://wa.me/?text=' + text,
        linkedin: 'https://www.linkedin.com/sharing/share-offsite/?url=' + url
      };
      [].forEach.call(d.querySelectorAll('[data-share]'), function (a) { a.href = map[a.getAttribute('data-share')] || '#'; });
    }
  }

  /* The signature count is shown only once the server says the threshold has been met */
  function loadCount() {
    var el = d.getElementById('pet-count');
    if (!el || !YM.api) return;
    fetch(YM.api.replace(/\/$/, '') + '/petition/count', { credentials: 'omit' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.visible) { el.textContent = T('people_signed', { n: Number(j.count).toLocaleString() }); el.hidden = false; } })
      .catch(function () {});
  }
  loadCount();
  loadTurnstile();
})();
