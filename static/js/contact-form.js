/**
 * Contact form: Uzbek phone mask, client validation, HTMX submit UX.
 */
(function () {
  'use strict';

  var EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
  var BOUND = 'data-contact-bound';

  function digitsOnly(value) {
    return String(value || '').replace(/\D/g, '');
  }

  function formatUzPhone(raw) {
    var digits = digitsOnly(raw);
    if (digits.indexOf('998') === 0) {
      digits = digits.slice(0, 12);
    } else if (digits.length) {
      digits = ('998' + digits).slice(0, 12);
    } else {
      return '';
    }

    var local = digits.slice(3);
    var out = '+998';
    if (local.length > 0) {
      out += ' (' + local.slice(0, Math.min(2, local.length));
    }
    if (local.length >= 2) {
      out += ')';
    }
    if (local.length > 2) {
      out += ' ' + local.slice(2, Math.min(5, local.length));
    }
    if (local.length > 5) {
      out += '-' + local.slice(5, Math.min(7, local.length));
    }
    if (local.length > 7) {
      out += '-' + local.slice(7, Math.min(9, local.length));
    }
    return out;
  }

  function isLetter(ch) {
    try {
      return /^\p{L}$/u.test(ch);
    } catch (err) {
      return ch.toLowerCase() !== ch.toUpperCase();
    }
  }

  function isValidName(value) {
    var name = String(value || '').trim();
    if (name.length < 2) return false;
    var hasLetter = false;
    for (var i = 0; i < name.length; i += 1) {
      var ch = name.charAt(i);
      if (ch === ' ' || ch === '-') continue;
      if (/\d/.test(ch) || !isLetter(ch)) return false;
      hasLetter = true;
    }
    return hasLetter;
  }

  function isValidPhone(value) {
    var digits = digitsOnly(value);
    return digits.length === 12 && digits.indexOf('998') === 0;
  }

  function isValidEmail(value) {
    return EMAIL_RE.test(String(value || '').trim());
  }

  function isValidPurpose(value) {
    return String(value || '').trim().length >= 5;
  }

  function msg(form, key) {
    return form.getAttribute('data-msg-' + key) || '';
  }

  function errorEl(form, field) {
    return form.querySelector('[data-error-for="' + field + '"]');
  }

  function fieldEl(form, field) {
    return form.querySelector('[data-field="' + field + '"]');
  }

  function clearError(form, field) {
    var input = fieldEl(form, field);
    var err = errorEl(form, field);
    if (input) {
      input.classList.remove('is-invalid');
      input.setAttribute('aria-invalid', 'false');
    }
    if (err) {
      err.textContent = '';
      err.hidden = true;
    }
  }

  function setError(form, field, text) {
    var input = fieldEl(form, field);
    var err = errorEl(form, field);
    if (input) {
      input.classList.add('is-invalid');
      input.setAttribute('aria-invalid', 'true');
    }
    if (err) {
      err.textContent = text || '';
      err.hidden = !text;
    }
  }

  function validateField(form, field) {
    var input = fieldEl(form, field);
    if (!input) return true;
    var value = input.value;
    var ok = true;
    var text = '';

    if (field === 'purpose') {
      ok = isValidPurpose(value);
      text = msg(form, 'purpose');
    } else if (field === 'name') {
      ok = isValidName(value);
      text = msg(form, 'name');
    } else if (field === 'phone') {
      ok = isValidPhone(value);
      text = msg(form, 'phone');
    } else if (field === 'email') {
      ok = isValidEmail(value);
      text = msg(form, 'email');
    }

    if (ok) {
      clearError(form, field);
      return true;
    }
    setError(form, field, text);
    return false;
  }

  function validateAll(form) {
    var fields = ['purpose', 'name', 'phone', 'email'];
    var firstInvalid = null;
    var ok = true;
    fields.forEach(function (field) {
      if (!validateField(form, field)) {
        ok = false;
        if (!firstInvalid) firstInvalid = fieldEl(form, field);
      }
    });
    return { ok: ok, firstInvalid: firstInvalid };
  }

  function setLoading(form, loading) {
    var btn = form.querySelector('.form__submit');
    if (!btn) return;
    var spinner = btn.querySelector('.form__submit-spinner');
    var icon = btn.querySelector('.form__submit-icon');
    btn.disabled = !!loading;
    btn.classList.toggle('is-loading', !!loading);
    btn.setAttribute('aria-busy', loading ? 'true' : 'false');
    if (spinner) spinner.hidden = !loading;
    if (icon) icon.hidden = !!loading;
  }

  function bindPhoneMask(input) {
    if (!input || input.getAttribute('data-mask-bound')) return;
    input.setAttribute('data-mask-bound', '1');

    input.addEventListener('focus', function () {
      if (!digitsOnly(input.value)) {
        input.value = '+998 ';
      }
    });

    input.addEventListener('keydown', function (evt) {
      var allow =
        evt.key === 'Backspace' ||
        evt.key === 'Delete' ||
        evt.key === 'Tab' ||
        evt.key === 'Escape' ||
        evt.key === 'Enter' ||
        evt.key === 'ArrowLeft' ||
        evt.key === 'ArrowRight' ||
        evt.key === 'Home' ||
        evt.key === 'End' ||
        evt.ctrlKey ||
        evt.metaKey ||
        evt.altKey;
      if (allow) return;
      if (!/^\d$/.test(evt.key)) {
        evt.preventDefault();
      }
    });

    input.addEventListener('input', function () {
      var formatted = formatUzPhone(input.value);
      if (input.value !== formatted) {
        input.value = formatted;
      }
    });

    input.addEventListener('paste', function (evt) {
      evt.preventDefault();
      var clip = evt.clipboardData || window.clipboardData;
      var text = '';
      try {
        text = clip && typeof clip.getData === 'function' ? clip.getData('text') : '';
      } catch (_err) {
        text = '';
      }
      input.value = formatUzPhone(text || '');
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }

  function bindForm(form) {
    if (!form || form.getAttribute(BOUND)) return;
    form.setAttribute(BOUND, '1');

    var phone = form.querySelector('[data-phone-mask]');
    if (phone) {
      bindPhoneMask(phone);
      if (phone.value) {
        phone.value = formatUzPhone(phone.value);
      }
    }

    ['purpose', 'name', 'phone', 'email'].forEach(function (field) {
      var input = fieldEl(form, field);
      if (!input) return;

      input.addEventListener('input', function () {
        clearError(form, field);
      });
      input.addEventListener('change', function () {
        clearError(form, field);
      });
      input.addEventListener('blur', function () {
        validateField(form, field);
      });
    });

    form.addEventListener(
      'submit',
      function (evt) {
        var result = validateAll(form);
        if (result.ok) return;
        evt.preventDefault();
        evt.stopPropagation();
        if (typeof evt.stopImmediatePropagation === 'function') {
          evt.stopImmediatePropagation();
        }
        if (result.firstInvalid) {
          result.firstInvalid.focus({ preventScroll: false });
          if (typeof result.firstInvalid.scrollIntoView === 'function') {
            result.firstInvalid.scrollIntoView({
              behavior: 'smooth',
              block: 'center',
            });
          }
        }
      },
      true
    );

    form.addEventListener('htmx:beforeRequest', function () {
      setLoading(form, true);
    });
    form.addEventListener('htmx:afterRequest', function () {
      setLoading(form, false);
    });
    form.addEventListener('htmx:responseError', function () {
      setLoading(form, false);
    });
    form.addEventListener('htmx:sendError', function () {
      setLoading(form, false);
    });
  }

  function initAll(root) {
    var scope = root || document;
    var forms = [];
    if (scope.matches && scope.matches('form[data-contact-form]')) {
      forms.push(scope);
    }
    if (scope.querySelectorAll) {
      scope.querySelectorAll('form[data-contact-form]').forEach(function (form) {
        forms.push(form);
      });
    }
    forms.forEach(bindForm);
  }

  document.addEventListener('DOMContentLoaded', function () {
    initAll(document);
  });

  document.body.addEventListener('htmx:beforeSwap', function (evt) {
    var xhr = evt.detail && evt.detail.xhr;
    var target = evt.detail && evt.detail.target;
    if (!xhr || !target) return;
    var status = xhr.status;
    if (status !== 400 && status !== 429) return;
    if (target.id === 'contact-modal-form-root' || target.id === 'contact-form-root') {
      evt.detail.shouldSwap = true;
      evt.detail.isError = false;
    }
  });

  document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (!evt.target) return;
    initAll(evt.target);
  });

  window.AJERES_initContactForms = initAll;
})();
