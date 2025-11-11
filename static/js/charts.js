// Fichier: static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer tous les canvas de graphiques
    const chartCanvases = document.querySelectorAll('canvas[data-chart-id]');
    
    chartCanvases.forEach(canvas => {
        const chartId = canvas.getAttribute('data-chart-id');
        
        // Récupérer les données du graphique via AJAX
        fetch(`/chart_data/${chartId}`)
            .then(response => response.json())
            .then(data => {
                const ctx = canvas.getContext('2d');
                
                // Configuration des couleurs
                const colors = [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)',
                    'rgba(255, 99, 255, 0.8)',
                    'rgba(99, 255, 132, 0.8)'
                ];
                
                // Configuration selon le type de graphique
                let chartConfig = {
                    type: data.chart_type,
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: data.chart_name,
                            data: data.values,
                            backgroundColor: data.chart_type === 'pie' || data.chart_type === 'doughnut' 
                                ? colors 
                                : 'rgba(54, 162, 235, 0.8)',
                            borderColor: data.chart_type === 'pie' || data.chart_type === 'doughnut'
                                ? colors.map(c => c.replace('0.8', '1'))
                                : 'rgba(54, 162, 235, 1)',
                            borderWidth: 2,
                            fill: data.chart_type === 'line' ? false : true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                display: data.chart_type === 'pie' || data.chart_type === 'doughnut',
                                position: 'bottom'
                            },
                            title: {
                                display: false
                            }
                        }
                    }
                };
                
                // Options spécifiques pour les graphiques à barres et lignes
                if (data.chart_type === 'bar' || data.chart_type === 'line') {
                    chartConfig.options.scales = {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    };
                }
                
                // Créer le graphique
                new Chart(ctx, chartConfig);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des données du graphique:', error);
                const parent = canvas.parentElement;
                parent.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement du graphique</div>';
            });
    });
});