// Dashboard JavaScript for Analytics and Visualizations

let analyticsData = null;
let charts = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadAnalytics();
    setupROICalculator();
    setupChartControls();
});

function initializeDashboard() {
    // Add loading states to metric cards
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.classList.add('loading');
    });
    
    // Initialize charts with loading states
    initializeCharts();
}

function loadAnalytics() {
    fetch('/analytics')
        .then(response => response.json())
        .then(data => {
            analyticsData = data;
            updateMetrics(data);
            updateCharts(data);
            updateActivityTable(data);
            removeLoadingStates();
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            removeLoadingStates();
        });
}

function updateMetrics(data) {
    // Update total documents
    document.getElementById('totalDocuments').textContent = data.total_documents || 0;
    
    // Update average processing time
    const avgTime = data.average_processing_time || 0;
    document.getElementById('avgProcessingTime').textContent = `${avgTime.toFixed(1)}s`;
    
    // Update efficiency gain
    document.getElementById('efficiencyGain').textContent = `${data.efficiency_gain || 0}%`;
    
    // Update time saved
    const timeSaved = data.time_saved || 0;
    document.getElementById('timeSaved').textContent = `${timeSaved.toFixed(1)}h`;
    
    // Update monthly impact
    document.getElementById('monthlyImpact').textContent = data.monthly_impact || 0;
    
    // Update time saved per document
    const timeSavedPerDoc = 5 - (avgTime / 60); // 5 minutes manual - automated time
    document.getElementById('timeSavedPerDoc').textContent = `${timeSavedPerDoc.toFixed(2)} min/doc`;
    
    // Update monthly hours saved
    const monthlyHours = (data.monthly_impact || 0) * timeSavedPerDoc / 60;
    document.getElementById('monthlyHours').textContent = `${monthlyHours.toFixed(1)}h`;
    
    // Update cost savings (assuming $25/hour)
    const costSavings = monthlyHours * 25;
    document.getElementById('costSavings').textContent = `$${costSavings.toFixed(0)}`;
}

function initializeCharts() {
    // Document Types Chart
    const docTypesChart = document.getElementById('documentTypesChart');
    if (docTypesChart) {
        charts.documentTypes = Plotly.newPlot(docTypesChart, [], {}, {
            responsive: true,
            displayModeBar: false
        });
    }
    
    // Processing Time Chart
    const processingTimeChart = document.getElementById('processingTimeChart');
    if (processingTimeChart) {
        charts.processingTime = Plotly.newPlot(processingTimeChart, [], {}, {
            responsive: true,
            displayModeBar: false
        });
    }
}

function updateCharts(data) {
    updateDocumentTypesChart(data);
    updateProcessingTimeChart(data);
}

function updateDocumentTypesChart(data) {
    const chartData = data.chart_data || {};
    const documentTypes = chartData.document_types || {};
    
    const labels = Object.keys(documentTypes);
    const values = Object.values(documentTypes);
    
    if (labels.length === 0) {
        // Show empty state
        const emptyTrace = {
            x: ['No Data'],
            y: [1],
            type: 'bar',
            marker: { color: '#e2e8f0' }
        };
        
        Plotly.react('documentTypesChart', [emptyTrace], {
            title: 'No documents processed yet',
            xaxis: { visible: false },
            yaxis: { visible: false },
            margin: { t: 40, b: 40, l: 40, r: 40 }
        });
        return;
    }
    
    const trace = {
        labels: labels,
        values: values,
        type: 'pie',
        marker: {
            colors: ['#2563eb', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
            line: { color: '#ffffff', width: 2 }
        },
        textinfo: 'label+percent',
        textposition: 'outside',
        hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Document Types Distribution',
            font: { size: 16, color: '#1e293b' }
        },
        margin: { t: 40, b: 40, l: 40, r: 40 },
        showlegend: true,
        legend: {
            orientation: 'v',
            x: 1.05,
            y: 0.5
        }
    };
    
    Plotly.react('documentTypesChart', [trace], layout);
}

