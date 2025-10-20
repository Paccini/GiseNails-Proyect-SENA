window.addEventListener("load", () => {
  // 🔒 Bloquear scroll al cargar
  document.body.style.overflow = "hidden";

  const svgG = document.querySelector("#svg-g");
  const text = document.querySelector(".welcome-text");

  // animación del trazo -> duración reducida (era 2s)
  gsap.to(svgG, { strokeDashoffset: 0, duration: 2, ease: "power2.out" });

  // mostrar texto -> delay y duración reducidos (era delay:2.2 dur:1)
  gsap.to(text, { opacity: 1, delay: 0.9, duration: 0.4 });

  // desvanecer pantalla de carga -> delay y duración reducidos (era delay:4 dur:1)
  gsap.to(".loading-page", {
    opacity: 0,
    delay: 1.6,
    duration: 0.5,
    onComplete: () => {
      // ocultar pantalla de carga
      document.querySelector(".loading-page").style.display = "none";

      // 🔓 Habilitar scroll nuevamente
      document.body.style.overflow = "auto";
    }
  });
});
