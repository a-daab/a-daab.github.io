/* Shop page gallery: click (or press Enter/Space on) a thumbnail and it swaps places with the large image. */
(function () {
  'use strict';
  var main = document.querySelector('[data-gallery-main]');
  var strip = document.querySelector('[data-gallery-thumbs]');
  if (!main || !strip) return;
  var big = main.querySelector('img');
  var thumbs = [].slice.call(strip.querySelectorAll('.media'));
  var ATTRS = ['src', 'srcset', 'sizes', 'alt', 'width', 'height'];

  function label(fig) {
    fig.setAttribute('aria-label', 'Show this photo large: ' + fig.querySelector('img').getAttribute('alt'));
  }
  function swap(fig) {
    var img = fig.querySelector('img');
    ATTRS.forEach(function (a) {
      var m = big.getAttribute(a), t = img.getAttribute(a);
      if (t === null) big.removeAttribute(a); else big.setAttribute(a, t);
      if (m === null) img.removeAttribute(a); else img.setAttribute(a, m);
    });
    img.removeAttribute('loading');
    label(fig);
    [main, fig].forEach(function (el) {
      el.classList.remove('is-swapped');
      void el.offsetWidth;                    // restart the fade
      el.classList.add('is-swapped');
    });
  }
  thumbs.forEach(function (fig) {
    fig.setAttribute('role', 'button');
    fig.setAttribute('tabindex', '0');
    label(fig);
    fig.addEventListener('click', function () { swap(fig); });
    fig.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); swap(fig); }
    });
  });
})();
