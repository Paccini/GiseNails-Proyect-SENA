// Espera a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    // Obtiene el contexto del canvas para el gráfico
    const ctx = document.getElementById('graficoCitas').getContext('2d');
    // Obtiene los datos globales definidos en el template
    const meses = window.graficoCitasMeses || [];
    const datos = window.graficoCitasDatos || [];

    // Inicializa el gráfico de líneas con Chart.js
    const graficoCitas = new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses,
            datasets: [{
                label: 'Citas realizadas por mes',
                data: datos,
                fill: true,
                borderColor: '#3b82f6',
                borderWidth: 3,
                backgroundColor: 'rgba(59,130,246,0.2)',
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
});