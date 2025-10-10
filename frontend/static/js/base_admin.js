// Tema oscuro/claro
document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        const toggleBtn = document.getElementById('toggleTheme');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
            }
        }
    }
});

const toggleThemeBtn = document.getElementById('toggleTheme');
if (toggleThemeBtn) {
    toggleThemeBtn.addEventListener('click', function () {
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
}

// Actualizar el nombre de usuario sugerido en el modal
const nombreInput = document.getElementById('id_nombre');
const nuevoUsername = document.getElementById('nuevoUsername');
if (nombreInput && nuevoUsername) {
    nombreInput.addEventListener('input', function () {
        var nuevo = this.value.replace(/\s+/g, '').toLowerCase();
        nuevoUsername.textContent = nuevo;
    });
}

// Mostrar modal y alertas con SweetAlert si corresponde
document.addEventListener('DOMContentLoaded', function () {
    if (typeof show_modal !== 'undefined' && show_modal) {
        var modal = new bootstrap.Modal(document.getElementById('updateUserModal'));
        modal.show();
        if (typeof update_error !== 'undefined' && update_error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: update_error,
                confirmButtonColor: '#3b82f6'
            });
        } else if (typeof update_success !== 'undefined' && update_success) {
            Swal.fire({
                icon: 'success',
                title: '¡Actualizado!',
                text: update_success,
                confirmButtonColor: '#3b82f6'
            });
        }
    }
});

// Gestión del contador de notificaciones
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