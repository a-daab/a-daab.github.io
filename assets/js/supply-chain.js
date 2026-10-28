/* The Supply Chain: pick a stage on the left, read its breakdown on the right. The product-number box is a shell until the tracing system exists. */
(function () {
  'use strict';
  var root = document.getElementById('sc');
  if (root) {
    var nodes = [].slice.call(root.querySelectorAll('.sc-node'));
    var panels = [].slice.call(root.querySelectorAll('.sc-panel'));
    var empty = document.getElementById('panel-empty');
    root.classList.add('is-js');
    var stacked = window.matchMedia && matchMedia('(max-width: 900px)');
    function open(id, fromUser) {
      nodes.forEach(function (n) {
        var on = n.getAttribute('data-panel') === id;
        n.classList.toggle('is-on', on);
        n.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
      panels.forEach(function (p) { p.hidden = p.id !== 'panel-' + id; });
      if (empty) empty.hidden = !!id;
      if (fromUser && stacked && stacked.matches) {
        var el = document.getElementById('panel-' + id), r = el.getBoundingClientRect();
        if (r.top > window.innerHeight * 0.75 || r.top < 0) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
    nodes.forEach(function (n) {
      n.addEventListener('click', function () { open(n.getAttribute('data-panel'), true); });
    });
    var h = (location.hash || '').replace('#', '');
    if (h && document.getElementById('panel-' + h)) open(h, false); else open('', false);
  }

  var form = document.getElementById('trace-form'), note = document.getElementById('trace-note');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      note.textContent = 'Tracing by product number isn’t live yet. For now you can browse a sample record in the Supply-Chain Explorer.';
    });
  }
})();
