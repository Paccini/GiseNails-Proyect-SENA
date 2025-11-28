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
});