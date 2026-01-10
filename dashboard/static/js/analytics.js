// Analytics Dashboard - Chart.js visualizations
let assetChart, patternChart, timelineChart;

// Load all data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadOverview();
    loadAssetChart();
    loadPatternChart();
    loadTimelineChart();
});

async function loadOverview() {
    try {
        const res = await fetch('/api/analytics/overview');
        const data = await res.json();

        document.getElementById('total-signals').textContent = data.total_signals;
        document.getElementById('total-wins').textContent = data.total_wins;
        document.getElementById('total-losses').textContent = data.total_losses;
        document.getElementById('win-rate').textContent = `${data.win_rate}%`;
    } catch (err) {
        console.error('Failed to load overview:', err);
    }
}

async function loadAssetChart() {
    try {
        const res = await fetch('/api/analytics/by-asset');
        const data = await res.json();

        const ctx = document.getElementById('assetChart').getContext('2d');
        assetChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.asset),
                datasets: [
                    {
                        label: 'Wins',
                        data: data.map(d => d.wins),
                        backgroundColor: '#10b981'
                    },
                    {
                        label: 'Losses',
                        data: data.map(d => d.losses),
                        backgroundColor: '#ef4444'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#fff' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#9ca3b8' } },
                    y: { ticks: { color: '#9ca3b8' } }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load asset chart:', err);
    }
}

async function loadPatternChart() {
    try {
        const res = await fetch('/api/analytics/by-pattern');
        const data = await res.json();

        const ctx = document.getElementById('patternChart').getContext('2d');
        patternChart = new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: data.map(d => d.pattern),
                datasets: [{
                    label: 'Win Rate %',
                    data: data.map(d => d.win_rate),
                    backgroundColor: '#8b5cf6'
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: { labels: { color: '#fff' } }
                },
                scales: {
                    x: { ticks: { color: '#9ca3b8' } },
                    y: { ticks: { color: '#9ca3b8' } }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load pattern chart:', err);
    }
}

async function loadTimelineChart() {
    try {
        const res = await fetch('/api/analytics/timeline');
        const data = await res.json();

        const ctx = document.getElementById('timelineChart').getContext('2d');
        timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [
                    {
                        label: 'Win Rate %',
                        data: data.map(d => d.win_rate),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                },
                scales: {
                    x: { ticks: { color: '#9ca3b8' } },
                    y: {
                        ticks: { color: '#9ca3b8' },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load timeline chart:', err);
    }
}
