// Confirmación al cancelar una cita usando SweetAlert2
document.addEventListener('DOMContentLoaded', function () {
    // Mostrar alerta solo una vez por sesión de login
    if (typeof show_cita_alert !== 'undefined' && show_cita_alert) {
        if (!sessionStorage.getItem('cita_alert_shown')) {
            Swal.fire({
                icon: 'info',
                title: '¡Importante!',
                text: '⚠️ Tu cita debe confirmarse con al menos 1 hora de anticipación. De no hacerlo, será cancelada automáticamente. ¡Gracias por tu puntualidad!.',
                timer: 7000,
                timerProgressBar: true,
                showCloseButton: true,
                confirmButtonText: 'Entendido',
                allowOutsideClick: false,
                allowEscapeKey: true
            });
            sessionStorage.setItem('cita_alert_shown', '1');
        }
    }

    // Borra la alerta al cerrar sesión
    var logoutForm = document.querySelector('form[action*="logout"]');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function () {
            sessionStorage.removeItem('cita_alert_shown');
        });
    }

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

    // Confirmación al confirmar cita
    document.querySelectorAll('.confirmar-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            Swal.fire({
                title: '¿Estás seguro que quieres confirmar la cita?',
                html: 'Recuerda que tienes que abonar un <b>30%</b> de la cita para poder que quede agendada.<br><br>Si en dado caso la cita se confirma y <b>NO</b> se llega a asistir, será cancelada y <b>no se devolverá el depósito</b>.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#198754',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, confirmar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    btn.closest('form').submit();
                }
            });
        });
    });

    // Cargar horas disponibles en el modal de agendar cita
    var fechaInput = document.getElementById('id_fecha');
    if (fechaInput) {
        fechaInput.addEventListener('change', function() {
            const fecha = fechaInput.value;
            const horaSelect = document.getElementById('id_hora');
            if (fecha) {
                fetch(`/reserva/horarios-disponibles/?fecha=${fecha}`)
                    .then(response => response.json())
                    .then(data => {
                        horaSelect.innerHTML = '<option value="">Seleccione una hora</option>';
                        data.horarios.forEach(function(h) {
                            const opt = document.createElement('option');
                            opt.value = h.id;
                            opt.textContent = h.hora;
                            horaSelect.appendChild(opt);
                        });
                    });
            } else {
                horaSelect.innerHTML = '<option value="">Seleccione una hora</option>';
            }
        });
    }

    // Mostrar el modal y alertas si corresponde (variables inyectadas por Django)
    if (typeof show_modal !== 'undefined' && show_modal) {
        var modalEl = document.getElementById('updateClienteModal');
        var modal = new bootstrap.Modal(modalEl);
        modal.show();

        // Si hay error: mostrar alerta tipo toast/auto-cierre y dejar el modal abierto
        if (typeof update_error !== 'undefined' && update_error) {
            console.log('panel_cliente: show_modal=', show_modal, 'update_error=', update_error);
            var errorTimer = 4000;
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: update_error,
                timer: errorTimer,
                timerProgressBar: true,
                showConfirmButton: false,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
            // Forzar cierre por si queda con botón OK en algunas condiciones
            setTimeout(function() {
                try { Swal.close(); } catch(e) { console.warn('Swal.close error', e); }
            }, errorTimer + 250);
            // Asegurar que el mensaje dentro del modal (si existe) sea visible
            var inlineAlert = modalEl.querySelector('.alert.alert-danger');
            if (inlineAlert) inlineAlert.style.display = 'block';

            // Enfocar el primer campo con error (si existe)
            var firstErrorInput = modalEl.querySelector('.is-invalid, .alert');
            if (firstErrorInput) firstErrorInput.scrollIntoView({behavior: 'smooth', block: 'center'});

        } else if (typeof update_success !== 'undefined' && update_success) {
            // En caso de éxito: cerrar modal y mostrar alerta de éxito que desaparece sola
            modal.hide();
            Swal.fire({
                icon: 'success',
                title: '¡Actualizado!',
                text: update_success,
                timer: 3500,
                timerProgressBar: true,
                showConfirmButton: false,
                allowOutsideClick: true,
                allowEscapeKey: true
            }).then(function () {
                // Recargar la página para reflejar los cambios
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

    // Eliminar notificación al hacer clic en la X (campanita)
    document.querySelectorAll('.notif-close-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const notifDiv = btn.closest('[data-notif-id]');
            const notifId = notifDiv.getAttribute('data-notif-id');
            notifDiv.style.display = 'none';
            // Guardar como eliminada en localStorage
            let eliminadas = JSON.parse(localStorage.getItem('notificaciones_eliminadas') || '[]');
            if (!eliminadas.includes(notifId)) {
                eliminadas.push(notifId);
                localStorage.setItem('notificaciones_eliminadas', JSON.stringify(eliminadas));
            }
            // Ocultar badge si ya no quedan notificaciones visibles
            const visibles = Array.from(document.querySelectorAll('[data-notif-id]')).filter(el => el.style.display !== 'none');
            const badge = document.querySelector('#notifDropdown .badge');
            if (badge && visibles.length === 0) badge.style.display = 'none';
        });
    });

    // Al cargar, ocultar las notificaciones eliminadas
    let eliminadas = JSON.parse(localStorage.getItem('notificaciones_eliminadas') || '[]');
    document.querySelectorAll('[data-notif-id]').forEach(function(el) {
        if (eliminadas.includes(el.getAttribute('data-notif-id'))) {
            el.style.display = 'none';
        }
    });

    // Enviar los eliminados al backend en cada carga del panel
    if (eliminadas.length > 0) {
        const url = new URL(window.location.href);
        url.searchParams.set('notifs_eliminadas', eliminadas.join(','));
        if (!window.location.search.includes('notifs_eliminadas=')) {
            window.location.replace(url.toString());
        }
    }

    // Limpia eliminados al cerrar sesión
    var logoutForm = document.querySelector('form[action*="logout"]');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function () {
            localStorage.removeItem('notificaciones_eliminadas');
        });
    }
});