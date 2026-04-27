let comparisonChart;

document.addEventListener('DOMContentLoaded', () => {
    initChart();

    const form = document.getElementById('telemetryForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('analyzeBtn');
        const status = document.getElementById('statusMessage');
        btn.disabled = true;
        btn.innerText = 'Analyzing...';
        status.innerText = '';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert to numbers
        Object.keys(data).forEach(key => {
            data[key] = parseFloat(data[key]);
        });

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const results = await response.json();
            updateDashboard(results);
            status.style.color = 'lightgreen';
            status.innerText = 'Analysis complete!';
        } catch (err) {
            console.error(err);
            status.style.color = 'tomato';
            status.innerText = `Error: ${err.message}`;
        } finally {
            btn.disabled = false;
            btn.innerText = 'Analyze Battery Health';
            setTimeout(() => { status.innerText = ''; }, 3000);
        }
    });
});

function updateDashboard(results) {
    // Update Cards
    document.getElementById('rf-soh').innerText = `${results.rf.soh.toFixed(2)}%`;
    document.getElementById('rf-rul').innerText = `${results.rf.rul} cycles`;

    document.getElementById('xgb-soh').innerText = `${results.xgb.soh.toFixed(2)}%`;
    document.getElementById('xgb-rul').innerText = `${results.xgb.rul} cycles`;

    document.getElementById('lgbm-soh').innerText = `${results.lgbm.soh.toFixed(2)}%`;
    document.getElementById('lgbm-rul').innerText = `${results.lgbm.rul} cycles`;

    // Update Chart
    comparisonChart.data.datasets[0].data = [
        results.rf.soh,
        results.xgb.soh,
        results.lgbm.soh
    ];
    comparisonChart.update();
}

function initChart() {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#334155';

    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Random Forest', 'XGBoost', 'LightGBM'],
            datasets: [{
                label: 'Predicted SoH (%)',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)', // RF
                    'rgba(245, 158, 11, 0.8)', // XGB
                    'rgba(139, 92, 246, 0.8)'  // LGBM
                ],
                borderWidth: 0,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'State of Health (SoH) Predictions by Model',
                    color: '#f8fafc',
                    font: { size: 16 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'State of Health (%)'
                    }
                }
            }
        }
    });
}