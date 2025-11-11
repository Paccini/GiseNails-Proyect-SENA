document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById('tipo-servicio');
    const serviciosContenedor = document.getElementById('servicios-contenedor');
    const serviciosDataElement = document.getElementById('servicios-data');
    const gestoraSelect = document.getElementById('gestora-select');
    const fechaSelect = document.getElementById('fecha-select');
    const horarioSelect = document.getElementById('horario-select');

    if (!tipoSelect || !serviciosContenedor || !serviciosDataElement || !gestoraSelect || !fechaSelect || !horarioSelect) {
        console.error("Algunos elementos necesarios no están presentes en el DOM.");
        return;
    }

    const serviciosPorCategoria = JSON.parse(serviciosDataElement.textContent || '{}');

    function mostrarServicios(tipo) {
        serviciosContenedor.innerHTML = '';
        if (serviciosPorCategoria[tipo]) {
            serviciosPorCategoria[tipo].forEach(servicio => {
                serviciosContenedor.innerHTML += `
                    <div class="servicio-card" tabindex="0" data-id="${servicio.id}">
                        <img src="${servicio.imagen}" alt="${servicio.nombre}" class="servicio-img">
                        <div class="servicio-nombre">${servicio.nombre}</div>
                        <div class="servicio-precio">$${servicio.precio}</div>
                    </div>
                `;
            });
            setTimeout(() => {
                const first = serviciosContenedor.querySelector('.servicio-card');
                const servicioInput = document.getElementById('servicio-input');
                if (first && servicioInput) {
                    first.classList.add('selected');
                    servicioInput.value = first.getAttribute('data-id');
                }
            }, 10);
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
                    data.horarios.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = item.hora;
                        horarioSelect.appendChild(option);
                    });
                });
        }
    }

    tipoSelect.addEventListener('change', function () {
        mostrarServicios(this.value);
        setTimeout(() => {
            document.querySelectorAll('.servicio-card').forEach(el => {
                el.style.display = '';
                el.classList.remove('selected');
            });
        }, 10);
    });

    gestoraSelect.addEventListener('change', cargarHorarios);
    fechaSelect.addEventListener('change', cargarHorarios);

    if (tipoSelect.value === "manicure") {
        mostrarServicios("manicure");
    }
});

// Selección automática del tipo de servicio al hacer clic en una tarjeta

document.addEventListener('DOMContentLoaded', function() {
    const serviciosContenedor = document.getElementById('servicios-contenedor');
    const selectServicio = document.getElementById('tipo-servicio');

    if (!serviciosContenedor || !selectServicio) {
        console.error("Elementos necesarios para la selección automática no están presentes en el DOM.");
        return;
    }

    serviciosContenedor.addEventListener('click', function(e) {
        const card = e.target.closest('.servicio-card');
        if (!card) return;
        document.querySelectorAll('.servicio-card.selected').forEach(el => el.classList.remove('selected'));
        card.classList.add('selected');
        const servicioId = card.getAttribute('data-id');
        const servicioInput = document.getElementById('servicio-input');
        if (servicioInput && servicioId) servicioInput.value = servicioId;
        document.querySelectorAll('.servicio-card').forEach(el => {
            if (el !== card) el.style.display = 'none';
        });
        const nombreServicio = card.querySelector('.servicio-nombre').textContent.trim().toLowerCase().replace(/\s+/g, '');
        for (let option of selectServicio.options) {
            const nombreOpcion = option.textContent.trim().toLowerCase().replace(/\s+/g, '');
            if (nombreOpcion === nombreServicio) {
                selectServicio.value = option.value;
                selectServicio.dispatchEvent(new Event('change'));
                break;
            }
        }
    });
});

