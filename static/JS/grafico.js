document.addEventListener("DOMContentLoaded", function () {
    console.log(sectorCosts);  // Verifique os dados no console

    // Verifique se 'sectorCosts' é um array e se contém dados
    if (Array.isArray(sectorCosts) && sectorCosts.length > 0) {
        const sectors = sectorCosts.map(item => item.sector);
        const costs = sectorCosts.map(item => item.total_cost);

        const ctx = document.getElementById('sectorChart').getContext('2d');
        const sectorChart = new Chart(ctx, {
            type: 'bar', // Tipo de gráfico
            data: {
                labels: sectors, // Nomes dos setores
                datasets: [{
                    label: 'Custo Total por Setor',
                    data: costs, // Custos correspondentes
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Custo Total por Setor' }
                }
            }
        });
    } else {
        console.error("Dados inválidos para sectorCosts.");
    }
});
