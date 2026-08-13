(function () {
  try {
    var stored = localStorage.getItem('adminTheme');
    if (stored === null || stored === '"auto"' || stored === 'auto') {
      localStorage.setItem('adminTheme', JSON.stringify('light'));
    }
  } catch (err) {
    /* private mode / blocked storage */
  }
})();
