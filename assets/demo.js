(function () {
  document.documentElement.classList.add('js');
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));
  var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
  function show(i, focus) {
    tabs.forEach(function (t, j) {
      var on = i === j;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      panels[j].hidden = !on;
    });
    if (focus) tabs[i].focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(i, false); });
    t.addEventListener('keydown', function (e) {
      var k = e.key, n = tabs.length;
      if (k === 'ArrowRight' || k === 'ArrowDown') { e.preventDefault(); show((i + 1) % n, true); }
      if (k === 'ArrowLeft' || k === 'ArrowUp') { e.preventDefault(); show((i - 1 + n) % n, true); }
      if (k === 'Home') { e.preventDefault(); show(0, true); }
      if (k === 'End') { e.preventDefault(); show(n - 1, true); }
    });
  });
  if (tabs.length) show(0, false);
  window.addEventListener('beforeprint', function () { panels.forEach(function (p) { p.hidden = false; }); });
  window.addEventListener('afterprint', function () {
    var i = tabs.findIndex(function (t) { return t.getAttribute('aria-selected') === 'true'; });
    show(i < 0 ? 0 : i, false);
  });
})();
