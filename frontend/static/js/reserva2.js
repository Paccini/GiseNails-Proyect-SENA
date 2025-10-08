// Selección automática del tipo de servicio al hacer clic en una tarjeta
document.addEventListener('DOMContentLoaded', function() {
	// Busca todas las tarjetas de servicio
	const servicioCards = document.querySelectorAll('.servicio-card');
	const selectServicio = document.getElementById('tipo-servicio');

	servicioCards.forEach(card => {
		card.addEventListener('click', function() {
			// Obtiene el nombre del servicio
			const nombreServicio = card.querySelector('h3').textContent.trim().toLowerCase();
			// Busca la opción en el select y la selecciona
			for (let option of selectServicio.options) {
				if (option.textContent.trim().toLowerCase() === nombreServicio) {
					selectServicio.value = option.value;
					break;
				}
			}
		});
	});
});

// Manejo del envío del formulario de reserva vía AJAX
document.addEventListener('DOMContentLoaded', function() {
	const form = document.querySelector('.form-section form');
	if (!form) return;
	form.addEventListener('submit', function(e) {
		e.preventDefault();
		// Validación básica antes de enviar
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
				// si success verdadero, si backend devolvió next o solo éxito
				if (data.next) {
					window.location.href = data.next;
				} else {
					// mostrar mensaje o redirigir a confirmación
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
