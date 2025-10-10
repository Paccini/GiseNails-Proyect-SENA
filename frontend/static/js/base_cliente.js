// Tema oscuro/claro
document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('toggleTheme').querySelector('i').classList.remove('bi-moon');
        document.getElementById('toggleTheme').querySelector('i').classList.add('bi-sun');
    }
});

document.getElementById('toggleTheme').addEventListener('click', function () {
    document.body.classList.toggle('dark-mode');
    const icon = this.querySelector('i');
    if (document.body.classList.contains('dark-mode')) {
        icon.classList.remove('bi-moon');
        icon.classList.add('bi-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        icon.classList.remove('bi-sun');
        icon.classList.add('bi-moon');
        localStorage.setItem('theme', 'light');
    }
});

// Script para gestionar notificaciones
document.addEventListener('DOMContentLoaded', function () {
    var notifDropdown = document.getElementById('notifDropdown');
    var notifBadge = notifDropdown ? notifDropdown.querySelector('.badge') : null;

    function clearNotifBadge() {
        if (notifBadge) {
            notifBadge.style.display = 'none';
            sessionStorage.setItem('notificaciones_vistas', 'true');
            window.dispatchEvent(new Event('notificaciones_vistas'));
        }
    }

    if (notifDropdown) {
        notifDropdown.addEventListener('show.bs.dropdown', clearNotifBadge);
        notifDropdown.addEventListener('hide.bs.dropdown', clearNotifBadge);
    }

    if (sessionStorage.getItem('notificaciones_vistas') === 'true') {
        if (notifBadge) notifBadge.style.display = 'none';
    }

    window.addEventListener('notificaciones_vistas', function () {
        if (notifBadge) notifBadge.style.display = 'none';
    });
});