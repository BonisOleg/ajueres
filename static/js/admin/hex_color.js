(function () {
  function syncPair(root) {
    var picker = root.querySelector("[data-hex-color-picker]");
    var text = root.querySelector("input[type='text'], input:not([type='color'])");
    if (!picker || !text) return;

    function normalize(value) {
      var v = (value || "").trim();
      if (/^#[0-9a-fA-F]{6}$/.test(v)) return v.toLowerCase();
      if (/^#[0-9a-fA-F]{3}$/.test(v)) {
        return (
          "#" +
          v
            .slice(1)
            .split("")
            .map(function (ch) {
              return ch + ch;
            })
            .join("")
            .toLowerCase()
        );
      }
      return "";
    }

    picker.addEventListener("input", function () {
      text.value = picker.value;
      text.dispatchEvent(new Event("change", { bubbles: true }));
    });

    text.addEventListener("input", function () {
      var hex = normalize(text.value);
      if (hex) picker.value = hex;
    });

    var initial = normalize(text.value);
    if (initial) picker.value = initial;
  }

  function boot(scope) {
    (scope || document).querySelectorAll(".hex-color-input").forEach(syncPair);
  }

  document.addEventListener("DOMContentLoaded", function () {
    boot(document);
  });
})();
