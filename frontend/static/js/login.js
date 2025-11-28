// Espera a que todo el HTML esté cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.querySelector('.wrapper');
    const registerLink = document.getElementById('register-link');
    const loginLink = document.querySelector('.login-link');
    if (registerLink) {
        registerLink.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.add('active');
        });
    }
    if (loginLink) {
        loginLink.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.remove('active');
        });
    }
});