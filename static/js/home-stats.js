(function () {
  'use strict';

  function initHeroStats() {
    var root = document.querySelector('[data-hero-stats]');
    var trigger = document.querySelector('[data-hero-stats-trigger]');
    if (!root || !trigger) return;

    var panel = root.querySelector('[data-hero-stats-panel]');
    if (!panel) return;

    var hideTimer = null;
    var openRaf = 0;
    var pressPointerId = null;
    var hoverMq = window.matchMedia('(hover: hover) and (pointer: fine)');
    var orbCount = root.querySelectorAll('.hero-stats__orb').length || 4;
    /* duration 1s + stagger between orbs */
    var hideDelay = 1050 + (orbCount - 1) * 180;

    function isHoverMode() {
      return hoverMq.matches;
    }

    function cancelOpenRaf() {
      if (openRaf) {
        window.cancelAnimationFrame(openRaf);
        openRaf = 0;
      }
    }

    function setOpen(open) {
      if (hideTimer) {
        window.clearTimeout(hideTimer);
        hideTimer = null;
      }
      cancelOpenRaf();

      if (open) {
        if (root.classList.contains('is-open') && !panel.hidden) return;

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
        if (!root.classList.contains('is-open')) panel.hidden = true;
      }, hideDelay);
    }

    function open() {
      setOpen(true);
    }

    function close() {
      pressPointerId = null;
      setOpen(false);
    }

    trigger.addEventListener('mouseenter', function () {
      if (!isHoverMode()) return;
      open();
    });

    trigger.addEventListener('mouseleave', function () {
      if (!isHoverMode()) return;
      close();
    });

    trigger.addEventListener('pointerdown', function (evt) {
      if (isHoverMode()) return;
      if (evt.pointerType === 'mouse' && evt.button !== 0) return;
      pressPointerId = evt.pointerId;
      try {
        trigger.setPointerCapture(evt.pointerId);
      } catch (err) {
        /* ignore */
      }
      open();
    });

    function endPress(evt) {
      if (isHoverMode()) return;
      if (pressPointerId !== null && evt.pointerId !== pressPointerId) return;
      close();
    }

    trigger.addEventListener('pointerup', endPress);
    trigger.addEventListener('pointercancel', endPress);
    trigger.addEventListener('lostpointercapture', function () {
      if (isHoverMode()) return;
      close();
    });

    trigger.addEventListener('click', function (evt) {
      evt.preventDefault();
    });

    trigger.addEventListener('contextmenu', function (evt) {
      if (!isHoverMode()) evt.preventDefault();
    });

    document.addEventListener('keydown', function (evt) {
      if (evt.key === 'Escape' && root.classList.contains('is-open')) close();
    });
  }

  document.addEventListener('DOMContentLoaded', initHeroStats);
})();
