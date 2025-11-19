// static/js/empleado_theme.js
(function () {
  const STORAGE_KEY = 'theme'; // 'light' o 'dark'
  const BTN_ID = 'toggleTheme';
  const ICON_ID = 'themeIcon';
  const DARK_CLASS = 'dark-mode';
  const html = document.documentElement;
  const body = document.body;

  function applyTheme(theme) {
    if (theme === 'dark') {
      body.classList.add(DARK_CLASS);
      html.setAttribute('data-theme', 'dark');
    } else {
      body.classList.remove(DARK_CLASS);
      html.setAttribute('data-theme', 'light');
    }
    updateIcon(theme);
    updateAria(theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) { }
  }

  function updateIcon(theme) {
    const icon = document.getElementById(ICON_ID);
    if (!icon) return;
    // usar bi-moon-fill para modo claro (mostrar luna) y bi-sun-fill en oscuro (mostrar sol)
    if (theme === 'dark') {
      icon.classList.remove('bi-moon-fill', 'bi-moon', 'bi-moon-fill');
      icon.classList.add('bi-sun-fill');
    } else {
      icon.classList.remove('bi-sun-fill', 'bi-sun');
      icon.classList.add('bi-moon-fill');
    }
  }

  function updateAria(theme) {
    const btn = document.getElementById(BTN_ID);
    if (!btn) return;
    btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    btn.title = theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
  }

  function init() {
    const btn = document.getElementById(BTN_ID);
    // Intentar leer localStorage
    let saved = null;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) { saved = null; }

    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (saved === 'dark' || (!saved && prefersDark)) {
      applyTheme('dark');
    } else {
      applyTheme('light');
    }

    if (!btn) return;

    btn.addEventListener('click', function () {
      const current = body.classList.contains(DARK_CLASS) ? 'dark' : 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
