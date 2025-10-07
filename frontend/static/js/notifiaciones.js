// warning de no guardar cambios
// error de no guardar cambios
// success de guardar cambios
// info de no guardar cambios

const si_guardado = () => {
    swal.fire({
        timer: 3000,
        timerProgressBar: true,
        icon: 'success',
        title: '¡GUARDADO!',
        text: 'Se guardaron los elementos',})
}

const not_guardado = () => {
    swal.fire({
        timer: 3000,
        timerProgressBar: true,
        icon: 'error',
        title: '¡ERROR!',
        text: 'No se guardaron los elementos',
    })
}