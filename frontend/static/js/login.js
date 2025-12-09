// Espera a que todo el HTML esté cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.querySelector('.wrapper');
    const registerLinks = document.querySelectorAll('.register-link');
    const loginLinks = document.querySelectorAll('.login-link');
    registerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.add('active');
        });
    });
    loginLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.remove('active');
        });
    });
    var regForm = document.querySelector('.form-box.register form');
    if (regForm) {
        regForm.addEventListener('submit', function(e) {
            var telefono = regForm.querySelector('input[name="telefono"]');
            var telRegex = /^\d{10}$/;
            if (!telefono.value.trim() || !telRegex.test(telefono.value.trim())) {
                e.preventDefault();
                if (window.Swal) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Teléfono inválido',
                        text: 'El número de teléfono debe tener exactamente 10 dígitos.',
                        confirmButtonColor: '#e91e63',
                        timer: 2200,
                        background: '#fff0fa',
                        color: '#d63384'
                    });
                } else {
                    alert('El número de teléfono debe tener exactamente 10 dígitos.');
                }
                telefono.focus();
                return false;
            }
            var pass = regForm.querySelector('input[name="password"]');
            if (pass && pass.value.length < 6) {
                e.preventDefault();
                // Puedes usar SweetAlert si está disponible
                if (window.Swal) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Contraseña muy corta',
                        text: 'Tu contraseña es muy corta. Debe tener 6 caracteres o más.',
                        confirmButtonColor: '#e91e63',
                        timer: 2200,
                        background: '#fff0fa',
                        color: '#d63384'
                    });
                } else {
                    alert('La contraseña debe tener al menos 6 caracteres.');
                }
                pass.focus();
            }
        });
    }
});