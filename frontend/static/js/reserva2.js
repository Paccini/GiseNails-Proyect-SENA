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
// Eliminado código de selección automática duplicado

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
	// Cancelar debe cerrar el modal y limpiar la selección de categoría/servicio
	// MODIFICADO: Solo mostrar advertencia personalizada al cancelar si no hay servicio
	// Eliminar declaración duplicada, warningJustShown ya está definida arriba
	modalCancel.addEventListener('click', function() {
		// Cierra el modal al cancelar
		modal.setAttribute('aria-hidden', 'true');
		// Limpia la selección del servicio
		servicioInput.value = '';
		resumen.hidden = true;
		// Si tienes un botón de cambiar servicio, también lo puedes ocultar
		let changeWrap = document.getElementById('change-wrap');
		if (changeWrap) changeWrap.innerHTML = '';
	});
	modal.addEventListener('click', function(e){ if(e.target === modal) closeModal(); });

	
	tipoSelect.addEventListener('change', function(){
		const cat = this.value;
		if(!cat) return;
		openModalForCategory(cat);
		servicioInput.value='';
		resumen.hidden = true;
	});

	// No mostrar servicios fuera del modal al cargar

	// --- Envío de formulario AJAX ---
	const form = document.querySelector('.form-section form');
	if (!form) return;
	form.addEventListener('submit', function(e) {
		e.preventDefault();

		// Validar campos requeridos
		const missing = new Set();
		const requiredFields = form.querySelectorAll('input[required], select[required]');
		requiredFields.forEach(function(field) {
			if (!field.value || field.value.trim() === '') {
				let label = '';
				const labelEl = form.querySelector('label[for="' + field.id + '"]');
				if (labelEl) {
					label = labelEl.textContent.trim();
				} else if (field.name) {
					label = field.name;
				}
				missing.add(label || field.id || 'campo');
			}
		});

		// Validar el campo oculto servicio
		const servicioVal = form.querySelector('input[name="servicio"]') ? form.querySelector('input[name="servicio"]').value : null;
		if (!servicioVal) missing.add('servicio');

		// Validar el select de horario
		const horaVal = form.querySelector('#horario-select') ? form.querySelector('#horario-select').value : null;
		if (!horaVal) missing.add('horario');

		if (missing.size) {
			const msg = 'Falta: ' + Array.from(missing).join(', ') + '. Por favor completa antes de continuar.';
			// Mostrar modal de validación si existe, si no usar alert() como fallback
			const validationModal = document.getElementById('validation-modal');
			const validationMsg = document.getElementById('validation-message');
			if (validationModal && validationMsg) {
				validationMsg.textContent = msg;
				validationModal.setAttribute('aria-hidden', 'false');
				const okBtn = document.getElementById('validation-ok');
				const closeValidation = () => validationModal.setAttribute('aria-hidden', 'true');
				// cerrar al hacer click en Aceptar
				if (okBtn) {
					okBtn.addEventListener('click', closeValidation, { once: true });
				}
				// cerrar al click fuera del panel
				validationModal.addEventListener('click', function(e){ if (e.target === validationModal) closeValidation(); }, { once: true });
			} else {
				alert(msg);
			}
			return;
		}

		// Enviar datos al backend
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
				alert('Error: ' + data.error);
			} else {
				alert('No se pudo procesar la reserva.');
			}
		})
		.catch(err => {
			console.error(err);
			alert('Error de red al intentar crear la reserva.');
		});
	});

	const modalCancelBtn = document.getElementById('modal-cancel');
	const modalServicios = document.getElementById('modal-servicios');
	const warningModal = document.getElementById('warning-modal');
	const warningMessage = document.getElementById('warning-message');
	const warningOkBtn = document.getElementById('warning-ok');

	let warningJustShown = false;

	if (modalCancelBtn && modalServicios && warningModal && warningMessage && warningOkBtn) {
		modalCancelBtn.addEventListener('click', function() {
			const servicioInput = document.getElementById('servicio-input');
			if (!servicioInput || !servicioInput.value) {
				// Mostrar solo la alerta personalizada y evitar que el formulario lance la validación general
				warningMessage.textContent = 'Por favor selecciona un servicio para continuar con tu reserva.';
				warningModal.setAttribute('aria-hidden', 'false');
				warningOkBtn.onclick = function() {
					warningModal.setAttribute('aria-hidden', 'true');
					// Limpiar la categoría de servicio después de la alerta
					if (tipoSelect) {
						tipoSelect.value = '';
					}
				};
				warningJustShown = true;
				return true;
			}
			modalServicios.setAttribute('aria-hidden', 'true');
		});
	}

	form.addEventListener('submit', function(e) {
		e.preventDefault();

		// Validar campos requeridos
		const missing = new Set();
		const requiredFields = form.querySelectorAll('input[required], select[required]');
		requiredFields.forEach(function(field) {
			if (!field.value || field.value.trim() === '') {
				let label = '';
				const labelEl = form.querySelector('label[for="' + field.id + '"]');
				if (labelEl) {
					label = labelEl.textContent.trim();
				} else if (field.name) {
					label = field.name;
				}
				missing.add(label || field.id || 'campo');
			}
		});

		// Validar el campo oculto servicio
		const servicioVal = form.querySelector('input[name="servicio"]') ? form.querySelector('input[name="servicio"]').value : null;
		if (!servicioVal) missing.add('servicio');

		// Validar el select de horario
		const horaVal = form.querySelector('#horario-select') ? form.querySelector('#horario-select').value : null;
		if (!horaVal) missing.add('horario');

		if (missing.size) {
			const msg = 'Falta: ' + Array.from(missing).join(', ') + '. Por favor completa antes de continuar.';
			// Mostrar modal de validación si existe, si no usar alert() como fallback
			const validationModal = document.getElementById('validation-modal');
			const validationMsg = document.getElementById('validation-message');
			if (validationModal && validationMsg) {
				validationMsg.textContent = msg;
				validationModal.setAttribute('aria-hidden', 'false');
				const okBtn = document.getElementById('validation-ok');
				const closeValidation = () => validationModal.setAttribute('aria-hidden', 'true');
				// cerrar al hacer click en Aceptar
				if (okBtn) {
					okBtn.addEventListener('click', closeValidation, { once: true });
				}
				// cerrar al click fuera del panel
				validationModal.addEventListener('click', function(e){ if (e.target === validationModal) closeValidation(); }, { once: true });
			} else {
				alert(msg);
			}
			return;
		}

		// Enviar datos al backend
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
			if (data.success) {
				if (data.next) {
					window.location.href = data.next;
				} else {
					window.location.href = window.location.pathname + '?success=1';
				}
			} else if (data.need && data.next) {
				window.location.href = data.next;
			} else if (data.next) {
				window.location.href = data.next;
			} else {
				alert('Error: ' + (data.error || 'No se pudo procesar la reserva'));
			}
		})
		.catch(err => {
			console.error(err);
			alert('Error de red al intentar crear la reserva.');
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
            // --- CORRECCIÓN: leer data.horarios y mostrar error si existe ---
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
});
