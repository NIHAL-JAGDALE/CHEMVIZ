import React, { useRef, useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { useTheme } from '../App';
import { exportChartAsPNG, copyChartToClipboard } from '../utils/chartExport';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

function TypeDistributionChart({ data, title = 'type_distribution' }) {
    const { isDark } = useTheme();
    const chartRef = useRef(null);
    const [exportStatus, setExportStatus] = useState(null);
    const [showExportMenu, setShowExportMenu] = useState(false);

    if (!data || Object.keys(data).length === 0) {
        return <p style={{ color: 'var(--text-muted)' }}>No data available</p>;
    }

    const labels = Object.keys(data).map(key =>
        key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    );
    const values = Object.values(data);

    const chartData = {
        labels,
        datasets: [
            {
                label: 'Equipment Count',
                data: values,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.7)',
                    'rgba(14, 165, 233, 0.7)',
                    'rgba(244, 63, 94, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(236, 72, 153, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                ],
                borderColor: 'transparent',
                borderWidth: 0,
                borderRadius: 8,
                hoverBackgroundColor: isDark ? [
                    'rgba(165, 180, 252, 1)',
                    'rgba(125, 211, 252, 1)',
                    'rgba(253, 164, 182, 1)',
                    'rgba(216, 180, 254, 1)',
                    'rgba(249, 168, 212, 1)',
                    'rgba(147, 197, 253, 1)',
                ] : [
                    'rgba(67, 56, 202, 1)',
                    'rgba(3, 105, 161, 1)',
                    'rgba(190, 18, 60, 1)',
                    'rgba(126, 34, 206, 1)',
                    'rgba(190, 24, 93, 1)',
                    'rgba(29, 78, 216, 1)',
                ],
                barThickness: 45,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                cornerRadius: 12,
                padding: 12,
                displayColors: false,
                titleFont: { family: 'Inter', size: 13, weight: '600' },
                bodyFont: { family: 'Inter', size: 13 },
            },
        },
        scales: {
            x: {
                ticks: {
                    color: isDark ? '#ffffff' : '#1e293b',
                    font: { family: 'Inter', size: 12, weight: '600' },
                },
                grid: { display: false },
            },
            y: {
                ticks: {
                    color: isDark ? '#ffffff' : '#1e293b',
                    font: { family: 'Inter', size: 12, weight: '600' },
                    padding: 10,
                },
                grid: {
                    color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    drawBorder: false,
                },
                border: { display: false },
            },
        },
        animation: {
            duration: 2000,
            easing: 'easeOutQuart',
        },
    };

    const handleExport = (format) => {
        const chart = chartRef.current;
        if (!chart) return;

        const canvas = chart.canvas;
        const filename = `${title.replace(/\s+/g, '_')}_chart`;
        const bgColor = isDark ? '#1e293b' : '#ffffff';

        if (format === 'png') {
            exportChartAsPNG(canvas, filename, { backgroundColor: bgColor, scale: 2 });
            setExportStatus('Downloaded as PNG!');
        } else if (format === 'hd') {
            exportChartAsPNG(canvas, filename + '_hd', { backgroundColor: bgColor, scale: 4 });
            setExportStatus('Downloaded in HD!');
        }

        setShowExportMenu(false);
        setTimeout(() => setExportStatus(null), 2000);
    };

    const handleCopy = async () => {
        const chart = chartRef.current;
        if (!chart) return;

        const result = await copyChartToClipboard(chart.canvas);
        setExportStatus(result.message);
        setShowExportMenu(false);
        setTimeout(() => setExportStatus(null), 2000);
    };

    return (
        <div style={{ position: 'relative', height: '100%' }}>
            {/* Export Controls */}
            <div className="chart-export-controls">
                <button
                    className="chart-export-btn"
                    onClick={() => setShowExportMenu(!showExportMenu)}
                    title="Export Chart"
                >
                    📥
                </button>
                {showExportMenu && (
                    <div className="chart-export-menu">
                        <button onClick={() => handleExport('png')}>
                            <span>🖼️</span> PNG
                        </button>
                        <button onClick={() => handleExport('hd')}>
                            <span>✨</span> HD PNG
                        </button>
                        <button onClick={handleCopy}>
                            <span>📋</span> Copy
                        </button>
                    </div>
                )}
                {exportStatus && (
                    <div className="export-toast">
                        {exportStatus}
                    </div>
                )}
            </div>

            <Bar ref={chartRef} data={chartData} options={options} />
        </div>
    );
}

export default TypeDistributionChart;
