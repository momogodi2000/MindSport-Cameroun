// static/js/admin_community.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggers = document.querySelectorAll('.tooltip');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            const tooltip = this.querySelector('.tooltip-text');
            tooltip.style.opacity = '1';
            tooltip.style.visibility = 'visible';
        });
        trigger.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.tooltip-text');
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
        });
    });

    // Initialize charts
    if (document.getElementById('categoryChart')) {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
                datasets: [{
                    label: 'Threads',
                    data: [12, 19, 3, 5],
                    backgroundColor: 'rgba(99, 102, 241, 0.6)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Add animation to cards on hover
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});