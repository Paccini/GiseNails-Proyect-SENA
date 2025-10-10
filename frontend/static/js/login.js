// Evitar el reenvío del formulario o navegación hacia atrás en la página de login
if (window.history && window.history.replaceState) {
    window.history.replaceState(null, '', window.location.href);
}

window.onload = function () {
    if (window.history && window.history.pushState) {
        window.history.pushState(null, '', window.location.href);
        window.onpopstate = function () {
            window.location.href = '/login/';
        }
    }
};