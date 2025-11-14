document.addEventListener('DOMContentLoaded', function () {

    const ctx = document.getElementById('graficoCitas').getContext('2d');
    const meses = window.graficoCitasMeses || [];
    const datos = window.graficoCitasDatos || [];

    const graficoCitas = new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses,
            datasets: [{
                label: 'Ventas realizadas',
                data: datos,
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
                y: { beginAtZero: true }
            }
        }
    });
});
