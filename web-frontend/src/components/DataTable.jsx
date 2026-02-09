import React, { useState, useMemo } from 'react';
import { analyzeDataset, detectAnomaly, getAnomalyTooltip } from '../utils/anomalyDetection';

function DataTable({ columns, data }) {
    const [currentPage, setCurrentPage] = useState(1);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [showAnomalies, setShowAnomalies] = useState(true);
    const [hoveredCell, setHoveredCell] = useState(null);
    const rowsPerPage = 10;

    // Analyze dataset for anomalies
    const anomalyAnalysis = useMemo(() => {
        if (!data || data.length === 0 || !columns) return null;
        return analyzeDataset(data, columns);
    }, [data, columns]);

    // Sorting
    const sortedData = useMemo(() => {
        if (!sortConfig.key) return data;

        return [...data].sort((a, b) => {
            const aVal = a[sortConfig.key];
            const bVal = b[sortConfig.key];

            if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
    }, [data, sortConfig]);

    // Pagination
    const totalPages = Math.ceil(sortedData.length / rowsPerPage);
    const paginatedData = sortedData.slice(
        (currentPage - 1) * rowsPerPage,
        currentPage * rowsPerPage
    );

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    const getSortIndicator = (key) => {
        if (sortConfig.key !== key) return ' ↕';
        return sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
    };

    // Get cell anomaly info
    const getCellAnomalyInfo = (row, col) => {
        if (!showAnomalies || !anomalyAnalysis) return null;
        const stats = anomalyAnalysis.columnStats[col];
        if (!stats) return null;

        const value = row[col];
        const anomaly = detectAnomaly(value, stats);
        if (!anomaly.isAnomaly) return null;

        return {
            ...anomaly,
            tooltip: getAnomalyTooltip(anomaly, stats, value)
        };
    };

    // Get cell class based on anomaly
    const getCellClass = (anomalyInfo) => {
        if (!anomalyInfo) return '';
        if (anomalyInfo.severity === 'extreme') {
            return anomalyInfo.type === 'high' ? 'anomaly-extreme-high' : 'anomaly-extreme-low';
        }
        return anomalyInfo.type === 'high' ? 'anomaly-mild-high' : 'anomaly-mild-low';
    };

    return (
        <div>
            {/* Anomaly Controls & Stats */}
            {anomalyAnalysis && anomalyAnalysis.totalAnomalies > 0 && (
                <div className="anomaly-controls">
                    <div className="anomaly-toggle">
                        <label className="toggle-switch">
                            <input
                                type="checkbox"
                                checked={showAnomalies}
                                onChange={(e) => setShowAnomalies(e.target.checked)}
                            />
                            <span className="toggle-slider"></span>
                        </label>
                        <span>Highlight Anomalies</span>
                    </div>
                    <div className="anomaly-summary">
                        <span className="anomaly-badge">
                            ⚠️ {anomalyAnalysis.totalAnomalies} anomalies detected
                        </span>
                        <div className="anomaly-legend">
                            <span className="legend-item mild-high">▲ High</span>
                            <span className="legend-item mild-low">▼ Low</span>
                            <span className="legend-item extreme">⚠ Extreme</span>
                        </div>
                    </div>
                </div>
            )}

            <div className="data-table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                >
                                    <div className="th-content">
                                        <span>{col}{getSortIndicator(col)}</span>
                                        {anomalyAnalysis?.anomalyCounts[col] > 0 && showAnomalies && (
                                            <span className="column-anomaly-count" title={`${anomalyAnalysis.anomalyCounts[col]} anomalies in this column`}>
                                                {anomalyAnalysis.anomalyCounts[col]}
                                            </span>
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {paginatedData.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                                {columns.map((col) => {
                                    const anomalyInfo = getCellAnomalyInfo(row, col);
                                    const cellKey = `${rowIdx}-${col}`;
                                    const isHovered = hoveredCell === cellKey;

                                    return (
                                        <td
                                            key={col}
                                            className={getCellClass(anomalyInfo)}
                                            onMouseEnter={() => anomalyInfo && setHoveredCell(cellKey)}
                                            onMouseLeave={() => setHoveredCell(null)}
                                        >
                                            <div className="cell-content">
                                                {typeof row[col] === 'number'
                                                    ? row[col].toFixed(2)
                                                    : row[col]}
                                                {anomalyInfo && (
                                                    <span className="anomaly-indicator">
                                                        {anomalyInfo.severity === 'extreme' ? '⚠️' : (anomalyInfo.type === 'high' ? '↑' : '↓')}
                                                    </span>
                                                )}
                                            </div>
                                            {anomalyInfo && isHovered && (
                                                <div className="anomaly-tooltip">
                                                    {anomalyInfo.tooltip}
                                                </div>
                                            )}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '1rem',
                    marginTop: '1rem'
                }}>
                    <button
                        className="btn btn-outline"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </button>
                    <span style={{ color: 'var(--text-secondary)' }}>
                        Page {currentPage} of {totalPages}
                    </span>
                    <button
                        className="btn btn-outline"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}

export default DataTable;
