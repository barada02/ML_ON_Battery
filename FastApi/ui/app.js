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
    // Update SoH Cards
    document.getElementById('rf-soh').innerText = `${results.soh.rf.toFixed(2)}%`;
    document.getElementById('xgb-soh').innerText = `${results.soh.xgb.toFixed(2)}%`;
    document.getElementById('lgbm-soh').innerText = `${results.soh.lgbm.toFixed(2)}%`;

    // Update RUL Cards
    document.getElementById('catboost-rul').innerText = `${results.rul.catboost} cycles`;
    document.getElementById('lstm-rul').innerText = `${results.rul.lstm} cycles`;

    // Update Chart
    comparisonChart.data.datasets[0].data = [
        results.soh.rf,
        results.soh.xgb,
        results.soh.lgbm
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