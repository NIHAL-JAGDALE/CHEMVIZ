/**
 * Anomaly Detection Utility
 * Uses IQR (Interquartile Range) method to detect statistical outliers
 */

/**
 * Calculate statistics for a numeric column
 * @param {Array} values - Array of numeric values
 * @returns {Object} Statistics including Q1, Q3, IQR, and bounds
 */
export function calculateStatistics(values) {
    const numericValues = values.filter(v => typeof v === 'number' && !isNaN(v));
    if (numericValues.length === 0) return null;

    const sorted = [...numericValues].sort((a, b) => a - b);
    const n = sorted.length;

    const q1 = sorted[Math.floor(n * 0.25)];
    const q3 = sorted[Math.floor(n * 0.75)];
    const iqr = q3 - q1;
    const median = sorted[Math.floor(n * 0.5)];
    const mean = numericValues.reduce((a, b) => a + b, 0) / n;

    // Using 1.5 * IQR for outlier detection (standard Tukey's fences)
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;

    // Extreme outliers use 3 * IQR
    const lowerExtreme = q1 - 3 * iqr;
    const upperExtreme = q3 + 3 * iqr;

    return {
        q1,
        q3,
        iqr,
        median,
        mean,
        min: sorted[0],
        max: sorted[n - 1],
        lowerBound,
        upperBound,
        lowerExtreme,
        upperExtreme,
        count: n
    };
}

/**
 * Detect if a value is an anomaly
 * @param {number} value - The value to check
 * @param {Object} stats - Statistics object from calculateStatistics
 * @returns {Object} Anomaly info { isAnomaly, type, severity }
 */
export function detectAnomaly(value, stats) {
    if (!stats || typeof value !== 'number' || isNaN(value)) {
        return { isAnomaly: false, type: null, severity: null };
    }

    // Extreme outlier (3 * IQR)
    if (value < stats.lowerExtreme) {
        return { isAnomaly: true, type: 'low', severity: 'extreme' };
    }
    if (value > stats.upperExtreme) {
        return { isAnomaly: true, type: 'high', severity: 'extreme' };
    }

    // Mild outlier (1.5 * IQR)
    if (value < stats.lowerBound) {
        return { isAnomaly: true, type: 'low', severity: 'mild' };
    }
    if (value > stats.upperBound) {
        return { isAnomaly: true, type: 'high', severity: 'mild' };
    }

    return { isAnomaly: false, type: null, severity: null };
}

/**
 * Analyze entire dataset for anomalies
 * @param {Array} data - Array of row objects
 * @param {Array} columns - Column names
 * @returns {Object} Anomaly analysis with column stats and anomaly count per column
 */
export function analyzeDataset(data, columns) {
    const numericColumns = columns.filter(col => {
        const values = data.map(row => row[col]);
        return values.some(v => typeof v === 'number' && !isNaN(v));
    });

    const columnStats = {};
    const anomalyCounts = {};

    numericColumns.forEach(col => {
        const values = data.map(row => row[col]);
        const stats = calculateStatistics(values);
        columnStats[col] = stats;

        let count = 0;
        data.forEach(row => {
            const anomaly = detectAnomaly(row[col], stats);
            if (anomaly.isAnomaly) count++;
        });
        anomalyCounts[col] = count;
    });

    return {
        columnStats,
        anomalyCounts,
        numericColumns,
        totalAnomalies: Object.values(anomalyCounts).reduce((a, b) => a + b, 0)
    };
}

/**
 * Get anomaly tooltip text
 * @param {Object} anomaly - Anomaly object from detectAnomaly
 * @param {Object} stats - Statistics object
 * @param {number} value - The actual value
 * @returns {string} Tooltip text
 */
export function getAnomalyTooltip(anomaly, stats, value) {
    if (!anomaly.isAnomaly) return '';

    const direction = anomaly.type === 'high' ? 'above' : 'below';
    const bound = anomaly.type === 'high' ? stats.upperBound : stats.lowerBound;
    const diff = Math.abs(value - bound).toFixed(2);
    const percentDiff = ((Math.abs(value - stats.mean) / stats.mean) * 100).toFixed(1);

    if (anomaly.severity === 'extreme') {
        return `⚠️ Extreme outlier! ${percentDiff}% ${direction} average (deviation: ${diff})`;
    }
    return `📊 Outlier detected: ${percentDiff}% ${direction} average`;
}
