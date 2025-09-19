// Horarios de ejemplo


function seleccionarBtnFecha(btnId) {
    document.querySelectorAll('.btn-fecha').forEach(b => b.classList.remove('selected'));
    document.getElementById(btnId).classList.add('selected');
}

function getFechaISO(date) {
    // Devuelve la fecha en formato YYYY-MM-DD
    return date.toISOString().split('T')[0];
}

// Botones de fecha
document.getElementById('btn-hoy').onclick = function () {
    seleccionarBtnFecha('btn-hoy');
    document.getElementById('fecha-input').style.display = '';
    document.getElementById('fecha-calendario').style.display = 'none';
    let hoy = new Date();
    let fechaISO = getFechaISO(hoy);
    document.getElementById('fecha-input').value = fechaISO;
    cargarHorariosDisponibles(fechaISO);
};
document.getElementById('btn-manana').onclick = function () {
    seleccionarBtnFecha('btn-manana');
    document.getElementById('fecha-input').style.display = '';
    document.getElementById('fecha-calendario').style.display = 'none';
    let manana = new Date();
    manana.setDate(manana.getDate() + 1);
    let fechaISO = getFechaISO(manana);
    document.getElementById('fecha-input').value = fechaISO;
    cargarHorariosDisponibles(fechaISO);
};
document.getElementById('btn-otra').onclick = function () {
    seleccionarBtnFecha('btn-otra');
    document.getElementById('fecha-input').style.display = 'none';
    document.getElementById('fecha-calendario').style.display = '';
    document.getElementById('horarios-disponibles').innerHTML = '';
};
document.getElementById('fecha-calendario').onchange = function () {
    let fecha = this.value;
    cargarHorariosDisponibles(fecha);
};

// Cambiar PERSONA 1 por el nombre
document.getElementById('input-nombre').addEventListener('input', function () {
    let nombre = this.value.trim();
    document.getElementById('persona-nombre').innerText = nombre ? nombre : 'PERSONA 1';
});

// Validación al continuar
document.getElementById('btn-continuar').onclick = function (e) {
    let nombre = document.getElementById('input-nombre').value.trim();
    let apellido = document.getElementById('input-apellido').value.trim();
    let celular = document.getElementById('input-celular').value.trim();
    let horarioSeleccionado = document.querySelector('.horarios-btn.selected');
    let fecha = document.getElementById('fecha-input').style.display !== 'none'
        ? document.getElementById('fecha-input').value
        : document.getElementById('fecha-calendario').value;

    if (!nombre || !apellido || !celular || !fecha || !horarioSeleccionado) {
        document.getElementById('alerta-mensaje').innerText = "Debes diligenciar todos los campos de las personas a reservar y seleccionar un horario.";
        document.getElementById('alerta-modal').style.display = 'flex';
        return false;
    }
    // Aquí puedes enviar el formulario o redirigir
    alert("¡Reserva lista para " + nombre + "!");
};

function cargarHorariosDisponibles(fecha) {
    fetch(`/reserva/horarios-disponibles/?fecha=${fecha}`)
        .then(response => response.json())
        .then(data => {
            const contenedor = document.getElementById('horarios-disponibles');
            contenedor.innerHTML = '';
            if (data.horarios && data.horarios.length > 0) {
                data.horarios.forEach(hora => {
                    const btn = document.createElement('button');
                    btn.className = 'horarios-btn';
                    btn.textContent = hora;
                    contenedor.appendChild(btn);
                });
            } else {
                contenedor.innerHTML = '<div class="alert alert-warning mt-2">No hay horarios disponibles para esta fecha.</div>';
            }
        });
}

// Ejemplo: llama esta función cuando el usuario seleccione una fecha
document.getElementById('fecha-input').addEventListener('change', function () {
    cargarHorariosDisponibles(this.value);
});