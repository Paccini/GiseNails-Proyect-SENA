// Script para permitir editar el correo si estaba bloqueado
document.addEventListener('DOMContentLoaded', function () {
    const link = document.getElementById('usar-otro-correo');
    if (!link) return;
    link.addEventListener('click', function (e) {
        e.preventDefault();
        // Busca el input del correo
        const emailInput = document.querySelector('input[name="correo"]');
        if (emailInput) {
            emailInput.removeAttribute('readonly');
            emailInput.focus();
            // Opcional: limpiar el valor del campo si se desea
            // emailInput.value = '';
        }
        link.style.display = 'none';
        // Oculta el enlace después de usarlo
    });
});