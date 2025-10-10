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
		card.className = 'servicio-card';
		card.innerHTML = `
			<img src="${s.imagen}" alt="${s.nombre}" class="servicio-img"/>
			<div class="servicio-body">
				<div class="servicio-nombre">${s.nombre}</div>
				<div class="servicio-precio">$${s.precio}</div>
			</div>
		`;
		return card;
	}

	// modal elements
	const modal = document.getElementById('modal-servicios');
	const modalList = document.getElementById('modal-servicios-list');
	const modalTitle = document.getElementById('modal-title');
	const modalClose = document.getElementById('modal-close');
	const modalCancel = document.getElementById('modal-cancel');

	function openModalForCategory(categoria){
		const lista = serviciosData[categoria] || [];
		modalTitle.textContent = categoria ? categoria.charAt(0).toUpperCase()+categoria.slice(1) : 'Servicios';
		modalList.innerHTML = '';
		if(!Array.isArray(lista) || lista.length === 0){
			modalList.innerHTML = '<p class="no-servicios">No hay servicios en esta categoría.</p>';
		} else {
			lista.forEach(s => {
				const card = document.createElement('div');
				card.className = 'modal-servicio-card';
				card.innerHTML = `<img src="${s.imagen}" alt="${s.nombre}"/><div class="m-nombre">${s.nombre}</div><div class="m-precio">$${s.precio}</div>`;
				card.addEventListener('click', () => {
					selectServicio(s);
					closeModal();
				});
				modalList.appendChild(card);
			});
		}
		modal.setAttribute('aria-hidden','false');
		currentCategory = categoria;
	}

	function closeModal(){ modal.setAttribute('aria-hidden','true'); }

	modalClose.addEventListener('click', closeModal);
	modalCancel.addEventListener('click', closeModal);
	modal.addEventListener('click', function(e){ if(e.target === modal) closeModal(); });

	function selectServicio(s) {
		servicioInput.value = s.id;
		resumenImg.src = s.imagen;
		resumenImg.alt = s.nombre;
		resumenNombre.textContent = s.nombre;
		resumenPrecio.textContent = `$${s.precio}`;
		resumenCategoria.textContent = (currentCategory || '').charAt(0).toUpperCase() + (currentCategory || '').slice(1);
		resumen.hidden = false;

		contenedor.innerHTML = '';
		const changeWrap = document.createElement('div');
		changeWrap.className = 'change-wrap';
		const changeBtn = document.createElement('button');
		changeBtn.type = 'button';
		changeBtn.className = 'btn-change';
		changeBtn.textContent = 'Cambiar servicio';
		changeBtn.addEventListener('click', () => {
			openModalForCategory(currentCategory);
			resumen.hidden = true;
		});
		changeWrap.appendChild(changeBtn);
		contenedor.appendChild(changeWrap);
	}

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
		const servicioVal = form.querySelector('input[name="servicio"]') ? form.querySelector('input[name="servicio"]').value : null;
		const horaVal = form.querySelector('#horario-select') ? form.querySelector('#horario-select').value : null;
		const missing = [];
		if (!servicioVal) missing.push('servicio');
		if (!horaVal) missing.push('horario');
		if (missing.length) {
			alert('Falta: ' + missing.join(', ') + '. Por favor completa antes de continuar.');
			return;
		}
		const formData = new FormData(form);
		fetch(window.location.pathname, {
			method: 'POST',
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			},
			body: formData
		}).then(r => r.json()).then(data => {
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
		}).catch(err => {
			console.error(err);
			alert('Error de red al intentar crear la reserva.');
		});
	});
});
