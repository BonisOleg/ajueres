(function () {
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

  function hsvToHex(h, s, v) {
    var c = v * s;
    var x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    var m = v - c;
    var r = 0;
    var g = 0;
    var b = 0;
    if (h < 60) {
      r = c;
      g = x;
    } else if (h < 120) {
      r = x;
      g = c;
    } else if (h < 180) {
      g = c;
      b = x;
    } else if (h < 240) {
      g = x;
      b = c;
    } else if (h < 300) {
      r = x;
      b = c;
    } else {
      r = c;
      b = x;
    }
    function toHex(n) {
      var out = Math.round((n + m) * 255).toString(16);
      return out.length === 1 ? "0" + out : out;
    }
    return "#" + toHex(r) + toHex(g) + toHex(b);
  }

  function hexToHsv(hex) {
    var raw = normalize(hex);
    if (!raw) return { h: 18, s: 0.8, v: 1 };
    var r = parseInt(raw.slice(1, 3), 16) / 255;
    var g = parseInt(raw.slice(3, 5), 16) / 255;
    var b = parseInt(raw.slice(5, 7), 16) / 255;
    var max = Math.max(r, g, b);
    var min = Math.min(r, g, b);
    var d = max - min;
    var h = 0;
    if (d !== 0) {
      if (max === r) h = ((g - b) / d) % 6;
      else if (max === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    return { h: h, s: max === 0 ? 0 : d / max, v: max };
  }

  function syncPair(root) {
    var picker = root.querySelector("[data-hex-color-picker]");
    var text = root.querySelector("input[type='text'], input:not([type='color']):not([type='range'])");
    var wheel = root.querySelector("[data-hex-color-wheel]");
    var knob = root.querySelector("[data-hex-color-knob]");
    var valueSlider = root.querySelector("[data-hex-color-value]");
    if (!picker || !text) return;

    var hsv = hexToHsv(text.value || picker.value);

    function applyHex(hex, fromText) {
      var clean = normalize(hex);
      if (!clean) return;
      picker.value = clean;
      hsv = hexToHsv(clean);
      if (valueSlider) valueSlider.value = String(Math.round(hsv.v * 100));
      placeKnob();
      if (!fromText) {
        text.value = clean;
        text.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }

    function placeKnob() {
      if (!wheel || !knob) return;
      var radius = wheel.clientWidth / 2;
      var dist = hsv.s * (radius - 8);
      var rad = (hsv.h * Math.PI) / 180;
      knob.style.left = radius + Math.cos(rad) * dist + "px";
      knob.style.top = radius + Math.sin(rad) * dist + "px";
    }

    function pickFromPointer(event) {
      if (!wheel) return;
      var rect = wheel.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top + rect.height / 2;
      var dx = event.clientX - cx;
      var dy = event.clientY - cy;
      var hue = (Math.atan2(dy, dx) * 180) / Math.PI;
      if (hue < 0) hue += 360;
      var sat = Math.min(1, Math.hypot(dx, dy) / (rect.width / 2 - 4));
      hsv.h = hue;
      hsv.s = sat;
      applyHex(hsvToHex(hsv.h, hsv.s, hsv.v), false);
    }

    picker.addEventListener("input", function () {
      applyHex(picker.value, false);
    });

    text.addEventListener("input", function () {
      var hex = normalize(text.value);
      if (hex) applyHex(hex, true);
    });

    if (valueSlider) {
      valueSlider.addEventListener("input", function () {
        hsv.v = Math.max(0.08, Number(valueSlider.value) / 100);
        applyHex(hsvToHex(hsv.h, hsv.s, hsv.v), false);
      });
    }

    if (wheel) {
      var dragging = false;
      wheel.addEventListener("pointerdown", function (event) {
        dragging = true;
        wheel.setPointerCapture(event.pointerId);
        pickFromPointer(event);
      });
      wheel.addEventListener("pointermove", function (event) {
        if (dragging) pickFromPointer(event);
      });
      wheel.addEventListener("pointerup", function () {
        dragging = false;
      });
      wheel.addEventListener("pointercancel", function () {
        dragging = false;
      });
    }

    var initial = normalize(text.value) || normalize(picker.value) || "#ff5a36";
    applyHex(initial, Boolean(normalize(text.value)));
  }

  function boot(scope) {
    (scope || document).querySelectorAll(".hex-color-input").forEach(syncPair);
  }

  document.addEventListener("DOMContentLoaded", function () {
    boot(document);
  });
})();
