window.addEventListener("load", () => {
  // 🔒 Bloquear scroll al cargar
  document.body.style.overflow = "hidden";

  const svgG = document.querySelector("#svg-g");
  const text = document.querySelector(".welcome-text");

  // animación del trazo
  gsap.to(svgG, { strokeDashoffset: 0, duration: 2, ease: "power2.out" });

  // mostrar texto
  gsap.to(text, { opacity: 1, delay: 2.2, duration: 1 });

  // desvanecer pantalla de carga
  gsap.to(".loading-page", {
    opacity: 0,
    delay: 4,
    duration: 1,
    onComplete: () => {
      // ocultar pantalla de carga
      document.querySelector(".loading-page").style.display = "none";

      // 🔓 Habilitar scroll nuevamente
      document.body.style.overflow = "auto";
    }
  });
});
