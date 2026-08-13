(function () {
  var DEFAULT_START = "#ff7a52";
  var DEFAULT_END = "#db3f1c";
  var DEFAULT_MID = "#ff5a36";

  function formValue(form, name) {
    var field = form.querySelector('[name="' + name + '"]');
    return field ? String(field.value || "").trim() : "";
  }

  function cssBackground(data) {
    if (data.fill_type === "solid") {
      return data.solid_color || DEFAULT_MID;
    }
    var start = data.gradient_start || DEFAULT_START;
    var end = data.gradient_end || DEFAULT_END;
    var angle = data.gradient_angle || "145";
    if (start.toLowerCase() === DEFAULT_START && end.toLowerCase() === DEFAULT_END) {
      return (
        "linear-gradient(" +
        angle +
        "deg, " +
        start +
        " 0%, " +
        DEFAULT_MID +
        " 48%, " +
        end +
        " 100%)"
      );
    }
    return "linear-gradient(" + angle + "deg, " + start + " 0%, " + end + " 100%)";
  }

  function readDraft(form, role) {
    return {
      role: role,
      fill_type: formValue(form, "fill_type") || "gradient",
      solid_color: formValue(form, "solid_color"),
      gradient_start: formValue(form, "gradient_start"),
      gradient_end: formValue(form, "gradient_end"),
      gradient_angle: formValue(form, "gradient_angle") || "145",
    };
  }

  function updateSample(root, form) {
    var sample = root.querySelector("[data-button-preview-sample]");
    if (!sample) return;
    var draft = readDraft(form, root.getAttribute("data-role") || "");
    sample.style.background = cssBackground(draft);
    sample.classList.toggle(
      "button-style-preview__btn--ghost",
      draft.role === "secondary" && draft.fill_type === "solid"
    );
  }

  function openSitePreview(root, form) {
    var home = root.getAttribute("data-site-home-url") || "/";
    var draft = readDraft(form, root.getAttribute("data-role") || "");
    var params = new URLSearchParams();
    params.set("btn_preview", "1");
    Object.keys(draft).forEach(function (key) {
      if (draft[key]) params.set(key, draft[key]);
    });
    var join = home.indexOf("?") >= 0 ? "&" : "?";
    window.open(home + join + params.toString(), "_blank", "noopener");
  }

  function boot() {
    var root = document.querySelector("[data-button-preview-root]");
    var form = document.getElementById("sitebuttonstyle_form");
    if (!root || !form) return;

    function refresh() {
      updateSample(root, form);
    }

    form.addEventListener("input", refresh);
    form.addEventListener("change", refresh);
    refresh();

    document.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-button-preview]");
      if (!trigger) return;
      event.preventDefault();
      openSitePreview(root, form);
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
