(function () {
  'use strict';

  function initBurger() {
    var burger = document.getElementById('burger');
    var nav = document.getElementById('mobile-nav');
    var backdrop = document.getElementById('nav-mobile-backdrop');
    var closeBtn = document.getElementById('nav-mobile-close');
    if (!burger || !nav) return;

    var labelOpen = burger.getAttribute('aria-label') || 'Menu';
    var labelClose = (closeBtn && closeBtn.getAttribute('aria-label')) || 'Close';
    var closeTimer = 0;
    var openRaf = 0;

    function isOpen() {
      return nav.classList.contains('is-open');
    }

    function setOpen(open) {
      window.clearTimeout(closeTimer);
      if (openRaf) {
        window.cancelAnimationFrame(openRaf);
        openRaf = 0;
      }

      burger.classList.toggle('is-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? labelClose : labelOpen);
      document.body.classList.toggle('is-nav-open', open);

      if (open) {
        nav.removeAttribute('hidden');
        nav.classList.remove('is-open');
        void nav.offsetWidth;
        openRaf = window.requestAnimationFrame(function () {
          openRaf = 0;
          nav.classList.add('is-open');
        });
        return;
      }

      nav.classList.remove('is-open');
      closeTimer = window.setTimeout(function () {
        closeTimer = 0;
        if (!nav.classList.contains('is-open')) {
          nav.setAttribute('hidden', '');
        }
      }, 400);
    }

    burger.addEventListener('click', function () {
      setOpen(!isOpen());
    });

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        setOpen(false);
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        setOpen(false);
      });
    }

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && isOpen()) {
        setOpen(false);
      }
    });
  }

  function initBrandsCarousel(root) {
    var track = root.querySelector('[data-brands-track]');
    var prev = root.querySelector('[data-brands-prev]');
    var next = root.querySelector('[data-brands-next]');
    if (!track) return;

    var originals = Array.prototype.slice.call(track.querySelectorAll('.brand-card'));
    var count = originals.length;
    if (!count) return;

    var cloneCount = 0;
    var infinite = count > 1;

    if (infinite) {
      var prependFrag = document.createDocumentFragment();
      var appendFrag = document.createDocumentFragment();

      originals.forEach(function (card, index) {
        var leading = card.cloneNode(true);
        leading.setAttribute('data-brand-clone', 'leading');
        leading.setAttribute('data-brand-logical', String(index));
        leading.setAttribute('aria-hidden', 'true');
        prependFrag.appendChild(leading);

        var trailing = card.cloneNode(true);
        trailing.setAttribute('data-brand-clone', 'trailing');
        trailing.setAttribute('data-brand-logical', String(index));
        trailing.setAttribute('aria-hidden', 'true');
        appendFrag.appendChild(trailing);
      });

      track.insertBefore(prependFrag, track.firstChild);
      track.appendChild(appendFrag);
      cloneCount = count;
    }

    var cards = Array.prototype.slice.call(track.querySelectorAll('.brand-card'));
    var activePhysical = cloneCount;
    var rafId = 0;
    var settleTimer = 0;
    var isJumping = false;

    function trackCenterX() {
      var rect = track.getBoundingClientRect();
      return rect.left + rect.width / 2;
    }

    function findClosestPhysical() {
      var center = trackCenterX();
      var best = 0;
      var bestDist = Infinity;
      for (var i = 0; i < cards.length; i += 1) {
        var r = cards[i].getBoundingClientRect();
        var dist = Math.abs(r.left + r.width / 2 - center);
        if (dist < bestDist) {
          bestDist = dist;
          best = i;
        }
      }
      return best;
    }

    function scrollDeltaForCard(card) {
      var trackRect = track.getBoundingClientRect();
      var cardRect = card.getBoundingClientRect();
      return cardRect.left + cardRect.width / 2 - (trackRect.left + trackRect.width / 2);
    }

    function positionNav() {
      if (!prev || !next) return;
      var active = cards[activePhysical];
      if (!active) return;

      var rootRect = root.getBoundingClientRect();
      var activeRect = active.getBoundingClientRect();
      var midY = activeRect.top + activeRect.height / 2 - rootRect.top;
      var leftNeighbor = cards[activePhysical - 1];
      var rightNeighbor = cards[activePhysical + 1];

      prev.style.top = midY + 'px';
      next.style.top = midY + 'px';
      prev.disabled = false;
      next.disabled = false;

      if (leftNeighbor) {
        var leftRect = leftNeighbor.getBoundingClientRect();
        prev.style.left = (leftRect.right + activeRect.left) / 2 - rootRect.left + 'px';
      } else {
        prev.style.left = activeRect.left - rootRect.left - 8 + 'px';
        prev.disabled = true;
      }

      if (rightNeighbor) {
        var rightRect = rightNeighbor.getBoundingClientRect();
        next.style.left = (activeRect.right + rightRect.left) / 2 - rootRect.left + 'px';
      } else {
        next.style.left = activeRect.right - rootRect.left + 8 + 'px';
        next.disabled = true;
      }
    }

    function updateClasses(physicalIndex) {
      activePhysical = physicalIndex;
      for (var i = 0; i < cards.length; i += 1) {
        var dist = Math.abs(i - physicalIndex);
        cards[i].classList.toggle('is-active', dist === 0);
        cards[i].classList.toggle('is-near', dist === 1);
        cards[i].classList.toggle('is-far', dist >= 2);
      }
      positionNav();
    }

    function applyScrollDelta(delta, behavior) {
      if (Math.abs(delta) < 1) return;
      var mode = behavior || 'smooth';
      if (mode === 'auto' || mode === 'instant') {
        track.scrollLeft += delta;
      } else {
        track.scrollBy({ left: delta, behavior: 'smooth' });
      }
    }

    function scrollToPhysical(physicalIndex, behavior) {
      if (!cards[physicalIndex]) return;
      updateClasses(physicalIndex);
      applyScrollDelta(scrollDeltaForCard(cards[physicalIndex]), behavior);
    }

    function jumpToPhysical(physicalIndex) {
      if (!cards[physicalIndex]) return;
      isJumping = true;
      updateClasses(physicalIndex);
      applyScrollDelta(scrollDeltaForCard(cards[physicalIndex]), 'instant');
      window.requestAnimationFrame(function () {
        isJumping = false;
      });
    }

    function normalizeLoop(physicalIndex) {
      if (!infinite) return;
      if (physicalIndex < cloneCount) {
        jumpToPhysical(physicalIndex + count);
      } else if (physicalIndex >= cloneCount + count) {
        jumpToPhysical(physicalIndex - count);
      }
    }

    function syncFromScroll() {
      if (isJumping) return;
      var physical = findClosestPhysical();
      updateClasses(physical);
      normalizeLoop(physical);
    }

    function onScroll() {
      if (isJumping) return;
      if (rafId) return;
      rafId = window.requestAnimationFrame(function () {
        rafId = 0;
        syncFromScroll();
      });
      window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(syncFromScroll, 80);
    }

    function startPhysicalIndex() {
      var wide = window.matchMedia('(min-width: 880px)').matches;
      var logical = 0;
      if (wide && count >= 5) logical = 2;
      else if (count >= 3) logical = 1;
      return cloneCount + logical;
    }

    function settleStart() {
      scrollToPhysical(startPhysicalIndex(), 'auto');
      syncFromScroll();
    }

    track.addEventListener('click', function (evt) {
      var card = evt.target.closest('.brand-card');
      if (!card || !track.contains(card)) return;
      var physical = cards.indexOf(card);
      if (physical < 0 || physical === activePhysical) return;
      evt.preventDefault();
      scrollToPhysical(physical);
    });

    if (prev) {
      prev.addEventListener('click', function () {
        scrollToPhysical(activePhysical - 1);
      });
    }
    if (next) {
      next.addEventListener('click', function () {
        scrollToPhysical(activePhysical + 1);
      });
    }

    track.addEventListener('scroll', onScroll, { passive: true });
    track.addEventListener('scrollend', syncFromScroll);

    window.addEventListener('resize', function () {
      scrollToPhysical(findClosestPhysical(), 'auto');
    });

    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(settleStart);
    });
    window.addEventListener('load', settleStart);
  }

  function initContactModal() {
    var modal = document.getElementById('contact-modal');
    if (!modal) return;

    var dialog = modal.querySelector('.contact-modal__dialog');
    var lastTrigger = null;
    var closeTimer = 0;

    function focusableNodes() {
      if (!dialog) return [];
      return Array.prototype.slice.call(
        dialog.querySelectorAll(
          'button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])'
        )
      ).filter(function (node) {
        return !node.disabled && node.offsetParent !== null;
      });
    }

    function openModal(trigger) {
      lastTrigger = trigger || null;
      window.clearTimeout(closeTimer);
      modal.removeAttribute('hidden');
      modal.setAttribute('aria-hidden', 'false');
      modal.classList.add('is-open');
      document.body.classList.add('modal-open');

      window.requestAnimationFrame(function () {
        var firstField = dialog.querySelector('textarea, input:not([type="hidden"])');
        if (firstField) firstField.focus();
      });
    }

    function closeModal() {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('modal-open');
      window.setTimeout(function () {
        if (!modal.classList.contains('is-open')) {
          modal.setAttribute('hidden', '');
        }
      }, 280);
      if (lastTrigger) lastTrigger.focus();
    }

    document.querySelectorAll('[data-open-contact-modal]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openModal(btn);
      });
    });

    modal.querySelectorAll('[data-close-contact-modal]').forEach(function (btn) {
      btn.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', function (evt) {
      if (!modal.classList.contains('is-open')) return;
      if (evt.key === 'Escape') {
        evt.preventDefault();
        closeModal();
        return;
      }
      if (evt.key !== 'Tab' || !dialog) return;
      var nodes = focusableNodes();
      if (!nodes.length) return;
      var first = nodes[0];
      var last = nodes[nodes.length - 1];
      if (evt.shiftKey && document.activeElement === first) {
        evt.preventDefault();
        last.focus();
      } else if (!evt.shiftKey && document.activeElement === last) {
        evt.preventDefault();
        first.focus();
      }
    });
  }

  function initAllCarousels() {
    document.querySelectorAll('[data-brands-carousel]').forEach(initBrandsCarousel);
  }

  function initAdvantageReveal() {
    var items = document.querySelectorAll('.advantage, .reveal');
    if (!items.length) return;

    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) {
        el.classList.add('is-inview');
      });
      return;
    }

    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      items.forEach(function (el) {
        el.classList.add('is-inview');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-inview');
        observer.unobserve(entry.target);
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -24px 0px',
    });

    items.forEach(function (el) {
      observer.observe(el);
    });
  }

  function parseCounterValue(raw) {
    var text = String(raw || '').trim();
    var match = text.match(/^(\d+(?:[.,]\d+)?)(.*)$/);
    if (!match) {
      return { target: 0, suffix: text, decimals: 0 };
    }
    var numStr = match[1].replace(',', '.');
    var decimals = (numStr.split('.')[1] || '').length;
    return {
      target: parseFloat(numStr) || 0,
      suffix: match[2] || '',
      decimals: decimals,
    };
  }

  function animateCounter(el, meta) {
    var duration = 900;
    var start = null;
    var finalText = el.getAttribute('data-counter') || (String(meta.target) + meta.suffix);

    function frame(ts) {
      if (start === null) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = meta.target * eased;
      if (progress >= 1) {
        el.textContent = finalText;
        return;
      }
      if (meta.decimals > 0) {
        el.textContent = current.toFixed(meta.decimals) + meta.suffix;
      } else {
        el.textContent = String(Math.round(current)) + meta.suffix;
      }
      window.requestAnimationFrame(frame);
    }

    window.requestAnimationFrame(frame);
  }

  function initStatCounters() {
    var items = document.querySelectorAll('[data-counter]');
    if (!items.length) return;

    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function run(el) {
      if (el.getAttribute('data-counter-done') === '1') return;
      el.setAttribute('data-counter-done', '1');
      var meta = parseCounterValue(el.getAttribute('data-counter'));
      if (prefersReduced || !meta.target) {
        el.textContent = el.getAttribute('data-counter') || '';
        return;
      }
      el.textContent = '0' + meta.suffix;
      animateCounter(el, meta);
    }

    if (!('IntersectionObserver' in window) || prefersReduced) {
      items.forEach(run);
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        run(entry.target);
        observer.unobserve(entry.target);
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -24px 0px',
    });

    items.forEach(function (el) {
      observer.observe(el);
    });
  }

  function initLangSwitch() {
    document.querySelectorAll('[data-lang-switch]').forEach(function (root) {
      var toggle = root.querySelector('[data-lang-toggle]');
      var menu = root.querySelector('.lang-switch__menu');
      if (!toggle) return;

      toggle.addEventListener('click', function (evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var open = !root.classList.contains('is-open');
        document.querySelectorAll('[data-lang-switch].is-open').forEach(function (node) {
          if (node === root) return;
          node.classList.remove('is-open');
          var btn = node.querySelector('[data-lang-toggle]');
          if (btn) btn.setAttribute('aria-expanded', 'false');
        });
        root.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });

      if (menu) {
        menu.addEventListener('click', function (evt) {
          evt.stopPropagation();
        });
      }
    });

    document.addEventListener('click', function () {
      document.querySelectorAll('[data-lang-switch].is-open').forEach(function (node) {
        node.classList.remove('is-open');
        var btn = node.querySelector('[data-lang-toggle]');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function initMegaMenu() {
    document.querySelectorAll('[data-mega]').forEach(function (root) {
      var closeTimer = 0;

      function open() {
        window.clearTimeout(closeTimer);
        root.classList.add('is-open');
      }

      function scheduleClose() {
        window.clearTimeout(closeTimer);
        closeTimer = window.setTimeout(function () {
          root.classList.remove('is-open');
        }, 160);
      }

      root.addEventListener('mouseenter', open);
      root.addEventListener('mouseleave', scheduleClose);
      root.addEventListener('focusin', open);
      root.addEventListener('focusout', function (evt) {
        if (!root.contains(evt.relatedTarget)) scheduleClose();
      });
    });
  }

  function initHomeCatalog() {
    var root = document.querySelector('[data-home-catalog]');
    if (!root) return;

    var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-cat-btn]'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('[data-cat-panel]'));
    if (!buttons.length || !panels.length) return;

    function activate(index, fromUser) {
      buttons.forEach(function (btn) {
        var active = btn.getAttribute('data-cat-btn') === String(index);
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      panels.forEach(function (panel) {
        var active = panel.getAttribute('data-cat-panel') === String(index);
        var img = panel.querySelector('.home-catalog__media-glass img');
        if (active) {
          panel.hidden = false;
          if (img) img.classList.remove('is-revealing');
          window.requestAnimationFrame(function () {
            panel.classList.add('is-active');
            if (img && fromUser) {
              void img.offsetWidth;
              img.classList.add('is-revealing');
            }
          });
        } else {
          panel.classList.remove('is-active');
          if (img) img.classList.remove('is-revealing');
          window.setTimeout(function () {
            if (!panel.classList.contains('is-active')) panel.hidden = true;
          }, 560);
        }
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activate(btn.getAttribute('data-cat-btn'), true);
      });
    });

    activate(buttons[0].getAttribute('data-cat-btn'), false);
  }

  document.addEventListener('DOMContentLoaded', function () {
    initBurger();
    initContactModal();
    initAllCarousels();
    initAdvantageReveal();
    initStatCounters();
    initLangSwitch();
    initMegaMenu();
    initHomeCatalog();
  });

  document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.target && evt.target.id === 'contact-modal-form-root') {
      if (evt.target.querySelector('.form-success')) {
        window.setTimeout(function () {
          var modal = document.getElementById('contact-modal');
          if (!modal || !modal.classList.contains('is-open')) return;
          modal.classList.remove('is-open');
          modal.setAttribute('aria-hidden', 'true');
          document.body.classList.remove('modal-open');
          window.setTimeout(function () {
            modal.setAttribute('hidden', '');
          }, 280);
        }, 2600);
      }
    }
  });
})();
