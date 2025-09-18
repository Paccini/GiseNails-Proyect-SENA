// Horarios de ejemplo
const horariosHoy = ["09:00", "10:00", "11:00", "14:00", "16:00"];
const horariosManana = ["10:00", "12:00", "15:00", "17:00"];

function mostrarHorarios(horarios) {
    const cont = document.getElementById('horarios-disponibles');
    cont.innerHTML = '';
    horarios.forEach(hora => {
        const btn = document.createElement('button');
        btn.className = 'horarios-btn';
        btn.innerText = hora;
        btn.onclick = function () {
            document.querySelectorAll('.horarios-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
        };
        cont.appendChild(btn);
    });
}

function seleccionarBtnFecha(btnId) {
    document.querySelectorAll('.btn-fecha').forEach(b => b.classList.remove('selected'));
    document.getElementById(btnId).classList.add('selected');
}

// Botones de fecha
document.getElementById('btn-hoy').onclick = function () {
    seleccionarBtnFecha('btn-hoy');
    document.getElementById('fecha-input').style.display = '';
    document.getElementById('fecha-calendario').style.display = 'none';
    document.getElementById('fecha-input').value = new Date().toLocaleDateString('es-CO');
    mostrarHorarios(horariosHoy);
};
document.getElementById('btn-manana').onclick = function () {
    seleccionarBtnFecha('btn-manana');
    document.getElementById('fecha-input').style.display = '';
    document.getElementById('fecha-calendario').style.display = 'none';
    let manana = new Date();
    manana.setDate(manana.getDate() + 1);
    document.getElementById('fecha-input').value = manana.toLocaleDateString('es-CO');
    mostrarHorarios(horariosManana);
};
document.getElementById('btn-otra').onclick = function () {
    seleccionarBtnFecha('btn-otra');
    document.getElementById('fecha-input').style.display = 'none';
    document.getElementById('fecha-calendario').style.display = '';
    document.getElementById('horarios-disponibles').innerHTML = '';
};
document.getElementById('fecha-calendario').onchange = function () {
    // Puedes cambiar los horarios según la fecha seleccionada
    mostrarHorarios(["09:00", "11:00", "13:00", "15:00"]);
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