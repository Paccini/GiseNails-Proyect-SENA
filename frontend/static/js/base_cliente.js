(function () {

    /* ===============================
       APLICAR TEMA
    =============================== */

    // Aplica el modo oscuro/claro al body
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    /* ===============================
       ICONOS DEL BOTÓN
    =============================== */

    function ensureIcon(button, sizeClass = 'fs-5') {
        let icon = button.querySelector('i');
        if (!icon) {
            icon = document.createElement('i');
            button.insertBefore(icon, button.firstChild);
        }
        if (![...icon.classList].some(c => c.startsWith('fs-'))) {
            icon.classList.add(sizeClass);
        }
        return icon;
    }

    function updateButtonIcon(button, theme) {
        const icon = ensureIcon(button);

        // Resetear estilos previos
        icon.classList.remove('bi-moon', 'bi-sun', 'bi');

        icon.classList.add('bi');
        icon.classList.add(theme === 'dark' ? 'bi-sun' : 'bi-moon');

        button.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    }

    /* ===============================
       TEMA INICIAL
    =============================== */

    let savedTheme = null;

    try {
        savedTheme = localStorage.getItem('theme');
    } catch (e) {
        savedTheme = null;
    }

    if (!savedTheme) {
        savedTheme =
            window.matchMedia &&
            window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
    }

    applyTheme(savedTheme);

    /* ===============================
       ACTIVAR BOTONES AL CARGAR DOM
    =============================== */

    document.addEventListener('DOMContentLoaded', function () {
        const toggles = Array.from(
            document.querySelectorAll('#toggleTheme, [data-toggle-theme]')
        );

        if (!toggles.length) return;

        // Actualizar icono inicial
        toggles.forEach(btn => updateButtonIcon(btn, savedTheme));

        function toggleAction() {
            const current = document.body.classList.contains('dark-mode')
                ? 'dark'
                : 'light';

            const next = current === 'dark' ? 'light' : 'dark';

            // Guardar preferencia
            try {
                localStorage.setItem('theme', next);
            } catch (err) {}

            // Aplicar modo
            applyTheme(next);

            // Actualizar iconos
            toggles.forEach(b => updateButtonIcon(b, next));
        }

        // Añadir listeners
        toggles.forEach(btn => {
            if (!btn._themeBound) {
                btn.addEventListener('click', toggleAction);
                btn.addEventListener('keydown', function (ev) {
                    if (ev.key === 'Enter' || ev.key === ' ') {
                        ev.preventDefault();
                        toggleAction(ev);
                    }
                });
                btn._themeBound = true;
            }
        });
    });

})();
