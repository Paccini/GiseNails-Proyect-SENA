// Espera a que todo el HTML esté cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", () => {

  // Selecciona los elementos que SÍ existen
  const wrapper = document.querySelector(".wrapper");
  const loginLink = document.querySelector(".login-link");
  const registerLink = document.querySelector(".register-link");

  // Revisa que los elementos existan antes de añadirles eventos
  if (registerLink) {
    registerLink.addEventListener("click", (e) => {
      e.preventDefault(); // Evita que la página salte por el href="#"
      wrapper.classList.add("active");
    });
  }

  if (loginLink) {
    loginLink.addEventListener("click", (e) => {
      e.preventDefault(); // Evita que la página salte por el href="#"
      wrapper.classList.remove("active");
    });
  }

  // El código para 'btnPopup' se elimina porque ese botón no está en tu HTML
  // y estaba causando que todo el script fallara.

});