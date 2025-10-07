// Abre el modal manualmente
function abrirModal() {
    const modal = document.getElementById('modal');
    if (modal) modal.style.display = 'block';
}

// Cierra el modal manualmente
function cerrarModal() {
    const modal = document.getElementById('modal');
    if (modal) modal.style.display = 'none';
}

// Cierra el modal si se hace clic fuera de él
window.onclick = function (event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Abre el modal automáticamente si hubo errores (lo llamaremos desde Django)
function abrirModalSiErrores() {
    const modal = document.getElementById('modal');
    if (modal) modal.style.display = 'block', not_guardado() ;
}

// Cierra el modal si todo fue correcto (sin errores)
function cerrarModalSiExito() {

    
    const modal = document.getElementById('modal');
    if (modal) modal.style.display = 'none' , si_guardado();
        
}
