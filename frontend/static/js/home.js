document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('mobileToggle');
    const menu = document.getElementById('mobileMenu');
    const navLinks = document.getElementById('navLinks');

    if (!btn || !menu) return;

    // Toggle menú
    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        menu.classList.toggle('hidden');

        const isOpen = !menu.classList.contains('hidden');
        btn.setAttribute('aria-expanded', isOpen);
        menu.setAttribute('aria-hidden', !isOpen);
    });

    // Cerrar si se hace clic fuera
    document.addEventListener('click', function (e) {
        if (!menu.contains(e.target) && !btn.contains(e.target)) {
            menu.classList.add('hidden');
            btn.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-hidden', 'true');
        }
    });

    // Ajustar cuando cambia la resolución
    window.addEventListener('resize', () => {
        if (window.innerWidth > 992) {
            menu.classList.add('hidden');
            navLinks.style.display = "flex";
        } else {
            navLinks.style.display = "none";
        }
    });
});
