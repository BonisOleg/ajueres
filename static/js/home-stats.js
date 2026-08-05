(function () {
  'use strict';

  function initHeroStats() {
    var root = document.querySelector('[data-hero-stats]');
    var trigger = document.querySelector('[data-hero-stats-trigger]');
    if (!root || !trigger) return;

    var panel = root.querySelector('[data-hero-stats-panel]');
    var closeBtn = root.querySelector('[data-hero-stats-close]');
    if (!panel) return;

    var hideTimer = null;
    var openRaf = 0;
    var orbCount = root.querySelectorAll('.hero-stats__orb').length || 4;
    /* duration 1s + stagger between orbs */
    var hideDelay = 1050 + (orbCount - 1) * 180;

    function cancelOpenRaf() {
      if (openRaf) {
        window.cancelAnimationFrame(openRaf);
        openRaf = 0;
      }
    }

    function isOpen() {
      return root.classList.contains('is-open');
    }

    function setOpen(open) {
      if (hideTimer) {
        window.clearTimeout(hideTimer);
        hideTimer = null;
      }
      cancelOpenRaf();

      if (open) {
        if (isOpen() && !panel.hidden) return;

        panel.hidden = false;
        /* ensure closed styles paint before opening — інакше transition не грає */
        root.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'true');
        void panel.offsetWidth;

        openRaf = window.requestAnimationFrame(function () {
          openRaf = window.requestAnimationFrame(function () {
            openRaf = 0;
            root.classList.add('is-open');
          });
        });
        return;
      }

      root.classList.remove('is-open');
      trigger.setAttribute('aria-expanded', 'false');

      hideTimer = window.setTimeout(function () {
        hideTimer = null;
        if (!isOpen()) panel.hidden = true;
      }, hideDelay);
    }

    function open() {
      setOpen(true);
    }

    function close() {
      setOpen(false);
    }

    function toggle() {
      if (isOpen()) close();
      else open();
    }

    trigger.addEventListener('click', function (evt) {
      evt.preventDefault();
      toggle();
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', function (evt) {
        evt.preventDefault();
        close();
      });
    }

    document.addEventListener('keydown', function (evt) {
      if (evt.key === 'Escape' && isOpen()) close();
    });
  }

  document.addEventListener('DOMContentLoaded', initHeroStats);
})();
