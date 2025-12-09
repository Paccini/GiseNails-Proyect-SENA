// Mostrar modal de éxito de reserva si corresponde
document.addEventListener('DOMContentLoaded', function(){
    const params = new URLSearchParams(window.location.search);
    if(params.get('success') === '1'){
        const modal = document.getElementById('reserva-success-modal');
        modal.setAttribute('aria-hidden','false');
        // quitar el parámetro ?success=1 de la URL (sin recargar)
        const url = new URL(window.location);
        url.searchParams.delete('success');
        window.history.replaceState({}, document.title, url.toString());
        // botón cerrar
        document.getElementById('reserva-success-close').addEventListener('click', function(){
            modal.setAttribute('aria-hidden','true');
        });
        // cerrar click fuera de la tarjeta
        modal.addEventListener('click', function(e){
            if(e.target === modal){
                modal.setAttribute('aria-hidden','true');
            }
        });
    }
});

// Manejo del envío del formulario de reserva vía AJAX
document.addEventListener('DOMContentLoaded', function() {
    // --- Modal y selección de servicios ---
    const serviciosData = JSON.parse(document.getElementById('servicios-data').textContent || '{}');
    const contenedor = document.getElementById('servicios-contenedor');
    const tipoSelect = document.getElementById('tipo-servicio');
    const servicioInput = document.getElementById('servicio-input');

    const resumen = document.getElementById('resumen-servicio');
    const resumenImg = document.getElementById('resumen-img');
    const resumenNombre = document.getElementById('resumen-nombre');
    const resumenPrecio = document.getElementById('resumen-precio');
    const resumenCategoria = document.getElementById('resumen-categoria');

    let currentCategory = '';

    function createCardElement(s) {
        const card = document.createElement('div');
        card.className = 'modal-servicio-card';
        card.innerHTML = `
            <img src="${s.imagen}" alt="${s.nombre}" />
            <div class="m-nombre">${s.nombre}</div>
            <div class="m-precio">$${s.precio}</div>
        `;
        return card;
    }

    // modal elements
    const modal = document.getElementById('modal-servicios');
    const modalList = document.getElementById('modal-servicios-list');
    const modalTitle = document.getElementById('modal-title');
    const modalClose = document.getElementById('modal-close');
    const modalCancel = document.getElementById('modal-cancel');

    function selectServicio(s) {
        servicioInput.value = s.id;
        resumenImg.src = s.imagen;
        resumenImg.alt = s.nombre;
        resumenNombre.textContent = s.nombre;
        resumenPrecio.textContent = `$${s.precio}`;
        resumenCategoria.textContent = (currentCategory || '').charAt(0).toUpperCase() + (currentCategory || '').slice(1);
        resumen.hidden = false;

        // Mostrar botón de cambiar servicio debajo del resumen
        let changeWrap = document.getElementById('change-wrap');
        if (!changeWrap) {
            changeWrap = document.createElement('div');
            changeWrap.id = 'change-wrap';
            changeWrap.className = 'change-wrap';
            resumen.parentNode.appendChild(changeWrap);
        }
        changeWrap.innerHTML = '';
        const changeBtn = document.createElement('button');
        changeBtn.type = 'button';
        changeBtn.className = 'btn-change';
        changeBtn.textContent = 'Cambiar servicio';
        changeBtn.onclick = function() {
            // Limpiar el campo oculto y el resumen antes de abrir el modal
            if (servicioInput) servicioInput.value = '';
            if (resumen) resumen.hidden = true;
            openModalForCategory(currentCategory);
        };
        changeWrap.appendChild(changeBtn);

        // Enfocar el primer campo del formulario
        setTimeout(() => {
            const firstInput = document.querySelector('.reserva-form input:not([type=hidden]), .reserva-form select');
            if (firstInput) firstInput.focus();
        }, 300);
    }

    function openModalForCategory(categoria){
        const lista = serviciosData[categoria] || [];
        modalTitle.textContent = categoria ? categoria.charAt(0).toUpperCase()+categoria.slice(1) : 'Servicios';
        modalList.innerHTML = '';
        if(!Array.isArray(lista) || lista.length === 0){
            modalList.innerHTML = '<p class="no-servicios">No hay servicios en esta categoría.</p>';
        } else {
            lista.forEach(s => {
                const card = document.createElement('div');
                card.className = 'servicio-card';
                card.style.cursor = 'pointer';
                card.innerHTML = `
                    <img src="${s.imagen}" alt="${s.nombre}" class="servicio-img"/>
                    <div class="servicio-body">
                        <div class="servicio-nombre">${s.nombre}</div>
                        <div class="servicio-precio">$${s.precio}</div>
                    </div>
                `;
                card.onclick = function() {
                    // Quitar selección previa
                    modalList.querySelectorAll('.servicio-card.selected').forEach(el => el.classList.remove('selected'));
                    card.classList.add('selected');
                    selectServicio(s);
                    closeModal();
                    // Enfocar el formulario para continuar
                    setTimeout(() => {
                        document.querySelector('.reserva-form input, .reserva-form select').focus();
                    }, 300);
                };
                modalList.appendChild(card);
                
            });
        }
        modal.setAttribute('aria-hidden','false');
        currentCategory = categoria;
    }

    function closeModal(){ modal.setAttribute('aria-hidden','true'); }

    modalClose.addEventListener('click', closeModal);
    modalCancel.addEventListener('click', function() {
        modal.setAttribute('aria-hidden', 'true');
        Swal.fire({
            icon: 'warning',
            title: 'Selecciona un servicio',
            text: 'Debes seleccionar un servicio para continuar con tu reserva.',
            confirmButtonColor: '#e91e63',
            background: '#fff0fa',
            color: '#d63384',
            timer: 2500,
            timerProgressBar: true,
            didClose: () => {
                // Al cerrar la alerta, limpiar los campos
                tipoSelect.value = '';
                servicioInput.value = '';
                resumen.hidden = true;
            }
        });
    });
    modal.addEventListener('click', function(e){ if(e.target === modal) closeModal(); });

    tipoSelect.addEventListener('change', function(){
        const cat = this.value;
        if(!cat) return;
        openModalForCategory(cat);
        servicioInput.value='';
        resumen.hidden = true;
    });

    // --- Envío de formulario AJAX ---
    const form = document.querySelector('.form-section form');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        let errores = [];

        // Validar nombre
        const nombre = form.querySelector('input[name="nombre"]');
        if (!nombre.value.trim()) {
            errores.push('El nombre es obligatorio.');
        }

        // Validar correo
        const correo = form.querySelector('input[name="correo"]');
        const correoRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!correo.value.trim()) {
            errores.push('El correo es obligatorio.');
        } else if (!correoRegex.test(correo.value.trim())) {
            errores.push('El correo no es válido.');
        }

        // Validar teléfono (10 dígitos)
        const telefono = form.querySelector('input[name="telefono"]');
        const telRegex = /^\d{10}$/;
        if (!telefono.value.trim()) {
            errores.push('El teléfono es obligatorio.');
        } else if (!telRegex.test(telefono.value.trim())) {
            errores.push('El teléfono debe tener 10 dígitos.');
        }

        // Validar gestora
        const gestora = form.querySelector('select[name="gestora"]');
        if (!gestora.value.trim()) {
            errores.push('Selecciona una gestora.');
        }

        // Validar categoría de servicio
        const tipoServicio = form.querySelector('select[name="tipo_servicio"]');
        if (!tipoServicio.value.trim()) {
            errores.push('Selecciona una categoría de servicio.');
        }

        // Validar fecha
        const fecha = form.querySelector('input[name="fecha"]');
        if (!fecha.value.trim()) {
            errores.push('Selecciona una fecha.');
        }

        // Validar horario
        const horario = form.querySelector('select[name="hora"]');
        if (!horario.value.trim()) {
            errores.push('Selecciona un horario.');
        }

        // Validar servicio (campo oculto)
        const servicio = form.querySelector('input[name="servicio"]');
        if (!servicio.value.trim()) {
            // Solo alerta personalizada si es el único error
            if (errores.length === 0) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Selecciona un servicio',
                    text: 'Debes seleccionar un servicio para continuar con tu reserva.',
                    confirmButtonColor: '#e91e63',
                    background: '#fff0fa',
                    color: '#d63384'
                });
                return false;
            } else {
                errores.push('Selecciona un servicio.');
            }
        }

        if (errores.length > 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Datos inválidos',
                html: errores.join('<br>'),
                confirmButtonColor: '#e91e63',
                background: '#fff0fa',
                color: '#d63384',
                timer: 3000, // 3 segundos
                timerProgressBar: true
            });
            return false;
        }

        // Si todo está bien, enviar datos al backend
        const formData = new FormData(form);
        fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.next) {
                window.location.href = data.next;
            } else if (data.error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error,
                    confirmButtonColor: '#e91e63'
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo procesar la reserva.',
                    confirmButtonColor: '#e91e63'
                });
            }
        })
        .catch(err => {
            console.error(err);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error de red al intentar crear la reserva.',
                confirmButtonColor: '#e91e63'
            });
        });
    });

    // --- Actualización dinámica de horarios ---
    const gestoraSelect = document.getElementById('gestora-select');
    const fechaInput = document.getElementById('fecha-select');
    const horarioSelect = document.getElementById('horario-select');

    function cargarHorariosDisponibles() {
        if (!gestoraSelect || !fechaInput || !horarioSelect) return;
        const gestoraId = gestoraSelect.value;
        const fecha = fechaInput.value;
        // Deshabilitar y mostrar opción de carga
        horarioSelect.innerHTML = '<option>Cargando...</option>';
        horarioSelect.disabled = true;
        if (!gestoraId || !fecha) {
            horarioSelect.innerHTML = '<option value="">Seleccione gestora y fecha</option>';
            horarioSelect.disabled = true;
            return;
        }
        fetch(`/reserva/horarios-disponibles/?gestora_id=${gestoraId}&fecha=${fecha}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(data => {
            horarioSelect.innerHTML = '';
            if (data.error) {
                horarioSelect.innerHTML = `<option value="">${data.error}</option>`;
                horarioSelect.disabled = true;
                return;
            }
            const horarios = Array.isArray(data.horarios) ? data.horarios : [];
            if (horarios.length > 0) {
                horarios.forEach(h => {
                    const opt = document.createElement('option');
                    opt.value = h.id;
                    opt.textContent = h.hora;
                    if (h.disabled) {
                        opt.disabled = true;
                        opt.style.opacity = '0.5'; // visualmente "apagado"
                    }
                    horarioSelect.appendChild(opt);
                });
                horarioSelect.disabled = false;
            } else {
                horarioSelect.innerHTML = '<option value="">No hay horarios disponibles</option>';
                horarioSelect.disabled = true;
            }
        })
        .catch(err => {
            horarioSelect.innerHTML = '<option value="">Error al cargar horarios</option>';
            horarioSelect.disabled = true;
        });
    }

    if (gestoraSelect && fechaInput) {
        gestoraSelect.addEventListener('change', cargarHorariosDisponibles);
        fechaInput.addEventListener('change', cargarHorariosDisponibles);
    }

    // Marcar campos llenos con clase 'filled'
    function marcarCamposLlenos() {
        document.querySelectorAll('.reserva-form input, .reserva-form select').forEach(function(el) {
            if (el.value && el.value.trim() !== '') {
                el.classList.add('filled');
            } else {
                el.classList.remove('filled');
            }
        });
    }
    document.querySelectorAll('.reserva-form input, .reserva-form select').forEach(function(el) {
        el.addEventListener('input', marcarCamposLlenos);
        el.addEventListener('change', marcarCamposLlenos);
    });
    // Ejecutar al cargar
    marcarCamposLlenos();

    const params = new URLSearchParams(window.location.search);
    const servicioId = params.get('servicio');

    if (servicioId) {
        const serviciosData = JSON.parse(document.getElementById('servicios-data').textContent || '{}');
        let servicioSeleccionado = null;

        // Buscar el servicio por ID en los datos
        Object.keys(serviciosData).forEach(categoria => {
            const servicios = serviciosData[categoria];
            const servicio = servicios.find(s => s.id === servicioId);
            if (servicio) {
                servicioSeleccionado = servicio;
                currentCategory = categoria;
            }
        });

        if (servicioSeleccionado) {
            selectServicio(servicioSeleccionado);

            // Mostrar la categoría en el formulario
            const categoriaSelect = document.getElementById('tipo-servicio');
            if (categoriaSelect) {
                categoriaSelect.value = currentCategory;
            }
        }
    }

    function clearSelectedService() {
        const servicioInput = document.getElementById('servicio-input');
        const resumen = document.getElementById('resumen-servicio');

        if (servicioInput) servicioInput.value = '';
        if (resumen) resumen.hidden = true;
    }

    // Agregar evento al botón de selección de servicio
    const selectServiceButton = document.getElementById('select-service-button');
    if (selectServiceButton) {
        selectServiceButton.addEventListener('click', clearSelectedService);
    }
});