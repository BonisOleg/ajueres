(function () {
  function rowsRoot(node) {
    return node.closest('[data-requisites-rows]');
  }

  function sync(root) {
    var hidden = root.querySelector('[data-requisites-json]');
    if (!hidden) return;
    var items = root.querySelectorAll('[data-requisites-row]');
    var rows = [];
    items.forEach(function (item) {
      var label = item.querySelector('[data-requisites-label]');
      var value = item.querySelector('[data-requisites-value]');
      var labelText = label ? String(label.value || '').trim() : '';
      var valueText = value ? String(value.value || '').trim() : '';
      if (!labelText && !valueText) return;
      rows.push({ label: labelText, value: valueText });
    });
    hidden.value = JSON.stringify(rows);
  }

  function bindRoot(root) {
    if (!root || root.dataset.requisitesBound === '1') return;
    root.dataset.requisitesBound = '1';
    var list = root.querySelector('[data-requisites-list]');
    var tmpl = root.querySelector('[data-requisites-template]');
    var addBtn = root.querySelector('[data-requisites-add]');

    root.addEventListener('input', function () {
      sync(root);
    });

    root.addEventListener('click', function (event) {
      var removeBtn = event.target.closest('[data-requisites-remove]');
      if (removeBtn && root.contains(removeBtn)) {
        var row = removeBtn.closest('[data-requisites-row]');
        if (row) row.remove();
        sync(root);
        return;
      }
    });

    if (addBtn) {
      addBtn.addEventListener('click', function () {
        if (!tmpl || !list) return;
        var node = tmpl.content.cloneNode(true);
        list.appendChild(node);
        sync(root);
      });
    }

    var form = root.closest('form');
    if (form) {
      form.addEventListener('submit', function () {
        sync(root);
      });
    }
    sync(root);
  }

  function init(scope) {
    (scope || document).querySelectorAll('[data-requisites-rows]').forEach(bindRoot);
  }

  document.addEventListener('DOMContentLoaded', function () {
    init(document);
  });
})();
