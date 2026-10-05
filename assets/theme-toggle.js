(function () {
  var root = document.documentElement;
  var btn = document.getElementById('themeToggle');
  var stored = null;
  try { stored = localStorage.getItem('rodado-theme'); } catch (e) { /* no-op */ }

  function effectiveTheme() {
    return stored || 'light';
  }

  // a barra do navegador no celular acompanha o fundo do tema escolhido
  function applyThemeColor(theme) {
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.name = 'theme-color';
      document.head.appendChild(meta);
    }
    meta.content = theme === 'dark' ? '#13161b' : '#f9f8f5';
  }

  function applyIcon(theme) {
    applyThemeColor(theme);
    if (!btn) return;
    btn.innerHTML = theme === 'dark'
      ? '<i class="fa-solid fa-lightbulb"></i>'
      : '<i class="fa-solid fa-moon"></i>';
  }

  if (stored) root.setAttribute('data-theme', stored);
  applyIcon(effectiveTheme());

  if (btn) {
    btn.addEventListener('click', function () {
      var next = effectiveTheme() === 'dark' ? 'light' : 'dark';
      stored = next;
      try { localStorage.setItem('rodado-theme', next); } catch (e) { /* no-op */ }
      root.setAttribute('data-theme', next);
      applyIcon(next);
    });
  }
})();
