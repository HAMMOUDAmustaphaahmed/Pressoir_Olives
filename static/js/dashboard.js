
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Gestion des cartes interactives
    const statCards = document.querySelectorAll('.stats-card');
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            if (target) {
                window.location.href = target;
            }
        });
    });

    // Animation pour les indicateurs
    animateValue('total-tables', 0, {{ tables|length }}, 1000);

    // Fonction pour animer les valeurs numériques
    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        if (!obj) return;
        
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Chargement des statistiques en temps réel
    loadDashboardStats();

    function loadDashboardStats() {
        // Ici vous pouvez ajouter des appels AJAX pour des données en temps réel
        console.log('Chargement des statistiques du dashboard...');
    }

    // Gestion des notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container.mt-4').prepend(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Exporter les fonctions globalement si nécessaire
    window.dashboard = {
        showNotification: showNotification
    };
});