// filepath: c:\Users\nioco\OneDrive - SENA\Documentos\GiseNails-Proyect-SENA\frontend\static\js\servicios.js
document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById('tipo-servicio');
    const serviciosContenedor = document.getElementById('servicios-contenedor');
    const serviciosPorCategoria = JSON.parse(document.getElementById('servicios-data').textContent);
    const gestoraSelect = document.getElementById('gestora-select');
    const fechaSelect = document.getElementById('fecha-select');
    const horarioSelect = document.getElementById('horario-select');

    function mostrarServicios(tipo) {
        serviciosContenedor.innerHTML = '';
        if (serviciosPorCategoria[tipo]) {
            serviciosPorCategoria[tipo].forEach(servicio => {
                serviciosContenedor.innerHTML += `
                    <div class="servicio-card">
                        <img src="${servicio.imagen}" alt="${servicio.nombre}" class="servicio-img">
                        <div class="servicio-nombre">${servicio.nombre}</div>
                        <div class="servicio-precio">$${servicio.precio}</div>
                    </div>
                `;
            });
        }
    }

    function cargarHorarios() {
        const gestoraId = gestoraSelect.value;
        const fecha = fechaSelect.value;
        horarioSelect.innerHTML = '<option value="">Selecciona horario</option>';
        if (gestoraId && fecha) {
            fetch(`/reserva/horarios-disponibles/?gestora_id=${gestoraId}&fecha=${fecha}`)
                .then(response => response.json())
                .then(data => {
                    data.horarios.forEach(hora => {
                        const option = document.createElement('option');
                        option.value = hora;
                        option.textContent = hora;
                        horarioSelect.appendChild(option);
                    });
                });
        }
    }

    tipoSelect.addEventListener('change', function () {
        mostrarServicios(this.value);
    });

    gestoraSelect.addEventListener('change', cargarHorarios);
    fechaSelect.addEventListener('change', cargarHorarios);

    // Mostrar los servicios de manicure al cargar si está seleccionado
    if (tipoSelect.value === "manicure") {
        mostrarServicios("manicure");
    }
});