function updateProcessingTimeChart(data) {
    const chartData = data.chart_data || {};
    const processingTimes = chartData.processing_times || [];
    const dates = chartData.dates || [];
    
    if (processingTimes.length === 0) {
        // Show empty state
        const emptyTrace = {
            x: ['No Data'],
            y: [1],
            type: 'scatter',
            mode: 'lines',
            line: { color: '#e2e8f0' }
        };
        
        Plotly.react('processingTimeChart', [emptyTrace], {
            title: 'No processing data available',
            xaxis: { visible: false },
            yaxis: { visible: false },
            margin: { t: 40, b: 40, l: 40, r: 40 }
        });
        return;
    }
    
    // Create indices for x-axis if no dates
    const xData = dates.length > 0 ? dates : Array.from({ length: processingTimes.length }, (_, i) => i + 1);
    
    const trace = {
        x: xData,
        y: processingTimes,
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#2563eb',
            width: 3
        },
        marker: {
            color: '#2563eb',
            size: 6
        },
        hovertemplate: '<b>Processing Time</b><br>Time: %{y:.2f}s<br>Document: %{x}<extra></extra>',
        fill: 'tonexty'
    };
    
    const layout = {
        title: {
            text: 'Processing Time Trends',
            font: { size: 16, color: '#1e293b' }
        },
        xaxis: {
            title: dates.length > 0 ? 'Date' : 'Document Number',
            gridcolor: '#f1f5f9'
        },
        yaxis: {
            title: 'Processing Time (seconds)',
            gridcolor: '#f1f5f9'
        },
        margin: { t: 40, b: 60, l: 60, r: 40 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.react('processingTimeChart', [trace], layout);
}

function updateActivityTable(data) {
    const tableBody = document.getElementById('activityTableBody');
    
    if (!analyticsData || analyticsData.total_documents === 0) {
        tableBody.innerHTML = `
            <tr class="no-data">
                <td colspan="6">No processing activity yet. Upload a document to get started!</td>
            </tr>
        `;
        return;
    }
    
    // This would normally come from the backend
    // For demo purposes, we'll show sample data
    const sampleActivities = [
        {
            timestamp: new Date().toISOString(),
            type: 'Invoice',
            filename: 'sample_invoice.pdf',
            processingTime: 2.3,
            status: 'success'
        }
    ];
    
    tableBody.innerHTML = sampleActivities.map(activity => `
        <tr>
            <td>${formatDate(activity.timestamp)}</td>
            <td>${activity.type}</td>
            <td>${activity.filename}</td>
            <td>${activity.processingTime.toFixed(1)}s</td>
            <td><span class="status-badge ${activity.status}">${activity.status}</span></td>
            <td><a href="#" class="action-link">View Details</a></td>
        </tr>
    `).join('');
}

function setupChartControls() {
    // Document Types Chart Controls
    const docTypeControls = document.querySelectorAll('[data-chart="pie"], [data-chart="bar"]');
    docTypeControls.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from siblings
            this.parentElement.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update chart type
            updateDocumentTypesChart(analyticsData);
        });
    });
    
    // Processing Time Chart Controls
    const processingTimeControls = document.querySelectorAll('[data-chart="line"], [data-chart="area"]');
    processingTimeControls.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from siblings
            this.parentElement.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update chart type
            updateProcessingTimeChart(analyticsData);
        });
    });
}

function setupROICalculator() {
    const inputs = ['monthlyDocuments', 'hourlyCost', 'manualTime'];
    
    inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', calculateROI);
        }
    });
    
    // Initial calculation
    calculateROI();
}

function calculateROI() {
    const monthlyDocs = parseInt(document.getElementById('monthlyDocuments').value) || 0;
    const hourlyCost = parseFloat(document.getElementById('hourlyCost').value) || 0;
    const manualTime = parseFloat(document.getElementById('manualTime').value) || 0;
    
    // Calculate savings
    const automatedTime = 0.33; // 20 seconds in minutes
    const timeSavedPerDoc = manualTime - automatedTime;
    const monthlyTimeSaved = monthlyDocs * timeSavedPerDoc;
    const monthlySavings = monthlyTimeSaved * hourlyCost;
    const annualSavings = monthlySavings * 12;
    
    // Calculate ROI (assuming $1000 implementation cost)
    const implementationCost = 1000;
    const roi = implementationCost > 0 ? ((annualSavings - implementationCost) / implementationCost) * 100 : 0;
    
    // Update UI
    document.getElementById('monthlySavings').textContent = `$${monthlySavings.toFixed(0)}`;
    document.getElementById('annualSavings').textContent = `$${annualSavings.toFixed(0)}`;
    document.getElementById('roiPercentage').textContent = `${roi.toFixed(1)}%`;
    
    // Update ROI color based on value
    const roiElement = document.getElementById('roiPercentage');
    if (roi > 100) {
        roiElement.style.color = '#10b981';
    } else if (roi > 0) {
        roiElement.style.color = '#f59e0b';
    } else {
        roiElement.style.color = '#ef4444';
    }
}

function refreshDashboard() {
    // Add loading states
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.classList.add('loading');
    });
    
    // Reload data
    loadAnalytics();
}

function exportAnalytics() {
    // Create a comprehensive report
    const reportData = {
        timestamp: new Date().toISOString(),
        metrics: analyticsData,
        generatedBy: 'Innovo IDP Dashboard'
    };
    
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `innovo_analytics_report_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
}

function removeLoadingStates() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => {
        el.classList.remove('loading');
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Add CSS for loading states and animations
const style = document.createElement('style');
style.textContent = `
    .loading {
        position: relative;
        overflow: hidden;
    }
    
    .loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        animation: loading 1.5s infinite;
    }
    
    @keyframes loading {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .metric-card {
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .chart-card {
        transition: all 0.3s ease;
    }
    
    .chart-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .impact-card {
        transition: all 0.3s ease;
    }
    
    .impact-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
