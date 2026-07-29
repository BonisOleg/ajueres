(function () {
  'use strict';

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
      if (!isMobile()) {
        panel.removeAttribute('aria-hidden');
        panel.removeAttribute('aria-modal');
        openBtn.setAttribute('aria-expanded', 'false');
        return;
      }
      panel.setAttribute('aria-hidden', open ? 'false' : 'true');
      panel.setAttribute('aria-modal', open ? 'true' : 'false');
      openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    function setOpen(open, silent) {
      if (!isMobile() && open) return;

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

      if (!silent && openBtn) openBtn.focus();
    }

    syncPlacement();
    syncA11y(false);

    openBtn.addEventListener('click', function () {
      setOpen(!isOpen());
    });

    document.addEventListener('click', function (evt) {
      var t = evt.target;
      if (!t || !t.closest) return;
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
})();
