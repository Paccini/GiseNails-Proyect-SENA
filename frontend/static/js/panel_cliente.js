// Confirmación al cancelar una cita usando SweetAlert2
document.addEventListener('DOMContentLoaded', function () {
    // Botón cancelar cita
    const botonesCancelar = document.querySelectorAll('.btn-cancelar-cita');
    botonesCancelar.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const servicio = this.getAttribute('data-servicio') || 'la cita';
            Swal.fire({
                title: '¿Cancelar cita?',
                text: `¿Estás seguro de cancelar ${servicio}?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, cancelar',
                cancelButtonText: 'No'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = url;
                }
            });
        });
    });

    // Mostrar el modal y alertas si corresponde (variables inyectadas por Django)
    if (typeof show_modal !== 'undefined' && show_modal) {
        var modal = new bootstrap.Modal(document.getElementById('updateClienteModal'));
        modal.show();

        if (typeof update_error !== 'undefined' && update_error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: update_error,
                confirmButtonColor: '#3b82f6',
                allowOutsideClick: false,
                allowEscapeKey: false
            }).then(function () {
                modal.hide();
            });
        } else if (typeof update_success !== 'undefined' && update_success) {
            Swal.fire({
                icon: 'success',
                title: '¡Actualizado!',
                text: update_success,
                confirmButtonColor: '#3b82f6',
                allowOutsideClick: false,
                allowEscapeKey: false
            }).then(function () {
                modal.hide();
                window.location.href = panel_url || window.location.href;
            });
        }
    }

    // Ocultar el contador de notificaciones al abrir el dropdown y guardar las vistas
    var notifDropdown = document.getElementById('notifDropdown');
    if (notifDropdown) {
        notifDropdown.addEventListener('show.bs.dropdown', function () {
            var badge = notifDropdown.querySelector('.badge');
            if (badge) {
                badge.style.display = 'none';
            }
            // Guardar los IDs de notificaciones vistas
            var notifs = document.querySelectorAll('[data-notif-id]');
            var vistos = JSON.parse(localStorage.getItem('notificaciones_vistas') || '[]');
            notifs.forEach(function (el) {
                var id = el.getAttribute('data-notif-id');
                if (vistos.indexOf(id) === -1) {
                    vistos.push(id);
                }
            });
            localStorage.setItem('notificaciones_vistas', JSON.stringify(vistos));
        });

        // Al cargar, ocultar las notificaciones ya vistas
        var vistos = JSON.parse(localStorage.getItem('notificaciones_vistas') || '[]');
        var notifs = document.querySelectorAll('[data-notif-id]');
        var nuevas = 0;
        notifs.forEach(function (el) {
            var id = el.getAttribute('data-notif-id');
            if (vistos.indexOf(id) !== -1) {
                el.style.display = 'none';
            } else {
                nuevas++;
            }
        });
        // Oculta el badge si no hay nuevas
        var badge = notifDropdown.querySelector('.badge');
        if (badge && nuevas === 0) {
            badge.style.display = 'none';
        }
    }
});