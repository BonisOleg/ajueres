(function () {
  var LANGS = ['ru', 'uz', 'en'];
  var STORAGE_KEY = 'ajeresAdminLang';
  var MT_CLASS = /\bmt-field-(.+)-(ru|uz|en)\b/;

  function preferredLang() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (LANGS.indexOf(stored) !== -1) return stored;
    } catch (err) {
      /* private mode */
    }
    return 'ru';
  }

  function storeLang(code) {
    try {
      localStorage.setItem(STORAGE_KEY, code);
    } catch (err) {
      /* private mode */
    }
  }

  function cleanLabel(text) {
    return String(text || '')
      .replace(/\s*\[[^\]]+\]\s*$/, '')
      .replace(/\s*\((?:ru|uz|en)\)\s*$/i, '')
      .trim();
  }

  function activateRoot(root, code) {
    root.querySelectorAll('[data-admin-lang-tab], [data-cms-lang-tab]').forEach(function (btn) {
      var active = btn.getAttribute('data-admin-lang-tab') === code
        || btn.getAttribute('data-cms-lang-tab') === code;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    root.querySelectorAll('[data-admin-lang-panel], [data-cms-lang-panel]').forEach(function (panel) {
      var active = panel.getAttribute('data-admin-lang-panel') === code
        || panel.getAttribute('data-cms-lang-panel') === code;
      panel.classList.toggle('is-active', active);
      panel.hidden = !active;
    });
  }

  function activateAll(code) {
    document.querySelectorAll('[data-admin-lang-root], [data-cms-lang-root]').forEach(function (root) {
      activateRoot(root, code);
    });
    storeLang(code);
  }

  function rowForWidget(el) {
    var grow = el.closest('.grow');
    if (grow && grow.parentElement) {
      var line = grow.parentElement;
      var row = line.parentElement;
      if (row && row.children && row.children.length === 1) return row;
      return line;
    }
    return el.closest('.form-field') || el.closest('.form-row') || el.parentElement;
  }

  function parseMt(el) {
    var cls = el.className || '';
    var match = String(cls).match(MT_CLASS);
    if (!match) return null;
    return { name: match[1], lang: match[2], el: el };
  }

  function makeTabs(langs, current) {
    var wrap = document.createElement('div');
    wrap.className = 'admin-lang-tabs';
    wrap.setAttribute('role', 'tablist');
    wrap.setAttribute('aria-label', 'Языки');
    langs.forEach(function (lang) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'admin-lang-tabs__btn' + (lang === current ? ' is-active' : '');
      btn.setAttribute('data-admin-lang-tab', lang);
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-selected', lang === current ? 'true' : 'false');
      btn.textContent = lang;
      wrap.appendChild(btn);
    });
    return wrap;
  }

  function groupModeltranslation() {
    var items = [];
    document.querySelectorAll('[class*="mt-field-"]').forEach(function (el) {
      var parsed = parseMt(el);
      if (!parsed) return;
      var row = rowForWidget(el);
      if (!row || row.dataset.adminLangBound === '1') return;
      items.push({ parsed: parsed, row: row });
    });
    var groups = {};
    items.forEach(function (item) {
      var key = item.parsed.name + '::' + (item.row.parentElement ? item.row.parentElement.id : '');
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });
    var current = preferredLang();
    Object.keys(groups).forEach(function (key) {
      var group = groups[key];
      if (group.length < 2) return;
      var first = group[0].row;
      var parent = first.parentElement;
      if (!parent) return;
      var shell = document.createElement('div');
      shell.className = 'admin-lang-field';
      shell.setAttribute('data-admin-lang-root', '');
      var bar = document.createElement('div');
      bar.className = 'admin-lang-field__bar';
      var title = document.createElement('span');
      title.className = 'admin-lang-field__title';
      var label = first.querySelector('label');
      title.textContent = cleanLabel(label ? label.textContent : '');
      bar.appendChild(title);
      var langs = group.map(function (item) { return item.parsed.lang; });
      bar.appendChild(makeTabs(langs, current));
      shell.appendChild(bar);
      parent.insertBefore(shell, first);
      group.forEach(function (item) {
        var panel = document.createElement('div');
        panel.setAttribute('data-admin-lang-panel', item.parsed.lang);
        panel.hidden = item.parsed.lang !== current;
        item.row.dataset.adminLangBound = '1';
        var rowLabel = item.row.querySelector('label');
        if (rowLabel) rowLabel.hidden = true;
        panel.appendChild(item.row);
        shell.appendChild(panel);
      });
    });
  }

  function bindClicks() {
    document.addEventListener('click', function (event) {
      var btn = event.target.closest('[data-admin-lang-tab], [data-cms-lang-tab]');
      if (!btn) return;
      event.preventDefault();
      var code = btn.getAttribute('data-admin-lang-tab') || btn.getAttribute('data-cms-lang-tab');
      if (code) activateAll(code);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    groupModeltranslation();
    activateAll(preferredLang());
    bindClicks();
  });
})();
