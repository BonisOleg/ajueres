(function () {
  'use strict';

  function syncFilterButtonState() {
    var btn = document.getElementById('catalog-filter-btn');
    var countEl = document.getElementById('catalog-filter-btn-count');
    if (!btn || !countEl) return;
    var raw = (countEl.textContent || '').trim();
    var has = raw !== '' && !countEl.classList.contains('is-empty');
    btn.classList.toggle('has-filters', has);
  }

  function initCatalogFilters() {
    var root = document.querySelector('[data-catalog-filters]');
    if (!root) return;

    var openBtn = root.querySelector('[data-catalog-filters-open]');
    var panel = root.querySelector('.catalog-filters__panel');
    var backdrop = root.querySelector('.catalog-filters__backdrop');
    if (!openBtn || !panel) return;

    var closeTimer = 0;
    var mq = window.matchMedia('(max-width: 767px)');
    var parked = false;

    function isMobile() {
      return mq.matches;
    }

    function isOpen() {
      return document.body.classList.contains('is-catalog-filters-open');
    }

    function parkDrawer() {
      if (parked || !isMobile()) return;
      document.body.appendChild(backdrop);
      document.body.appendChild(panel);
      parked = true;
    }

    function unparkDrawer() {
      if (!parked) return;
      root.appendChild(backdrop);
      root.appendChild(panel);
      parked = false;
    }

    function syncPlacement() {
      if (isMobile()) {
        parkDrawer();
      } else {
        setOpen(false, true);
        unparkDrawer();
      }
      syncA11y(isOpen());
    }

    function syncA11y(open) {
      var currentBtn = document.getElementById('catalog-filter-btn') || openBtn;
      if (!isMobile()) {
        panel.removeAttribute('aria-hidden');
        panel.removeAttribute('aria-modal');
        currentBtn.setAttribute('aria-expanded', 'false');
        return;
      }
      panel.setAttribute('aria-hidden', open ? 'false' : 'true');
      panel.setAttribute('aria-modal', open ? 'true' : 'false');
      currentBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    function setOpen(open, silent) {
      if (!isMobile() && open) return;

      var currentBtn = document.getElementById('catalog-filter-btn') || openBtn;
      window.clearTimeout(closeTimer);
      parkDrawer();
      syncA11y(!!open);
      document.body.classList.toggle('is-catalog-filters-open', !!open);
      root.classList.toggle('is-open', !!open);
      panel.classList.toggle('is-open', !!open);
      backdrop.classList.toggle('is-open', !!open);

      if (open) {
        backdrop.removeAttribute('hidden');
        panel.removeAttribute('hidden');
        var closeBtn = panel.querySelector('.catalog-filters__close');
        if (closeBtn) closeBtn.focus();
        return;
      }

      closeTimer = window.setTimeout(function () {
        if (!isOpen()) backdrop.setAttribute('hidden', '');
      }, 280);

      if (!silent && currentBtn) currentBtn.focus();
    }

    syncPlacement();
    syncA11y(false);
    syncFilterButtonState();

    document.addEventListener('click', function (evt) {
      var t = evt.target;
      if (!t || !t.closest) return;
      if (t.closest('[data-catalog-filters-open]')) {
        setOpen(!isOpen());
        return;
      }
      if (t.closest('[data-catalog-filters-close]')) {
        if (isOpen()) setOpen(false);
      }
    });

    document.addEventListener('keydown', function (evt) {
      if (evt.key === 'Escape' && isOpen()) setOpen(false);
    });

    if (typeof mq.addEventListener === 'function') {
      mq.addEventListener('change', syncPlacement);
    } else if (typeof mq.addListener === 'function') {
      mq.addListener(syncPlacement);
    }
  }

  document.addEventListener('DOMContentLoaded', initCatalogFilters);
  document.body.addEventListener('htmx:afterSwap', syncFilterButtonState);

  /* Badge label: long-press only on touch / coarse pointers */
  (function initBadgeLongPressTooltip() {
    var DELAY_MS = 480;
    var timer = 0;
    var openBadge = null;
    var coarseMq = window.matchMedia('(hover: none), (pointer: coarse)');

    function isTouchUi() {
      return coarseMq.matches;
    }

    function closeTooltip() {
      if (timer) {
        window.clearTimeout(timer);
        timer = 0;
      }
      if (openBadge) {
        openBadge.classList.remove('is-tooltip-open');
        openBadge = null;
      }
    }

    function onTouchStart(evt) {
      if (!isTouchUi()) return;
      var t = evt.target;
      if (!t || !t.closest) return;
      var badge = t.closest('.product-group__badge[data-tooltip]');
      closeTooltip();
      if (!badge) return;
      timer = window.setTimeout(function () {
        timer = 0;
        openBadge = badge;
        badge.classList.add('is-tooltip-open');
      }, DELAY_MS);
    }

    function onTouchMove() {
      if (timer) {
        window.clearTimeout(timer);
        timer = 0;
      }
    }

    document.addEventListener('touchstart', onTouchStart, { passive: true });
    document.addEventListener('touchmove', onTouchMove, { passive: true });
    document.addEventListener('touchend', closeTooltip, { passive: true });
    document.addEventListener('touchcancel', closeTooltip, { passive: true });
    document.addEventListener('scroll', closeTooltip, { passive: true, capture: true });

    document.addEventListener('contextmenu', function (evt) {
      if (!isTouchUi()) return;
      var t = evt.target;
      if (t && t.closest && t.closest('.product-group__badge[data-tooltip]')) {
        evt.preventDefault();
      }
    });
  })();
})();
