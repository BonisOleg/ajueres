(function () {
  function activate(root, code) {
    root.querySelectorAll("[data-cms-lang-tab]").forEach(function (btn) {
      var active = btn.getAttribute("data-cms-lang-tab") === code;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", active ? "true" : "false");
    });
    root.querySelectorAll("[data-cms-lang-panel]").forEach(function (panel) {
      var active = panel.getAttribute("data-cms-lang-panel") === code;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  }

  function boot(root) {
    root.querySelectorAll("[data-cms-lang-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activate(root, btn.getAttribute("data-cms-lang-tab"));
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-cms-lang-root]").forEach(boot);
  });
})();
